# SCM Client

The `Scm` class provides methods to interact with the Palo Alto Networks Strata Cloud Manager API.

---

## Importing the Scm Class

```python
from scm.client import Scm
```

## Class: Scm

Manages authentication and API requests.

### Attributes

- `api_base_url` (str): Base URL for the API.
- `oauth_client` (OAuth2Client): OAuth2 client for authentication.
- `session` (requests.Session): HTTP session for requests.

### Methods

- `__init__(client_id: str, client_secret: str, tsg_id: str, api_base_url: str)`: Initializes the client.
- `request(method: str, endpoint: str, **kwargs)`: Makes an HTTP request.
- `get(endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs)`: Makes a GET request.
- `post(endpoint: str, **kwargs)`: Makes a POST request.
- `put(endpoint: str, **kwargs)`: Makes a PUT request.
- `delete(endpoint: str, **kwargs)`: Makes a DELETE request.

### Usage Example

```python
from scm.client import Scm

scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Make a GET request
response = scm.get("/path/to/endpoint")
```
