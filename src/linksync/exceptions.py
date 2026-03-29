"""
Custom exceptions for linksnip SDK
"""


class LinksnipError(Exception):
    """Base exception for all linksnip errors"""
    pass


class AuthenticationError(LinksnipError):
    """Raised when API key is invalid or missing"""
    pass


class InvalidURLError(LinksnipError):
    """Raised when provided URL is invalid"""
    pass


class LinkNotFoundError(LinksnipError):
    """Raised when link ID does not exist"""
    pass


class LinkExistsError(LinksnipError):
    """Raised when trying to create a link that already exists"""
    pass


class ValidationError(LinksnipError):
    """Raised when input validation fails"""
    pass


class APIError(LinksnipError):
    """Raised when API returns an error"""
    
    def __init__(self, message, status_code=None, error_code=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class ConnectionError(LinksnipError):
    """Raised when unable to connect to API"""
    pass
