from __future__ import annotations

from types import SimpleNamespace

import pytest

from whero.vatbrain import (
    FunctionResultItem,
    GenerationConfig,
    GenerationRequest,
    MessageItem,
    ReasoningConfig,
    RemoteContextHint,
    ResponseFormat,
    StreamOptions,
    TextPart,
    ToolCallConfig,
    ToolChoice,
    ToolSpec,
    VideoPart,
)
from whero.vatbrain.core.errors import InvalidItemError, ProviderResponseMappingError
from whero.vatbrain.core.items import FunctionCallItem
from whero.vatbrain.providers.openai.mapper import (
    from_openai_generation_response,
    to_openai_generation_params,
)


def test_generation_request_maps_common_reasoning_and_tool_config() -> None:
    request = GenerationRequest(
        model="gpt-test",
        items=[
            MessageItem.system("be terse"),
            MessageItem.user([TextPart("hello")]),
            FunctionResultItem(call_id="call_1", output='{"ok":true}'),
        ],
        tools=[
            ToolSpec(
                name="lookup",
                description="Lookup data",
                parameters_schema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
                strict=True,
            )
        ],
        generation_config=GenerationConfig(temperature=0.2, max_output_tokens=128),
        reasoning=ReasoningConfig(mode="auto", effort="medium", budget_tokens=1024, summary="auto"),
        tool_call_config=ToolCallConfig(
            parallel_tool_calls=False,
            tool_choice=ToolChoice.AUTO,
        ),
        provider_options={"metadata": {"trace_id": "t-1"}},
    )

    params = to_openai_generation_params(request)

    assert params["model"] == "gpt-test"
    assert params["input"][0]["type"] == "message"
    assert params["input"][0]["role"] == "system"
    assert params["input"][1]["content"] == [{"type": "input_text", "text": "hello"}]
    assert params["input"][2] == {
        "type": "function_call_output",
        "call_id": "call_1",
        "output": '{"ok":true}',
    }
    assert params["tools"] == [
        {
            "type": "function",
            "name": "lookup",
            "description": "Lookup data",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            "strict": True,
        }
    ]
    assert params["temperature"] == 0.2
    assert params["max_output_tokens"] == 128
    assert params["reasoning"] == {
        "mode": "auto",
        "effort": "medium",
        "budget_tokens": 1024,
        "summary": "auto",
    }
    assert params["parallel_tool_calls"] is False
    assert params["tool_choice"] == "auto"
    assert params["metadata"] == {"trace_id": "t-1"}


def test_generation_request_maps_remote_context_hint() -> None:
    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user("hello")],
        remote_context=RemoteContextHint(
            previous_response_id="resp_1",
            store=True,
            cache_policy="24h",
            provider_options={"prompt_cache_key": "cache-key"},
        ),
    )

    params = to_openai_generation_params(request)

    assert params["previous_response_id"] == "resp_1"
    assert params["store"] is True
    assert params["prompt_cache_retention"] == "24h"
    assert params["prompt_cache_key"] == "cache-key"


def test_openai_generation_mapper_rejects_unsupported_new_parts() -> None:
    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user([VideoPart(url="https://example.test/a.mp4")])],
    )

    with pytest.raises(InvalidItemError):
        to_openai_generation_params(request)



def test_stream_options_include_usage_is_not_mapped_to_openai_stream_options() -> None:
    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user("hello")],
        stream_options=StreamOptions(include_usage=True),
    )

    params = to_openai_generation_params(request, stream=True)

    assert params["stream"] is True
    assert "stream_options" not in params


def test_provider_specific_stream_options_are_passthrough() -> None:
    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user("hello")],
        provider_options={"stream_options": {"include_obfuscation": True}},
    )

    params = to_openai_generation_params(request, stream=True)

    assert params["stream_options"] == {"include_obfuscation": True}


def test_provider_options_override_default_params() -> None:
    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user("hello")],
        generation_config=GenerationConfig(temperature=0.2),
        provider_options={"temperature": 0.7},
    )

    params = to_openai_generation_params(request)

    assert params["temperature"] == 0.7


def test_json_object_response_format_maps_to_text_format() -> None:
    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user("json please")],
        response_format=ResponseFormat(type="json_object"),
    )

    params = to_openai_generation_params(request)

    assert params["text"] == {"format": {"type": "json_object"}}


def test_json_schema_response_format_maps_to_openai_text_format() -> None:
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
        "additionalProperties": False,
    }
    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user("extract")],
        response_format=ResponseFormat(
            type="json_schema",
            json_schema=schema,
            json_schema_name="person",
            json_schema_description="A person record.",
            json_schema_strict=True,
        ),
    )

    params = to_openai_generation_params(request)

    assert params["text"] == {
        "format": {
            "type": "json_schema",
            "name": "person",
            "description": "A person record.",
            "schema": schema,
            "strict": True,
        }
    }


def test_legacy_openai_json_schema_wrapper_is_preserved() -> None:
    wrapper = {
        "type": "json_schema",
        "name": "wrapped",
        "schema": {"type": "object", "properties": {}},
        "strict": False,
    }
    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user("extract")],
        response_format=ResponseFormat(type="json_schema", json_schema=wrapper),
    )

    params = to_openai_generation_params(request)

    assert params["text"] == {"format": wrapper}


def test_openai_response_maps_message_function_call_and_usage() -> None:
    response = SimpleNamespace(
        id="resp_1",
        model="gpt-test",
        status="completed",
        output=[
            SimpleNamespace(
                type="message",
                id="msg_1",
                role="assistant",
                content=[
                    SimpleNamespace(type="output_text", text="hello there"),
                ],
            ),
            SimpleNamespace(
                type="function_call",
                id="fc_1",
                name="lookup",
                arguments='{"query":"x"}',
                call_id="call_1",
                status="completed",
            ),
        ],
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            input_tokens_details=SimpleNamespace(cached_tokens=3),
            output_tokens_details=SimpleNamespace(reasoning_tokens=2),
        ),
    )

    mapped = from_openai_generation_response(response)

    assert mapped.id == "resp_1"
    assert mapped.model == "gpt-test"
    assert mapped.stop_reason == "completed"
    assert isinstance(mapped.output_items[0], MessageItem)
    assert mapped.output_items[0].role.value == "assistant"
    assert mapped.output_items[0].parts == (TextPart("hello there"),)
    assert isinstance(mapped.output_items[1], FunctionCallItem)
    assert mapped.output_items[1].name == "lookup"
    assert mapped.output_items[1].call_id == "call_1"
    assert mapped.usage is not None
    assert mapped.usage.input_tokens == 10
    assert mapped.usage.output_tokens == 5
    assert mapped.usage.cached_tokens == 3
    assert mapped.usage.reasoning_tokens == 2


def test_openai_response_records_unsupported_output_items_when_other_items_map() -> None:
    response = SimpleNamespace(
        id="resp_1",
        model="gpt-test",
        status="completed",
        output=[
            SimpleNamespace(
                type="message",
                id="msg_1",
                role="assistant",
                content=[SimpleNamespace(type="output_text", text="hello")],
            ),
            SimpleNamespace(type="reasoning", id="rs_1", status="completed"),
        ],
        usage=None,
    )

    mapped = from_openai_generation_response(response)

    assert len(mapped.output_items) == 1
    assert mapped.metadata["unsupported_output_items"] == [
        {"id": "rs_1", "type": "reasoning", "status": "completed"}
    ]


def test_openai_response_raises_when_only_unsupported_items_are_returned() -> None:
    response = SimpleNamespace(
        id="resp_1",
        model="gpt-test",
        status="completed",
        output=[SimpleNamespace(type="reasoning", id="rs_1", status="completed")],
        usage=None,
    )

    with pytest.raises(ProviderResponseMappingError) as exc_info:
        from_openai_generation_response(response)

    assert exc_info.value.details.provider == "openai"
    assert exc_info.value.details.operation == "responses.create"


def test_openai_response_raises_mapping_error_for_malformed_supported_item() -> None:
    response = SimpleNamespace(
        id="resp_1",
        model="gpt-test",
        status="completed",
        output=[SimpleNamespace(type="message", id="msg_1", role="not-a-role", content=[])],
        usage=None,
    )

    with pytest.raises(ProviderResponseMappingError) as exc_info:
        from_openai_generation_response(response)

    assert exc_info.value.details.provider == "openai"
    assert exc_info.value.details.raw is response
