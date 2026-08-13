"""Controlled retry helpers for recoverable pipeline failures."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import sleep
from typing import TypeVar


ResultType = TypeVar("ResultType")


class RetryExhaustedError(RuntimeError):
    """Raised when every permitted retry attempt has failed."""


@dataclass
class RetryResult:
    """Result details for a successful retried action."""

    value: object
    attempts: int
    failure_messages: list[str]


def run_with_retry(
    action: Callable[[], ResultType],
    *,
    max_attempts: int = 3,
    delay_seconds: float = 0.0,
) -> RetryResult:
    """Run an action again for transient operating-system failures.

    ValueError and other data-quality errors are not retried because retrying
    invalid input would not fix it.
    """

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1.")

    failure_messages: list[str] = []

    for attempt in range(1, max_attempts + 1):
        try:
            value = action()

            return RetryResult(
                value=value,
                attempts=attempt,
                failure_messages=failure_messages,
            )
        except (ConnectionError, OSError, TimeoutError) as error:
            failure_messages.append(
                f"Attempt {attempt}: {type(error).__name__}: {error}"
            )

            if attempt == max_attempts:
                raise RetryExhaustedError(
                    f"Recovery failed after {max_attempts} attempt(s)."
                ) from error

            if delay_seconds > 0:
                sleep(delay_seconds)