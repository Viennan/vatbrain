from __future__ import annotations

from whero.vatbrain import GenerationRequest, MessageItem, ReasoningConfig, RemoteContextHint


def test_generation_request_accepts_remote_context_hint() -> None:
    remote_context = RemoteContextHint(
        previous_response_id="resp_1",
        cache_policy="24h",
        store=True,
        provider_options={"prompt_cache_key": "k"},
    )

    request = GenerationRequest(
        model="gpt-test",
        items=[MessageItem.user("hello")],
        remote_context=remote_context,
    )

    assert request.remote_context is remote_context
    assert request.remote_context.previous_response_id == "resp_1"


def test_reasoning_config_accepts_mode_and_provider_options() -> None:
    reasoning = ReasoningConfig(
        mode="auto",
        effort="low",
        provider_options={"summary": "auto"},
    )

    assert reasoning.mode == "auto"
    assert reasoning.provider_options == {"summary": "auto"}
