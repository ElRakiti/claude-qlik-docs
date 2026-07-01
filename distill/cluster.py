"""Cluster raw pages into topics, deterministically.

Strategy:
- Within each product_group, pages are grouped first by `product_slug`
  (the URL-level guide name, e.g. `studio-user-guide`,
  `management-console-user-guide`).
- Inside each guide, sitemap order is the source of truth (= TOC order).
- We split the ordered page list into "topic chunks" using two heuristics:
    1. **Hard breaks** at known section markers (slugs starting with
       common section keywords like `tmc-`, `logging-`, `installing-`, etc.).
    2. **Soft chunking** to cap topic size at ~25 pages, which keeps each
       distilled topic file readable.

Output: `topic_map.yaml` listing each topic with its ordered page slugs and
metadata (group, guide, version).

Run: uv run python -m distill.cluster
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from crawler.extract import _parse_url

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skill-output" / "qlik-talend" / "meta" / "manifest.json"
TOPIC_MAP = ROOT / "topic_map.yaml"

MAX_PAGES_PER_TOPIC = 25
MIN_PAGES_PER_TOPIC = 2  # tiny clusters get merged into the previous topic


@dataclass
class PageRef:
    url: str
    title: str
    slug: str
    product_group: str
    product_slug: str
    version: str
    out_path: str
    sitemap_index: int  # order in sitemap == TOC order


# Topic boundaries: when a slug starts with one of these prefixes (case-insensitive),
# we begin a new topic. The prefix becomes the topic id.
TOPIC_PREFIXES: list[str] = [
    "what-is-",
    "introduction",
    "getting-started",
    "functional-architecture",
    "installing-",
    "installation-",
    "uninstalling-",
    "upgrading-",
    "migrating-",
    "configuring-",
    "configuration-",
    "managing-",
    "monitoring-",
    "logging-",
    "logging-in",
    "creating-",
    "creating-a-",
    "deleting-",
    "deactivating-",
    "running-",
    "executing-",
    "scheduling-",
    "deploying-",
    "publishing-",
    "importing-",
    "exporting-",
    "designing-",
    "editing-",
    "working-with-",
    "using-",
    "troubleshooting-",
    "tmc-",
    "remote-engine-",
    "dynamic-engine-",
    "studio-",
    "git-",
    "ci-cd",
    "sdlc",
    "security-",
    "authentication",
    "sso-",
    "role",
    "permission",
    "license",
    "engine",
    "task",
    "job",
    "pipeline",
    "connector",
    "context-",
    "metadata",
    "schema",
    "log",
    "audit",
    "encryption",
    "backup",
    "tomcat",
    "jdbc",
    "kerberos",
    "ssl",
    "ldap",
    "saml",
    "okta",
]


def _topic_prefix_for(slug: str) -> str | None:
    """Return the matching prefix from TOPIC_PREFIXES for this slug, longest match wins."""
    s = slug.lower()
    matches = [p for p in TOPIC_PREFIXES if s.startswith(p)]
    return max(matches, key=len) if matches else None


def _fallback_topic_id(slug: str) -> str:
    """When no curated prefix matches, group by the slug's first word.

    This produces topic ids like "accessing", "centralizing", "defining" which
    naturally cluster related pages and stay alphabetically stable.
    """
    head = slug.split("-", 1)[0]
    return head if len(head) >= 3 else "misc"


def _topic_id(prefix: str) -> str:
    return prefix.rstrip("-") or "misc"


def load_pages() -> list[PageRef]:
    if not MANIFEST.exists():
        raise SystemExit("manifest.json not found — run crawler first")
    manifest = json.loads(MANIFEST.read_text())
    # Re-fetch sitemap order so we cluster in TOC order (manifest is dict-unordered).
    # We use the order they appear in `pages` dict, which IS insertion order in py3.7+.
    # The crawler iterates sitemaps sequentially, so this preserves TOC order per guide.
    refs: list[PageRef] = []
    for idx, (url, meta) in enumerate(manifest["pages"].items()):
        # parse version + slug from URL via the shared parser (Talend + Cloud Help)
        try:
            parts = _parse_url(url)
        except ValueError:
            continue
        if not meta.get("out_path", ""):
            continue  # skip pages that failed to crawl (no raw file)
        refs.append(
            PageRef(
                url=url,
                title=meta.get("title", ""),
                slug=parts["page_slug"],
                product_group=meta.get("product_group", "?"),
                product_slug=parts["product_slug"],
                version=parts["version"],
                out_path=meta.get("out_path", ""),
                sitemap_index=idx,
            )
        )
    return refs


def cluster_guide(pages: list[PageRef]) -> list[dict]:
    """Cluster one guide's ordered pages into topics."""
    if not pages:
        return []
    topics: list[dict] = []
    current: dict | None = None
    last_prefix: str | None = None

    for p in pages:
        prefix = _topic_prefix_for(p.slug)
        # Use curated prefix if matched, else first-word fallback for stable grouping
        effective = prefix if prefix is not None else _fallback_topic_id(p.slug)
        new_topic = (
            current is None
            or effective != last_prefix
            or (current is not None and len(current["pages"]) >= MAX_PAGES_PER_TOPIC)
        )
        if new_topic:
            tid = _topic_id(effective)
            # Make unique within this guide
            existing_ids = {t["id"] for t in topics}
            uniq = tid
            n = 2
            while uniq in existing_ids:
                uniq = f"{tid}-{n}"
                n += 1
            current = {
                "id": uniq,
                "first_slug": p.slug,
                "first_title": p.title,
                "pages": [],
            }
            topics.append(current)
            last_prefix = effective
        assert current is not None
        current["pages"].append(
            {
                "slug": p.slug,
                "title": p.title,
                "url": p.url,
                "out_path": p.out_path,
            }
        )

    # Merge tiny tail topics back into preceding to avoid 1-page topics
    merged: list[dict] = []
    for t in topics:
        if merged and len(t["pages"]) < MIN_PAGES_PER_TOPIC:
            merged[-1]["pages"].extend(t["pages"])
        else:
            merged.append(t)
    return merged


def current_id(current: dict | None) -> str:
    return current["id"] if current else ""


def main() -> int:
    all_pages = load_pages()
    # Group by (product_group, product_slug, version)
    by_guide: dict[tuple[str, str, str], list[PageRef]] = {}
    for p in all_pages:
        key = (p.product_group, p.product_slug, p.version)
        by_guide.setdefault(key, []).append(p)
    # Order pages by sitemap_index inside each guide
    for v in by_guide.values():
        v.sort(key=lambda x: x.sitemap_index)

    topic_map: dict = {"guides": []}
    grand_total = 0
    for (group, guide, version), pages in sorted(by_guide.items()):
        topics = cluster_guide(pages)
        n_pages = sum(len(t["pages"]) for t in topics)
        grand_total += n_pages
        topic_map["guides"].append(
            {
                "product_group": group,
                "product_slug": guide,
                "version": version,
                "page_count": n_pages,
                "topics": topics,
            }
        )

    TOPIC_MAP.write_text(
        yaml.safe_dump(
            topic_map, sort_keys=False, allow_unicode=True, width=1000
        )
    )
    n_topics = sum(len(g["topics"]) for g in topic_map["guides"])
    print(f"[cluster] {len(by_guide)} guides → {n_topics} topics covering {grand_total} pages")
    print(f"[cluster] wrote {TOPIC_MAP.relative_to(ROOT)}")

    # quick distribution diagnostic
    from collections import Counter

    sizes = Counter(len(t["pages"]) for g in topic_map["guides"] for t in g["topics"])
    print(f"[cluster] topic-size histogram: {dict(sorted(sizes.items()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
