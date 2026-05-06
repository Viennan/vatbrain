"""Provider resource and file lifecycle models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from os import PathLike
from typing import Any


class FileStatus(StrEnum):
    """Provider file lifecycle status."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class FilePurpose(StrEnum):
    """Provider file purpose."""

    ASSISTANTS = "assistants"
    BATCH = "batch"
    FINE_TUNE = "fine_tune"
    VISION = "vision"
    RETRIEVAL = "retrieval"
    MEDIA = "media"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class FilePreprocessConfig:
    """Optional provider-side file preprocessing hints."""

    video_fps: float | None = None
    image_detail: str | None = None
    extract_text: bool | None = None
    provider_options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FileUploadRequest:
    """A file upload request model; core does not perform local I/O."""

    file: bytes | str | PathLike[str] | Any
    filename: str | None = None
    purpose: FilePurpose | str | None = None
    mime_type: str | None = None
    preprocess: FilePreprocessConfig | None = None
    provider_options: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.file is None:
            raise ValueError("FileUploadRequest.file is required.")
        if self.purpose is not None and not isinstance(self.purpose, FilePurpose):
            object.__setattr__(self, "purpose", FilePurpose(self.purpose))


@dataclass(frozen=True, slots=True)
class FileResource:
    """A provider-managed file resource."""

    id: str
    provider: str
    filename: str | None = None
    purpose: FilePurpose | str | None = None
    mime_type: str | None = None
    bytes: int | None = None
    status: FileStatus | str = FileStatus.UNKNOWN
    created_at: datetime | str | None = None
    expires_at: datetime | str | None = None
    preprocess: FilePreprocessConfig | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: Any | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("FileResource.id is required.")
        if not self.provider:
            raise ValueError("FileResource.provider is required.")
        if self.purpose is not None and not isinstance(self.purpose, FilePurpose):
            object.__setattr__(self, "purpose", FilePurpose(self.purpose))
        if not isinstance(self.status, FileStatus):
            object.__setattr__(self, "status", FileStatus(self.status))
