"""Tests for SentinelLake database configuration."""

import os
import unittest
from unittest.mock import patch

from src.sentinellake.database import (
    DEFAULT_DATABASE_URL,
    get_database_url,
)


class DatabaseConfigurationTests(unittest.TestCase):
    def test_default_database_url_is_used_when_not_configured(self) -> None:
        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            self.assertEqual(
                get_database_url(),
                DEFAULT_DATABASE_URL,
            )

    def test_environment_database_url_overrides_default(self) -> None:
        custom_url = "postgresql://example-user@localhost:5432/example-db"

        with patch.dict(
            os.environ,
            {"SENTINELLAKE_DATABASE_URL": custom_url},
            clear=True,
        ):
            self.assertEqual(get_database_url(), custom_url)


if __name__ == "__main__":
    unittest.main()