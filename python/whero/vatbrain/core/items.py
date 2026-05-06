"""Content item models shared by generation and embedding APIs."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Literal


class Role(StrEnum):
    """Source or speaker role for a content item."""

    SYSTEM = "system"
    DEVELOPER = "developer"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ItemKind(StrEnum):
    """High-level kind of a vatbrain item."""

    MESSAGE = "message"
    FUNCTION_CALL = "function_call"
    FUNCTION_RESULT = "function_result"
    REASONING = "reasoning"


class ItemPurpose(StrEnum):
    """Optional purpose annotation for an item."""

    INSTRUCTION = "instruction"
    QUERY = "query"
    CONTEXT = "context"
    ANSWER = "answer"
    TOOL_IO = "tool_io"
    ARTIFACT = "artifact"


class PartKind(StrEnum):
    """Content part kind inside a message item."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"


@dataclass(frozen=True, slots=True)
class TextPart:
    """A text content part."""

    text: str
    kind: Literal[PartKind.TEXT] = PartKind.TEXT


@dataclass(frozen=True, slots=True)
class ImagePart:
    """An image content part for generation inputs."""

    url: str | None = None
    data: str | None = None
    mime_type: str | None = None
    detail: str | None = None
    kind: Literal[PartKind.IMAGE] = PartKind.IMAGE

    def __post_init__(self) -> None:
        if bool(self.url) == bool(self.data):
            raise ValueError("ImagePart requires exactly one of url or data.")


@dataclass(frozen=True, slots=True)
class AudioPart:
    """An audio content part reference."""

    url: str | None = None
    data: str | None = None
    file_id: str | None = None
    local_path: str | None = None
    mime_type: str | None = None
    format: str | None = None
    provider: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: Literal[PartKind.AUDIO] = PartKind.AUDIO

    def __post_init__(self) -> None:
        _validate_single_source(
            "AudioPart",
            file_id=self.file_id,
            url=self.url,
            data=self.data,
            local_path=self.local_path,
        )


@dataclass(frozen=True, slots=True)
class VideoPart:
    """A video content part reference."""

    url: str | None = None
    data: str | None = None
    file_id: str | None = None
    local_path: str | None = None
    mime_type: str | None = None
    format: str | None = None
    provider: str | None = None
    fps: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: Literal[PartKind.VIDEO] = PartKind.VIDEO

    def __post_init__(self) -> None:
        _validate_single_source(
            "VideoPart",
            file_id=self.file_id,
            url=self.url,
            data=self.data,
            local_path=self.local_path,
        )


@dataclass(frozen=True, slots=True)
class FilePart:
    """A provider file or local file reference used as content."""

    file_id: str | None = None
    url: str | None = None
    data: str | None = None
    local_path: str | None = None
    filename: str | None = None
    mime_type: str | None = None
    media_type: str | None = None
    provider: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: Literal[PartKind.FILE] = PartKind.FILE

    def __post_init__(self) -> None:
        _validate_single_source(
            "FilePart",
            file_id=self.file_id,
            url=self.url,
            data=self.data,
            local_path=self.local_path,
        )


ContentPart = TextPart | ImagePart | AudioPart | VideoPart | FilePart


@dataclass(frozen=True, slots=True)
class MessageItem:
    """A message-like item made of one or more content parts."""

    role: Role
    parts: tuple[ContentPart, ...]
    purpose: ItemPurpose | None = None
    id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: ClassVar[ItemKind] = ItemKind.MESSAGE

    def __init__(
        self,
        role: Role | str,
        parts: list[ContentPart] | tuple[ContentPart, ...] | str,
        *,
        purpose: ItemPurpose | str | None = None,
        id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        object.__setattr__(self, "role", Role(role))
        if isinstance(parts, str):
            normalized_parts: tuple[ContentPart, ...] = (TextPart(parts),)
        else:
            normalized_parts = tuple(parts)
        if not normalized_parts:
            raise ValueError("MessageItem requires at least one content part.")
        object.__setattr__(self, "parts", normalized_parts)
        object.__setattr__(
            self,
            "purpose",
            ItemPurpose(purpose) if purpose is not None else None,
        )
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "metadata", dict(metadata or {}))

    @classmethod
    def system(cls, parts: list[ContentPart] | tuple[ContentPart, ...] | str) -> MessageItem:
        return cls(Role.SYSTEM, parts, purpose=ItemPurpose.INSTRUCTION)

    @classmethod
    def developer(cls, parts: list[ContentPart] | tuple[ContentPart, ...] | str) -> MessageItem:
        return cls(Role.DEVELOPER, parts, purpose=ItemPurpose.INSTRUCTION)

    @classmethod
    def user(cls, parts: list[ContentPart] | tuple[ContentPart, ...] | str) -> MessageItem:
        return cls(Role.USER, parts, purpose=ItemPurpose.QUERY)

    @classmethod
    def assistant(cls, parts: list[ContentPart] | tuple[ContentPart, ...] | str) -> MessageItem:
        return cls(Role.ASSISTANT, parts, purpose=ItemPurpose.ANSWER)


@dataclass(frozen=True, slots=True)
class FunctionCallItem:
    """A model request to call a function tool."""

    name: str
    arguments: str
    call_id: str
    id: str | None = None
    status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: ClassVar[ItemKind] = ItemKind.FUNCTION_CALL
    role: ClassVar[Role] = Role.ASSISTANT
    purpose: ClassVar[ItemPurpose] = ItemPurpose.TOOL_IO


@dataclass(frozen=True, slots=True)
class FunctionResultItem:
    """A user-supplied function result to feed back into generation."""

    call_id: str
    output: str
    id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    kind: ClassVar[ItemKind] = ItemKind.FUNCTION_RESULT
    role: ClassVar[Role] = Role.TOOL
    purpose: ClassVar[ItemPurpose] = ItemPurpose.TOOL_IO


@dataclass(frozen=True, slots=True)
class ReasoningItem:
    """Provider-returned reasoning content or summary."""

    text: str | None = None
    summary: str | None = None
    provider: str | None = None
    visibility: str | None = None
    can_be_replayed: bool | None = False
    id: str | None = None
    status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: Any | None = None
    kind: ClassVar[ItemKind] = ItemKind.REASONING
    role: ClassVar[Role] = Role.ASSISTANT
    purpose: ClassVar[ItemPurpose] = ItemPurpose.CONTEXT

    def __post_init__(self) -> None:
        if self.text is None and self.summary is None and self.raw is None:
            raise ValueError("ReasoningItem requires text, summary, or raw.")


Item = MessageItem | FunctionCallItem | FunctionResultItem | ReasoningItem


def _validate_single_source(name: str, **sources: str | None) -> None:
    provided = [source_name for source_name, value in sources.items() if bool(value)]
    if not provided:
        raise ValueError(f"{name} requires one of {', '.join(sources)}.")
    if len(provided) > 1:
        raise ValueError(f"{name} requires exactly one content source; got {', '.join(provided)}.")
