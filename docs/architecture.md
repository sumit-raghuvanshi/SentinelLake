# SentinelLake Architecture

## Purpose

SentinelLake is a self-healing cyber threat intelligence data platform. It ingests threat intelligence feeds, converts them into a common IOC format, validates data quality, quarantines invalid records, stores accepted records for analysis, and records pipeline health.

## MVP pipeline

```text
Threat intelligence source files / public feeds
        |
        v
Python ingestion layer
        |
        v
Raw data storage
        |
        v
Normalization to a canonical IOC schema
        |
        +--> Invalid records --> Quarantine storage
        |
        v
Deduplication and validation
        |
        v
PostgreSQL threat-intelligence warehouse
        |
        v
Pipeline metrics, logs, incidents, and retry handling