"""Auto-update README.md and SKILL.md from config + build artifacts.

Called as the last step of `tasks build`. Keeps in sync:
  README.md  — "Integrated documentation guides" section + summary stats line
  SKILL.md   — coverage table rows (| group | versions | pages | topics |)

The SKILL.md `description` frontmatter (auto-trigger keywords for claude.ai)
is NOT auto-generated — see the CHECKLIST comment in crawler/config.py.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skill-output" / "qlik-talend" / "meta" / "manifest.json"
TOPIC_MAP = ROOT / "topic_map.yaml"
README = ROOT / "README.md"
SKILL_MD = ROOT / "skill-output" / "qlik-talend" / "SKILL.md"


def _resolve_r_code(manifest_pages: dict) -> str:
    """Find the actual studio-user-guide R-code from crawled URLs."""
    for url in manifest_pages:
        m = re.search(r"/studio-user-guide/(8\.0-R\d{4}-\d{2})/", url)
        if m:
            return m.group(1)
    return "8.0-R<latest>"


def _sitemap_to_url(name: str, r_code: str) -> str:
    """Convert a sitemap name to its canonical entry URL."""
    if "<latest-r>" in name:
        slug = name.split("_")[0]
        return f"https://help.qlik.com/talend/en-US/{slug}/{r_code}/"
    slug, version = name.rsplit("_", 1)
    return f"https://help.qlik.com/talend/en-US/{slug}/{version}/"


def _cloud_entry_urls(manifest_pages: dict, sections: list[str]) -> list[str]:
    """One representative Qlik Cloud Help entry URL per Data-Integration section.

    Cloud groups have no per-guide sitemap name to convert, so we pick a landing
    page straight from the crawl manifest — preferring an overview/introduction
    page, else the shortest crawled URL in the section."""
    out: list[str] = []
    for section in sections:
        needle = f"/DataIntegration/{section}/"
        candidates = [
            u
            for u, m in manifest_pages.items()
            if needle in u and isinstance(m, dict) and m.get("out_path")
        ]
        if not candidates:
            continue
        # Match only the leaf filename — matching the whole URL would let a
        # section folder named e.g. "Introduction" mark every page as preferred.
        preferred = [
            u
            for u in candidates
            if re.search(
                r"(introduction|overview|getting-started|-intro)",
                u.rsplit("/", 1)[-1],
                re.IGNORECASE,
            )
        ]
        out.append(sorted(preferred or candidates, key=len)[0])
    return out


def _group_stats(tm: dict) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = {}
    for g in tm["guides"]:
        pg = g["product_group"]
        if pg == "?":
            continue
        s = stats.setdefault(pg, {"pages": 0, "topics": 0})
        s["pages"] += g["page_count"]
        s["topics"] += len(g["topics"])
    return stats


def update_readme(readme: str, manifest_pages: dict, tm: dict) -> str:
    from crawler.config import CLOUD_PRODUCT_SECTIONS, GROUP_LABELS, PRODUCT_SITEMAPS

    r_code = _resolve_r_code(manifest_pages)
    stats = _group_stats(tm)
    total_pages = sum(s["pages"] for s in stats.values())
    total_topics = sum(s["topics"] for s in stats.values())

    lines = [
        "Each line below is one **canonical Qlik Talend doc entry page**; all",
        "sub-pages of that guide are crawled via Qlik's official sitemap (so",
        "coverage is essentially complete — no recursive link-walking needed).",
        f"The current build covers **{total_pages:,} pages → {total_topics:,} topics** across these guides:",
        "",
    ]
    for group, sitemaps in PRODUCT_SITEMAPS.items():
        label = GROUP_LABELS.get(group, group)
        lines.append(f"**{group}** ({label}):")
        for name in sitemaps:
            lines.append(f"- {_sitemap_to_url(name, r_code)}")
        lines.append("")

    # Cloud Help groups (help.qlik.com/cloud-services) — one entry page per
    # Data-Integration section, taken from the crawl manifest. Only groups that
    # were actually built (present in topic_map stats) are listed.
    for group, sections in CLOUD_PRODUCT_SECTIONS.items():
        if group not in stats:
            continue
        label = GROUP_LABELS.get(group, group)
        lines.append(f"**{group}** ({label}):")
        for url in _cloud_entry_urls(manifest_pages, sections):
            lines.append(f"- {url}")
        lines.append("")

    new_body = "\n".join(lines)
    pattern = r"(## Integrated documentation guides\n\n).*?(The same list)"
    replacement = r"\g<1>" + new_body + r"\g<2>"
    updated = re.sub(pattern, replacement, readme, flags=re.DOTALL)
    if updated == readme:
        print("[update_meta] WARNING: README section not found — skipped", file=sys.stderr)
    return updated


def update_skill_md(skill_md: str, tm: dict) -> str:
    from crawler.config import GROUP_VERSIONS

    stats = _group_stats(tm)
    rows = []
    for group in sorted(stats):
        s = stats[group]
        version = GROUP_VERSIONS.get(group, "?")
        rows.append(f"| {group} | {version} | ~{s['pages']:,} | ~{s['topics']:,} |")

    new_rows = "\n".join(rows)
    pattern = r"(\|[-|: ]+\|\n).*?(\n\n\*\*Out of scope)"
    replacement = r"\g<1>" + new_rows + r"\g<2>"
    updated = re.sub(pattern, replacement, skill_md, flags=re.DOTALL)
    if updated == skill_md:
        print("[update_meta] WARNING: SKILL.md coverage table not found — skipped", file=sys.stderr)
    return updated


def main() -> int:
    if not MANIFEST.exists():
        print("[update_meta] manifest.json not found — skipping", file=sys.stderr)
        return 0
    if not TOPIC_MAP.exists():
        print("[update_meta] topic_map.yaml not found — skipping", file=sys.stderr)
        return 0

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tm = yaml.safe_load(TOPIC_MAP.read_text(encoding="utf-8"))

    readme = README.read_text(encoding="utf-8")
    readme_new = update_readme(readme, manifest.get("pages", {}), tm)
    if readme_new != readme:
        README.write_text(readme_new, encoding="utf-8")
        print(f"[update_meta] updated {README.relative_to(ROOT)}")
    else:
        print(f"[update_meta] {README.relative_to(ROOT)} unchanged")

    skill_md = SKILL_MD.read_text(encoding="utf-8")
    skill_new = update_skill_md(skill_md, tm)
    if skill_new != skill_md:
        SKILL_MD.write_text(skill_new, encoding="utf-8")
        print(f"[update_meta] updated {SKILL_MD.relative_to(ROOT)}")
    else:
        print(f"[update_meta] {SKILL_MD.relative_to(ROOT)} unchanged")

    return 0


if __name__ == "__main__":
    sys.exit(main())
