"""OpenAI streaming event mapping."""

from __future__ import annotations

from typing import Any

from whero.vatbrain.core.generation import (
    GenerationResponse,
    GenerationStreamEvent,
    StreamEventType,
)
from whero.vatbrain.core.items import FunctionCallItem
from whero.vatbrain.providers.openai.mapper import PROVIDER, from_openai_generation_response, usage_from_openai


def from_openai_stream_event(event: Any, *, sequence: int) -> GenerationStreamEvent:
    """Convert one OpenAI stream event to a vatbrain stream event."""

    event_type = _get_attr(event, "type", None)
    response_id = _response_id_from_event(event)
    item_id = _get_attr(event, "item_id", None)

    if event_type == "response.created":
        response = _get_attr(event, "response", None)
        return GenerationStreamEvent(
            type=StreamEventType.RESPONSE_CREATED.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=_get_attr(response, "id", response_id),
            response=_safe_response(response),
            raw_event=event,
        )
    if event_type in {"response.in_progress", "response.started"}:
        return GenerationStreamEvent(
            type=StreamEventType.RESPONSE_STARTED.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=response_id,
            raw_event=event,
        )
    if event_type == "response.output_item.added":
        item = _get_attr(event, "item", None)
        normalized_item = None
        if _get_attr(item, "type", None) == "function_call":
            normalized_item = FunctionCallItem(
                id=_get_attr(item, "id", None),
                name=_get_attr(item, "name", ""),
                arguments=_get_attr(item, "arguments", ""),
                call_id=_get_attr(item, "call_id", ""),
                status=_get_attr(item, "status", None),
            )
        return GenerationStreamEvent(
            type=StreamEventType.ITEM_CREATED.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=response_id,
            item_id=_get_attr(item, "id", item_id),
            item=normalized_item,
            raw_event=event,
        )
    if event_type == "response.output_item.done":
        return GenerationStreamEvent(
            type=StreamEventType.ITEM_COMPLETED.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=response_id,
            item_id=_get_attr(_get_attr(event, "item", None), "id", item_id),
            raw_event=event,
        )
    if event_type in {"response.output_text.delta", "response.text.delta"}:
        return GenerationStreamEvent(
            type=StreamEventType.ITEM_DELTA.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=response_id,
            item_id=item_id,
            delta=_get_attr(event, "delta", ""),
            raw_event=event,
        )
    if event_type in {"response.function_call_arguments.delta", "response.tool_call.delta"}:
        return GenerationStreamEvent(
            type=StreamEventType.TOOL_CALL_DELTA.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=response_id,
            item_id=item_id,
            delta=_get_attr(event, "delta", ""),
            raw_event=event,
        )
    if event_type in {"response.function_call_arguments.done", "response.tool_call.done"}:
        return GenerationStreamEvent(
            type=StreamEventType.TOOL_CALL_COMPLETED.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=response_id,
            item_id=item_id,
            delta=_get_attr(event, "arguments", None),
            raw_event=event,
        )
    if event_type == "response.usage.updated":
        return GenerationStreamEvent(
            type=StreamEventType.USAGE_UPDATED.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=response_id,
            usage=usage_from_openai(_get_attr(event, "usage", None)),
            raw_event=event,
        )
    if event_type == "response.completed":
        response = _get_attr(event, "response", None)
        return GenerationStreamEvent(
            type=StreamEventType.RESPONSE_COMPLETED.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=_get_attr(response, "id", response_id),
            response=_safe_response(response),
            usage=usage_from_openai(_get_attr(response, "usage", None)),
            raw_event=event,
        )
    if event_type in {"response.failed", "error"}:
        error = _get_attr(event, "error", None)
        return GenerationStreamEvent(
            type=StreamEventType.RESPONSE_FAILED.value,
            sequence=sequence,
            provider=PROVIDER,
            response_id=response_id,
            error=str(error) if error is not None else None,
            raw_event=event,
        )
    return GenerationStreamEvent(
        type=StreamEventType.UNKNOWN.value,
        sequence=sequence,
        provider=PROVIDER,
        response_id=response_id,
        item_id=item_id,
        metadata={"provider_event_type": event_type},
        raw_event=event,
    )


def _safe_response(response: Any | None) -> GenerationResponse | None:
    if response is None:
        return None
    try:
        return from_openai_generation_response(response)
    except Exception:
        return GenerationResponse(
            id=_get_attr(response, "id", None),
            provider=PROVIDER,
            model=_get_attr(response, "model", None),
            raw=response,
        )


def _response_id_from_event(event: Any) -> str | None:
    response = _get_attr(event, "response", None)
    return _get_attr(response, "id", _get_attr(event, "response_id", None))


def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)
