# Changelog

All notable changes to SentinelLake are documented in this file.

## 1.0.0 - 2026-08-14

### Added

- Fictional multi-format threat-feed ingestion and canonical IOC normalization.
- Validation, quarantine routing, deduplication, incremental history, local data-lake archiving, and local PostgreSQL loading.
- Local Docker Compose services for PostgreSQL, Airflow, and Spark analytics.
- Observability, health checks, incident recording, controlled retry, unit tests, and GitHub Actions test automation.
- Optional manual URLhaus recent-CSV raw download with local Auth-Key handling and no key persistence in manifests.

### Release notes

- Generated runtime data is intentionally local only and excluded from Git.
- URLhaus download is not automatically integrated into the scheduled pipeline in this release.
