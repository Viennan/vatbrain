from __future__ import annotations

import pytest

from whero.vatbrain import CapabilitySource
from whero.vatbrain.providers.openai import OpenAIClient


def test_openai_adapter_capability_is_provider_level() -> None:
    client = OpenAIClient(client=object(), async_client=object())

    capability = client.get_adapter_capability()

    assert capability.provider == "openai"
    assert capability.supports_generation is True
    assert capability.supports_stream_generation is True
    assert capability.supports_text_embedding is True
    assert capability.supports_multimodal_embedding is False


def test_model_capability_defaults_to_unknown_and_accepts_overrides() -> None:
    client = OpenAIClient(
        client=object(),
        async_client=object(),
        model_capability_overrides={
            "gpt-test": {"supports_streaming": True},
        },
    )

    capability = client.get_model_capability(
        "gpt-test",
        overrides={"max_context_tokens": 128000},
    )

    assert capability.max_context_tokens.value == 128000
    assert capability.max_context_tokens.source == CapabilitySource.USER_CONFIG
    assert capability.supports_streaming.value is True
    assert capability.output_dimensions.value is None
    assert capability.output_dimensions.source == CapabilitySource.UNKNOWN


def test_model_capability_overrides_cannot_replace_identity() -> None:
    client = OpenAIClient(client=object(), async_client=object())

    with pytest.raises(ValueError):
        client.get_model_capability("gpt-test", overrides={"model": "other"})
