"""Tool declaration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal


class ToolChoice(StrEnum):
    """Common tool choice values."""

    AUTO = "auto"
    NONE = "none"
    REQUIRED = "required"


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """Function tool declaration."""

    name: str
    description: str | None = None
    parameters_schema: dict[str, Any] = field(default_factory=dict)
    strict: bool | None = None
    type: Literal["function"] = "function"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("ToolSpec.name is required.")
