"""URL parsing + canonicalisation."""
from __future__ import annotations

import pytest

from crawler.extract import URL_RE, _parse_url, canonicalize


class TestParseURL:
    def test_cloud_version(self):
        url = "https://help.qlik.com/talend/en-US/management-console-user-guide/Cloud/tmc-ug"
        p = _parse_url(url)
        assert p["product_slug"] == "management-console-user-guide"
        assert p["version"] == "Cloud"
        assert p["major_version"] == "Cloud"
        assert p["r_code"] == ""
        assert p["page_slug"] == "tmc-ug"
        assert p["locale"] == "en-US"

    def test_studio_with_r_code(self):
        url = "https://help.qlik.com/talend/en-US/studio-user-guide/8.0-R2026-04/what-is-talend-studio"
        p = _parse_url(url)
        assert p["version"] == "8.0-R2026-04"
        assert p["major_version"] == "8.0"
        assert p["r_code"] == "R2026-04"

    def test_8_0_without_r_code(self):
        url = "https://help.qlik.com/talend/en-US/software-dev-lifecycle-best-practices-guide/8.0/what-is-software-development-life-cycle"
        p = _parse_url(url)
        assert p["major_version"] == "8.0"
        assert p["r_code"] == ""

    def test_url_with_query_string_matches(self):
        # Sitemaps include duplicate ?id=N variants — regex must accept them.
        url = "https://help.qlik.com/talend/en-US/remote-engine-user-guide-linux/Cloud/creating-remote-engines?id=2"
        m = URL_RE.match(url)
        assert m is not None
        assert m.group("page_slug") == "creating-remote-engines"

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError):
            _parse_url("https://example.com/not-a-talend-url")


CLOUD_BASE = (
    "https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub"
    "/DataIntegration"
)


class TestParseCloudURL:
    def test_flat_cloud_page(self):
        p = _parse_url(f"{CLOUD_BASE}/Lakehouse/lakehouse-pipeline-architecture.htm")
        assert p["source"] == "cloud-services"
        assert p["locale"] == "en-US"
        assert p["product_slug"] == "lakehouse"  # section, lower-cased
        assert p["version"] == "Cloud"
        assert p["major_version"] == "Cloud"
        assert p["r_code"] == ""
        assert p["page_slug"] == "lakehouse-pipeline-architecture"

    def test_deep_cloud_page_keeps_subfolders_in_slug(self):
        # section/<subfolder>/<page>.htm — subfolders folded into the slug so
        # two connectors with the same page name don't collide on disk.
        p = _parse_url(f"{CLOUD_BASE}/SourcesConnections/MySQL/MySQL-source.htm")
        assert p["product_slug"] == "sourcesconnections"
        assert p["page_slug"] == "MySQL__MySQL-source"

    def test_cloud_page_with_query_string(self):
        p = _parse_url(f"{CLOUD_BASE}/DeclarativePipelines/Declarative-pipelines-overview.htm?id=7")
        assert p["product_slug"] == "declarativepipelines"
        assert p["page_slug"] == "Declarative-pipelines-overview"

    def test_talend_regex_does_not_match_cloud(self):
        assert URL_RE.match(f"{CLOUD_BASE}/Lakehouse/x.htm") is None

    def test_canonicalize_cloud_strips_query(self):
        u = f"{CLOUD_BASE}/Lakehouse/x.htm"
        assert canonicalize(u + "?id=9") == u


class TestCanonicalize:
    def test_strips_query(self):
        assert (
            canonicalize("https://help.qlik.com/talend/en-US/x/Cloud/y?id=2")
            == "https://help.qlik.com/talend/en-US/x/Cloud/y"
        )

    def test_strips_fragment(self):
        assert (
            canonicalize("https://help.qlik.com/talend/en-US/x/Cloud/y#section")
            == "https://help.qlik.com/talend/en-US/x/Cloud/y"
        )

    def test_passthrough_clean_url(self):
        clean = "https://help.qlik.com/talend/en-US/x/Cloud/y"
        assert canonicalize(clean) == clean
