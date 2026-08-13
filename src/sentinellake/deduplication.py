"""Consolidate repeated accepted IOCs from multiple threat feeds."""

from collections import defaultdict


def get_ioc_key(record: dict[str, object]) -> tuple[str, str]:
    """Return a normalized key used to identify the same IOC."""
    ioc_type = str(record.get("ioc_type") or "").strip().lower()
    ioc_value = str(record.get("ioc_value") or "").strip().lower()

    return ioc_type, ioc_value


def unique_non_empty_values(values: list[object]) -> list[str]:
    """Return unique non-empty strings while preserving their order."""
    unique_values = []

    for value in values:
        text = str(value or "").strip()

        if text != "" and text not in unique_values:
            unique_values.append(text)

    return unique_values


def deduplicate_accepted_records(
    records: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Consolidate accepted records that represent the same IOC."""
    grouped_records: dict[tuple[str, str], list[dict[str, object]]] = (
        defaultdict(list)
    )

    for record in records:
        if record.get("validation_status") != "accepted":
            raise ValueError(
                "Only accepted records can be sent to IOC deduplication."
            )

        grouped_records[get_ioc_key(record)].append(record)

    consolidated_records = []

    for group in grouped_records.values():
        consolidated_record = dict(group[0])
        source_names = unique_non_empty_values(
            [record.get("source_name") for record in group]
        )
        source_record_ids = unique_non_empty_values(
            [record.get("source_record_id") for record in group]
        )
        threat_categories = unique_non_empty_values(
            [record.get("threat_category") for record in group]
        )
        confidence_scores = [
            score
            for score in (
                record.get("confidence_score")
                for record in group
            )
            if isinstance(score, int)
        ]
        first_seen_values = unique_non_empty_values(
            [record.get("first_seen") for record in group]
        )
        last_seen_values = unique_non_empty_values(
            [record.get("last_seen") for record in group]
        )
        source_evidence = [
            {
                "source_name": record.get("source_name"),
                "source_record_id": record.get("source_record_id"),
                "raw_record": record.get("raw_record"),
            }
            for record in group
        ]

        consolidated_record["source_count"] = len(source_names)
        consolidated_record["source_names"] = source_names
        consolidated_record["source_record_ids"] = source_record_ids
        consolidated_record["source_evidence"] = source_evidence
        consolidated_record["threat_categories"] = threat_categories
        consolidated_record["record_count_before_deduplication"] = len(group)

        if confidence_scores:
            consolidated_record["confidence_score"] = max(confidence_scores)

        if first_seen_values:
            consolidated_record["first_seen"] = min(first_seen_values)

        if last_seen_values:
            consolidated_record["last_seen"] = max(last_seen_values)

        consolidated_records.append(consolidated_record)

    return consolidated_records