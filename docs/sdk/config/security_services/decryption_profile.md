# Decryption Profile Configuration Object

The `DecryptionProfile` class provides functionality to manage decryption profiles in Palo Alto Networks' Strata Cloud
Manager. Decryption profiles define SSL/TLS inspection settings for both forward proxy and inbound proxy scenarios,
allowing
granular control over encryption protocols, algorithms, and certificate validation.

## Overview

Decryption profiles in Strata Cloud Manager allow you to:

- Configure SSL/TLS protocol versions and cipher suites
- Define forward proxy settings for outbound traffic inspection
- Set up inbound proxy settings for inbound traffic inspection
- Specify certificate validation requirements
- Control protocol downgrades and extensions
- Organize profiles within folders, snippets, or devices

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during profile
management.

## Methods

| Method     | Description                                     |
|------------|-------------------------------------------------|
| `create()` | Creates a new decryption profile                |
| `get()`    | Retrieves a decryption profile by ID            |
| `update()` | Updates an existing decryption profile          |
| `delete()` | Deletes a decryption profile                    |
| `list()`   | Lists decryption profiles with optional filters |
| `fetch()`  | Retrieves a single decryption profile by name   |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when profile data is invalid or for invalid response formats
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when a profile doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when profile names conflict
- `NameNotUniqueError`: Raised when creating duplicate profile names
- `ReferenceNotZeroError`: Raised when deleting profiles still referenced by policies

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out

## Creating Decryption Profiles

The `create()` method allows you to create new decryption profiles with proper error handling.

**Example: Forward Proxy Profile**

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DecryptionProfile
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

decryption_profiles = DecryptionProfile(client)

try:
    forward_proxy = {
        "name": "forward-proxy",
        "folder": "Texas",
        "ssl_forward_proxy": {
            "auto_include_altname": True,
            "block_expired_certificate": True,
            "block_untrusted_issuer": True,
            "strip_alpn": False
        },
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "tls1-3"
        }
    }

    new_profile = decryption_profiles.create(forward_proxy)
    print(f"Created profile: {new_profile.name}")

except NameNotUniqueError as e:
    print(f"Profile name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid profile data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

**Example: Inbound Proxy Profile**

<div class="termy">

<!-- termynal -->

```python
try:
    inbound_proxy = {
        "name": "inbound-proxy",
        "folder": "Shared",
        "ssl_inbound_proxy": {
            "block_if_no_resource": True,
            "block_unsupported_cipher": True,
            "block_unsupported_version": True
        },
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "tls1-3",
            "auth_algo_sha256": True,
            "auth_algo_sha384": True
        }
    }

    new_profile = decryption_profiles.create(inbound_proxy)
    print(f"Created profile: {new_profile.name}")

except InvalidObjectError as e:
    print(f"Invalid profile data: {e.message}")
    print(f"Error code: {e.error_code}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Decryption Profiles

Use the `get()` method to retrieve a decryption profile by its ID.

<div class="termy">

<!-- termynal -->

```python
try:
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    profile = decryption_profiles.get(profile_id)
    print(f"Profile Name: {profile.name}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
```

</div>

## Updating Decryption Profiles

The `update()` method allows you to modify existing decryption profiles using Pydantic models.

<div class="termy">

<!-- termynal -->

```python
try:
    fetched_profile = decryption_profiles.fetch(folder='Texas', name="forward-proxy")
    fetched_profile.ssl_forward_proxy.auto_include_altname = False

    updated_profile = decryption_profiles.update(fetched_profile)
    print(f"Updated profile: {updated_profile.name}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting Decryption Profiles

Use the `delete()` method to remove a decryption profile.

<div class="termy">

<!-- termynal -->

```python
try:
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    decryption_profiles.delete(profile_id)
    print("Profile deleted successfully")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Profile still in use: {e.message}")
```

</div>

## Listing Decryption Profiles

The `list()` method retrieves multiple decryption profiles with optional filtering. You can filter the results using the
following kwargs:

- `types`: List[str] - Filter by proxy types (e.g., ['forward', 'inbound', 'no'])

<div class="termy">

<!-- termynal -->

```python
try:
    # List all profiles in a folder
    profiles = decryption_profiles.list(folder="Texas")

    # List only forward proxy profiles
    forward_profiles = decryption_profiles.list(
        folder="Texas",
        types=['forward']
    )

    # List both forward and inbound proxy profiles
    mixed_profiles = decryption_profiles.list(
        folder="Texas",
        types=['forward', 'inbound']
    )

    # Print the results
    for profile in profiles:
        print(f"Name: {profile.name}")
        if profile.ssl_forward_proxy:
            print("Type: Forward Proxy")
        elif profile.ssl_inbound_proxy:
            print("Type: Inbound Proxy")
        else:
            print("Type: No Proxy")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching Decryption Profiles

The `fetch()` method retrieves a single decryption profile by name from a specific container, returning a Pydantic
model.

<div class="termy">

<!-- termynal -->

```python
try:
    profile = decryption_profiles.fetch(name="Oblivion", folder="Texas")
    print(f"Found profile: {profile.name}")
    print(f"Current settings: {profile.ssl_protocol_settings}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a decryption profile with proper error handling:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DecryptionProfile
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
    ReferenceNotZeroError
)

try:
    # Initialize client with debug logging
    client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        log_level="DEBUG"  # Enable detailed logging
    )

    # Initialize decryption profile object
    decryption_profiles = DecryptionProfile(client)

    try:
        # Create new profile
        forward_proxy = {
            "name": "forward-proxy",
            "folder": "Texas",
            "ssl_forward_proxy": {
                "auto_include_altname": True,
                "block_expired_certificate": True,
                "block_untrusted_issuer": True,
                "strip_alpn": False
            },
            "ssl_protocol_settings": {
                "min_version": "tls1-2",
                "max_version": "tls1-3"
            }
        }

        new_profile = decryption_profiles.create(forward_proxy)
        print(f"Created profile: {new_profile.name}")

        # Fetch the profile by name
        try:
            fetched_profile = decryption_profiles.fetch(
                name="forward-proxy",
                folder="Texas"
            )
            print(f"Found profile: {fetched_profile.name}")

            # Update the profile using Pydantic model
            fetched_profile.ssl_forward_proxy.auto_include_altname = False
            updated_profile = decryption_profiles.update(fetched_profile)
            print(f"Updated profile: {updated_profile.name}")

        except NotFoundError as e:
            print(f"Profile not found: {e.message}")

        # Clean up
        try:
            decryption_profiles.delete(new_profile.id)
            print("Profile deleted successfully")
        except ReferenceNotZeroError as e:
            print(f"Cannot delete profile - still in use: {e.message}")

    except NameNotUniqueError as e:
        print(f"Profile name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid profile data: {e.message}")
        if e.details:
            print(f"Details: {e.details}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.http_status_code}")
```

</div>

## Related Models

- [DecryptionProfileCreateModel](../../models/security_services/decryption_profile_models.md#Overview)
- [DecryptionProfileUpdateModel](../../models/security_services/decryption_profile_models.md#Overview)
- [DecryptionProfileResponseModel](../../models/security_services/decryption_profile_models.md#Overview)