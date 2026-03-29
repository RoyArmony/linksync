"""
linksnip - Generic URL shortening client
"""

import requests
from typing import Dict, List, Optional, Union
from .exceptions import (
    AuthenticationError,
    InvalidURLError,
    LinkNotFoundError,
    LinkExistsError,
    ValidationError,
    APIError,
    ConnectionError
)


class Client:
    """
    Generic client for URL shortening APIs
    
    Args:
        base_url: Base URL of the shortening service (e.g., "https://yourdomain.com")
        api_key: API key for authentication
        timeout: Request timeout in seconds (default: 30)
    
    Examples:
        >>> client = Client(base_url="https://yourdomain.com", api_key="your-key")
        >>> url = client.shorten("https://example.com/long-url")
        >>> print(url)
        https://yourdomain.com/abc123
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
        
        Returns:
            Response JSON as dict
        
        Raises:
            AuthenticationError: Invalid API key
            ConnectionError: Unable to connect
            APIError: API returned an error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self._session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )
        except requests.exceptions.Timeout:
            raise ConnectionError(f"Request to {url} timed out after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {url}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {str(e)}")
        
        # Handle non-2xx responses
        if not response.ok:
            try:
                error_data = response.json()
                error_info = error_data.get('error', {})
                error_code = error_info.get('code', 'UNKNOWN')
                error_message = error_info.get('message', 'Unknown error')
            except:
                error_code = 'UNKNOWN'
                error_message = response.text or 'Unknown error'
            
            # Map error codes to specific exceptions
            if response.status_code == 401:
                raise AuthenticationError(error_message)
            elif response.status_code == 404:
                if error_code == 'LINK_NOT_FOUND':
                    raise LinkNotFoundError(error_message)
            elif response.status_code == 409:
                if error_code == 'LINK_EXISTS':
                    raise LinkExistsError(error_message)
            elif response.status_code == 400:
                if 'URL' in error_code or 'INVALID' in error_code:
                    raise ValidationError(error_message)
            
            # Generic API error
            raise APIError(error_message, status_code=response.status_code, error_code=error_code)
        
        # Parse and return JSON
        try:
            return response.json()
        except:
            return {}
    
    def shorten(
        self,
        url: str,
        structure: Optional[str] = None,
        project: Optional[str] = None,
        brand: Optional[str] = None,
        post_id: Optional[str] = None,
        platforms: Optional[List[str]] = None
    ) -> Union[str, Dict[str, str]]:
        """
        Create a short link
        
        Args:
            url: The long URL to shorten
            structure: Link structure - "simple" (default) or "hierarchical"
            project: Project name (required for hierarchical)
            brand: Brand name (required for hierarchical)
            post_id: Custom post ID (optional, auto-generated if omitted)
            platforms: List of platform codes for attribution (e.g., ["fb", "ig", "tg"])
        
        Returns:
            If platforms is None: Short URL string
            If platforms provided: Dict with "base" and platform-specific URLs
        
        Raises:
            InvalidURLError: URL is invalid
            ValidationError: Invalid parameters
            AuthenticationError: Invalid API key
            LinkExistsError: Link already exists
            APIError: Other API errors
        
        Examples:
            Simple shortening:
            >>> url = client.shorten("https://example.com")
            >>> print(url)
            https://yourdomain.com/abc123
            
            With platform tracking:
            >>> urls = client.shorten(
            ...     "https://example.com",
            ...     platforms=["fb", "ig", "tg"]
            ... )
            >>> print(urls["fb"])
            https://yourdomain.com/abc123-fb
            
            Hierarchical structure:
            >>> url = client.shorten(
            ...     "https://example.com",
            ...     structure="hierarchical",
            ...     project="<project-name>",
            ...     brand="<brand-name>",
            ...     post_id="p381"
            ... )
            >>> print(url)
            https://yourdomain.com/<project-name>/<brand-name>/p381
        """
        # Build request payload
        payload = {"url": url}
        
        if structure:
            payload["structure"] = structure
        
        if project:
            payload["project"] = project
        
        if brand:
            payload["brand"] = brand
        
        if post_id:
            payload["post_id"] = post_id
        
        if platforms:
            if not isinstance(platforms, list):
                raise ValidationError("platforms must be a list")
            payload["platforms"] = platforms
        
        # Make API request
        response = self._request('POST', '/api/shorten', json=payload)
        
        # Return appropriate format
        if platforms:
            return response.get('platforms', {})
        else:
            return response.get('short_url', '')
    
    def delete(self, link_id: str) -> Dict[str, any]:
        """
        Delete a short link
        
        Args:
            link_id: The link ID to delete
                    For simple links: "abc123"
                    For hierarchical: "project:brand:id" (will be URL-encoded)
        
        Returns:
            Dict with deletion details
        
        Raises:
            LinkNotFoundError: Link does not exist
            AuthenticationError: Invalid API key
            APIError: Other API errors
        
        Examples:
            >>> client.delete("abc123")
            >>> client.delete("<project-name>:<brand-name>:p381")
        """
        # URL encode the ID (handles colons in hierarchical keys)
        from urllib.parse import quote
        encoded_id = quote(link_id, safe='')
        
        response = self._request('DELETE', f'/api/links/{encoded_id}')
        return response
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session"""
        self._session.close()
    
    def close(self):
        """Close the HTTP session"""
        self._session.close()
