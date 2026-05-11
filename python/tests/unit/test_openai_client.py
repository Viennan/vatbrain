from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from whero.vatbrain import (
    ClientConfig,
    MessageItem,
    ReasoningConfig,
    RemoteContextHint,
    RemoteContextInvalidBehavior,
    ReplayPolicy,
    ToolCallConfig,
)
from whero.vatbrain.core.errors import ProviderRequestError
from whero.vatbrain.core.generation import StreamEventType
from whero.vatbrain.providers.openai import OpenAIClient


class FakeResponses:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self.result


class RaisingResponses:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def create(self, **kwargs: object) -> object:
        raise self.exc


class FallbackResponses:
    def __init__(self, *, first_exc: Exception, result: object) -> None:
        self.first_exc = first_exc
        self.result = result
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            raise self.first_exc
        return self.result


class AsyncFallbackResponses:
    def __init__(self, *, first_exc: Exception, result: object) -> None:
        self.first_exc = first_exc
        self.result = result
        self.calls: list[dict[str, object]] = []

    async def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            raise self.first_exc
        return self.result


class AsyncFakeResponses:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    async def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self.result


class FakeEmbeddings:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self.result


class FakeOpenAI:
    def __init__(self, *, response: object, embedding: object | None = None) -> None:
        self.responses = FakeResponses(response)
        self.embeddings = FakeEmbeddings(embedding or SimpleNamespace(data=[], usage=None))


class FakeOpenAIRaising:
    def __init__(self, exc: Exception) -> None:
        self.responses = RaisingResponses(exc)
        self.embeddings = FakeEmbeddings(SimpleNamespace(data=[], usage=None))


class FakeOpenAIFallback:
    def __init__(self, *, first_exc: Exception, response: object) -> None:
        self.responses = FallbackResponses(first_exc=first_exc, result=response)
        self.embeddings = FakeEmbeddings(SimpleNamespace(data=[], usage=None))


class FakeAsyncOpenAIFallback:
    def __init__(self, *, first_exc: Exception, response: object) -> None:
        self.responses = AsyncFallbackResponses(first_exc=first_exc, result=response)


class FakeAsyncOpenAI:
    def __init__(self, *, response: object) -> None:
        self.responses = AsyncFakeResponses(response)


class FakeOpenAIError(Exception):
    status_code = 400
    request_id = "req_1"
    body = {
        "error": {
            "type": "invalid_request_error",
            "code": "bad_param",
            "param": "stream_options",
        }
    }


class FakePreviousResponseExpiredError(Exception):
    status_code = 400
    request_id = "req_expired"
    body = {
        "error": {
            "type": "invalid_request_error",
            "code": "previous_response_expired",
            "param": "previous_response_id",
            "message": "The previous response has expired.",
        }
    }


class Contact(BaseModel):
    name: str
    email: str


def test_client_generate_uses_explicit_model_and_common_options() -> None:
    raw_response = SimpleNamespace(
        id="resp_1",
        model="gpt-test",
        status="completed",
        output=[],
        usage=None,
    )
    fake = FakeOpenAI(response=raw_response)
    client = OpenAIClient(client=fake, async_client=object())

    response = client.generate(
        model="gpt-test",
        items=[MessageItem.system("covered"), MessageItem.user("hello")],
        reasoning=ReasoningConfig(effort="low"),
        tool_call_config=ToolCallConfig(parallel_tool_calls=True),
        remote_context=RemoteContextHint(previous_response_id="resp_old", covered_item_count=1),
    )

    assert response.id == "resp_1"
    assert fake.responses.calls[0]["model"] == "gpt-test"
    assert fake.responses.calls[0]["reasoning"] == {"effort": "low"}
    assert fake.responses.calls[0]["parallel_tool_calls"] is True
    assert fake.responses.calls[0]["previous_response_id"] == "resp_old"
    assert len(fake.responses.calls[0]["input"]) == 1
    assert fake.responses.calls[0]["input"][0]["role"] == "user"


def test_client_generate_replays_without_remote_context_when_enabled() -> None:
    raw_response = SimpleNamespace(
        id="resp_2",
        model="gpt-test",
        status="completed",
        output=[],
        usage=None,
    )
    fake = FakeOpenAIFallback(first_exc=FakePreviousResponseExpiredError("expired"), response=raw_response)
    client = OpenAIClient(client=fake, async_client=object())

    response = client.generate(
        model="gpt-test",
        items=[MessageItem.system("covered"), MessageItem.user("hello")],
        remote_context=RemoteContextHint(
            previous_response_id="resp_old",
            covered_item_count=1,
            store=True,
        ),
        replay_policy=ReplayPolicy(
            on_remote_context_invalid=RemoteContextInvalidBehavior.REPLAY_WITHOUT_REMOTE_CONTEXT,
        ),
    )

    assert response.id == "resp_2"
    assert len(fake.responses.calls) == 2
    assert fake.responses.calls[0]["previous_response_id"] == "resp_old"
    assert len(fake.responses.calls[0]["input"]) == 1
    assert fake.responses.calls[0]["input"][0]["role"] == "user"
    assert "previous_response_id" not in fake.responses.calls[1]
    assert fake.responses.calls[1]["store"] is True
    assert len(fake.responses.calls[1]["input"]) == 2
    assert fake.responses.calls[1]["input"][0]["role"] == "system"
    assert fake.responses.calls[1]["input"][1]["role"] == "user"


def test_client_generate_does_not_replay_remote_context_by_default() -> None:
    exc = FakePreviousResponseExpiredError("expired")
    client = OpenAIClient(client=FakeOpenAIRaising(exc), async_client=object())

    try:
        client.generate(
            model="gpt-test",
            items=[MessageItem.system("covered"), MessageItem.user("hello")],
            remote_context=RemoteContextHint(previous_response_id="resp_old", covered_item_count=1),
        )
    except ProviderRequestError as wrapped:
        assert wrapped.cause is exc
        assert wrapped.details.error_param == "previous_response_id"
    else:
        raise AssertionError("Expected ProviderRequestError")


def test_client_generate_parsed_builds_response_format_and_parses_output() -> None:
    raw_response = SimpleNamespace(
        id="resp_1",
        model="gpt-test",
        status="completed",
        output=[
            SimpleNamespace(
                type="message",
                id="msg_1",
                role="assistant",
                content=[
                    SimpleNamespace(
                        type="output_text",
                        text='{"name":"Ada","email":"ada@example.test"}',
                    )
                ],
            )
        ],
        usage=None,
    )
    fake = FakeOpenAI(response=raw_response)
    client = OpenAIClient(client=fake, async_client=object())

    parsed = client.generate_parsed(
        model="gpt-test",
        items=[MessageItem.user("extract")],
        output_type=Contact,
    )

    assert fake.responses.calls[0]["text"]["format"]["type"] == "json_schema"
    assert fake.responses.calls[0]["text"]["format"]["strict"] is True
    assert fake.responses.calls[0]["text"]["format"]["name"] == "Contact"
    assert parsed.response.id == "resp_1"
    assert parsed.output_parsed == Contact(name="Ada", email="ada@example.test")


@pytest.mark.anyio
async def test_async_client_generate_replays_without_remote_context_when_enabled() -> None:
    raw_response = SimpleNamespace(
        id="resp_async",
        model="gpt-test",
        status="completed",
        output=[],
        usage=None,
    )
    fake_async = FakeAsyncOpenAIFallback(
        first_exc=FakePreviousResponseExpiredError("expired"),
        response=raw_response,
    )
    client = OpenAIClient(client=object(), async_client=fake_async)

    response = await client.agenerate(
        model="gpt-test",
        items=[MessageItem.system("covered"), MessageItem.user("hello")],
        remote_context=RemoteContextHint(previous_response_id="resp_old", covered_item_count=1),
        replay_policy=ReplayPolicy(
            on_remote_context_invalid=RemoteContextInvalidBehavior.REPLAY_WITHOUT_REMOTE_CONTEXT,
        ),
    )

    assert response.id == "resp_async"
    assert len(fake_async.responses.calls) == 2
    assert fake_async.responses.calls[0]["previous_response_id"] == "resp_old"
    assert len(fake_async.responses.calls[0]["input"]) == 1
    assert "previous_response_id" not in fake_async.responses.calls[1]
    assert len(fake_async.responses.calls[1]["input"]) == 2


@pytest.mark.anyio
async def test_async_client_generate_parsed_builds_response_format_and_parses_output() -> None:
    raw_response = SimpleNamespace(
        id="resp_async_parsed",
        model="gpt-test",
        status="completed",
        output=[
            SimpleNamespace(
                type="message",
                id="msg_1",
                role="assistant",
                content=[
                    SimpleNamespace(
                        type="output_text",
                        text='{"name":"Ada","email":"ada@example.test"}',
                    )
                ],
            )
        ],
        usage=None,
    )
    fake_async = FakeAsyncOpenAI(response=raw_response)
    client = OpenAIClient(client=object(), async_client=fake_async)

    parsed = await client.agenerate_parsed(
        model="gpt-test",
        items=[MessageItem.user("extract")],
        output_type=Contact,
    )

    assert fake_async.responses.calls[0]["text"]["format"]["name"] == "Contact"
    assert parsed.response.id == "resp_async_parsed"
    assert parsed.output_parsed.email == "ada@example.test"


def test_client_stream_generate_maps_events() -> None:
    stream = [
        SimpleNamespace(
            type="response.output_text.delta",
            response_id="resp_1",
            item_id="msg_1",
            delta="hi",
        )
    ]
    fake = FakeOpenAI(response=stream)
    client = OpenAIClient(client=fake, async_client=object())

    events = list(client.stream_generate(model="gpt-test", items=[MessageItem.user("hello")]))

    assert fake.responses.calls[0]["stream"] is True
    assert events[0].delta == "hi"
    assert events[0].type == StreamEventType.TEXT_DELTA.value


def test_client_stream_generate_replays_without_remote_context_when_enabled() -> None:
    stream = [
        SimpleNamespace(
            type="response.output_text.delta",
            response_id="resp_2",
            item_id="msg_1",
            delta="hi",
        )
    ]
    fake = FakeOpenAIFallback(first_exc=FakePreviousResponseExpiredError("expired"), response=stream)
    client = OpenAIClient(client=fake, async_client=object())

    events = list(
        client.stream_generate(
            model="gpt-test",
            items=[MessageItem.system("covered"), MessageItem.user("hello")],
            remote_context=RemoteContextHint(previous_response_id="resp_old", covered_item_count=1),
            replay_policy=ReplayPolicy(
                on_remote_context_invalid=RemoteContextInvalidBehavior.REPLAY_WITHOUT_REMOTE_CONTEXT,
            ),
        )
    )

    assert len(fake.responses.calls) == 2
    assert fake.responses.calls[0]["previous_response_id"] == "resp_old"
    assert len(fake.responses.calls[0]["input"]) == 1
    assert "previous_response_id" not in fake.responses.calls[1]
    assert len(fake.responses.calls[1]["input"]) == 2
    assert events[0].delta == "hi"


def test_client_embed_uses_embedding_endpoint() -> None:
    raw_embedding = SimpleNamespace(
        model="text-embedding-test",
        data=[SimpleNamespace(index=0, embedding=[1.0, 2.0])],
        usage=None,
    )
    fake = FakeOpenAI(response=SimpleNamespace(output=[]), embedding=raw_embedding)
    client = OpenAIClient(client=fake, async_client=object())

    response = client.embed(model="text-embedding-test", inputs=["hello"])

    assert fake.embeddings.calls[0]["model"] == "text-embedding-test"
    assert fake.embeddings.calls[0]["input"] == ["hello"]
    assert response.vectors[0].embedding == [1.0, 2.0]


def test_client_common_init_options_are_collected() -> None:
    client = OpenAIClient(
        config=ClientConfig(
            api_key="from-config",
            base_url="https://example.test/v1",
            timeout=30.0,
            max_retries=1,
            provider_options={"default_headers": {"x-config": "yes"}},
        ),
        api_key="explicit",
        timeout=10.0,
        organization="org_1",
    )

    assert client._client_options == {
        "api_key": "explicit",
        "base_url": "https://example.test/v1",
        "timeout": 10.0,
        "max_retries": 1,
        "default_headers": {"x-config": "yes"},
        "organization": "org_1",
    }


def test_client_reads_provider_scoped_vatbrain_env_api_key(monkeypatch) -> None:
    monkeypatch.setenv("ENV_VATBRAIN_OPENAI_API_KEY", "env-key")

    client = OpenAIClient()

    assert client._client_options["api_key"] == "env-key"


def test_client_request_error_is_wrapped_with_provider_details() -> None:
    exc = FakeOpenAIError("bad request")
    client = OpenAIClient(client=FakeOpenAIRaising(exc), async_client=object())

    try:
        client.generate(model="gpt-test", items=[MessageItem.user("hello")])
    except ProviderRequestError as wrapped:
        assert wrapped.cause is exc
        assert wrapped.details.provider == "openai"
        assert wrapped.details.operation == "responses.create"
        assert wrapped.details.status_code == 400
        assert wrapped.details.request_id == "req_1"
        assert wrapped.details.error_type == "invalid_request_error"
        assert wrapped.details.error_code == "bad_param"
        assert wrapped.details.error_param == "stream_options"
    else:
        raise AssertionError("Expected ProviderRequestError")
