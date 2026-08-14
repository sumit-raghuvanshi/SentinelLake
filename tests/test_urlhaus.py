"""Tests for URLhaus download helpers."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.sentinellake.urlhaus import (
    build_recent_csv_url,
    download_recent_csv,
    load_local_environment,
)


class FakeResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self.content


class URLhausDownloadTests(unittest.TestCase):
    def test_local_environment_settings_are_loaded(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            env_path = Path(temporary_directory) / ".env"
            env_path.write_text(
                "# Local secrets\n"
                "URLHAUS_AUTH_KEY=example-key\n",
                encoding="utf-8",
            )

            settings = load_local_environment(env_path)

            self.assertEqual(
                settings["URLHAUS_AUTH_KEY"],
                "example-key",
            )

    def test_recent_csv_url_uses_the_auth_key(self) -> None:
        url = build_recent_csv_url("example-key")

        self.assertEqual(
            url,
            "https://urlhaus-api.abuse.ch/v2/files/exports/"
            "example-key/recent.csv",
        )

    def test_empty_auth_key_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_recent_csv_url("   ")

    def test_downloaded_csv_is_saved_with_ssl_context(self) -> None:
        received_requests = []

        def fake_urlopen(request, timeout, context):
            received_requests.append((request, timeout, context))
            return FakeResponse(b"id,url\n1,https://example.test/\n")

        with TemporaryDirectory() as temporary_directory:
            destination_path = (
                Path(temporary_directory) / "urlhaus_recent.csv"
            )

            saved_path = download_recent_csv(
                "example-key",
                destination_path,
                urlopen_function=fake_urlopen,
            )

            self.assertEqual(saved_path, destination_path)
            self.assertEqual(
                destination_path.read_text(encoding="utf-8"),
                "id,url\n1,https://example.test/\n",
            )
            self.assertEqual(len(received_requests), 1)
            self.assertIsNotNone(received_requests[0][2])


if __name__ == "__main__":
    unittest.main()