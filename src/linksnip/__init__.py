"""linksnip - Python SDK for creating and managing short URLs.

A generic URL shortening client that works with any compatible backend API.
"""

__version__ = "0.2.0"

from .client import Client
from .exceptions import (
    LinksnipError,
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
    "LinksnipError",
    "AuthenticationError",
    "InvalidURLError",
    "LinkNotFoundError",
    "LinkExistsError",
    "ValidationError",
    "APIError",
    "ConnectionError",
]
