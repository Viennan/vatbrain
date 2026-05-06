from __future__ import annotations

import pytest

from whero.vatbrain import (
    FilePreprocessConfig,
    FilePurpose,
    FileResource,
    FileStatus,
    FileUploadRequest,
)


def test_file_upload_request_normalizes_purpose() -> None:
    request = FileUploadRequest(
        file=b"hello",
        filename="hello.txt",
        purpose="retrieval",
        preprocess=FilePreprocessConfig(extract_text=True),
    )

    assert request.purpose == FilePurpose.RETRIEVAL
    assert request.preprocess is not None
    assert request.preprocess.extract_text is True


def test_file_upload_request_requires_file_reference() -> None:
    with pytest.raises(ValueError):
        FileUploadRequest(file=None)


def test_file_resource_normalizes_status_and_requires_identity() -> None:
    resource = FileResource(
        id="file_1",
        provider="volcengine",
        status="ready",
        purpose="media",
    )

    assert resource.status == FileStatus.READY
    assert resource.purpose == FilePurpose.MEDIA

    with pytest.raises(ValueError):
        FileResource(id="", provider="volcengine")
