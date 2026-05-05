"""OpenAI adapter capability declarations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from whero.vatbrain.core.capabilities import AdapterCapability, ModelCapability

PROVIDER = "openai"


def get_adapter_capability() -> AdapterCapability:
    """Return capabilities implemented by this adapter, independent of model choice."""

    return AdapterCapability(
        provider=PROVIDER,
        supports_generation=True,
        supports_stream_generation=True,
        supports_async=True,
        supports_text_embedding=True,
        supports_multimodal_embedding=False,
        supports_function_tools=True,
        supports_usage_mapping=True,
    )


def get_model_capability(
    model: str,
    *,
    overrides: Mapping[str, Any] | None = None,
) -> ModelCapability:
    """Return best-known model capabilities, defaulting volatile model facts to unknown."""

    capability = ModelCapability(provider=PROVIDER, model=model)
    if overrides:
        capability = capability.with_overrides(**dict(overrides))
    return capability
