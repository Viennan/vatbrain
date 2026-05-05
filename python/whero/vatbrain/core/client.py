"""Common provider client configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ClientConfig:
    """Common provider client initialization options."""

    api_key: str | None = None
    base_url: str | None = None
    timeout: float | None = None
    max_retries: int | None = None
    provider_options: dict[str, Any] | None = None
