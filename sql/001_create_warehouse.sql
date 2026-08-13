CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id BIGSERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    source_count INTEGER,
    records_ingested INTEGER,
    records_accepted_before_deduplication INTEGER,
    unique_iocs_accepted INTEGER,
    duplicate_ioc_records_consolidated INTEGER,
    records_quarantined INTEGER,
    processing_duration_milliseconds NUMERIC(12, 2),
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS threat_iocs (
    ioc_id BIGSERIAL PRIMARY KEY,
    ioc_type TEXT NOT NULL CHECK (
        ioc_type IN ('ipv4', 'domain', 'url', 'sha256')
    ),
    ioc_value TEXT NOT NULL,
    confidence_score INTEGER CHECK (
        confidence_score BETWEEN 0 AND 100
    ),
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    first_ingested_at TIMESTAMPTZ NOT NULL,
    last_ingested_at TIMESTAMPTZ NOT NULL,
    source_count INTEGER NOT NULL DEFAULT 1 CHECK (
        source_count >= 1
    ),
    source_names JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_record_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    threat_categories JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (ioc_type, ioc_value)
);

CREATE TABLE IF NOT EXISTS ioc_observations (
    observation_id BIGSERIAL PRIMARY KEY,
    ioc_id BIGINT NOT NULL REFERENCES threat_iocs(ioc_id),
    run_id BIGINT NOT NULL REFERENCES pipeline_runs(run_id),
    source_name TEXT NOT NULL,
    source_record_id TEXT,
    threat_category TEXT,
    confidence_score INTEGER CHECK (
        confidence_score BETWEEN 0 AND 100
    ),
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_record JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS quarantined_iocs (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES pipeline_runs(run_id),
    source_name TEXT,
    source_record_id TEXT,
    ioc_type TEXT,
    ioc_value TEXT,
    quarantine_reason TEXT NOT NULL,
    raw_record JSONB NOT NULL,
    quarantined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_threat_iocs_type_value
    ON threat_iocs (ioc_type, ioc_value);

CREATE INDEX IF NOT EXISTS idx_ioc_observations_ioc_id
    ON ioc_observations (ioc_id);

CREATE INDEX IF NOT EXISTS idx_quarantined_iocs_run_id
    ON quarantined_iocs (run_id);