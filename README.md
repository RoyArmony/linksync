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
- **Channel suffix tracking**: Append any `-suffix` to a link URL for per-channel analytics (e.g. `-fb`, `-tg`, `-newsletter`). No registration needed.
- **Auto-generated IDs**: Post IDs are generated automatically if not provided
- **Type hints**: Full typing support for better IDE experience

## Usage

### `client.shorten()`

```python
client.shorten(
    dest_long_url,        # Required: The long URL to shorten
    brand=None,           # Optional: Brand name (e.g., "mybrand"). Omit for brand-less links.
    post_id=None,         # Optional: Custom post ID. If omitted, auto-generated as a 6-char random ID (e.g. "Xy3KpL").
                          #           Must be alphanumeric only — no dashes.
)
```

In Python, **required** parameters have no default value — passing them by name is optional
but recommended for clarity. **Optional** parameters always have a default (here `=None`).

**URL structure depending on `brand`:**

| `brand` provided | Short URL format |
|-----------------|------------------|
| Yes | `https://domain.com/{project}/{brand}/{post_id}` |
| No  | `https://domain.com/{project}/{post_id}` |

The `{project}` is always extracted automatically from your API key.

**Returns:** `str` — the short URL.

**Channel suffix tracking:**  
You can append any `-suffix` to any short URL at any time — no declaration needed.
The worker strips the suffix, redirects to the correct destination, and records per-suffix
counts in the `clicks_per_suffix` field of that link.

```
https://domain.com/myproject/mybrand/Xy3KpL        → direct click
https://domain.com/myproject/mybrand/Xy3KpL-fb     → Facebook
https://domain.com/myproject/mybrand/Xy3KpL-tg     → Telegram
https://domain.com/myproject/mybrand/Xy3KpL-newsletter → email newsletter
```

Suffix rules: 2–10 alphanumeric characters, no dashes.

**How post IDs are auto-generated:**
When `post_id` is not provided, a 6-character random base62 string is generated
(`a–z`, `A–Z`, `0–9` → 62⁶ ≈ 56 billion possible values). The ID is checked against
the database to avoid collisions, with up to 5 retries.

---

### Example 1 — Basic shortening (no brand)

```python
short_url = client.shorten(
    dest_long_url="https://example.com/long-url"
)
print(short_url)
# https://domain.com/myproject/Xy3KpL
```

### Example 2 — With brand

```python
short_url = client.shorten(
    dest_long_url="https://example.com/long-url",
    brand="mybrand"
)
print(short_url)
# https://domain.com/myproject/mybrand/Xy3KpL
```

### Example 3 — Custom post ID

```python
short_url = client.shorten(
    dest_long_url="https://example.com/long-url",
    brand="mybrand",
    post_id="p381"
)
print(short_url)
# https://domain.com/myproject/mybrand/p381
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

Delete a link by its hierarchical ID (`project:brand:post_id`).

```python
client.delete("myproject:mybrand:p381")
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
    short_url = client.shorten(dest_long_url="invalid-url", brand="mybrand")
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
