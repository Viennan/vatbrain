from __future__ import annotations

from types import SimpleNamespace

from whero.vatbrain import (
    FunctionResultItem,
    GenerationConfig,
    GenerationRequest,
    MessageItem,
    ReasoningConfig,
    TextPart,
    ToolCallConfig,
    ToolChoice,
    ToolSpec,
)
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
        reasoning=ReasoningConfig(effort="medium", budget_tokens=1024, summary="auto"),
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
        "effort": "medium",
        "budget_tokens": 1024,
        "summary": "auto",
    }
    assert params["parallel_tool_calls"] is False
    assert params["tool_choice"] == "auto"
    assert params["metadata"] == {"trace_id": "t-1"}


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
