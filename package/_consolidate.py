"""Shared consolidation logic for Chat and Project bundles.

Both surfaces need the same artefacts:
- Per-guide+version consolidated markdown with anchored topic sections
- Top-level index.md
- Per-group sub-indexes linking to topic anchors

The Skill (Chat) and Project (Project Knowledge) bundles differ only in their
"front matter" file (SKILL.md vs PROJECT-INSTRUCTIONS.md) and packaging
(ZIP vs folder). Everything below this line is shared.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "skill-output" / "qlik-talend"
TOPIC_MAP = ROOT / "topic_map.yaml"

CITATION_HEADER_RE = re.compile(r"\|\s*Anchor\s*\|\s*Raw file\s*\|\s*Source URL\s*\|")
CITATION_SEPARATOR_RE = re.compile(r"\|-+\|-+\|-+\|")
CITATION_ROW_RE = re.compile(
    r"\|\s*(`\[\^P-\d+\]`)\s*\|\s*`[^`]+`\s*\|\s*([^|]+?)\s*\|"
)


GROUP_DESCRIPTIONS: dict[str, str] = {
    "studio": "Talend Studio (8.0) — job design, components, projects, Git, metadata, deployment.",
    "tmc": "Talend Management Console (Cloud) — promotions, schedules, users, tokens, environments, audit.",
    "remote-engine": "Talend Remote Engine (Cloud, Linux & Windows) + Dynamic Engine — install, configure, run.",
    "installation": "Studio + TMC + Engine installation, hybrid deployments, migration / upgrade (Cloud + 8.0).",
    "sdlc-cicd": "Software Development Life Cycle, CI/CD, Git, environments, promotions, operational mgmt.",
    "cloud-platform": "Talend Cloud platform basics — getting started, glossary, account, regions.",
    # Qlik Cloud Help (help.qlik.com/cloud-services) — Qlik Talend Cloud Data Integration:
    "cloud-lakehouse": "Qlik Talend Cloud Open Lakehouse — Apache Iceberg lakehouse in your AWS account: ingestion, streaming, compute clusters, optimization, monitoring.",
    "cloud-pipelines": "Qlik Talend Cloud pipelines — transformation flows (incl. AI-assisted / SQL-from-prompt), declarative pipelines, data products & data marts, knowledge mart, replication.",
    "cloud-connections": "Qlik Talend Cloud connections — source & target connectors plus 100+ SaaS web-application connectors, landing, file storage.",
    "cloud-genai": "Qlik Talend Cloud GenAI building blocks — LLM connections and vector-database connections used by AI-assisted pipelines.",
    "cloud-api-designer": "Qlik Talend Cloud API Designer (Data Integration) — design, document and mock REST APIs.",
    "cloud-di-platform": "Qlik Talend Cloud Data Integration platform — getting started, spaces, deployment/requirements, data stewardship, catalog, version control, marketplace.",
}


@dataclass
class TopicSummary:
    topic_id: str
    blurb: str
    anchor: str
    pages: int


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", s)[:120]


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    return yaml.safe_load(text[4:end]) or {}, text[end + 5 :]


def transform_topic_body(text: str) -> str:
    """Strip frontmatter, drop Raw-file column, demote H1 → H2 (so the
    consolidated guide file's structure is: H1 = guide, H2 = topic)."""
    _, body = split_frontmatter(text)
    body = body.lstrip()
    out_lines: list[str] = []
    for line in body.splitlines():
        if CITATION_HEADER_RE.search(line):
            out_lines.append("| Anchor | Source URL |")
            continue
        if CITATION_SEPARATOR_RE.search(line):
            out_lines.append("|--------|-----------|")
            continue
        m = CITATION_ROW_RE.match(line)
        if m:
            anchor, url = m.group(1), m.group(2).strip()
            out_lines.append(f"| {anchor} | {url} |")
            continue
        out_lines.append(line)
    body = "\n".join(out_lines)
    demoted: list[str] = []
    for line in body.splitlines():
        if line.startswith("### "):
            demoted.append("#### " + line[4:])
        elif line.startswith("## "):
            demoted.append("### " + line[3:])
        elif line.startswith("# "):
            demoted.append("## " + line[2:])
        else:
            demoted.append(line)
    return "\n".join(demoted).rstrip() + "\n"


def consolidate_guide(
    *, group: str, guide: str, version: str, topic_blocks: list[dict]
) -> tuple[str, list[TopicSummary]]:
    """Build one combined markdown for a single guide+version.

    Returns (markdown_text, [TopicSummary, ...]).
    """
    src_topic_dir = SRC / "topics" / group / safe_id(guide) / safe_id(version)
    out_lines: list[str] = [
        f"# {guide} — {version}",
        "",
        f"_Group:_ `{group}`  ·  _Version:_ `{version}`  ·  "
        f"_Topics:_ {len(topic_blocks)}",
        "",
        "## Table of contents",
        "",
    ]
    summaries: list[TopicSummary] = []
    body_blocks: list[str] = []

    for tb in topic_blocks:
        topic_id = tb["id"]
        anchor = f"topic-{safe_id(topic_id)}"
        topic_file = src_topic_dir / f"{safe_id(topic_id)}.md"
        if not topic_file.exists():
            continue
        text = topic_file.read_text(encoding="utf-8")
        m = re.search(r"_TL;DR:_\s+(.+?)\n", text)
        blurb = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        if len(blurb) > 200:
            blurb = blurb[:200] + "…"
        summaries.append(
            TopicSummary(
                topic_id=topic_id, blurb=blurb, anchor=anchor, pages=len(tb["pages"])
            )
        )
        out_lines.append(
            f"- [{topic_id}](#{anchor}) ({len(tb['pages'])} pages) — {blurb}"
        )
        body_blocks.append(
            f'\n<a id="{anchor}"></a>\n\n## Topic: `{topic_id}`\n\n{transform_topic_body(text)}'
        )

    return "\n".join(out_lines) + "\n" + "\n".join(body_blocks), summaries


def load_topic_map() -> dict:
    if not TOPIC_MAP.exists():
        raise SystemExit("topic_map.yaml not found — run `make cluster` first")
    return yaml.safe_load(TOPIC_MAP.read_text())


def write_consolidated_artefacts(
    *, target_dir: Path
) -> tuple[dict[str, list[dict]], dict[tuple[str, str], list[TopicSummary]], int]:
    """Write the shared content (consolidated guide files + index.md +
    per-group sub-indexes) into target_dir/topics, target_dir/index.md,
    target_dir/index/<group>.md.

    Caller is responsible for adding the surface-specific front-matter
    (SKILL.md or PROJECT-INSTRUCTIONS.md) and packaging (ZIP or folder).
    """
    tm = load_topic_map()
    by_group: dict[str, list[dict]] = {}
    for g in tm["guides"]:
        by_group.setdefault(g["product_group"], []).append(g)

    summaries_by_guide: dict[tuple[str, str], list[TopicSummary]] = {}
    n_guide_files = 0
    for group, guides in by_group.items():
        group_dir = target_dir / "topics" / group
        group_dir.mkdir(parents=True, exist_ok=True)
        for guide_block in guides:
            guide = guide_block["product_slug"]
            version = guide_block["version"]
            md, summaries = consolidate_guide(
                group=group,
                guide=guide,
                version=version,
                topic_blocks=guide_block["topics"],
            )
            (group_dir / f"{safe_id(guide)}__{safe_id(version)}.md").write_text(
                md, encoding="utf-8"
            )
            summaries_by_guide[(guide, version)] = summaries
            n_guide_files += 1

    (target_dir / "index.md").write_text(
        _build_top_index(by_group), encoding="utf-8"
    )
    (target_dir / "index").mkdir(parents=True, exist_ok=True)
    for group, guides in by_group.items():
        (target_dir / "index" / f"{group}.md").write_text(
            _build_group_index(group, guides, summaries_by_guide), encoding="utf-8"
        )

    return by_group, summaries_by_guide, n_guide_files


def _build_top_index(by_group: dict) -> str:
    n_topics = sum(
        len(g["topics"]) for guides in by_group.values() for g in guides
    )
    n_pages = sum(g["page_count"] for guides in by_group.values() for g in guides)
    n_guides = sum(len(guides) for guides in by_group.values())
    lines = [
        "# Qlik Talend Documentation — Index",
        "",
        "Distilled hybrid documentation reference. Topics are consolidated "
        "per guide+version into single files with anchored sections (`<a "
        "id=\"topic-<id>\">`) so individual topics can be navigated within "
        "one combined guide file.",
        "",
        "## Product groups",
        "",
        "| Group | Description | Guides | Topics | Pages |",
        "|-------|-------------|-------:|-------:|------:|",
    ]
    for group in sorted(by_group):
        guides = by_group[group]
        gt = sum(len(g["topics"]) for g in guides)
        gp = sum(g["page_count"] for g in guides)
        desc = GROUP_DESCRIPTIONS.get(group, "")
        lines.append(
            f"| [`{group}`](index/{group}.md) | {desc} | {len(guides)} | {gt} | {gp} |"
        )
    lines += [
        "",
        f"**Total:** {len(by_group)} groups, {n_guides} guides, {n_topics} "
        f"topics, {n_pages} pages.",
        "",
        "## Navigation",
        "",
        "1. Pick the product group that matches the user's question.",
        "2. Open `index/<group>.md` for the topic listing with anchored links.",
        "3. Open the consolidated guide file `topics/<group>/<guide>__<version>.md` and jump to the topic anchor (large guide files: use Read with offset/limit).",
        "4. For exact wording or full procedure detail, follow the canonical URL in the topic's Citations table (WebFetch).",
    ]
    return "\n".join(lines) + "\n"


def _build_group_index(
    group: str, guides: list[dict], summaries_by_guide: dict
) -> str:
    lines = [
        f"# {group} — Topic Index",
        "",
        GROUP_DESCRIPTIONS.get(group, ""),
        "",
    ]
    for guide_block in sorted(guides, key=lambda x: x["product_slug"]):
        guide = guide_block["product_slug"]
        version = guide_block["version"]
        guide_filename = f"{safe_id(guide)}__{safe_id(version)}.md"
        summaries = summaries_by_guide.get((guide, version), [])
        lines += [
            f"## {guide} (`{version}`) — "
            f"{guide_block['page_count']} pages, "
            f"{len(guide_block['topics'])} topics",
            "",
            f"Combined guide file: [`topics/{group}/{guide_filename}`](../topics/{group}/{guide_filename})",
            "",
            "| Topic | Pages | Blurb |",
            "|-------|------:|-------|",
        ]
        for s in summaries:
            blurb = (s.blurb or "").replace("|", r"\|")
            link = f"../topics/{group}/{guide_filename}#{s.anchor}"
            lines.append(f"| [`{s.topic_id}`]({link}) | {s.pages} | {blurb} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def reset_dir(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)
