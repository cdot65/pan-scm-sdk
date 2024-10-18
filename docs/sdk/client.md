# SCM Client

The `Scm` class provides methods to interact with the Palo Alto Networks Strata Cloud Manager API.

---

## Importing the Scm Class

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
```

</div>

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

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm

api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Import Address from SDK and pass the `scm` instance into the Address class
from scm.config.objects import Address

addresses = Address(api_client)

# list all configured addresses in Prisma Access folder
addresses.list(folder='Prisma Access')
```

</div>

