# linksnip

Python SDK for creating and managing short URLs with project-based isolation.

## Installation

```bash
pip install linksnip
```

## Quick Start

```python
from linksnip import Client

client = Client(
    base_url="https://yourdomain.com",
    api_key="lsnp_myproject_abc123..."
)

short_url = client.shorten(
    dest_long_url="https://example.com/long-product-url",
    brand="mybrand"
)
print(short_url)
# https://yourdomain.com/myproject/mybrand/Xy3KpL
```

## Features

- **Project-based isolation**: Each API key is scoped to a specific project
- **Hierarchical URLs**: All links follow `{project}/{brand}/{post_id}` format
- **Platform tracking**: Create platform-specific variations (Facebook, Instagram, etc.)
- **Auto-generated IDs**: Post IDs are generated automatically if not provided
- **Type hints**: Full typing support for better IDE experience

## Usage

### `client.shorten()`

```python
client.shorten(
    dest_long_url,   # Required: The long URL to shorten
    brand,           # Required: Brand name (e.g., "isrotel")
    post_id=None,    # Optional: Custom post ID. Auto-generated if omitted (see below)
    platforms=None,  # Optional: List of platform codes, e.g. ["fb", "ig", "tg"]
)
```

In Python, **required** parameters have no default value — passing them by name is optional
but recommended for clarity. **Optional** parameters always have a default (here `=None`).

**Returns:**
- `str` — the short URL, when `platforms` is not provided
- `dict` — when `platforms` is provided: a dict keyed by platform code, in the same order
  as the input list, plus a `"base"` entry. Example for `platforms=["fb", "ig", "tg"]`:
  ```python
  {
      "base": "https://yourdomain.com/myproject/mybrand/Xy3KpL",
      "fb":   "https://yourdomain.com/myproject/mybrand/Xy3KpL-fb",
      "ig":   "https://yourdomain.com/myproject/mybrand/Xy3KpL-ig",
      "tg":   "https://yourdomain.com/myproject/mybrand/Xy3KpL-tg",
  }
  ```

**How post IDs are auto-generated:**
When `post_id` is not provided, a 6-character random base62 string is generated
(`a–z`, `A–Z`, `0–9` → 62⁶ ≈ 56 billion possible values). The ID is checked against
the database to avoid collisions, with up to 5 retries.

---

### Example 1 — Basic shortening

```python
short_url = client.shorten(
    dest_long_url="https://www.isrotel.co.il/rooms",
    brand="isrotel"
)
print(short_url)
# https://yourdomain.com/myproject/isrotel/Xy3KpL
```

### Example 2 — Custom post ID

```python
short_url = client.shorten(
    dest_long_url="https://www.isrotel.co.il/rooms",
    brand="isrotel",
    post_id="p381"
)
print(short_url)
# https://yourdomain.com/myproject/isrotel/p381
```

### Example 3 — Platform tracking

```python
urls = client.shorten(
    dest_long_url="https://www.isrotel.co.il/rooms",
    brand="isrotel",
    platforms=["fb", "ig", "tg"]
)

# urls is a dict in the same order as the input list, plus "base":
print(urls["base"])  # https://yourdomain.com/myproject/isrotel/Xy3KpL
print(urls["fb"])    # https://yourdomain.com/myproject/isrotel/Xy3KpL-fb
print(urls["ig"])    # https://yourdomain.com/myproject/isrotel/Xy3KpL-ig
print(urls["tg"])    # https://yourdomain.com/myproject/isrotel/Xy3KpL-tg
```

### Example 4 — Custom ID + Platforms

```python
urls = client.shorten(
    dest_long_url="https://www.isrotel.co.il/rooms",
    brand="isrotel",
    post_id="p381",
    platforms=["fb", "ig"]
)
```

---

## Other Methods

### `client.list(limit=100, cursor=None)`

List all links for your project.

```python
result = client.list()
for link in result["links"]:
    print(f"{link['id']}: {link['url']}")
```

### `client.delete(link_id)`

Delete a link by its hierarchical ID (`project:brand:post_id`). Also automatically
deletes all platform variants.

```python
client.delete("myproject:isrotel:p381")
```

---

## Error Handling

```python
from linksnip import (
    AuthenticationError,
    InvalidURLError,
    LinkExistsError,
    ValidationError,
    APIError
)

try:
    short_url = client.shorten(dest_long_url="invalid-url", brand="test")
except AuthenticationError:
    print("Invalid API key")
except InvalidURLError:
    print("Invalid URL format")
except LinkExistsError:
    print("Link already exists")
except ValidationError as e:
    print(f"Validation error: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## API Reference

### `Client(base_url, api_key, timeout=30)`

**Parameters:**
- `base_url` (str): Base URL of your shortening service
- `api_key` (str): Your API key (format: `lsnp_{project}_{random}`) — the project is extracted automatically
- `timeout` (int): Request timeout in seconds (default: 30)

## Requirements

- Python 3.8+
- requests >= 2.28.0

## License

MIT


## Features

- **Project-based isolation**: Each API key is scoped to a specific project
- **Hierarchical URLs**: All links follow `{project}/{brand}/{post_id}` format
- **Platform tracking**: Create platform-specific variations (Facebook, Instagram, etc.)
- **Auto-generated IDs**: Post IDs are generated automatically if not provided
- **Type hints**: Full typing support for better IDE experience

## Usage

### Basic Shortening

```python
url = client.shorten(
    url="https://example.com",
    brand="mybrand"
)
```

### Custom Post ID

```python
url = client.shorten(
    url="https://example.com",
    brand="mybrand",
    post_id="summer-sale-2026"
)
```

### Platform Tracking

Create platform-specific URLs for attribution:

```python
urls = client.shorten(
    url="https://example.com",
    brand="mybrand",
    platforms=["fb", "ig", "tg"]
)

print(urls["fb"])  # https://yourdomain.com/myproject/mybrand/abc123-fb
print(urls["ig"])  # https://yourdomain.com/myproject/mybrand/abc123-ig
```

### Delete a Link

```python
result = client.delete("myproject:mybrand:p381")
print(result["message"])  # Link deleted successfully
```

## API Reference

### `Client(base_url, api_key, timeout=30)`

Initialize the client.

**Parameters:**
- `base_url` (str): Base URL of your shortening service
- `api_key` (str): Your API key (format: `lsnp_{project}_{random}`)
- `timeout` (int): Request timeout in seconds (default: 30)

### `client.shorten(url, brand, post_id=None, platforms=None)`

Create a short link.

**Parameters:**
- `url` (str): Long URL to shorten
- `brand` (str): Brand identifier
- `post_id` (str, optional): Custom post ID (auto-generated if omitted)
- `platforms` (list, optional): Platform codes for UTM tracking

**Returns:**
- str: Short URL (if `platforms` is None)
- dict: Platform URLs (if `platforms` provided)

### `client.delete(link_id)`

Delete a short link.

**Parameters:**
- `link_id` (str): Link ID in format `project:brand:post_id`

**Returns:**
- dict: Deletion confirmation

## Error Handling

```python
from linksnip import (
    AuthenticationError,
    InvalidURLError,
    LinkExistsError,
    ValidationError,
    APIError
)

try:
    url = client.shorten(url="invalid-url", brand="test")
except AuthenticationError:
    print("Invalid API key")
except InvalidURLError:
    print("Invalid URL format")
except LinkExistsError:
    print("Link already exists")
except ValidationError as e:
    print(f"Validation error: {e}") 
except APIError as e:
    print(f"API error: {e}")
```

## Requirements

- Python 3.8+
- requests >= 2.28.0

## License

MIT
