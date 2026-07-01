# claude-qlik-docs — Project Guide for Claude Code

This repo is the **build pipeline** for the `qlik-talend` documentation skill. It
crawls the official Qlik Talend docs (help.qlik.com/talend) **and the Qlik Talend
Cloud Data Integration docs in Qlik Cloud Help (help.qlik.com/en-US/cloud-services)**,
distils them into a citation-exact skill, and packages that skill for Claude Code / claude.ai.

It is the companion repo of [`cimt-claude-talend`](https://github.com/mkcimt/cimt-claude-talend)
(the "kit"). The kit's `setup/update.py` pulls this repo too, so changes pushed here
reach every kit user on their next update.

## Core principle — the pipeline is pure Python, no LLM. Keep it that way.

`crawler/` (fetch + extract) and `distill/` (cluster + build_topics) are **deterministic
Python**. Nothing is paraphrased; topic files are *citation-perfect by construction*
(TL;DR = first sentence, procedure outline = literal headings, every claim maps to a raw
file + canonical URL). **Do not introduce an LLM into the extraction/distillation path** —
it would add hallucination and citation-drift, which is exactly what this design avoids.
The only dependencies are `beautifulsoup4`, `httpx`, `lxml`, `markdownify`, `pyyaml`, `tenacity`.

## Two doc sources — Talend docs + Qlik Cloud Help

The pipeline crawls **two** documentation systems, unified downstream because both
are MadCap Flare output with the same `div#topicContent` container (so `extract.py`
and the whole distill/build path are source-agnostic):

1. **Talend docs** — `help.qlik.com/talend/en-US/<guide>/<version>/<page>`. Discovered
   via the Talend **sitemap-index** (`config.PRODUCT_SITEMAPS` → per-guide sub-sitemaps).
   Studio's R-code is resolved dynamically. Groups: studio, tmc, remote-engine,
   installation, sdlc-cicd, cloud-platform, data-apps, api, esb.
2. **Qlik Cloud Help** — `help.qlik.com/en-US/cloud-services/.../Content/Sense_Hub/
   DataIntegration/<Section>/<page>.htm`. This is where Qlik Talend Cloud's "agentic
   data engineering" docs live (Open Lakehouse, declarative/AI-assisted pipelines,
   connections, GenAI, API Designer, DI platform). Discovered via a **single flat
   url-set sitemap** (`config.CLOUD_SERVICES_SITEMAP`); pages route to a group by their
   `/DataIntegration/<Section>/` segment (`config.CLOUD_PRODUCT_SECTIONS`). Version is
   the synthetic string `Cloud`; `product_slug` is the section (e.g. `lakehouse`), and
   `page_slug` folds any sub-folders with `__`. Frontmatter carries `source: cloud-services`.
   robots.txt here requests `Crawl-delay: 5` — crawl these groups with `--delay 5`.

`config.ALL_GROUPS` is the union of both; `--product` choices and `doctor` use it.
URL parsing for both schemes lives in `crawler/extract.py:_parse_url` (dispatches on
the URL) and is reused by `distill/cluster.py` — do not re-hardcode a URL regex elsewhere.

## What is tracked vs. generated

Crawled / derived content is **gitignored** (Qlik copyright — not redistributable):
`skill-output/qlik-talend/raw/`, `topics/`, `index/`, `index.md`, `meta/` (manifest),
and `topic_map.yaml`. They are regenerated locally per user via `make crawl && make build`.

**Tracked** (so editing these is what actually ships): all code, plus
`skill-output/qlik-talend/SKILL.md` and `README.md`.

## After a pull or update — ALWAYS check for drift first

Crawled/derived content is gitignored (see above), so a `git pull` — or the
kit's `setup/update.py` pulling this repo — advances **code and config only**.
The local crawl, build, and installed Claude Code skill do **not** come with it.
This silently desyncs three things, and a new Claude session will serve stale or
partial content without any error:

1. `crawler/config.py` may have gained a group or guides that were never crawled
   / built on this machine → the skill is missing content its `SKILL.md` claims.
2. The built `SKILL.md` / `index` may predate the config change.
3. `~/.claude/skills/qlik-talend` may still point at a **different / older
   checkout** (e.g. after a repo move or a second clone), so the live skill
   isn't even this one.

**Therefore, immediately after any pull/update of this repo — and before
rebuilding or trusting the skill — run the drift check:**

```
uv run python tasks.py doctor      # or: make doctor
```

It verifies: every group in `ALL_GROUPS` (both doc sources) is present in the local
build, studio is a single R-code, and `~/.claude/skills/qlik-talend` resolves to *this*
checkout. Resolve every `WARN` (each prints its exact fix) before proceeding —
the usual remedy is `tasks.py crawl --product <group>` → `tasks.py build` →
`tasks.py cc-install`. (Caveat: doctor derives "built groups" from the crawl
**manifest**, i.e. it checks *crawled*, not *distilled into topic_map.yaml* — a
crawled-but-not-built group can still pass. If a group is missing from `SKILL.md`/
`index.md` yet doctor is green, check `topic_map.yaml` and re-run `tasks.py build`.)

## Adding or changing a guide — the complete checklist

The canonical step list lives in the docstring of [`crawler/config.py`](crawler/config.py).
Follow it exactly. The trap is that **several spots are hand-maintained and easy to miss** —
forgetting one leaves a silent gap (empty cell, stale "out of scope", missing trigger keyword):

1. **Verify the sitemap name exists** before adding it — don't guess:
   `curl -s https://help.qlik.com/talend/sitemap.xml | grep -oE 'sitemap_<slug>[^<]*\.xml'`.
   Use `<slug>_Cloud` or `<slug>_8.0` (the part before `_en-US.xml`).
2. **`crawler/config.py`** — for a **Talend** group add the sitemap(s) to `PRODUCT_SITEMAPS`;
   for a **Cloud Help** group add the exact `/DataIntegration/<Section>/` segment(s) to
   `CLOUD_PRODUCT_SECTIONS` (verify against `sitemap_cloud-services_en-US.xml` first). Either
   way add the group to `GROUP_LABELS` and `GROUP_VERSIONS` (use `Cloud` for Cloud Help groups).
   (Also add the entry-page URLs to the docstring list for human readers.)
3. **`package/build_index.py` → `GROUP_DESCRIPTIONS`** — add a one-line blurb for the new
   group. **Easy to forget**; if missed, the Description column in `index.md` is blank.
4. **`skill-output/qlik-talend/SKILL.md`** — hand-edit the parts that are NOT auto-generated:
   the `description:` frontmatter (claude.ai trigger keywords), the "When to use this skill"
   bullets, and the "Out of scope" line (remove the product if it was listed there).
5. **`README.md`** — hand-edit the "### Out of scope (current)" list (remove the product).
6. **Run the crawl + build** (see below), then commit.

Auto-generated by `package/update_meta.py` during `make build` — **do not hand-edit**:
the SKILL.md coverage table rows, and the README "Integrated documentation guides" guide list.

## Crawl mechanics & gotchas

- **Crawl only what you added** with `--product`: `uv run python -m crawler.run --product <group> --delay 0.5`.
  `--product` is repeatable. A no-filter crawl issues an HTTP *conditional* GET for **every**
  cached page (etag/last-modified) with the full delay each — so it re-walks all ~4–5k pages
  (~30 min) even though nothing new is fetched. Targeted crawl skips that.
- **Cloud Help groups (`cloud-*`) use `--delay 5`** (robots.txt `Crawl-delay: 5`), e.g.
  `uv run python -m crawler.run --product cloud-lakehouse --product cloud-pipelines … --delay 5`.
  They all read the one `sitemap_cloud-services_en-US.xml` and are bucketed by section, so the
  `[run] N unique URLs across M sitemaps/sections` line counts sections, not sub-sitemaps. Full
  DataIntegration (~617 pages) is ~50 min at delay 5. There is no R-code subtlety for Cloud groups.
- **Studio is special — exactly ONE R-code must exist in the mirror.** `studio-user-guide_<latest-r>`
  resolves the newest R-code at crawl time and writes to `raw/studio/studio-user-guide/<R>/`.
  A killed/partial crawl, or crawling on two different days, can leave **multiple R-code dirs**
  (e.g. `8.0-R2026-04` and a partial `8.0-R2026-05`). The build then **double-counts** studio
  and the skill ships two versions. Before building, check:
  `ls raw/studio/studio-user-guide/` — if more than one R-code, delete the unwanted/partial one
  from **both** `raw/.../<R>/` **and** the matching manifest entries, then also remove the stale
  `topics/studio/studio-user-guide/<R>/` dir, then rebuild. (A clean `make fresh` avoids this by
  wiping first, but re-fetches everything.)
- **Exit code 2 from the crawler = some pages failed** (usually a couple of 404 section-landing
  pages in Qlik's sitemap, e.g. `esb-service-developer-guide/8.0/apis`). Check the `404`/`FAIL`
  lines; a handful of 404s on parent pages is normal and harmless.

## Build & verify

- `make build` = cluster → topics → index → validate → update_meta + citation validation.
- **`update_meta` printing `WARNING: ... section not found — skipped` + `unchanged` is NOT an error.**
  It means the section was already up to date (the code reports "no substitution" as "not found").
  Only worry if the content is actually wrong.
- After a build, sanity-check:
  - per-group page/topic counts are plausible and **studio is a single R-code** (no double-count);
  - `all citations valid` from the citation validator;
  - the new group appears with a non-empty Description in `index.md`, a coverage row in `SKILL.md`,
    and a guide block + corrected "out of scope" in `README.md`.
- Cross-check counts independently from `topic_map.yaml` if a number looks off (group → `page_count`
  + `len(topics)`).

## Git workflow

- Work on a **feature branch**, never commit directly to `main`. Commit under the cimt identity
  (`mirco.kriesten@cimt-ag.de` — set repo-locally).
- **Never commit crawled/derived content or secrets.** The gitignore already excludes the mirror;
  keep it that way. No Qlik raw pages, no PATs/tokens.
- Claude writes and commits; **ask before pushing** unless told otherwise.
