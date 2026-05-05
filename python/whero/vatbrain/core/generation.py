"""Generation request, response, and event models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable

from whero.vatbrain.core.items import Item
from whero.vatbrain.core.tools import ToolChoice, ToolSpec
from whero.vatbrain.core.usage import Usage


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    """Common generation controls."""

    temperature: float | None = None
    top_p: float | None = None
    max_output_tokens: int | None = None
    stop: str | list[str] | None = None


@dataclass(frozen=True, slots=True)
class ResponseFormat:
    """Common response format request."""

    type: str
    json_schema: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ReasoningConfig:
    """Common reasoning behavior controls."""

    effort: str | None = None
    budget_tokens: int | None = None
    summary: str | None = None
    include_trace: bool | None = None


@dataclass(frozen=True, slots=True)
class ToolCallConfig:
    """Common tool-call behavior controls."""

    parallel_tool_calls: bool | None = None
    tool_choice: ToolChoice | str | dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class StreamOptions:
    """Common streaming options."""

    include_usage: bool | None = None


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """A full-context generation request."""

    model: str
    items: tuple[Item, ...]
    tools: tuple[ToolSpec, ...] = ()
    generation_config: GenerationConfig | None = None
    response_format: ResponseFormat | None = None
    reasoning: ReasoningConfig | None = None
    tool_call_config: ToolCallConfig | None = None
    stream_options: StreamOptions | None = None
    provider_options: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        model: str,
        items: Iterable[Item],
        *,
        tools: Iterable[ToolSpec] = (),
        generation_config: GenerationConfig | None = None,
        response_format: ResponseFormat | None = None,
        reasoning: ReasoningConfig | None = None,
        tool_call_config: ToolCallConfig | None = None,
        stream_options: StreamOptions | None = None,
        provider_options: dict[str, Any] | None = None,
    ) -> None:
        if not model:
            raise ValueError("GenerationRequest.model is required.")
        normalized_items = tuple(items)
        if not normalized_items:
            raise ValueError("GenerationRequest.items must not be empty.")
        object.__setattr__(self, "model", model)
        object.__setattr__(self, "items", normalized_items)
        object.__setattr__(self, "tools", tuple(tools))
        object.__setattr__(self, "generation_config", generation_config)
        object.__setattr__(self, "response_format", response_format)
        object.__setattr__(self, "reasoning", reasoning)
        object.__setattr__(self, "tool_call_config", tool_call_config)
        object.__setattr__(self, "stream_options", stream_options)
        object.__setattr__(self, "provider_options", dict(provider_options or {}))


@dataclass(frozen=True, slots=True)
class GenerationResponse:
    """Normalized generation response."""

    id: str | None
    provider: str
    model: str | None
    output_items: tuple[Item, ...] = ()
    stop_reason: str | None = None
    usage: Usage | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: Any | None = None


class StreamEventType(StrEnum):
    """Known normalized stream event types."""

    RESPONSE_CREATED = "response.created"
    RESPONSE_STARTED = "response.started"
    ITEM_CREATED = "item.created"
    ITEM_DELTA = "item.delta"
    ITEM_COMPLETED = "item.completed"
    TOOL_CALL_CREATED = "tool_call.created"
    TOOL_CALL_DELTA = "tool_call.delta"
    TOOL_CALL_COMPLETED = "tool_call.completed"
    USAGE_UPDATED = "usage.updated"
    RESPONSE_COMPLETED = "response.completed"
    RESPONSE_FAILED = "response.failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class GenerationStreamEvent:
    """Normalized generation streaming event."""

    type: str
    sequence: int
    provider: str
    response_id: str | None = None
    item_id: str | None = None
    delta: Any | None = None
    item: Item | None = None
    usage: Usage | None = None
    response: GenerationResponse | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw_event: Any | None = None
