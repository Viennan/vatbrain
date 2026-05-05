from __future__ import annotations

from types import SimpleNamespace

from whero.vatbrain.core.generation import StreamEventType
from whero.vatbrain.providers.openai.stream import from_openai_stream_event


def test_stream_text_delta_maps_to_item_delta() -> None:
    event = SimpleNamespace(
        type="response.output_text.delta",
        response_id="resp_1",
        item_id="msg_1",
        delta="hello",
    )

    mapped = from_openai_stream_event(event, sequence=3)

    assert mapped.type == StreamEventType.ITEM_DELTA.value
    assert mapped.sequence == 3
    assert mapped.response_id == "resp_1"
    assert mapped.item_id == "msg_1"
    assert mapped.delta == "hello"


def test_stream_function_arguments_delta_maps_to_tool_delta() -> None:
    event = {
        "type": "response.function_call_arguments.delta",
        "response_id": "resp_1",
        "item_id": "fc_1",
        "delta": '{"q"',
    }

    mapped = from_openai_stream_event(event, sequence=4)

    assert mapped.type == StreamEventType.TOOL_CALL_DELTA.value
    assert mapped.delta == '{"q"'


def test_stream_completed_event_maps_response_and_usage() -> None:
    response = SimpleNamespace(
        id="resp_1",
        model="gpt-test",
        status="completed",
        output=[],
        usage=SimpleNamespace(input_tokens=1, output_tokens=2, total_tokens=3),
    )
    event = SimpleNamespace(type="response.completed", response=response)

    mapped = from_openai_stream_event(event, sequence=5)

    assert mapped.type == StreamEventType.RESPONSE_COMPLETED.value
    assert mapped.response_id == "resp_1"
    assert mapped.response is not None
    assert mapped.usage is not None
    assert mapped.usage.total_tokens == 3
