-- Tracks the latest processed version of every consolidated IOC.
-- This lets SentinelLake identify new, changed, and unchanged IOCs.

CREATE TABLE IF NOT EXISTS ioc_processing_state (
    ioc_type TEXT NOT NULL,
    ioc_value TEXT NOT NULL,
    record_fingerprint TEXT NOT NULL,
    first_processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    times_seen INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (ioc_type, ioc_value)
);

CREATE INDEX IF NOT EXISTS idx_ioc_processing_state_last_changed_at
    ON ioc_processing_state (last_changed_at DESC);