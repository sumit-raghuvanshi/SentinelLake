"""Tests for SentinelLake incident storage."""

import unittest

from src.sentinellake.incidents import save_incidents


class FakeCursor:
    def __init__(self) -> None:
        self.saved_rows = []

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def executemany(self, query: str, rows: list[tuple]) -> None:
        self.saved_rows.extend(rows)


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()
        self.commit_count = 0

    def cursor(self) -> FakeCursor:
        return self.cursor_instance

    def commit(self) -> None:
        self.commit_count += 1


class IncidentStorageTests(unittest.TestCase):
    def test_no_database_write_for_a_healthy_result(self) -> None:
        connection = FakeConnection()

        saved_count = save_incidents(
            connection,
            {
                "records_ingested": 9,
                "quarantine_rate": 22.22,
                "incidents": [],
            },
        )

        self.assertEqual(saved_count, 0)
        self.assertEqual(connection.cursor_instance.saved_rows, [])
        self.assertEqual(connection.commit_count, 0)

    def test_detected_incidents_are_saved(self) -> None:
        connection = FakeConnection()

        saved_count = save_incidents(
            connection,
            {
                "records_ingested": 3,
                "quarantine_rate": 40.0,
                "incidents": [
                    {
                        "incident_type": "volume_anomaly",
                        "severity": "high",
                        "message": "Too few records were received.",
                    },
                    {
                        "incident_type": "high_quarantine_rate",
                        "severity": "medium",
                        "message": "Too many records were quarantined.",
                    },
                ],
            },
        )

        self.assertEqual(saved_count, 2)
        self.assertEqual(len(connection.cursor_instance.saved_rows), 2)
        self.assertEqual(connection.commit_count, 1)


if __name__ == "__main__":
    unittest.main()