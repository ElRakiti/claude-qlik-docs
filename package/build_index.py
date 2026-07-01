"""Build navigation index for the qlik-talend skill.

Outputs:
- skill-output/qlik-talend/index.md   — top-level navigation pointing to per-group sub-indexes
- skill-output/qlik-talend/index/<group>.md  — per-group topic listing with one-line blurbs

Progressive disclosure: SKILL.md → index.md → index/<group>.md → topics/.../*.md → raw/.../*.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILL_OUT = ROOT / "skill-output" / "qlik-talend"
TOPIC_MAP = ROOT / "topic_map.yaml"
INDEX = SKILL_OUT / "index.md"
INDEX_DIR = SKILL_OUT / "index"

GROUP_DESCRIPTIONS: dict[str, str] = {
    "api": "Talend Cloud APIs — TMC management API, API Designer, API Portal, API Tester.",
    "cloud-platform": "Talend Cloud platform basics — getting started, glossary, account, regions.",
    "data-apps": "Talend Data Stewardship (campaigns, tasks, data models, TDQL, REST API, DQ rules + Data Shaping Expression Language) + Data Preparation (recipes, datasets, functions).",
    "esb": "Talend ESB (8.0) — Camel routes, CXF services, Karaf container, STS, infrastructure services, microservices, Activity Monitoring Console, JMX monitoring, runtime ops (auto-scaling, multi-container).",
    "installation": "Studio + TMC + Engine installation, hybrid deployments, migration / upgrade (Cloud + 8.0).",
    "remote-engine": "Talend Remote Engine (Cloud, Linux & Windows) + Dynamic Engine — install, configure, run.",
    "sdlc-cicd": "Software Development Life Cycle, CI/CD, Git, environments, promotions, operational mgmt.",
    "studio": "Talend Studio (8.0) — job design, components, projects, Git, metadata, deployment.",
    "tmc": "Talend Management Console (Cloud) — promotions, schedules, users, tokens, environments, audit.",
    # Qlik Cloud Help (help.qlik.com/cloud-services) — Qlik Talend Cloud Data Integration:
    "cloud-lakehouse": "Qlik Talend Cloud Open Lakehouse — Apache Iceberg lakehouse in your AWS account: ingestion, streaming, compute clusters, optimization, monitoring.",
    "cloud-pipelines": "Qlik Talend Cloud pipelines — transformation flows (incl. AI-assisted / SQL-from-prompt), declarative pipelines, data products & data marts, knowledge mart, replication.",
    "cloud-connections": "Qlik Talend Cloud connections — source & target connectors plus 100+ SaaS web-application connectors, landing, file storage. Large; load only for a specific connector's settings.",
    "cloud-genai": "Qlik Talend Cloud GenAI building blocks — LLM connections and vector-database connections used by AI-assisted pipelines.",
    "cloud-api-designer": "Qlik Talend Cloud API Designer (Data Integration) — design, document and mock REST APIs.",
    "cloud-di-platform": "Qlik Talend Cloud Data Integration platform — getting started, spaces, deployment/requirements, data stewardship, catalog, version control, marketplace.",
}


def first_tldr_for_topic(topic_file: Path) -> str:
    """Return the topic's first TL;DR line as one-sentence blurb."""
    text = topic_file.read_text(encoding="utf-8")
    m = re.search(r"_TL;DR:_\s+(.+?)\n", text)
    if not m:
        return ""
    s = re.sub(r"\s+", " ", m.group(1)).strip()
    return s[:200] + ("…" if len(s) > 200 else "")


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", s)[:120]


def build() -> int:
    if not TOPIC_MAP.exists():
        print("topic_map.yaml not found", file=sys.stderr)
        return 1
    tm = yaml.safe_load(TOPIC_MAP.read_text())

    # Group guides by product_group
    by_group: dict[str, list[dict]] = {}
    for g in tm["guides"]:
        by_group.setdefault(g["product_group"], []).append(g)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    total_topics = 0
    total_pages = 0

    # Top-level index
    top_lines: list[str] = [
        "# Qlik Talend Documentation — Skill Index",
        "",
        "Distilled hybrid skill for Qlik Talend documentation.",
        "Use this index to find the right topic file, then load the topic file for a "
        "structured per-page summary. Each topic file points at the exact raw markdown "
        "for full-fidelity lookups.",
        "",
        "## Product groups",
        "",
        "| Group | Description | Guides | Topics | Pages |",
        "|-------|-------------|-------:|-------:|------:|",
    ]
    for group in sorted(by_group):
        guides = by_group[group]
        n_guides = len(guides)
        n_topics = sum(len(gd["topics"]) for gd in guides)
        n_pages = sum(gd["page_count"] for gd in guides)
        total_topics += n_topics
        total_pages += n_pages
        desc = GROUP_DESCRIPTIONS.get(group, "")
        top_lines.append(
            f"| [`{group}`](index/{group}.md) | {desc} | {n_guides} | {n_topics} | {n_pages} |"
        )

    top_lines += [
        "",
        f"**Total:** {len(by_group)} groups, "
        f"{sum(len(g) for g in by_group.values())} guides, "
        f"{total_topics} topics, {total_pages} pages.",
        "",
        "## How to navigate",
        "",
        "1. Pick the product group that matches the user's question (table above).",
        "2. Open `index/<group>.md` — it lists all guides and their topics with one-line blurbs.",
        "3. Load the matching `topics/<group>/<guide>/<version>/<topic>.md` for a structured summary "
        "(TL;DR per page, procedure outline, notes, citations).",
        "4. Only when you need exact wording or full procedure detail, open the raw file referenced "
        "in the topic's Citations table.",
        "",
        "## Versioning",
        "",
        f"Each artifact is versioned. Most Cloud-only docs use version `Cloud`; Studio uses "
        f"`8.0-R<YYYY>-<MM>` (latest snapshot at crawl time). Always cite the version when "
        f"answering — version-specific behavior is common.",
    ]
    INDEX.write_text("\n".join(top_lines) + "\n", encoding="utf-8")

    # Per-group sub-indexes
    for group, guides in by_group.items():
        lines: list[str] = [
            f"# {group} — Topic Index",
            "",
            GROUP_DESCRIPTIONS.get(group, ""),
            "",
        ]
        for guide_block in sorted(guides, key=lambda x: x["product_slug"]):
            guide = guide_block["product_slug"]
            version = guide_block["version"]
            n_pages = guide_block["page_count"]
            lines += [
                f"## {guide} (`{version}`) — {n_pages} pages, {len(guide_block['topics'])} topics",
                "",
                "| Topic | Pages | Blurb |",
                "|-------|------:|-------|",
            ]
            for t in guide_block["topics"]:
                topic_path = (
                    SKILL_OUT
                    / "topics"
                    / group
                    / safe_id(guide)
                    / safe_id(version)
                    / f"{safe_id(t['id'])}.md"
                )
                blurb = first_tldr_for_topic(topic_path) if topic_path.exists() else ""
                blurb = blurb.replace("|", r"\|")
                rel = topic_path.relative_to(SKILL_OUT).as_posix()
                lines.append(
                    f"| [`{t['id']}`]({'../' + rel}) | {len(t['pages'])} | {blurb} |"
                )
            lines.append("")
        (INDEX_DIR / f"{group}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[build_index] wrote {INDEX.relative_to(ROOT)}")
    print(
        f"[build_index] wrote {len(by_group)} per-group sub-indexes under "
        f"{INDEX_DIR.relative_to(ROOT)}"
    )
    sizes = sorted(p.stat().st_size for p in INDEX_DIR.glob("*.md"))
    if sizes:
        print(
            f"[build_index] sub-index sizes: p50={sizes[len(sizes) // 2]} "
            f"max={sizes[-1]} total={sum(sizes) // 1024} KB"
        )
        print(f"[build_index] top-level index: {INDEX.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(build())
