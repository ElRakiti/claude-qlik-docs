"""Crawler configuration: which Talend sitemaps to crawl.

Each entry maps a logical product group → list of sub-sitemap names (without
.xml suffix). The crawler resolves these against
`https://help.qlik.com/talend/sitemap_<name>_en-US.xml`.

Studio User Guide is special: its sitemap name embeds the R-code. We resolve
the latest R-code at runtime by inspecting the Talend sitemap-index.

Integrated documentation entry pages (one per sitemap below):

studio:
- https://help.qlik.com/talend/en-US/studio-user-guide/8.0-R<latest>/
- https://help.qlik.com/talend/en-US/discovering-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/creating-using-metadata-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/using-context-variables-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/studio-getting-started-guide-data-integration/8.0/
- https://help.qlik.com/talend/en-US/joining-two-data-sources-tmap-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/reading-a-file-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/sorting-a-file-talend-studio/8.0/
- https://help.qlik.com/talend/en-US/access-secure-services-with-studio-and-runtime/8.0/
- https://help.qlik.com/talend/en-US/studio-components-availability/8.0/

tmc:
- https://help.qlik.com/talend/en-US/management-console-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/management-console-with-pipeline-designer/Cloud/
- https://help.qlik.com/talend/en-US/tmc-account-limits/Cloud/

remote-engine:
- https://help.qlik.com/talend/en-US/remote-engine-user-guide-linux/Cloud/
- https://help.qlik.com/talend/en-US/remote-engine-user-guide-windows/Cloud/
- https://help.qlik.com/talend/en-US/remote-engine-gen2-quick-start-guide/Cloud/
- https://help.qlik.com/talend/en-US/dynamic-engine-configuration-guide/Cloud/

installation:
- https://help.qlik.com/talend/en-US/installation-guide-linux/Cloud/
- https://help.qlik.com/talend/en-US/installation-guide-windows/Cloud/
- https://help.qlik.com/talend/en-US/installation-guide-linux/8.0/
- https://help.qlik.com/talend/en-US/installation-guide-windows/8.0/
- https://help.qlik.com/talend/en-US/hybrid-installation-guide-linux/Cloud/
- https://help.qlik.com/talend/en-US/hybrid-installation-guide-windows/Cloud/
- https://help.qlik.com/talend/en-US/migration-upgrade-guide/8.0/

sdlc-cicd:
- https://help.qlik.com/talend/en-US/software-dev-lifecycle-best-practices-guide/8.0/
- https://help.qlik.com/talend/en-US/development-operational-management/Cloud/

cloud-platform:
- https://help.qlik.com/talend/en-US/talend-cloud-getting-started/Cloud/
- https://help.qlik.com/talend/en-US/talend-glossary/Cloud/

data-apps:
- https://help.qlik.com/talend/en-US/data-stewardship-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/data-stewardship-getting-started-guide/Cloud/
- https://help.qlik.com/talend/en-US/data-stewardship-examples/Cloud/
- https://help.qlik.com/talend/en-US/data-stewardship-components-query-language/8.0/
- https://help.qlik.com/talend/en-US/data-preparation-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/data-preparation-getting-started/Cloud/
- https://help.qlik.com/talend/en-US/data-shaping-language-reference-guide/8.0/

api:
- https://help.qlik.com/talend/en-US/api-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/api-designer-getting-started-guide/Cloud/
- https://help.qlik.com/talend/en-US/api-designer-user-guide/Cloud/
- https://help.qlik.com/talend/en-US/api-portal-deployment-guide/Cloud/
- https://help.qlik.com/talend/en-US/api-services-getting-started-guide-api-services-platform/Cloud/
- https://help.qlik.com/talend/en-US/api-tester-user-guide/Cloud/

esb:
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

--- SECOND DOC SOURCE: Qlik Cloud Help (help.qlik.com/en-US/cloud-services) ---
The Qlik Talend Cloud "agentic data engineering" docs do NOT live under
help.qlik.com/talend. They are published in the Qlik Cloud Help system, which
uses a different URL scheme (`/en-US/cloud-services/.../Content/Sense_Hub/
DataIntegration/<Section>/<page>.htm`) and a single flat url-set sitemap
(`https://help.qlik.com/sitemap_cloud-services_en-US.xml`) instead of a
per-guide sitemap-index. We crawl the Data Integration subtree and route pages
to groups by their `/DataIntegration/<Section>/` path segment (see
CLOUD_PRODUCT_SECTIONS). Same MadCap `div#topicContent` container as Talend, so
the extractor is shared. Section landing pages:

cloud-lakehouse:
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Lakehouse/lakehouse-pipeline-architecture.htm

cloud-pipelines:
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Transformation/Transformations.htm
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/DeclarativePipelines/Declarative-pipelines-overview.htm

cloud-connections:
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/SourcesConnections/supported-sources.htm

cloud-genai:
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/LLMConnections/
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/VectorDBs/

cloud-api-designer:
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/APIDesigner/

cloud-di-platform:
- https://help.qlik.com/en-US/cloud-services/Subsystems/Hub/Content/Sense_Hub/DataIntegration/Introduction/Data-services-introduction.htm

To extend coverage with another TALEND guide:
1. Look up the sub-sitemap name in https://help.qlik.com/talend/sitemap.xml
   (filter for `_<latest-version>_en-US.xml`).
2. Add `<sitemap-name>_<version>` to the appropriate group below (or create
   a new group key).
3. Add a display label to GROUP_LABELS and a version string to GROUP_VERSIONS
   below (used by `package/update_meta.py` to regenerate README + SKILL.md),
   and a one-line blurb to GROUP_DESCRIPTIONS in `package/build_index.py`
   (used for the Description column of `index.md` — easy to forget, leaves an
   empty cell if missed).
4. Hand-update the bits that are NOT auto-generated:
   - SKILL.md `description` frontmatter (the auto-trigger keywords for claude.ai),
   - SKILL.md "When to use this skill" bullets and the "Out of scope" line,
   - README.md "### Out of scope (current)" list.
   (The SKILL.md coverage table and the README guide list ARE auto-generated.)
5. Run `make fresh` (or just `make crawl && make build`).

To extend coverage with a CLOUD (help.qlik.com/cloud-services) section: add
the exact `/DataIntegration/<Section>/` segment to a group in
CLOUD_PRODUCT_SECTIONS (verify it exists first:
`curl -s https://help.qlik.com/sitemap_cloud-services_en-US.xml | grep -oE
'DataIntegration/[^/]+/' | sort -u`), then do steps 3-5 above. Cloud groups
use "Cloud" as their version and need no sitemap-name entry.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Group metadata — used by package/update_meta.py to auto-regenerate
# README.md and SKILL.md after each build.
# Add an entry here whenever you add a new product group to PRODUCT_SITEMAPS.
# ---------------------------------------------------------------------------

# Short parenthetical label shown in README "Integrated documentation guides".
GROUP_LABELS: dict[str, str] = {
    "studio": "Talend Studio 8.0 — latest R-code at crawl",
    "tmc": "Talend Management Console, Cloud",
    "remote-engine": "Remote Engine + Dynamic Engine, Cloud",
    "installation": "Cloud + 8.0",
    "sdlc-cicd": "SDLC / CI-CD",
    "cloud-platform": "Talend Cloud platform basics",
    "data-apps": "Talend Data Stewardship + Data Preparation, Cloud",
    "api": "Talend Cloud APIs + API Designer / Portal / Services / Tester",
    "esb": "Talend ESB 8.0 — Camel routes, CXF services, Karaf container, microservices, Activity Monitoring Console",
    # Cloud Help (help.qlik.com/cloud-services) — Qlik Talend Cloud Data Integration:
    "cloud-lakehouse": "Qlik Talend Cloud — Open Lakehouse (Apache Iceberg, streaming, compute)",
    "cloud-pipelines": "Qlik Talend Cloud — transformations, declarative/AI-assisted pipelines, data products & marts, replication",
    "cloud-connections": "Qlik Talend Cloud — source/target & SaaS-application connections, landing, file storage",
    "cloud-genai": "Qlik Talend Cloud — GenAI: LLM connections & vector databases",
    "cloud-api-designer": "Qlik Talend Cloud — API Designer (Data Integration)",
    "cloud-di-platform": "Qlik Talend Cloud — Data Integration platform: intro, spaces, deploy, stewardship, catalog",
}

# Version string shown in the SKILL.md coverage table.
GROUP_VERSIONS: dict[str, str] = {
    "studio": "8.0 (latest R-code at crawl)",
    "tmc": "Cloud",
    "remote-engine": "Cloud",
    "installation": "Cloud + 8.0",
    "sdlc-cicd": "Cloud + 8.0",
    "cloud-platform": "Cloud",
    "data-apps": "Cloud + 8.0",
    "api": "Cloud",
    "esb": "8.0",
    "cloud-lakehouse": "Cloud",
    "cloud-pipelines": "Cloud",
    "cloud-connections": "Cloud",
    "cloud-genai": "Cloud",
    "cloud-api-designer": "Cloud",
    "cloud-di-platform": "Cloud",
}

USER_AGENT = "qlik-docs-skill-builder/0.1 (+https://github.com/mkcimt/claude-qlik-docs)"
LOCALE = "en-US"
TALEND_SITEMAP_INDEX = "https://help.qlik.com/talend/sitemap.xml"
SITEMAP_URL_TEMPLATE = "https://help.qlik.com/talend/sitemap_{name}_{locale}.xml"

# Conservative throttle (sequential, 1 req/s)
REQUEST_DELAY_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 30.0
MAX_RETRIES = 5

# Qlik Cloud Help robots.txt requests `Crawl-delay: 5`. This is enforced as a
# per-request floor for cloud-services pages regardless of the --delay flag, so
# a no-filter `tasks.py crawl` can't accidentally hammer them at 0.5s (see run.py).
CLOUD_CRAWL_DELAY_SECONDS = 5.0

# Logical groups → static sitemap names (no R-codes here; Studio is dynamic).
# Any name containing the placeholder "<latest-r>" gets resolved against the
# sitemap-index for the most recent matching variant.
PRODUCT_SITEMAPS: dict[str, list[str]] = {
    "studio": [
        "studio-user-guide_<latest-r>",
        "discovering-talend-studio_8.0",
        "creating-using-metadata-talend-studio_8.0",
        "using-context-variables-talend-studio_8.0",
        "studio-getting-started-guide-data-integration_8.0",
        "joining-two-data-sources-tmap-talend-studio_8.0",
        "reading-a-file-talend-studio_8.0",
        "sorting-a-file-talend-studio_8.0",
        "access-secure-services-with-studio-and-runtime_8.0",
        "studio-components-availability_8.0",
    ],
    "tmc": [
        "management-console-user-guide_Cloud",
        "management-console-with-pipeline-designer_Cloud",
        "tmc-account-limits_Cloud",
    ],
    "remote-engine": [
        "remote-engine-user-guide-linux_Cloud",
        "remote-engine-user-guide-windows_Cloud",
        "remote-engine-gen2-quick-start-guide_Cloud",
        "dynamic-engine-configuration-guide_Cloud",
    ],
    "installation": [
        "installation-guide-linux_Cloud",
        "installation-guide-windows_Cloud",
        "installation-guide-linux_8.0",
        "installation-guide-windows_8.0",
        "hybrid-installation-guide-linux_Cloud",
        "hybrid-installation-guide-windows_Cloud",
        "migration-upgrade-guide_8.0",
    ],
    "sdlc-cicd": [
        "software-dev-lifecycle-best-practices-guide_8.0",
        "development-operational-management_Cloud",
    ],
    "cloud-platform": [
        "talend-cloud-getting-started_Cloud",
        "talend-glossary_Cloud",
    ],
    "data-apps": [
        "data-stewardship-user-guide_Cloud",
        "data-stewardship-getting-started-guide_Cloud",
        "data-stewardship-examples_Cloud",
        "data-stewardship-components-query-language_8.0",
        "data-preparation-user-guide_Cloud",
        "data-preparation-getting-started_Cloud",
        "data-shaping-language-reference-guide_8.0",
    ],
    "api": [
        "api-user-guide_Cloud",
        "api-designer-getting-started-guide_Cloud",
        "api-designer-user-guide_Cloud",
        "api-portal-deployment-guide_Cloud",
        "api-services-getting-started-guide-api-services-platform_Cloud",
        "api-tester-user-guide_Cloud",
    ],
    "esb": [
        "talend-esb_8.0",
        "esb-developer-guide_8.0",
        "esb-service-developer-guide_8.0",
        "esb-container-administration-guide_8.0",
        "esb-sts-user-guide_8.0",
        "esb-infra-services-configuration-guide_8.0",
        "esb-system-management_8.0",
        "esb-best-practices_8.0",
        "studio-getting-started-guide-esb_8.0",
        "studio-getting-started-guide-data-services-platform_8.0",
        "esb-glossary_8.0",
        "activity-monitoring-console-user-guide_8.0",
        "microservice-introduction_8.0",
        "microservice-best-practice_8.0",
        "esb-runtime-auto-scaling-on-aws_8.0",
        "configure-multiple-container_8.0",
        "use-syncope-with-esb_8.0",
        "core-framework-updates-of-esb-801-r2023-08_8.0",
        "data-service-route-example_8.0",
        "esb-read-hl7-message_8.0",
        "web-service-proxy_8.0",
    ],
}

# ---------------------------------------------------------------------------
# Second doc source: Qlik Cloud Help (help.qlik.com/en-US/cloud-services).
# One flat url-set sitemap (not a per-guide index). We select the Data
# Integration subtree and route each page to a group by its
# `/DataIntegration/<Section>/` path segment. The section segments are
# case-sensitive and must match the URL exactly (verify against the sitemap).
# ---------------------------------------------------------------------------
CLOUD_SERVICES_SITEMAP = "https://help.qlik.com/sitemap_cloud-services_en-US.xml"

# Logical group -> Data Integration section segments it collects.
CLOUD_PRODUCT_SECTIONS: dict[str, list[str]] = {
    "cloud-lakehouse": ["Lakehouse"],
    "cloud-pipelines": [
        "Transformation",
        "DeclarativePipelines",
        "DataProducts",
        "DataMarts",
        "KnowledgeMart",
        "Replicating",
    ],
    "cloud-connections": [
        "SourcesConnections",
        "TargetConnections",
        "WebApplications",
        "Landing",
        "FileStorage",
        "Storage",
    ],
    "cloud-genai": ["LLMConnections", "VectorDBs"],
    "cloud-api-designer": ["APIDesigner"],
    "cloud-di-platform": [
        "Introduction",
        "Onboarding",
        "Deploying",
        "DataSpaces",
        "DataStewardship",
        "Catalog",
        "VersionControl",
        "Marketplace",
        "Analytics",
    ],
}

# All crawlable logical groups across both doc sources (Talend + Cloud Help).
# Used for the `--product` choices and the `doctor` drift check.
ALL_GROUPS: list[str] = sorted(set(PRODUCT_SITEMAPS) | set(CLOUD_PRODUCT_SECTIONS))
