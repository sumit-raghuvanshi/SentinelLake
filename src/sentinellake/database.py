"""PostgreSQL connection helpers for SentinelLake."""

import os

import psycopg


DEFAULT_DATABASE_URL = "postgresql://postgres@localhost:5432/sentinellake"


def get_database_url() -> str:
    """Return the configured database URL without storing a password in code."""
    return os.environ.get(
        "SENTINELLAKE_DATABASE_URL",
        DEFAULT_DATABASE_URL,
    )


def get_database_connection() -> psycopg.Connection:
    """Open a connection to the SentinelLake PostgreSQL warehouse."""
    return psycopg.connect(get_database_url())