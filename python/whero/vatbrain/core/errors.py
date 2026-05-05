"""vatbrain error hierarchy."""

from __future__ import annotations


class VatbrainError(Exception):
    """Base class for vatbrain errors."""


class InvalidItemError(VatbrainError):
    """Raised when an item cannot be used in the requested API family."""


class UnsupportedCapabilityError(VatbrainError):
    """Raised when a request requires a known unsupported capability."""


class ProviderRequestError(VatbrainError):
    """Raised when a provider SDK call fails."""

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(message)
        self.cause = cause


class ProviderResponseMappingError(VatbrainError):
    """Raised when a provider response cannot be mapped into vatbrain models."""
