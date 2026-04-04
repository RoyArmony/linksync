"""
linksnip - Generic URL shortening client
"""

import requests
from typing import Dict, Optional
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
        api_key: API key for authentication (format: lsnp_{project}_{random})
        timeout: Request timeout in seconds (default: 30)
    
    Examples:
        >>> client = Client(base_url="https://yourdomain.com", api_key="lsnp_myproject_abc123...")
        >>> short_url = client.shorten(dest_long_url="https://example.com/long-url", brand="mybrand")
        >>> print(short_url)
        https://yourdomain.com/myproject/mybrand/abc123
    
    Note:
        The project name is automatically extracted from your API key.
        With brand:    {project}/{brand}/{post_id}
        Without brand: {project}/{post_id}
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
        dest_long_url: str,
        brand: Optional[str] = None,
        post_id: Optional[str] = None,
        metadata=None,
    ) -> str:
        """
        Create a short link. See README for full usage and examples.

        Args:
            dest_long_url: The long URL to shorten
            brand: Brand name (e.g., 'mybrand'). Optional — omit for brand-less links.
            post_id: Custom post ID. Auto-generated (6-char base62) if omitted.
                     Must be alphanumeric only — no dashes.
            metadata: Optional metadata to store with the link (str, list, or dict).
                      Use this to attach context for later analysis
                      (e.g. hotel name, area, dates).

        Returns:
            str — the short URL

        Raises:
            InvalidURLError: URL is invalid
            ValidationError: Invalid parameters
            AuthenticationError: Invalid API key
            LinkExistsError: Link already exists
            APIError: Other API errors
        """
        payload = {"url": dest_long_url}

        if brand:
            payload["brand"] = brand

        if post_id:
            payload["post_id"] = post_id

        if metadata is not None:
            payload["metadata"] = metadata

        response = self._request('POST', '/api/shorten', json=payload)
        return response.get('short_url', '')
    
    def list(
        self,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, any]:
        """
        List all links for the authenticated project
        
        Args:
            limit: Maximum number of links to return (1-1000, default: 100)
            cursor: Pagination cursor from previous response (optional)
        
        Returns:
            Dict with:
                - links: List of link objects
                - count: Number of links returned
                - list_complete: Whether all links have been returned
                - cursor: Cursor for next page (if list_complete is False)
        
        Raises:
            AuthenticationError: Invalid API key
            APIError: Other API errors
        
        Examples:
            >>> result = client.list()
            >>> for link in result['links']:
            ...     print(f"{link['id']}: {link['url']}")
            
            >>> # Pagination
            >>> result = client.list(limit=50)
            >>> if not result['list_complete']:
            ...     next_result = client.list(cursor=result['cursor'])
        """
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        
        from urllib.parse import urlencode
        query_string = urlencode(params)
        
        response = self._request('GET', f'/api/links?{query_string}')
        return response
    
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

    def get_link(self, link_id: str) -> Dict[str, any]:
        """
        Get full details for a single link by its ID.

        Args:
            link_id: The full link ID, e.g. "myproject:mybrand:p381" or "myproject:p381"

        Returns:
            Dict with all link fields (same shape as a single entry from list())

        Raises:
            LinkNotFoundError: Link does not exist
            AuthenticationError: Invalid API key
            APIError: Other API errors
        """
        from urllib.parse import quote
        encoded_id = quote(link_id, safe='')

        response = self._request('GET', f'/api/links/{encoded_id}')
        return response

    def edit_link_metadata(self, link_id: str, metadata) -> Dict[str, any]:
        """
        Update the metadata of an existing link. Pass None to clear the metadata.

        Args:
            link_id: The full link ID, e.g. "myproject:mybrand:p381"
            metadata: New metadata value (str, list, dict, or None to clear)

        Returns:
            Dict with {success, id, metadata}

        Raises:
            LinkNotFoundError: Link does not exist
            AuthenticationError: Invalid API key
            APIError: Other API errors
        """
        from urllib.parse import quote
        encoded_id = quote(link_id, safe='')

        response = self._request('PATCH', f'/api/links/{encoded_id}', json={'metadata': metadata})
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
