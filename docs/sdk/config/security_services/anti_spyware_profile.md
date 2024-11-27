# Anti-Spyware Profile Configuration Object

The `AntiSpywareProfile` class provides functionality to manage anti-spyware profiles in Palo Alto Networks' Strata
Cloud Manager. Anti-spyware profiles define threat detection and prevention settings for identifying and blocking
spyware,
command-and-control traffic, and other malicious activities.

## Overview

Anti-spyware profiles in Strata Cloud Manager allow you to:

- Define rules for different threat severities and categories
- Configure actions for detected threats (alert, block, reset connections)
- Set up threat exceptions for specific cases
- Enable cloud-based inline analysis
- Configure MICA engine spyware detection
- Organize profiles within folders, snippets, or devices

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during profile
management.

## Methods

| Method     | Description                                         |
|------------|-----------------------------------------------------|
| `create()` | Creates a new anti-spyware profile                  |
| `get()`    | Retrieves an anti-spyware profile by ID             |
| `update()` | Updates an existing anti-spyware profile            |
| `delete()` | Deletes an anti-spyware profile                     |
| `list()`   | Lists anti-spyware profiles with optional filtering |
| `fetch()`  | Retrieves a single anti-spyware profile by name     |

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

## Creating Anti-Spyware Profiles

The `create()` method allows you to create new anti-spyware profiles with proper error handling.

**Example: Basic Profile with Single Rule**

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import AntiSpywareProfile
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

profiles = AntiSpywareProfile(client)

try:
    profile_data = {
        "name": "basic-profile",
        "description": "Basic anti-spyware profile",
        "folder": "Texas",
        "rules": [
            {
                "name": "block-critical",
                "severity": ["critical"],
                "category": "spyware",
                "action": {"block_ip": {"track_by": "source", "duration": 300}}
            }
        ]
    }

    new_profile = profiles.create(profile_data)
    print(f"Created profile: {new_profile.name}")

except NameNotUniqueError as e:
    print(f"Profile name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid profile data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

**Example: Profile with Multiple Rules and MICA Engine**

<div class="termy">

<!-- termynal -->

```python
try:
    profile_data = {
        "name": "advanced-profile",
        "description": "Advanced anti-spyware profile",
        "folder": "Texas",
        "cloud_inline_analysis": True,
        "mica_engine_spyware_enabled": [
            {
                "name": "HTTP Command and Control detector",
                "inline_policy_action": "alert"
            }
        ],
        "rules": [
            {
                "name": "critical-threats",
                "severity": ["critical", "high"],
                "category": "command-and-control",
                "action": {"reset_both": {}}
            },
            {
                "name": "medium-threats",
                "severity": ["medium"],
                "category": "spyware",
                "action": {"alert": {}}
            }
        ]
    }

    new_profile = profiles.create(profile_data)
    print(f"Created profile: {new_profile.name}")

except InvalidObjectError as e:
    print(f"Invalid profile data: {e.message}")
    print(f"Error code: {e.error_code}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Anti-Spyware Profiles

Use the `get()` method to retrieve an anti-spyware profile by its ID.

<div class="termy">

<!-- termynal -->

```python
try:
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    profile = profiles.get(profile_id)
    print(f"Profile Name: {profile.name}")
    print(f"Number of Rules: {len(profile.rules)}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
```

</div>

## Updating Anti-Spyware Profiles

> There is currently a requirement by the SCM API to have at least four characters for objects like `threat_name`, but
> this unfortunately conflicts with defaults like `any`. The SDK will conform to the API, but note that this affects
> methods like `update()` from being able to edit existing rules that have attributes with values of `any`. Sorry :'(

The `update()` method allows you to modify existing anti-spyware profiles using Pydantic models.

<div class="termy">

<!-- termynal -->

```python
try:
    fetched_profile = profiles.fetch(folder='Texas', name='advanced-profile')
    fetched_profile.description = 'updated description'

    updated_profile = profiles.update(fetched_profile)
    print(f"Updated profile: {updated_profile.name}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting Anti-Spyware Profiles

Use the `delete()` method to remove an anti-spyware profile.

<div class="termy">

<!-- termynal -->

```python
try:
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    profiles.delete(profile_id)
    print("Profile deleted successfully")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Profile still in use: {e.message}")
```

</div>

## Listing Anti-Spyware Profiles

The `list()` method retrieves multiple anti-spyware profiles with optional filtering. You can filter the results using
the following kwargs:

- `rules`: List[str] - Filter by rule names (e.g., ['block-critical', 'medium-threats'])

<div class="termy">

<!-- termynal -->

```python
try:
    # List all profiles in a folder
    existing_profiles = profiles.list(folder="Texas")

    # List profiles containing specific rules
    critical_profiles = profiles.list(
        folder="Texas",
        rules=['block-critical']
    )

    # List profiles with multiple rule matches
    filtered_profiles = profiles.list(
        folder="Texas",
        rules=['block-critical', 'medium-threats']
    )

    # Print the results
    for profile in existing_profiles:
        print(f"Name: {profile.name}")
        print(f"Rules: {len(profile.rules)}")
        for rule in profile.rules:
            print(f"  - {rule.name}")
        print("---")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching Anti-Spyware Profiles

The `fetch()` method retrieves a single anti-spyware profile by name from a specific container, returning a Pydantic
model.

<div class="termy">

<!-- termynal -->

```python
try:
    profile = profiles.fetch(
        name="basic-profile",
        folder="Texas"
    )

    print(f"Found profile: {profile.name}")
    print(f"Current rules: {len(profile.rules)}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an anti-spyware profile with proper error handling:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import AntiSpywareProfile
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

    # Initialize anti-spyware profile object
    profiles = AntiSpywareProfile(client)

    try:
        # Create new profile
        create_data = {
            "name": "test-profile",
            "description": "Test anti-spyware profile",
            "folder": "Texas",
            "rules": [
                {
                    "name": "test-rule",
                    "severity": ["critical"],
                    "category": "spyware",
                    "action": {"alert": {}}
                }
            ]
        }

        new_profile = profiles.create(create_data)
        print(f"Created profile: {new_profile.name}")

        # Fetch the profile by name
        try:
            fetched_profile = profiles.fetch(
                name="test-profile",
                folder="Texas"
            )
            print(f"Found profile: {fetched_profile.name}")

            # Update the profile using Pydantic model
            fetched_profile.description = "Updated test profile"
            fetched_profile.rules.append({
                "name": "additional-rule",
                "severity": ["high"],
                "category": "command-and-control",
                "action": {"reset_both": {}}
            })

            updated_profile = profiles.update(fetched_profile)
            print(f"Updated profile: {updated_profile.name}")
            print(f"New description: {updated_profile.description}")

        except NotFoundError as e:
            print(f"Profile not found: {e.message}")

        # Clean up
        try:
            profiles.delete(new_profile.id)
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

## Full script examples

Refer to the [examples](../../../../examples/scm/config/security_services) directory.

## Related Models

- [AntiSpywareProfileRequestModel](../../models/security_services/anti_spyware_profile_models.md#Overview)
- [AntiSpywareProfileUpdateModel](../../models/security_services/anti_spyware_profile_models.md#Overview)
- [AntiSpywareProfileResponseModel](../../models/security_services/anti_spyware_profile_models.md#Overview)