from __future__ import annotations

import pytest

from whero.vatbrain import (
    AudioPart,
    FilePart,
    ImagePart,
    ItemKind,
    MessageItem,
    ReasoningItem,
    Role,
    TextPart,
    VideoPart,
)


def test_message_item_accepts_string_parts() -> None:
    item = MessageItem.user("hello")

    assert item.role == Role.USER
    assert item.parts == (TextPart("hello"),)


def test_image_part_requires_exactly_one_source() -> None:
    with pytest.raises(ValueError):
        ImagePart()

    with pytest.raises(ValueError):
        ImagePart(url="https://example.test/a.png", data="abc")

    assert ImagePart(url="https://example.test/a.png").url == "https://example.test/a.png"


@pytest.mark.parametrize("part_cls", [AudioPart, VideoPart, FilePart])
def test_media_and_file_parts_require_exactly_one_source(part_cls: type[object]) -> None:
    with pytest.raises(ValueError):
        part_cls()

    with pytest.raises(ValueError):
        part_cls(url="https://example.test/a", data="abc")

    part = part_cls(local_path="/tmp/example.bin")

    assert part.local_path == "/tmp/example.bin"


def test_file_part_accepts_provider_file_id() -> None:
    part = FilePart(file_id="file_1", provider="openai", mime_type="application/pdf")

    assert part.file_id == "file_1"
    assert part.provider == "openai"


def test_reasoning_item_defaults_to_not_replayable() -> None:
    item = ReasoningItem(summary="short reasoning", provider="openai")

    assert item.kind == ItemKind.REASONING
    assert item.can_be_replayed is False

    with pytest.raises(ValueError):
        ReasoningItem()
