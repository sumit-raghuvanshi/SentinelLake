# SentinelLake Canonical IOC Data Dictionary

## Purpose

Every threat-intelligence source uses different column names and formats. SentinelLake converts source records into this canonical Indicator of Compromise (IOC) schema before validation and storage.

## Canonical IOC fields

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `ioc_type` | string | Yes | Indicator category | `ipv4`, `domain`, `url`, `sha256` |
| `ioc_value` | string | Yes | Normalized indicator value | `185.220.101.34` |
| `threat_category` | string | No | Threat classification supplied by the source | `malware` |
| `confidence_score` | integer | No | Source confidence score from 0 to 100 | `85` |
| `first_seen` | ISO 8601 timestamp | No | Earliest known observation time | `2026-08-13T08:00:00Z` |
| `last_seen` | ISO 8601 timestamp | No | Most recent known observation time | `2026-08-13T09:00:00Z` |
| `source_name` | string | Yes | Name of the threat feed | `abuse_ch_feed` |
| `source_record_id` | string | No | Source-specific identifier, if available | `feed-1001` |
| `ingested_at` | ISO 8601 timestamp | Yes | Time SentinelLake received the record | `2026-08-13T10:00:00Z` |
| `raw_record` | object | Yes | Original source record for traceability | Source JSON object |
| `validation_status` | string | Yes | Processing result | `accepted` or `quarantined` |
| `quarantine_reason` | string | No | Reason for rejection | `invalid_ipv4_format` |

## Supported IOC types in the first MVP

- `ipv4`
- `domain`
- `url`
- `sha256`

## Validation rules

| Rule | Result if invalid |
|---|---|
| `ioc_type` is missing or unsupported | Quarantine record |
| `ioc_value` is blank | Quarantine record |
| IPv4 value is not a valid IPv4 address | Quarantine record |
| Domain value is incorrectly formatted | Quarantine record |
| URL value is incorrectly formatted | Quarantine record |
| SHA-256 hash is not exactly 64 hexadecimal characters | Quarantine record |
| `confidence_score` is present but outside 0 to 100 | Quarantine record |
| `source_name` is blank | Quarantine record |

## Example accepted record

```json
{
  "ioc_type": "ipv4",
  "ioc_value": "185.220.101.34",
  "threat_category": "malware",
  "confidence_score": 85,
  "first_seen": "2026-08-13T08:00:00Z",
  "last_seen": "2026-08-13T09:00:00Z",
  "source_name": "demo_ip_feed",
  "source_record_id": "ip-1001",
  "ingested_at": "2026-08-13T10:00:00Z",
  "raw_record": {
    "ip_address": "185.220.101.34",
    "category": "malware",
    "confidence": "85"
  },
  "validation_status": "accepted",