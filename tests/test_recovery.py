"""Tests for controlled retry and recovery."""

import unittest

from src.sentinellake.recovery import (
    RetryExhaustedError,
    run_with_retry,
)


class RetryRecoveryTests(unittest.TestCase):
    def test_transient_failure_is_recovered(self) -> None:
        call_count = 0

        def temporary_failure() -> str:
            nonlocal call_count
            call_count += 1

            if call_count < 3:
                raise ConnectionError("Temporary feed connection problem.")

            return "pipeline completed"

        result = run_with_retry(temporary_failure, max_attempts=3)

        self.assertEqual(result.value, "pipeline completed")
        self.assertEqual(result.attempts, 3)
        self.assertEqual(len(result.failure_messages), 2)

    def test_retry_exhaustion_raises_an_error(self) -> None:
        def permanent_transient_error() -> None:
            raise TimeoutError("Source did not respond.")

        with self.assertRaises(RetryExhaustedError):
            run_with_retry(permanent_transient_error, max_attempts=2)

    def test_invalid_configuration_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_with_retry(lambda: "unused", max_attempts=0)


if __name__ == "__main__":
    unittest.main()