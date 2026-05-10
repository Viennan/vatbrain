from __future__ import annotations

import pytest

from whero.vatbrain import (
    AssistantMessagePhase,
    AudioPart,
    FilePart,
    ImagePart,
    ItemKind,
    MessageItem,
    ProviderItemSnapshot,
    ReasoningItem,
    Role,
    TextPart,
    VideoPart,
    provider_snapshot_for,
)


def test_message_item_accepts_string_parts() -> None:
    item = MessageItem.user("hello")

    assert item.role == Role.USER
    assert item.parts == (TextPart("hello"),)


def test_message_item_accepts_assistant_phase() -> None:
    item = MessageItem.assistant("working", assistant_phase="commentary")

    assert item.assistant_phase == AssistantMessagePhase.COMMENTARY

    with pytest.raises(ValueError):
        MessageItem(Role.USER, "hello", assistant_phase=AssistantMessagePhase.FINAL_ANSWER)


def test_provider_item_snapshot_attaches_to_item_field() -> None:
    snapshot = ProviderItemSnapshot(
        provider="openai",
        api_family="responses",
        item_type="message",
        payload={"type": "message", "role": "assistant", "content": []},
        captured_from="response",
    )
    item = MessageItem(Role.ASSISTANT, "hello", provider_snapshots=[snapshot])

    assert item.provider_snapshots == (snapshot,)
    assert provider_snapshot_for(item, provider="openai", api_family="responses") is snapshot
    assert provider_snapshot_for(item, provider="volcengine", api_family="responses") is None


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
