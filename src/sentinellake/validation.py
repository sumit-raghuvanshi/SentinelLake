"""Validate canonical SentinelLake IOC records."""

import ipaddress
import re


SUPPORTED_IOC_TYPES = {"ipv4", "domain", "url", "sha256"}
DOMAIN_PATTERN = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$",
    re.IGNORECASE,
)
SHA256_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")


def is_valid_ipv4(value: str) -> bool:
    """Return whether value is a valid IPv4 address."""
    try:
        return isinstance(ipaddress.ip_address(value), ipaddress.IPv4Address)
    except ValueError:
        return False


def is_valid_domain(value: str) -> bool:
    """Return whether value matches SentinelLake's basic domain format."""
    return bool(DOMAIN_PATTERN.fullmatch(value))


def is_valid_url(value: str) -> bool:
    """Return whether value has a basic HTTP or HTTPS URL format."""
    return value.startswith(("http://", "https://")) and "." in value


def is_valid_sha256(value: str) -> bool:
    """Return whether value is a 64-character hexadecimal SHA-256 hash."""
    return bool(SHA256_PATTERN.fullmatch(value))


def get_validation_error(record: dict[str, object]) -> str | None:
    """Return a quarantine reason, or None when a record is valid."""
    ioc_type = str(record.get("ioc_type") or "").strip()
    ioc_value = str(record.get("ioc_value") or "").strip()
    source_name = str(record.get("source_name") or "").strip()
    ingested_at = str(record.get("ingested_at") or "").strip()
    confidence_score = record.get("confidence_score")

    if ioc_type not in SUPPORTED_IOC_TYPES:
        return "unsupported_ioc_type"

    if ioc_value == "":
        return "missing_ioc_value"

    if source_name == "":
        return "missing_source_name"

    if ingested_at == "":
        return "missing_ingested_at"

    if ioc_type == "ipv4" and not is_valid_ipv4(ioc_value):
        return "invalid_ipv4_format"

    if ioc_type == "domain" and not is_valid_domain(ioc_value):
        return "invalid_domain_format"

    if ioc_type == "url" and not is_valid_url(ioc_value):
        return "invalid_url_format"

    if ioc_type == "sha256" and not is_valid_sha256(ioc_value):
        return "invalid_sha256_format"

    if confidence_score is not None and (
        not isinstance(confidence_score, int)
        or confidence_score < 0
        or confidence_score > 100
    ):
        return "invalid_confidence_score"

    return None


def validate_record(record: dict[str, object]) -> dict[str, object]:
    """Return a record marked as accepted or quarantined."""
    validated_record = dict(record)
    error = get_validation_error(validated_record)

    if error is None:
        validated_record["validation_status"] = "accepted"
        validated_record["quarantine_reason"] = None
    else:
        validated_record["validation_status"] = "quarantined"
        validated_record["quarantine_reason"] = error

    return validated_record