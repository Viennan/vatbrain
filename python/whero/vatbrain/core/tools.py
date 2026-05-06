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


class ToolExecutionOwner(StrEnum):
    """Who executes a declared tool."""

    USER = "user"


@dataclass(frozen=True, slots=True)
class FunctionToolSpec:
    """Function tool declaration."""

    name: str
    description: str | None = None
    parameters_schema: dict[str, Any] = field(default_factory=dict)
    strict: bool | None = None
    type: Literal["function"] = "function"
    execution_owner: Literal[ToolExecutionOwner.USER] = ToolExecutionOwner.USER
    provider_options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("FunctionToolSpec.name is required.")


ToolSpec = FunctionToolSpec
