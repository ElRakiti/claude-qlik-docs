"""README/SKILL.md meta regeneration — Cloud Help entry-URL derivation."""
from __future__ import annotations

from package.update_meta import _cloud_entry_urls

CLOUD_BASE = (
    "https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub"
    "/DataIntegration"
)


class TestCloudEntryURLs:
    def test_one_per_section_prefers_overview_skips_uncrawled(self):
        pages = {
            f"{CLOUD_BASE}/Lakehouse/zzzzz-deep-detail.htm": {"out_path": "raw/a.md"},
            f"{CLOUD_BASE}/Lakehouse/lakehouse-overview.htm": {"out_path": "raw/b.md"},
            # 404 / uncrawled page (no out_path) must not be chosen as an entry:
            f"{CLOUD_BASE}/Transformation/broken.htm": {"status": 404},
            f"{CLOUD_BASE}/Transformation/Transformations.htm": {"out_path": "raw/c.md"},
            # a Talend URL must be ignored entirely:
            "https://help.qlik.com/talend/en-US/x/Cloud/y": {"out_path": "raw/t.md"},
        }
        urls = _cloud_entry_urls(pages, ["Lakehouse", "Transformation", "Missing"])
        assert urls == [
            f"{CLOUD_BASE}/Lakehouse/lakehouse-overview.htm",  # overview preferred
            f"{CLOUD_BASE}/Transformation/Transformations.htm",  # only crawled one
        ]

    def test_missing_section_yields_no_entry(self):
        assert _cloud_entry_urls({}, ["Lakehouse"]) == []

    def test_section_folder_name_does_not_falsely_prefer_pages(self):
        # The section folder is literally "Introduction"; matching the whole URL
        # would mark EVERY page preferred and collapse to shortest. We must match
        # only the leaf filename, so the real intro page wins.
        pages = {
            f"{CLOUD_BASE}/Introduction/aa.htm": {"out_path": "raw/a.md"},
            f"{CLOUD_BASE}/Introduction/Data-services-introduction.htm": {"out_path": "raw/b.md"},
        }
        assert _cloud_entry_urls(pages, ["Introduction"]) == [
            f"{CLOUD_BASE}/Introduction/Data-services-introduction.htm"
        ]

    def test_falls_back_to_shortest_when_no_overview(self):
        pages = {
            f"{CLOUD_BASE}/DataProducts/a-very-long-page-name.htm": {"out_path": "raw/a.md"},
            f"{CLOUD_BASE}/DataProducts/short.htm": {"out_path": "raw/b.md"},
        }
        assert _cloud_entry_urls(pages, ["DataProducts"]) == [
            f"{CLOUD_BASE}/DataProducts/short.htm"
        ]
