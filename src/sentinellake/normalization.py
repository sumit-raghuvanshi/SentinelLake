"""Convert source-specific threat-feed records into canonical IOC records."""

from datetime import datetime, timezone


def get_ingested_at() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_confidence_score(value: object) -> int | str | None:
    """Convert a supplied confidence value to an integer when possible."""
    if value is None:
        return None

    text = str(value).strip()

    if text == "":
        return None

    try:
        return int(text)
    except ValueError:
        return text


def build_canonical_record(
    source_record: dict[str, object],
    *,
    ioc_type: str,
    ioc_value: object,
    threat_category: object,
    confidence_score: object,
    first_seen: object,
    last_seen: object,
    source_record_id: object,
    ingested_at: str,
) -> dict[str, object]:
    """Build one canonical IOC record while preserving source evidence."""
    return {
        "ioc_type": ioc_type,
        "ioc_value": str(ioc_value or "").strip(),
        "threat_category": str(threat_category or "").strip() or None,
        "confidence_score": normalize_confidence_score(confidence_score),
        "first_seen": str(first_seen or "").strip() or None,
        "last_seen": str(last_seen or "").strip() or None,
        "source_name": source_record["source_name"],
        "source_record_id": str(source_record_id or "").strip() or None,
        "ingested_at": ingested_at,
        "raw_record": source_record["raw_record"],
        "validation_status": "pending",
        "quarantine_reason": None,
    }


def normalize_demo_ip_feed(
    source_record: dict[str, object],
    ingested_at: str,
) -> dict[str, object]:
    """Normalize a record from the CSV IP reputation feed."""
    raw_record = source_record["raw_record"]

    return build_canonical_record(
        source_record,
        ioc_type="ipv4",
        ioc_value=raw_record.get("indicator"),
        threat_category=raw_record.get("category"),
        confidence_score=raw_record.get("confidence"),
        first_seen=raw_record.get("first_observed"),
        last_seen=raw_record.get("last_observed"),
        source_record_id=raw_record.get("feed_id"),
        ingested_at=ingested_at,
    )


def normalize_demo_domain_feed(
    source_record: dict[str, object],
    ingested_at: str,
) -> dict[str, object]:
    """Normalize a record from the JSON domain watchlist feed."""
    raw_record = source_record["raw_record"]

    return build_canonical_record(
        source_record,
        ioc_type="domain",
        ioc_value=raw_record.get("domain"),
        threat_category=raw_record.get("classification"),
        confidence_score=raw_record.get("score"),
        first_seen=raw_record.get("first_seen_at"),
        last_seen=raw_record.get("last_seen_at"),
        source_record_id=raw_record.get("id"),
        ingested_at=ingested_at,
    )


def normalize_demo_community_feed(
    source_record: dict[str, object],
    ingested_at: str,
) -> dict[str, object]:
    """Normalize a record from the community IOC JSON feed."""
    raw_record = source_record["raw_record"]

    return build_canonical_record(
        source_record,
        ioc_type=str(raw_record.get("indicator_kind") or "").strip(),
        ioc_value=raw_record.get("value"),
        threat_category=raw_record.get("threat_label"),
        confidence_score=raw_record.get("reputation"),
        first_seen=raw_record.get("seen_at"),
        last_seen=raw_record.get("seen_at"),
        source_record_id=raw_record.get("reference_id"),
        ingested_at=ingested_at,
    )


def normalize_record(
    source_record: dict[str, object],
    ingested_at: str | None = None,
) -> dict[str, object]:
    """Normalize one known threat-feed record into the canonical schema."""
    timestamp = ingested_at or get_ingested_at()
    source_name = source_record["source_name"]

    if source_name == "demo_ip_feed":
        return normalize_demo_ip_feed(source_record, timestamp)

    if source_name == "demo_domain_feed":
        return normalize_demo_domain_feed(source_record, timestamp)

    if source_name == "demo_community_feed":
        return normalize_demo_community_feed(source_record, timestamp)

    raise ValueError(f"Unsupported threat-feed source: {source_name}")