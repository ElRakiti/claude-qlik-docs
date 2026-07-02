"""HTML → markdown extraction (the title-bug regression test lives here)."""
from __future__ import annotations

from pathlib import Path

import pytest

from crawler.extract import extract, render_with_frontmatter

FIXTURE = Path(__file__).parent / "fixtures" / "sample_studio.html"
SAMPLE_URL = (
    "https://help.qlik.com/talend/en-US/studio-user-guide/8.0-R2026-04/what-is-talend-studio"
)


@pytest.fixture
def page():
    html = FIXTURE.read_text(encoding="utf-8")
    return extract(html, SAMPLE_URL)


class TestExtract:
    def test_title_no_isTalend_regression(self, page):
        # Pre-fix output was "What isTalend Studio?" (missing space due to <svg> icon).
        # After fix, separator=" " plus whitespace collapse should yield correct title.
        assert page.title == "What is Talend Studio?"

    def test_markdown_starts_with_h1(self, page):
        assert page.content_markdown.lstrip().startswith("# ")

    def test_junk_stripped(self, page):
        body = page.content_markdown
        assert "junk" not in body.lower()
        assert "feedback widget" not in body
        assert "Was this helpful?" not in body
        assert "copyright stuff" not in body

    def test_content_sha_is_stable(self, page):
        # SHA should be deterministic given identical input — re-run yields same hash.
        html = FIXTURE.read_text(encoding="utf-8")
        again = extract(html, SAMPLE_URL)
        assert again.content_sha == page.content_sha

    def test_version_constraints_extracted(self, page):
        # Fixture contains "Talend Studio 8.0.1 R2024-05 or higher" — regex should catch it.
        joined = " ".join(page.version_constraints).lower()
        assert "8.0.1" in joined or "r2024-05" in joined.replace(" ", "")

    def test_compression_meaningful(self, page):
        # markdown should be substantially smaller than raw HTML
        assert page.markdown_bytes < page.raw_html_bytes
        assert page.markdown_bytes > 0


class TestFrontmatter:
    def test_frontmatter_has_required_fields(self, page):
        rendered = render_with_frontmatter(page, product_group="studio")
        assert rendered.startswith("---\n")
        # essential fields
        for field in (
            "source_url:",
            "title:",
            "product_group: studio",
            "major_version:",
            "r_code:",
            "content_sha:",
            "crawled_at:",
        ):
            assert field in rendered, f"missing field: {field}"


# Qlik Cloud Help pages use the SAME MadCap `div#topicContent` container as
# Talend, so the shared extractor must work on them with cloud frontmatter.
CLOUD_HTML = """<!doctype html><html><head><title>ignored</title></head><body>
<nav class="breadcrumb">Home &gt; Data Integration &gt; Lakehouse</nav>
<div id="topicContent">
  <h1>Qlik Open Lakehouse architecture</h1>
  <p>Qlik Open Lakehouse ingests data into an Apache Iceberg lakehouse.</p>
  <h2>Components</h2>
  <p>The data movement gateway captures changes from source systems.</p>
  <script>var junk = 1;</script>
</div>
<footer>copyright stuff</footer>
</body></html>"""
CLOUD_URL = (
    "https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub"
    "/DataIntegration/Lakehouse/lakehouse-pipeline-architecture.htm"
)


class TestExtractCloud:
    def test_cloud_page_extracts_title_and_body(self):
        p = extract(CLOUD_HTML, CLOUD_URL)
        assert p.title == "Qlik Open Lakehouse architecture"
        assert p.content_markdown.lstrip().startswith("# ")
        assert "junk" not in p.content_markdown.lower()
        assert "copyright stuff" not in p.content_markdown

    def test_cloud_frontmatter_marks_source_and_version(self):
        p = extract(CLOUD_HTML, CLOUD_URL)
        rendered = render_with_frontmatter(p, product_group="cloud-lakehouse")
        assert "source: cloud-services" in rendered
        assert "product_group: cloud-lakehouse" in rendered
        assert "product_slug: lakehouse" in rendered
        assert "version: Cloud" in rendered
