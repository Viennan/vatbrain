from __future__ import annotations

import pytest

from whero.vatbrain import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    MediaArtifact,
    MediaGenerationTask,
    MediaKind,
    TaskStatus,
)


def test_media_artifact_requires_a_reference() -> None:
    artifact = MediaArtifact(kind="image", url="https://example.test/a.png", width=512, height=512)

    assert artifact.kind == MediaKind.IMAGE
    assert artifact.width == 512

    with pytest.raises(ValueError):
        MediaArtifact(kind="image")


def test_image_generation_request_and_response_construct() -> None:
    request = ImageGenerationRequest(
        model="image-test",
        prompt="a small robot",
        count=2,
        output_format="png",
    )
    artifact = MediaArtifact(kind=MediaKind.IMAGE, data="abc")
    response = ImageGenerationResponse(provider="test", model="image-test", artifacts=(artifact,))

    assert request.prompt == "a small robot"
    assert request.count == 2
    assert response.artifacts == (artifact,)


def test_media_generation_task_normalizes_status() -> None:
    task = MediaGenerationTask(id="task_1", provider="volcengine", model="video-test", status="running")

    assert task.status == TaskStatus.RUNNING

    with pytest.raises(ValueError):
        MediaGenerationTask(id="", provider="volcengine", model="video-test")
