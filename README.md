# claude-qlik-docs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A pipeline that turns the public [Qlik Talend documentation](https://help.qlik.com/talend/)
— **plus the Qlik Talend Cloud Data Integration docs in [Qlik Cloud Help](https://help.qlik.com/en-US/cloud-services/)**
(Open Lakehouse, declarative/AI-assisted pipelines, and the rest of the "agentic
data engineering" release) — into a token-efficient knowledge base for Claude. Two
Qlik doc sources, three distribution targets — local Claude Code, claude.ai Skill,
claude.ai Project Knowledge — sharing the same distilled content but packaged for the
mechanics of each surface.

Why this exists: out-of-the-box, Claude either answers Talend questions from
stale model knowledge or requires you to attach the entire Qlik docs to
every prompt. This project produces a structured, versioned reference that
Claude pulls in progressively — typical Talend question costs **25–40 KB of
context**, not 14 MB.

## What it does, end to end

1. **Crawls** all relevant Talend sub-sitemaps (Studio 8.x, TMC, Remote Engine
   Linux/Windows, Dynamic Engine, installation, SDLC/CI-CD, Cloud platform, ESB,
   APIs, Data apps) **and the Qlik Cloud Help Data-Integration subtree** (Open
   Lakehouse, pipelines, connections, GenAI, API Designer, DI platform) with
   `httpx + BeautifulSoup + markdownify`. Honours `robots.txt` (incl. the Cloud
   Help `Crawl-delay: 5`), throttles, retries, hash-caches.
2. **Clusters and distils**: 3,261 raw pages → 497 topic clusters. Each
   topic gets a markdown file with TL;DR, procedure outline, notes /
   restrictions, and a citations table that maps every anchor exactly to
   its raw file and canonical URL. Distillation is **mechanical** — no LLM
   in the loop, so no hallucination risk.
3. **Builds three distribution artefacts** from the same distilled content:
   one for the Claude Code CLI, one for claude.ai as a Skill, one for
   claude.ai as Project Knowledge.

## The three distribution modes

All three are produced from the same source. Pick whichever fits your
workflow — you can also use several in parallel.

| Mode | Surface | Activation | Build target | Output |
|------|---------|------------|--------------|--------|
| **Claude Code skill** | Claude Code CLI | **Auto-triggered** by SKILL description | `make cc-install` | symlink `~/.claude/skills/qlik-talend` |
| **Chat Skill** | claude.ai (Settings → Skills) | **Slash command + auto-trigger** | `make chat-bundle` | `dist/qlik-talend-chat.zip` (~300 KB, 37 files) |
| **Project Knowledge** | claude.ai Projects | **Implicit** via Custom Instructions | `make project-bundle` | `dist/qlik-talend-project/` (~1.8 MB folder) |

### How each mode actually works

**Claude Code skill.** At session start the Claude Code harness scans
`~/.claude/skills/*/SKILL.md` and loads only name + description (~80 tokens
each) into the system prompt. The model decides per-turn whether the skill
is relevant; if it is, it reads the full SKILL.md and follows its routing
instructions. Detail look-ups go straight to the local raw markdown files.

**Chat Skill (claude.ai).** You upload the ZIP under Settings → Skills.
The skill then appears in the `/`-picker (mode label: *"Slash command +
auto"*), so it can be invoked **two ways**: explicitly via
`/qlik-talend`, or **auto-triggered** by Claude when the user's question
matches the SKILL description. The description in `SKILL.md` therefore
serves both as the slash-picker label and as the auto-trigger signal —
which is why it lists Talend keywords explicitly. There are no raw files
in the bundle; citations point at canonical URLs on `help.qlik.com/talend`,
and Claude `WebFetch`es them when verbatim text is needed.

**Project Knowledge.** You create a Project in claude.ai, paste the
generated `PROJECT-INSTRUCTIONS.md` into the Project's Custom Instructions
field, and upload the rest of the folder as Project Knowledge. From then
on, every chat in that Project has the Talend reference available
implicitly — no slash command. Like the Chat Skill, citations point at
URLs, and `WebFetch` is the path to verbatim text.

### Trade-offs side by side

| | Claude Code | Chat Skill | Project Knowledge |
|---|---|---|---|
| **Activation** | Implicit (description match) | `/qlik-talend` **or** auto-trigger via description | Implicit (Project Instructions) |
| **Onboarding cost** | One-time `make cc-install` | Upload ZIP per machine | Project setup per Project |
| **Verbatim-text fidelity** | Highest — local raw markdown always available | Good — `WebFetch` of canonical URL | Good — `WebFetch` of canonical URL |
| **Offline use** | Yes | No (URL fetches need network) | No |
| **Typical context per question** | ~25–40 KB | ~25–40 KB + occasional `WebFetch` | ~25–40 KB + Custom Instructions baseline (~3 KB) |
| **Persistent baseline cost** | ~80 tokens per session (description) | ~80 tokens in slash picker (only if Skills feature loaded) | Custom Instructions reload every chat in Project |
| **Cross-project / cross-team reuse** | Per-developer install | Once per workspace | Once per Project |
| **Update flow** | `make fresh && make cc-install` | `make chat-bundle` + re-upload | `make project-bundle` + re-upload |
| **Best for** | Daily local development | Ad-hoc Talend questions in Chat | Long-running Project where Talend is a recurring topic |

### Quality differences

The **distilled topic content is identical** across all three modes — same
TL;DRs, same procedure outlines, same notes, same citation anchors. The
only quality differential comes from the **detail look-up path**:

- **Claude Code** can open the raw `.md` file directly. Zero latency, no
  network, exact wording always available.
- **Chat Skill / Project Knowledge** must `WebFetch` the canonical URL when
  verbatim text is needed. This is correct as long as the Qlik page hasn't
  changed since the crawl — which is almost always true within a major
  version, but can drift between R-codes for Studio.

For all three modes, claims that the topic file already states
authoritatively (TL;DR, procedure outline, notes, version constraints) are
identical. The trade-off only shows up when you ask "give me the exact
parameter list for this component" — that's when local raw files vs.
WebFetch matters.

## Setup

Works on **macOS**, **Linux**, and **Windows** (native — no WSL required).
All targets are driven by [`tasks.py`](tasks.py); the [`Makefile`](Makefile)
is a thin convenience wrapper for users with `make` installed.

### macOS

```bash
brew install uv
git clone https://github.com/mkcimt/claude-qlik-docs.git
cd claude-qlik-docs
uv sync
make fresh                  # crawl (~30 min) + build + cc-install
```

### Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/mkcimt/claude-qlik-docs.git
cd claude-qlik-docs
uv sync
make fresh
```

### Windows (PowerShell, no WSL)

```powershell
# Install uv (one-time, https://docs.astral.sh/uv/getting-started/installation/)
winget install --id=astral-sh.uv -e
# or: irm https://astral.sh/uv/install.ps1 | iex

git clone https://github.com/mkcimt/claude-qlik-docs.git
cd claude-qlik-docs
uv sync
uv run python tasks.py fresh
```

`tasks.py` provides the same target set as `make` on the other platforms:
`crawl, cluster, topics, index, validate, build, test, cc-install,
cc-uninstall, chat-bundle, project-bundle, fresh, clean, help`.

On Windows `cc-install` creates a **directory junction** instead of a
symlink — this works without Developer Mode or admin privileges. From
Claude Code's perspective the result is identical to the macOS/Linux
symlink.

### What `fresh` does (any OS)

1. Crawl the configured guides on `help.qlik.com/talend` (~30 min,
   ~3,300 pages, throttled to 1 req/s).
2. Build the distilled artefacts (cluster → topics → indexes → validate).
3. Install the Claude Code skill into your user config (symlink on
   macOS/Linux, junction on Windows).

If you only need one of the other modes, build it separately:

```bash
# macOS / Linux:
make build
make chat-bundle           # → dist/qlik-talend-chat.zip
make project-bundle        # → dist/qlik-talend-project/

# Windows:
uv run python tasks.py build
uv run python tasks.py chat-bundle
uv run python tasks.py project-bundle
```

## Mode-specific instructions

### Claude Code

```bash
# macOS / Linux:
make cc-install      # symlink skill-output/qlik-talend → ~/.claude/skills/qlik-talend
make cc-uninstall    # remove the symlink

# Windows:
uv run python tasks.py cc-install      # directory junction (no admin rights needed)
uv run python tasks.py cc-uninstall
```

After install, open a **new** Claude Code session and just ask a Talend
question. The skill triggers automatically.

### Chat Skill (claude.ai)

```bash
make chat-bundle     # → dist/qlik-talend-chat.zip
```

In claude.ai: **Settings → Skills → Upload** and pick the ZIP. In any chat,
either type `/qlik-talend` to invoke it explicitly, or just ask a Talend
question — the skill description lets Claude auto-trigger it (mode label
in the Skills UI: *"Slash command + auto"*).

The bundle has no raw files (Chat has no filesystem) and consolidates
topics per guide+version into single files with anchored sections, to fit
under claude.ai's 200-file Skill-upload limit.

### Project Knowledge (claude.ai)

```bash
make project-bundle  # → dist/qlik-talend-project/  (folder, no ZIP)
```

1. Create a new Project in claude.ai.
2. Open `dist/qlik-talend-project/PROJECT-INSTRUCTIONS.md`, copy its
   contents, paste into the Project's **Custom Instructions** field.
3. Upload the rest of the folder (`index.md`, `index/`, `topics/`,
   `BUNDLE-INFO.txt`, `README-FOR-USER.md`) as Project Knowledge.

Every chat in that Project then has the Talend reference available without
any slash command.

## Tests

```bash
make test            # 44 unit tests, no network, ~1 s
```

Tests cover the pure transforms: URL parsing, HTML extraction (with a
title-bug regression test), topic clustering heuristics, citation
validation, chat-bundle topic transformer. Heuristic boundaries (regex
patterns, prefix lists, title cleanup) have regression tests so tuning
them later doesn't silently break existing behaviour.

## Re-crawl

```bash
make crawl           # idempotent; ETag/hash cache saves bandwidth
make build           # rebuild topics + index
make chat-bundle     # rebuild Chat ZIP if needed
make project-bundle  # rebuild Project folder if needed
```

## License / redistribution

The crawled Qlik content is **not** in this repo — it's `.gitignore`d. The
repo ships only **code and skill scaffolding** (e.g. `SKILL.md`,
`PROJECT-INSTRUCTIONS.md`). Each user crawls locally — comparable to a
`pip install`, not a content mirror.

## Integrated documentation guides

Each line below is one **canonical Qlik Talend doc entry page**; all
sub-pages of that guide are crawled via Qlik's official sitemap (so
coverage is essentially complete — no recursive link-walking needed).
The current build covers **5,520 pages → 833 topics** across these guides:

**studio** (Talend Studio 8.0 — latest R-code at crawl):
- https://help.qlik.com/talend/en-US/studio-user-guide/8.0-R2026-04/
- https://help.qlik.com/talend/en-US/discovering-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/creating-using-metadata-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/using-context-variables-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/studio-getting-started-guide-data-integration/8.0/
- https://help.qlik.com/talend/en-US/joining-two-data-sources-tmap-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/reading-a-file-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/sorting-a-file-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/access-secure-services-with-studio-and-runtime/8.0/
- https://help.qlik.com/talend/en-US/studio-components-availability/8.0/

**tmc** (Talend Management Console, Cloud):
- https://help.qlik.com/talend/en-US/management-console-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/management-console-with-pipeline-designer/Cloud/
- https://help.qlik.com/talend/en-US/tmc-account-limits/Cloud/

**remote-engine** (Remote Engine + Dynamic Engine, Cloud):
- https://help.qlik.com/talend/en-US/remote-engine-user-guide-linux/Cloud/
- https://help.qlik.com/talend/en-US/remote-engine-user-guide-windows/Cloud/
- https://help.qlik.com/talend/en-US/remote-engine-gen2-quick-start-guide/Cloud/
- https://help.qlik.com/talend/en-US/dynamic-engine-configuration-guide/Cloud/

**installation** (Cloud + 8.0):
- https://help.qlik.com/talend/en-US/installation-guide-linux/Cloud/
- https://help.qlik.com/talend/en-US/installation-guide-windows/Cloud/
- https://help.qlik.com/talend/en-US/installation-guide-linux/8.0/
- https://help.qlik.com/talend/en-US/installation-guide-windows/8.0/
- https://help.qlik.com/talend/en-US/hybrid-installation-guide-linux/Cloud/
- https://help.qlik.com/talend/en-US/hybrid-installation-guide-windows/Cloud/
- https://help.qlik.com/talend/en-US/migration-upgrade-guide/8.0/

**sdlc-cicd** (SDLC / CI-CD):
- https://help.qlik.com/talend/en-US/software-dev-lifecycle-best-practices-guide/8.0/
- https://help.qlik.com/talend/en-US/development-operational-management/Cloud/

**cloud-platform** (Talend Cloud platform basics):
- https://help.qlik.com/talend/en-US/talend-cloud-getting-started/Cloud/
- https://help.qlik.com/talend/en-US/talend-glossary/Cloud/

**data-apps** (Talend Data Stewardship + Data Preparation, Cloud):
- https://help.qlik.com/talend/en-US/data-stewardship-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/data-stewardship-getting-started-guide/Cloud/
- https://help.qlik.com/talend/en-US/data-stewardship-examples/Cloud/
- https://help.qlik.com/talend/en-US/data-stewardship-components-query-language/8.0/
- https://help.qlik.com/talend/en-US/data-preparation-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/data-preparation-getting-started/Cloud/
- https://help.qlik.com/talend/en-US/data-shaping-language-reference-guide/8.0/

**api** (Talend Cloud APIs + API Designer / Portal / Services / Tester):
- https://help.qlik.com/talend/en-US/api-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/api-designer-getting-started-guide/Cloud/
- https://help.qlik.com/talend/en-US/api-designer-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/api-portal-deployment-guide/Cloud/
- https://help.qlik.com/talend/en-US/api-services-getting-started-guide-api-services-platform/Cloud/
- https://help.qlik.com/talend/en-US/api-tester-user-guide/Cloud/

**esb** (Talend ESB 8.0 — Camel routes, CXF services, Karaf container, microservices, Activity Monitoring Console):
- https://help.qlik.com/talend/en-US/talend-esb/8.0/
- https://help.qlik.com/talend/en-US/esb-developer-guide/8.0/
- https://help.qlik.com/talend/en-US/esb-service-developer-guide/8.0/
- https://help.qlik.com/talend/en-US/esb-container-administration-guide/8.0/
- https://help.qlik.com/talend/en-US/esb-sts-user-guide/8.0/
- https://help.qlik.com/talend/en-US/esb-infra-services-configuration-guide/8.0/
- https://help.qlik.com/talend/en-US/esb-system-management/8.0/
- https://help.qlik.com/talend/en-US/esb-best-practices/8.0/
- https://help.qlik.com/talend/en-US/studio-getting-started-guide-esb/8.0/
- https://help.qlik.com/talend/en-US/studio-getting-started-guide-data-services-platform/8.0/
- https://help.qlik.com/talend/en-US/esb-glossary/8.0/
- https://help.qlik.com/talend/en-US/activity-monitoring-console-user-guide/8.0/
- https://help.qlik.com/talend/en-US/microservice-introduction/8.0/
- https://help.qlik.com/talend/en-US/microservice-best-practice/8.0/
- https://help.qlik.com/talend/en-US/esb-runtime-auto-scaling-on-aws/8.0/
- https://help.qlik.com/talend/en-US/configure-multiple-container/8.0/
- https://help.qlik.com/talend/en-US/use-syncope-with-esb/8.0/
- https://help.qlik.com/talend/en-US/core-framework-updates-of-esb-801-r2023-08/8.0/
- https://help.qlik.com/talend/en-US/data-service-route-example/8.0/
- https://help.qlik.com/talend/en-US/esb-read-hl7-message/8.0/
- https://help.qlik.com/talend/en-US/web-service-proxy/8.0/

**cloud-lakehouse** (Qlik Talend Cloud — Open Lakehouse (Apache Iceberg, streaming, compute)):
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Lakehouse/s3-bucket.htm

**cloud-pipelines** (Qlik Talend Cloud — transformations, declarative/AI-assisted pipelines, data products & marts, replication):
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Transformation/Add-columns.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/DeclarativePipelines/Declarative-pipelines-overview.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/DataProducts/Data-products.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/DataMarts/DataMarts.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/KnowledgeMart/Test-Assistant.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Replicating/ddl_history.htm

**cloud-connections** (Qlik Talend Cloud — source/target & SaaS-application connections, landing, file storage):
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/SourcesConnections/SSH-tunnel.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/TargetConnections/aws-target.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/WebApplications/Connecting-Dixa.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Landing/Lake-landing.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/FileStorage/connecting-ftp.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Storage/dataset-tables.htm

**cloud-genai** (Qlik Talend Cloud — GenAI: LLM connections & vector databases):
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/LLMConnections/connecting-openAI.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/VectorDBs/connecting-pinecone.htm

**cloud-api-designer** (Qlik Talend Cloud — API Designer (Data Integration)):
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/APIDesigner/IntroductionToApiDesigner.htm

**cloud-di-platform** (Qlik Talend Cloud — Data Integration platform: intro, spaces, deploy, stewardship, catalog):
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Introduction/Getting-started-QTC.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Onboarding/Onboarding-data.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Deploying/Troubleshooting-data-assets.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/DataSpaces/working-spaces.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/DataStewardship/Creating-sprint.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Catalog/Understanding-data-catalog.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/VersionControl/Project-version-control.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Marketplace/Updating-the-marketplace.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Analytics/Developing-app-with-datasets.htm
The same list — with comments on the doubled `/talend/talend/...` robots
quirk and "how to add another guide" — also lives in the docstring of
[`crawler/config.py`](crawler/config.py).

### Out of scope (current)

- Components reference (Studio components / connectors)
- Data Quality, Data Catalog
- MDM, Data Inventory
- Talend 7.x

## Architecture

```
crawler/       # discovery / fetch / extract / run / validate
distill/       # cluster / build_topics / validate_citations
package/       # build_index, build_chat_bundle, build_project_bundle, _consolidate
spike/         # MS0 discovery findings + extract spike
tests/         # 44 unit tests on pure transforms
skill-output/  # build artefact → linked into ~/.claude/skills/ via cc-install
dist/          # claude.ai distribution → ZIP for Skill, folder for Project
```

## Extending

To cover additional Talend products or other Qlik docs (Sense, QlikView):

1. Look up sub-sitemap names in `https://help.qlik.com/talend/sitemap.xml`
   (or `https://help.qlik.com/sitemap.xml`).
2. For **Talend docs**, add the sitemap name(s) to `PRODUCT_SITEMAPS` in
   `crawler/config.py`. For **Qlik Cloud Help** (`/cloud-services/`), add the
   `/DataIntegration/<Section>/` segment(s) to `CLOUD_PRODUCT_SECTIONS` instead —
   the crawler already knows the cloud-services sitemap and URL scheme.
3. Add the group to `GROUP_LABELS` / `GROUP_VERSIONS` and a blurb to
   `GROUP_DESCRIPTIONS`, then `make fresh`.

## Roadmap / next milestones

Tracked here at a high level — concrete plans live in
`~/.claude/plans/ich-will-ein-tool-linear-sundae.md` (local, not in the
repo).

### MS2 — quality polish

- LLM-based distillation as an additional topic layer for sharper TL;DRs
  and better-structured procedure summaries (current build is purely
  mechanical — zero hallucination risk, but lower compression).
- Sharper procedure-outline extractor: skip the standard Qlik scaffolding
  headings (`Procedure`, `In this section`) and surface H4 / strong-text
  inside the body.
- Multi-line Note / Restriction extractor: current regex stops at the first
  newline, missing the second clause of two-sentence notes.

### MS3 — operations

- Re-crawl diff report: surface added / removed / changed pages between
  snapshots, with a per-topic delta digest.
- Optional CI workflow that crawls monthly and publishes a versioned
  bundle (Chat ZIP + Project folder) as a GitHub Release artefact, so
  team-mates can download a fresh build without running the crawler
  themselves.

### MS4 — coverage expansion

- Components reference (Studio components / connectors). Out of MS1 because
  it would multiply the page count by ~5×; deserves its own sub-skill.
- Talend 7.x as a parallel version slot in the same skill (frontmatter
  already supports it; just needs sitemap config + index split).
- Generalise the crawler to non-Talend Qlik docs (Qlik Sense, QlikView,
  Replicate, Compose). The pipeline is product-agnostic; only sitemap
  config and a few selectors would need to be revisited.

### MS5 — distribution

- Internal cimt distribution: monthly CI build pushed to a private artefact
  registry; team-mates `curl | tar xz` instead of running the crawler.
- Public Plugin Marketplace entry for the Claude Code skill (crawler-only,
  Qlik content regenerated locally per install).

## License

The code in this repository is licensed under [MIT](LICENSE).

### Note on crawled content

The MIT license covers **the source code only**. The crawler downloads
documentation from `help.qlik.com/talend` and `help.qlik.com/en-US/cloud-services`,
which is owned by Qlik and governed by Qlik's own terms of use. The crawled and
distilled content is **not** part of this repo and must be regenerated locally by
each user via `make fresh`. Users are responsible for complying with Qlik's terms
of use when running the crawler.

This project is **not** affiliated with or endorsed by Qlik.
