from __future__ import annotations

from types import SimpleNamespace

from whero.vatbrain import ClientConfig, MessageItem, ReasoningConfig, ToolCallConfig
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
        items=[MessageItem.user("hello")],
        reasoning=ReasoningConfig(effort="low"),
        tool_call_config=ToolCallConfig(parallel_tool_calls=True),
    )

    assert response.id == "resp_1"
    assert fake.responses.calls[0]["model"] == "gpt-test"
    assert fake.responses.calls[0]["reasoning"] == {"effort": "low"}
    assert fake.responses.calls[0]["parallel_tool_calls"] is True


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
