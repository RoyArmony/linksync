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
    brand="mybrand",   # optional
    post_id="p001",   # optional — auto-generated if omitted
)
print(short_url)
# https://yourdomain.com/myproject/mybrand/p001
```

## Features

- **Project-based isolation**: Each API key is scoped to a specific project
- **Hierarchical URLs**: All links follow `{project}/{brand}/{post_id}` format
- **Channel suffix tracking**: Append any `-suffix` to a link URL for per-channel analytics (e.g. `-fb`, `-tg`, `-newsletter`). No registration needed.
- **Auto-generated IDs**: Post IDs are generated automatically if not provided
- **Type hints**: Full typing support for better IDE experience

## Usage

### `client.shorten()`

Shortens a long URL and returns the new short URL as a string.

```python
client.shorten(
    dest_long_url,        # Required: The long URL to shorten
    brand=None,           # Optional: Brand/channel name (e.g. "mybrand"). Omit for brand-less links.
    post_id=None,         # Optional: Custom short ID (e.g. "p001"). Auto-generated if omitted.
)
```

**Parameters:**

| Parameter | Required | Allowed characters | Result URL format | Notes |
|-----------|----------|--------------------|-------------------|-------|
| `dest_long_url` | ✅ | Any valid `http`/`https` URL | — | No private IPs or localhost |
| `brand` | ❌ | `a–z`, `A–Z`, `0–9`, `-` | `/{project}/{brand}/{post_id}` | Omit for brand-less links |
| `post_id` | ❌ | `a–z`, `A–Z`, `0–9` | `/{project}/{post_id}` or `/{project}/{brand}/{post_id}` | No dashes. `"base"` is reserved. Auto-generated (6 chars) if omitted. |
| `metadata` | ❌ | str, list, or dict | — | Optional context to store with the link (e.g. hotel name, area, dates). Returned by `get_link()` and `list()`. |

The `{project}` is always extracted automatically from your API key.

**Returns:** `str` — the short URL.

**Channel suffix tracking:**  
All suffix variants share the **same underlying link** (same KV key, same destination URL).
You simply append `-<suffix>` to any short URL at any time — no registration needed.
The worker detects and strips the suffix, redirects to the correct destination, and
increments per-suffix click counts in the `clicks_per_suffix` field of that link.

For example, the link `Xy3KpL` created once can be distributed on multiple channels:

```
https://domain.com/myproject/mybrand/Xy3KpL           → no suffix   → counted as "base"
https://domain.com/myproject/mybrand/Xy3KpL-fb        → suffix "fb" → Facebook traffic
https://domain.com/myproject/mybrand/Xy3KpL-tg        → suffix "tg" → Telegram traffic
https://domain.com/myproject/mybrand/Xy3KpL-email     → suffix "email" → email newsletter
```

All four URLs above redirect to the **same destination** and all clicks accumulate under
the same link entry. The resulting `clicks_per_suffix` might look like:

```python
{"base": 5, "fb": 12, "tg": 3, "email": 8}
```

Suffix rules: 1–10 alphanumeric characters (`a–z`, `A–Z`, `0–9`), no dashes.

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

### Example 3 — With brand and custom post ID

```python
short_url = client.shorten(
    dest_long_url="https://example.com/long-url",
    brand="mybrand",
    post_id="p381"
)
print(short_url)
# https://domain.com/myproject/mybrand/p381
```

### Example 4 — Custom post ID, no brand

```python
short_url = client.shorten(
    dest_long_url="https://example.com/long-url",
    post_id="p001"
)
print(short_url)
# https://domain.com/myproject/p001
```

---

## Other Methods

### `client.list(limit=100, cursor=None)`

List all links for your project. Returns up to `limit` links per call (max 1000).

**Response fields per link:**

| Field | Always present | Description |
|---|---|---|
| `id` | ✅ | Full KV key, e.g. `myproject:mybrand:p381` |
| `project` | ✅ | Your project name (from API key) |
| `post_id` | ✅ | The short ID part, e.g. `p381` |
| `brand` | only if brand was used | Brand name |
| `url` | ✅ | The original long URL |
| `clicks` | ✅ | Total click count (0 if never clicked) |
| `created_at` | ✅ | ISO timestamp of creation |
| `last_click` | only after first click | ISO timestamp of last click |
| `clicks_per_suffix` | only after first click | Dict of per-suffix click counts, e.g. `{"base": 3, "fb": 2}`. `base` = clicks with no suffix. |
| `metadata` | only if set | Any value passed at creation or via `edit_link_metadata()` (str, list, or dict). |

**Example response:**

```python
{
    "count": 42,
    "list_complete": False,
    "cursor": "AYcx...",
    "links": [
        {
            "id":               "myproject:mybrand:p381",
            "project":          "myproject",
            "brand":            "mybrand",
            "post_id":          "p381",
            "url":              "https://example.com/some-long-url",
            "clicks":           28,
            "created_at":       "2026-04-01T10:00:00.000Z",
            "last_click":       "2026-04-04T18:05:10.888Z",
            "clicks_per_suffix": {"base": 15, "fb": 8, "tg": 5},
        },
        # ... more links
    ]
}
```

**Basic usage:**

```python
result = client.list()
for link in result["links"]:
    print(link["id"], link["clicks"])
```

**Pagination with cursor** (when you have more than `limit` links):

```python
all_links = []
result = client.list(limit=50)
all_links.extend(result["links"])

while not result["list_complete"]:
    result = client.list(limit=50, cursor=result["cursor"])
    all_links.extend(result["links"])

# all_links now contains every link in your project
print(f"Total: {len(all_links)}")
```

### `client.get_link(link_id)`

Get full details for a single link by its ID. Returns the same fields as a single entry from `list()`.

```python
info = client.get_link("myproject:mybrand:p381")
```

**Example response:**

```python
{
    "id":                "myproject:mybrand:p381",
    "project":           "myproject",
    "brand":             "mybrand",
    "post_id":           "p381",
    "url":               "https://example.com/some-long-url",
    "clicks":            28,
    "created_at":        "2026-04-01T10:00:00.000Z",
    "last_click":        "2026-04-04T18:05:10.888Z",
    "clicks_per_suffix": {"base": 15, "fb": 8, "tg": 5},
    "metadata":          {"hotel": "Dan Tel Aviv", "area": "Tel Aviv", "dates": "15-17 Apr"},
}
```

(`last_click`, `clicks_per_suffix`, and `metadata` only appear if set.)

---

### `client.edit_link_metadata(link_id, metadata)`

Update the metadata of an existing link without affecting any other fields. Pass `None` to clear it.

```python
# Set or replace metadata
client.edit_link_metadata(
    "myproject:mybrand:p381",
    {"hotel": "Dan Tel Aviv", "area": "Tel Aviv", "dates": "15-17 Apr"}
)

# Update to a plain string
client.edit_link_metadata("myproject:mybrand:p381", "Dan Tel Aviv promo")

# Clear metadata
client.edit_link_metadata("myproject:mybrand:p381", None)
```

**Returns:** `{"success": True, "id": "...", "metadata": ...}`

---

### `client.delete(link_id)`

Delete a link by its full ID.

**Returns:**

```python
{"success": True, "message": "Link deleted successfully", "id": "myproject:mybrand:p381"}
```

**Example:**

```python
result = client.delete("myproject:mybrand:p381")
print(result["message"])  # Link deleted successfully
```

**Delete all links in your project:**

```python
result = client.list(limit=1000)
all_links = result["links"]

while not result["list_complete"]:
    result = client.list(limit=1000, cursor=result["cursor"])
    all_links.extend(result["links"])

for link in all_links:
    client.delete(link["id"])

print(f"Deleted {len(all_links)} links")
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
