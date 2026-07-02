"""CLI: crawl Talend docs to versioned raw-markdown mirror.

Usage:
    uv run python -m crawler.run                    # crawl everything in config
    uv run python -m crawler.run --product studio   # only one logical group
    uv run python -m crawler.run --limit 5          # smoke test
    uv run python -m crawler.run --force            # ignore cache, re-fetch all
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from time import monotonic

from crawler.config import ALL_GROUPS, CLOUD_CRAWL_DELAY_SECONDS, PRODUCT_SITEMAPS
from crawler.discovery import (
    SitemapRef,
    fetch_urls,
    resolve_cloud_sections,
    resolve_sitemap_refs,
)
from crawler.extract import (
    _parse_url,
    canonicalize,
    extract,
    render_with_frontmatter,
    safe_filename,
)
from crawler.fetch import Fetcher

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "skill-output" / "qlik-talend" / "raw"
META_DIR = ROOT / "skill-output" / "qlik-talend" / "meta"
MANIFEST_PATH = META_DIR / "manifest.json"


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"pages": {}, "stats": {}}


def save_manifest(manifest: dict) -> None:
    META_DIR.mkdir(parents=True, exist_ok=True)
    # Always UTF-8: on Windows write_text/read_text default to cp1252, which
    # corrupts non-ASCII page titles (e.g. a "™" becomes byte 0x99) and makes
    # the manifest invalid UTF-8 for the downstream distill steps.
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def output_path(product_group: str, url: str) -> Path:
    parts = _parse_url(url)
    return (
        RAW_DIR
        / product_group
        / parts["product_slug"]
        / parts["version"]
        / f"{safe_filename(parts['page_slug'])}.md"
    )


def crawl(
    products: list[str] | None,
    limit: int | None,
    force: bool,
    delay: float,
) -> int:
    # Only resolve the Talend sitemap-index when a Talend group is in scope.
    # A cloud-only crawl must not depend on (or pay two GETs for) the Talend
    # index — and resolve_latest_studio_r_code() would otherwise raise if the
    # Talend side ever lacked a studio sitemap.
    want_talend = products is None or any(p in PRODUCT_SITEMAPS for p in products)
    talend_refs = (
        [r for r in resolve_sitemap_refs() if products is None or r.product in products]
        if want_talend
        else []
    )
    cloud_sections = resolve_cloud_sections(products)
    if not talend_refs and not cloud_sections:
        print(f"[run] no sitemaps match {products!r}", file=sys.stderr)
        return 1

    # Uniform (ref, urls) work sources across both doc sources: Talend
    # sub-sitemaps and Qlik Cloud Help Data-Integration sections.
    ref_url_lists: list[tuple[SitemapRef, list[str]]] = [
        (ref, fetch_urls(ref)) for ref in talend_refs
    ] + cloud_sections

    # Collect all URLs grouped by ref, deduped by canonical URL across the run.
    work: list[tuple[SitemapRef, str]] = []
    seen: set[str] = set()
    n_dupes = 0
    for ref, urls in ref_url_lists:
        if limit:
            urls = urls[:limit]
        for u in urls:
            canon = canonicalize(u)
            if canon in seen:
                n_dupes += 1
                continue
            seen.add(canon)
            work.append((ref, canon))
    print(
        f"[run] {len(work)} unique URLs across {len(ref_url_lists)} sitemaps/sections "
        f"({n_dupes} ?id= duplicates dropped)"
    )

    manifest = load_manifest()
    pages: dict = manifest.setdefault("pages", {})
    started = monotonic()
    n_fetched = n_cached = n_unchanged = n_failed = 0

    with Fetcher(delay_seconds=delay) as fetcher:
        for i, (ref, url) in enumerate(work, 1):
            prev = pages.get(url, {}) if not force else {}
            # Cloud Help pages get a stricter per-request delay floor (robots
            # Crawl-delay: 5) even when the run's --delay is lower.
            min_delay = (
                CLOUD_CRAWL_DELAY_SECONDS
                if ref.source == "cloud-services"
                else None
            )
            try:
                res = fetcher.get(
                    url,
                    prev_etag=prev.get("etag"),
                    prev_last_modified=prev.get("last_modified"),
                    min_delay=min_delay,
                )
                if res.from_cache:
                    n_cached += 1
                    pages[url]["last_seen_at"] = _now_iso()
                    continue
                if res.status == 404:
                    pages[url] = {**prev, "status": 404, "last_seen_at": _now_iso()}
                    n_failed += 1
                    print(f"  [{i}/{len(work)}] 404 {url}", file=sys.stderr)
                    continue
                page = extract(res.text, url)
                # Skip-write if content unchanged
                if (
                    not force
                    and prev.get("content_sha") == page.content_sha
                    and output_path(ref.product, url).exists()
                ):
                    n_unchanged += 1
                else:
                    out = output_path(ref.product, url)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(
                        render_with_frontmatter(page, ref.product), encoding="utf-8"
                    )
                    n_fetched += 1
                pages[url] = {
                    "product_group": ref.product,
                    "sitemap": ref.name,
                    "out_path": str(output_path(ref.product, url).relative_to(ROOT)),
                    "etag": res.etag,
                    "last_modified": res.last_modified,
                    "content_sha": page.content_sha,
                    "title": page.title,
                    "raw_html_bytes": page.raw_html_bytes,
                    "markdown_bytes": page.markdown_bytes,
                    "version_constraints_n": len(page.version_constraints),
                    "last_seen_at": _now_iso(),
                }
            except Exception as e:
                n_failed += 1
                print(f"  [{i}/{len(work)}] FAIL {url}: {e}", file=sys.stderr)
            if i % 25 == 0:
                save_manifest(manifest)
                print(
                    f"  [{i}/{len(work)}] fetched={n_fetched} cached={n_cached} "
                    f"unchanged={n_unchanged} failed={n_failed}"
                )

    elapsed = monotonic() - started
    manifest["stats"] = {
        "last_run_at": _now_iso(),
        "duration_seconds": round(elapsed, 1),
        "urls_total": len(work),
        "fetched": n_fetched,
        "cached_304": n_cached,
        "unchanged_sha": n_unchanged,
        "failed": n_failed,
    }
    save_manifest(manifest)
    print(
        f"[run] done in {elapsed:.1f}s — fetched={n_fetched} cached={n_cached} "
        f"unchanged={n_unchanged} failed={n_failed}"
    )
    return 0 if n_failed == 0 else 2


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--product",
        action="append",
        choices=ALL_GROUPS,
        help="logical product group (repeatable). Default: all",
    )
    p.add_argument("--limit", type=int, help="cap URLs per sitemap (smoke testing)")
    p.add_argument("--force", action="store_true", help="ignore cache, refetch all")
    p.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="seconds between requests (default 1.0)",
    )
    args = p.parse_args()
    return crawl(args.product, args.limit, args.force, args.delay)


if __name__ == "__main__":
    sys.exit(main())
