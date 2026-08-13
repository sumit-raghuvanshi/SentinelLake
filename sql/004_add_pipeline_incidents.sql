-- Stores health incidents detected during SentinelLake pipeline monitoring.

CREATE TABLE IF NOT EXISTS pipeline_incidents (
    incident_id BIGSERIAL PRIMARY KEY,
    incident_type TEXT NOT NULL,
    severity TEXT NOT NULL
        CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'resolved', 'ignored')),
    message TEXT NOT NULL,
    incident_context JSONB NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recovery_attempted BOOLEAN NOT NULL DEFAULT FALSE,
    recovery_status TEXT,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_pipeline_incidents_open
    ON pipeline_incidents (status, detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_pipeline_incidents_type
    ON pipeline_incidents (incident_type, detected_at DESC);