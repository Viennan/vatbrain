"""Embedding request and response models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from whero.vatbrain.core.items import ContentPart, MessageItem, TextPart
from whero.vatbrain.core.usage import Usage


@dataclass(frozen=True, slots=True)
class EmbeddingInput:
    """One embedding sample made of embedding-compatible content."""

    parts: tuple[ContentPart, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        parts: Iterable[ContentPart] | str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if isinstance(parts, str):
            normalized_parts: tuple[ContentPart, ...] = (TextPart(parts),)
        else:
            normalized_parts = tuple(parts)
        if not normalized_parts:
            raise ValueError("EmbeddingInput.parts must not be empty.")
        object.__setattr__(self, "parts", normalized_parts)
        object.__setattr__(self, "metadata", dict(metadata or {}))

    @classmethod
    def text(cls, text: str) -> EmbeddingInput:
        return cls(text)

    @classmethod
    def from_message(cls, item: MessageItem) -> EmbeddingInput:
        return cls(item.parts, metadata=item.metadata)


@dataclass(frozen=True, slots=True)
class EmbeddingRequest:
    """Embedding request."""

    model: str
    inputs: tuple[EmbeddingInput, ...]
    dimensions: int | None = None
    encoding_format: str | None = None
    provider_options: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        model: str,
        inputs: Iterable[EmbeddingInput | str],
        *,
        dimensions: int | None = None,
        encoding_format: str | None = None,
        provider_options: dict[str, Any] | None = None,
    ) -> None:
        if not model:
            raise ValueError("EmbeddingRequest.model is required.")
        normalized_inputs = tuple(
            EmbeddingInput.text(item) if isinstance(item, str) else item
            for item in inputs
        )
        if not normalized_inputs:
            raise ValueError("EmbeddingRequest.inputs must not be empty.")
        object.__setattr__(self, "model", model)
        object.__setattr__(self, "inputs", normalized_inputs)
        object.__setattr__(self, "dimensions", dimensions)
        object.__setattr__(self, "encoding_format", encoding_format)
        object.__setattr__(self, "provider_options", dict(provider_options or {}))


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    """One embedding vector result."""

    index: int
    embedding: list[float] | str
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: Any | None = None


@dataclass(frozen=True, slots=True)
class EmbeddingResponse:
    """Normalized embedding response."""

    provider: str
    model: str | None
    vectors: tuple[EmbeddingVector, ...]
    dimensions: int | None = None
    usage: Usage | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: Any | None = None
