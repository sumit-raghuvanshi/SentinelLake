# SentinelLake Canonical IOC Data Dictionary

## Purpose

Threat-intelligence sources use different schemas and formats. SentinelLake converts them into one canonical Indicator of Compromise (IOC) schema before validation, quarantine routing, and deduplication.

## Canonical IOC fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `ioc_type` | string | Yes | IOC category: `ipv4`, `domain`, `url`, or `sha256` |
| `ioc_value` | string | Yes | Normalized indicator value |
| `threat_category` | string | No | Threat category from the first source record |
| `confidence_score` | integer | No | Confidence score from 0 to 100 |
| `first_seen` | ISO 8601 timestamp | No | Earliest known observation time |
| `last_seen` | ISO 8601 timestamp | No | Most recent known observation time |
| `source_name` | string | Yes | Name of the first source that supplied the IOC |
| `source_record_id` | string | No | Source identifier from the first source record |
| `ingested_at` | ISO 8601 timestamp | Yes | Time SentinelLake processed the record |
| `raw_record` | object | Yes | First original source record |
| `validation_status` | string | Yes | `accepted` or `quarantined` |
| `quarantine_reason` | string | No | Rejection reason for quarantined records |

## Consolidated IOC fields

These fields are added after deduplication when the same IOC is found in more than one accepted source record.

| Field | Type | Description |
|---|---|---|
| `source_count` | integer | Number of distinct sources that reported the IOC |
| `source_names` | array | Distinct source names that reported the IOC |
| `source_record_ids` | array | Source record identifiers associated with the IOC |
| `source_evidence` | array | Source name, source record ID, and raw record from every source |
| `threat_categories` | array | All observed non-blank threat categories |
| `record_count_before_deduplication` | integer | Number of accepted source records consolidated into this IOC |

## Validation rules

| Rule | Result if invalid |
|---|---|
| Unsupported or missing IOC type | Quarantine record |
| Missing IOC value | Quarantine record |
| Invalid IPv4 address | Quarantine record |
| Invalid domain format | Quarantine record |
| Invalid URL format | Quarantine record |
| Invalid SHA-256 format | Quarantine record |
| Missing source name or ingestion timestamp | Quarantine record |
| Confidence score outside 0 to 100 | Quarantine record |

## Demo deduplication example

`185.220.101.34` appears in both `demo_ip_feed` and `demo_community_feed`.

After deduplication, SentinelLake stores one accepted IOC with:

- `source_count`: `2`
- Both source names and raw records in `source_evidence`
- Highest confidence score: `90`
- Both categories: `malware` and `ransomware`