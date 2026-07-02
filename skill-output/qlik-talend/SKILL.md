---
name: qlik-talend
description: Authoritative reference for Qlik Talend (Studio 8.0, Talend Management Console, Remote Engine, SDLC/CI-CD, installation/migration, ESB, Talend APIs, Data Stewardship, Data Preparation) and Qlik Talend Cloud Data Integration. Use when answering questions about Talend Studio jobs/components, TMC promotions/schedules/users, Remote Engine setup/configuration, Dynamic Engine, hybrid installations, Studio→TMC publishing, Git/CI-CD with Talend, ESB routes/services/container/microservices/Activity Monitoring Console (AMC)/JMX monitoring, Talend Data Stewardship campaigns/tasks/data-models and its REST API, Talend Data Preparation recipes/datasets/preparations, API Designer/Tester, or anything mentioning Talend on Qlik Cloud. Also covers the Qlik "agentic data engineering" release: Qlik Open Lakehouse (Apache Iceberg, streaming, compute), declarative pipelines, AI-assisted / SQL-from-prompt transformations, data products and data marts, knowledge marts, source/target and SaaS-application connections, LLM and vector-database connections, and replication tasks. Sourced from help.qlik.com/talend and the Qlik Cloud Help (help.qlik.com/en-US/cloud-services).
---

# Qlik Talend Documentation Skill

## When to use this skill

Trigger on questions that mention Talend products or workflows, including but not limited to:

- **Talend Studio**: jobs, joblets, routes, components (`tFooBar`), context variables, metadata, palette, projects, Git, build/export, publish to cloud, debug, MapReduce/Spark, ESB, MDM (note: MDM 8.0 is out of scope here).
- **Talend ESB (8.0)**: Routes, Services, Camel, CXF, Container-Administration (Karaf/Felix), Security Token Service (STS), Infrastructure Services (Service Registry, Service Activity Monitoring), System Management Integration (JMX/Jolokia/Nagios monitoring), ESB Best Practices, the Activity Monitoring Console (AMC), Talend microservices (introduction + best practices), and runtime operations (auto-scaling on AWS, multi-container setup, Syncope IAM).
- **Talend Management Console (TMC)**: promotions, environments, workspaces, run profiles, schedules, plans, tasks, artifact repository, users/roles/tokens, audit logs, SSO, account.
- **Remote Engine / Dynamic Engine**: install (Linux & Windows), configure, pair with TMC, run jobs/pipelines, troubleshooting, upgrade, Gen2.
- **Installation / migration / upgrade**: Studio installer, TAC upgrade paths, hybrid deployments, JDK requirements, Tomcat upgrades.
- **SDLC / CI-CD with Talend**: development life-cycle, environment promotions, Git workflows, automation patterns.
- **Talend Cloud platform**: getting started, glossary, regions, account migration, Qlik-Talend integration.
- **Talend Data Stewardship**: campaigns, tasks, data models, workflows (arbitration / resolution / merging / grouping), label & validation rules, assignment, the stewardship console, the TDQL query language, **data quality rules** (basic & advanced mode, the **Data Shaping Expression Language**), and the **Data Stewardship REST API**.
- **Talend Data Preparation**: preparations, recipes, datasets, functions, data cleansing/masking, exporting prepared data, and using Data Prep within pipelines.

**Qlik Talend Cloud — Data Integration** (Qlik Cloud Help; the "agentic data engineering" release):

- **Qlik Open Lakehouse**: Apache Iceberg lakehouse in your own AWS account, batch + streaming ingestion, compute clusters, optimization, monitoring, cost/compute value meters.
- **Pipelines & transformations**: declarative pipelines, transformation flows, AI-assisted transformations and SQL-from-text-prompt, processors, data products & data marts, knowledge marts, replication tasks.
- **Connections**: source & target connectors, 100+ SaaS web-application connectors, landing, file storage.
- **GenAI building blocks**: LLM connections (OpenAI, Azure OpenAI, Amazon Bedrock, …) and vector-database connections (Pinecone, Elasticsearch, OpenSearch, …).
- **API Designer** (Data Integration): design, document and mock REST APIs.
- **DI platform**: getting started, spaces, deployment / system requirements, data stewardship, catalog, version control, marketplace.

If a question is *vaguely* Talend-related but really about a non-Talend product (Qlik Sense, QlikView, Replicate, Compose, NPrinting), do **not** rely on this skill — it does not contain those docs.

## Coverage scope

| Group | Versions | Pages | Topics |
|-------|---------|------:|-------:|
| api | Cloud | ~314 | ~56 |
| cloud-api-designer | Cloud | ~59 | ~1 |
| cloud-connections | Cloud | ~246 | ~26 |
| cloud-di-platform | Cloud | ~37 | ~13 |
| cloud-genai | Cloud | ~6 | ~3 |
| cloud-lakehouse | Cloud | ~192 | ~11 |
| cloud-pipelines | Cloud | ~77 | ~12 |
| cloud-platform | Cloud | ~127 | ~20 |
| data-apps | Cloud + 8.0 | ~579 | ~75 |
| esb | 8.0 | ~1,063 | ~195 |
| installation | Cloud + 8.0 | ~1,032 | ~150 |
| remote-engine | Cloud | ~324 | ~69 |
| sdlc-cicd | Cloud + 8.0 | ~68 | ~16 |
| studio | 8.0 (latest R-code at crawl) | ~1,068 | ~128 |
| tmc | Cloud | ~328 | ~58 |

**Out of scope (do not assume coverage):** Components/connectors reference, Data Catalog, Data Quality, MDM, Data Inventory, all 7.x docs.

## How to look something up — progressive disclosure

Always work outside-in. Do NOT load the entire skill folder; pick the smallest path:

1. **Read `index.md`** (≈2 KB). Identify which **product group** matches the question.
2. **Read `index/<group>.md`** (≈10–30 KB). Find the matching **topic** (one-line blurb per topic shows what's inside).
3. **Read `topics/<group>/<guide>/<version>/<topic>.md`** (≈3–10 KB). This gives you:
   - TL;DR per page in the cluster
   - Procedure outlines (H2/H3 headings of each page)
   - Note / Restriction / Important blocks
   - Version constraints
   - A `## Citations` table mapping each `[^P-N]` anchor → exact raw file path + canonical URL.
4. **Only if you need full procedure text, exact parameter values, or verbatim quotes**, open the raw file from the topic's Citations table:  
   `raw/<group>/<guide>/<version>/<page>.md`. Each raw file has a YAML frontmatter with `source_url`, `source` (`talend` or `cloud-services`), `major_version`, `r_code`, `version_constraints`, `breadcrumbs`. Cloud Data Integration pages use `version: Cloud` and cite `help.qlik.com/en-US/cloud-services/...` URLs.

## Citation discipline

When you answer from this skill, **always cite**:

- The Qlik major version (`Cloud` or `8.0`) and, for Studio, the R-code (e.g. `8.0-R2026-04`).
- The source URL from the raw file's frontmatter (or the `Source URL` column of the topic's Citations table).

Example: "In TMC (Cloud), promotion environments are configured under … [source: help.qlik.com/talend/en-US/management-console-user-guide/Cloud/manage-promotion]."

## Versioning gotchas

- Studio R-codes (`R2026-04`, etc.) bump monthly. The R-code in this skill is whatever was latest at crawl time — see `meta/manifest.json` (`stats.last_run_at`). If the user is on an older R-code, flag that some procedures may have shifted.
- Cloud docs are continuously updated; treat as "as of crawl date".
- 7.x is **not** included. If the user is on 7.x, say so explicitly and do not extrapolate.
- Some pages have explicit `version_constraints` in their frontmatter (e.g. "Talend Studio 8.0.1 R2024-05 or higher"). Honor these when applicable.

## Anti-patterns

- Do NOT load `topics/**/*.md` recursively — that's the whole index in one go (~2 MB) and defeats the purpose.
- Do NOT answer "from memory" if the topic file disagrees — the skill is the source of truth.
- Do NOT cite the topic file's TL;DR alone for safety-relevant answers (security, encryption, license, upgrade compatibility) — open the raw file and verify.

## Troubleshooting the skill

- If a topic looks empty or its Citations table is missing rows, the topic may need rebuilding (`uv run python -m distill.build_topics` in the source repo).
- If a question's answer isn't in `index/<group>.md`, the topic may have been clustered under a sibling guide. Try other groups (e.g. a "Studio Git" question may live under `sdlc-cicd` rather than `studio`).
- If the user asks about a product that's listed as out-of-scope, say so plainly and offer to expand the skill in a future crawl.
