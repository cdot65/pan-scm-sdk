# Authentication Module

The `OAuth2Client` class handles OAuth2 authentication with Palo Alto Networks' Strata Cloud Manager.

---

## Importing the OAuth2Client Class

```python
from scm.auth import OAuth2Client
```

## Class: OAuth2Client

Handles token acquisition, validation, and refresh.

### Attributes

- `auth_request` (AuthRequestModel): Authentication parameters.
- `session` (OAuth2Session): Authenticated session.
- `signing_key`: Key used for verifying JWT tokens.

### Methods

- `__init__(auth_request: AuthRequestModel)`: Initializes the client.
- `decode_token() -> dict`: Decodes the JWT token.
- `is_expired() -> bool`: Checks if the token is expired.
- `refresh_token()`: Refreshes the authentication token.

### Usage Example

```python
from scm.auth import OAuth2Client
from scm.models.auth import AuthRequestModel

auth_request = AuthRequestModel(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

oauth_client = OAuth2Client(auth_request)
```
