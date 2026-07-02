"""HTML → cleaned Markdown + frontmatter for Talend doc pages.

Polishing fixes (vs. spike):
- get_text(separator=" ", strip=True) for proper word spacing
- strip Qlik info-icon spans before extracting text/markdown
- tighter version_constraints regex (concrete version numbers only)
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone

import yaml
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify

URL_RE = re.compile(
    r"^https?://help\.qlik\.com/talend/(?P<locale>[a-z]{2}-[A-Z]{2})/"
    r"(?P<product_slug>[^/]+)/(?P<version>[^/]+)/(?P<page_slug>[^/?#]+)/?"
    r"(?:\?[^#]*)?(?:#.*)?$"
)

# Second doc source — Qlik Cloud Help (help.qlik.com/en-US/cloud-services).
# MadCap pages under a deep, unversioned path, e.g.
#   .../cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Lakehouse/foo.htm
#   .../cloud-services/.../DataIntegration/SourcesConnections/MySQL/mysql-source.htm
# We anchor on the /DataIntegration/<Section>/ segment; the remaining path
# (which may itself contain sub-folders) becomes the page slug.
CLOUD_URL_RE = re.compile(
    r"^https?://help\.qlik\.com/(?P<locale>[a-z]{2}-[A-Z]{2})/cloud-services/"
    r".*?/DataIntegration/(?P<section>[^/]+)/(?P<rest>.+?)\.htm"
    r"(?:\?[^#]*)?(?:#.*)?$"
)


def canonicalize(url: str) -> str:
    """Drop query string + fragment. The Talend sitemaps list the same page
    multiple times with `?id=N` variants — content is identical, so we crawl
    only the bare canonical URL once."""
    return re.sub(r"[?#].*$", "", url)

# Tight regex: catches "version 8.0", "8.0.1 R2024-05", "Talend Studio 8.0-R2026-01"
# and qualifier ("required", "or higher", "or earlier", "and earlier", "and later").
VERSION_NUM = r"(?:\d+\.\d+(?:\.\d+)?(?:[ -]R\d{4}-\d{2})?)"
VERSION_CONSTRAINT_RE = re.compile(
    rf"(?:requires?|required|since|as of|available (?:in|since|as of)|deprecated (?:in|since|as of)|applies to)"
    rf"[^.\n]*?(?:Talend [A-Za-z ]+ )?{VERSION_NUM}(?:\s*(?:or higher|or later|or earlier|and earlier|and later))?",
    flags=re.IGNORECASE,
)

JUNK_SELECTORS = [
    "script",
    "style",
    "noscript",
    "iframe",
    "svg",
    "nav",
    "footer",
    "header",
    "button",
    ".feedback",
    ".rating",
    "[class*=version-selector]",
    "[class*=breadcrumb]",
    "[class*=footer]",
    "[id*=feedback]",
    ".did-this-help",
    ".doc-feedback",
    # Qlik info-icon: empty span that gets concatenated to next word
    "span.icon",
    "span[class*=icon-]",
    "span.note-label-icon",
    # social-share, edit-on-github, etc.
    "[class*=share]",
    "[class*=edit-on]",
]


@dataclass
class ExtractedPage:
    url: str
    title: str
    content_markdown: str
    breadcrumbs: list[str]
    version_constraints: list[str]
    content_sha: str
    raw_html_bytes: int
    markdown_bytes: int


def _parse_url(url: str) -> dict[str, str]:
    """Parse a doc URL into path/version parts, dispatching by doc source.

    Talend docs (help.qlik.com/talend/<locale>/<slug>/<version>/<page>) and
    Qlik Cloud Help (help.qlik.com/<locale>/cloud-services/.../DataIntegration/
    <Section>/<page>.htm) have different URL schemes but yield the same field
    shape (product_slug / version / page_slug / major_version / r_code / locale
    / source) so the rest of the pipeline is source-agnostic.
    """
    m = URL_RE.match(url)
    if m:
        parts = m.groupdict()
        v = parts["version"]
        if v.lower() == "cloud":
            parts["major_version"] = "Cloud"
            parts["r_code"] = ""
        else:
            rm = re.match(r"^(\d+\.\d+)(?:-(R\d{4}-\d{2}.*))?$", v)
            parts["major_version"] = rm.group(1) if rm else v
            parts["r_code"] = (rm.group(2) or "") if rm else ""
        parts["source"] = "talend"
        return parts

    cm = CLOUD_URL_RE.match(url)
    if cm:
        # product_slug = the Data Integration section (the "guide"); page_slug
        # keeps any sub-folders (joined with "__") to stay unique on disk.
        return {
            "locale": cm.group("locale"),
            "product_slug": cm.group("section").lower(),
            "version": "Cloud",
            "page_slug": cm.group("rest").replace("/", "__"),
            "major_version": "Cloud",
            "r_code": "",
            "source": "cloud-services",
        }

    raise ValueError(f"URL does not match expected pattern: {url}")


def _strip_junk(soup: BeautifulSoup) -> None:
    for sel in JUNK_SELECTORS:
        for el in soup.select(sel):
            el.decompose()


def extract(html: str, url: str) -> ExtractedPage:
    soup = BeautifulSoup(html, "lxml")
    _strip_junk(soup)

    main = soup.select_one("div#topicContent") or soup.select_one("main#main")
    if main is None:
        raise RuntimeError(f"No main content container in {url}")
    if not isinstance(main, Tag):
        raise RuntimeError(f"Unexpected main container type in {url}")

    h1 = main.find("h1")
    if h1:
        title = re.sub(r"\s+", " ", h1.get_text(separator=" ", strip=True)).strip()
        # tighten punctuation: "Studio ?" -> "Studio?"
        title = re.sub(r"\s+([?!.,;:])", r"\1", title)
    else:
        title = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else _parse_url(url)["page_slug"].replace("-", " ").title()
        )

    # Breadcrumbs from the un-stripped document
    bc_soup = BeautifulSoup(html, "lxml")
    breadcrumbs: list[str] = []
    bc = bc_soup.select_one("[class*=breadcrumb]")
    if bc:
        breadcrumbs = [
            re.sub(r"\s+", " ", t).strip()
            for t in bc.stripped_strings
            if t.strip() and t.strip() not in {">", "/", "·"}
        ]

    text = main.get_text(" ", strip=True)
    version_constraints = list(
        dict.fromkeys(
            re.sub(r"\s+", " ", m.group(0)).strip()
            for m in VERSION_CONSTRAINT_RE.finditer(text)
        )
    )[:8]

    md_body = markdownify(str(main), heading_style="ATX", bullets="-")
    md_body = re.sub(r"\n{3,}", "\n\n", md_body).strip() + "\n"
    # Common Qlik artefacts: "Information note Note:" → keep as is (it's readable);
    # but "Information note**Note:**" patterns can be normalised later in MS2.

    content_sha = hashlib.sha256(md_body.encode("utf-8")).hexdigest()[:12]

    return ExtractedPage(
        url=url,
        title=title,
        content_markdown=md_body,
        breadcrumbs=breadcrumbs,
        version_constraints=version_constraints,
        content_sha=content_sha,
        raw_html_bytes=len(html),
        markdown_bytes=len(md_body),
    )


def render_with_frontmatter(page: ExtractedPage, product_group: str) -> str:
    parts = _parse_url(page.url)
    fm = {
        "source_url": page.url,
        "title": page.title,
        "source": parts.get("source", "talend"),  # doc source: talend | cloud-services
        "product_group": product_group,  # logical group: studio / tmc / remote-engine / ...
        "product_slug": parts["product_slug"],  # raw URL product slug
        "version": parts["version"],
        "major_version": parts["major_version"],
        "r_code": parts["r_code"],
        "locale": parts["locale"],
        "slug": parts["page_slug"],
        "breadcrumbs": page.breadcrumbs,
        "version_constraints": page.version_constraints,
        "content_sha": page.content_sha,
        "crawled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    yml = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000)
    return f"---\n{yml}---\n\n{page.content_markdown}"


def safe_filename(slug: str) -> str:
    # slugs are already URL-safe; just guard against weird chars
    return re.sub(r"[^A-Za-z0-9._-]", "_", slug)[:200]
