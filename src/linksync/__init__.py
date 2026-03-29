"""linksync - Python SDK for creating and managing short URLs.

A generic URL shortening client that works with any compatible backend API.
"""

# Read version from package metadata (single source of truth in pyproject.toml)
try:
    from importlib.metadata import version
    __version__ = version("linksync")
except Exception:
    __version__ = "unknown"

from .client import Client
from .exceptions import (
    LinksyncError,
    AuthenticationError,
    InvalidURLError,
    LinkNotFoundError,
    LinkExistsError,
    ValidationError,
    APIError,
    ConnectionError
)

__all__ = [
    "Client",
    "LinksyncError",
    "AuthenticationError",
    "InvalidURLError",
    "LinkNotFoundError",
    "LinkExistsError",
    "ValidationError",
    "APIError",
    "ConnectionError",
]
