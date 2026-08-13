-- Stores an immutable history event only when an IOC is new or changes.

CREATE TABLE IF NOT EXISTS ioc_change_history (
    change_id BIGSERIAL PRIMARY KEY,
    ioc_type TEXT NOT NULL,
    ioc_value TEXT NOT NULL,
    change_type TEXT NOT NULL
        CHECK (change_type IN ('new', 'changed')),
    record_fingerprint TEXT NOT NULL,
    record_snapshot JSONB NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ioc_change_history_ioc
    ON ioc_change_history (ioc_type, ioc_value, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_ioc_change_history_type
    ON ioc_change_history (change_type, observed_at DESC);