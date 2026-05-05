from __future__ import annotations

import pytest

from whero.vatbrain import ImagePart, MessageItem, Role, TextPart


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
