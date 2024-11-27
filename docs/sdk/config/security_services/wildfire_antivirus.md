# WildFire Antivirus Profile Configuration Object

The `WildfireAntivirusProfile` class provides functionality to manage WildFire antivirus profiles in Palo Alto Networks'
Strata Cloud Manager. WildFire profiles define settings for malware analysis, file inspection, and threat detection
using both
cloud and local analysis capabilities.

## Overview

WildFire antivirus profiles in Strata Cloud Manager allow you to:

- Configure rules for file analysis in WildFire cloud
- Define direction-based scanning (upload, download, or both)
- Specify application and file type filters
- Set up MLAV (Machine Learning Anti-Virus) exceptions
- Configure threat exceptions for known cases
- Organize profiles within folders, snippets, or devices

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during profile
management.

## Methods

| Method     | Description                                             |
|------------|---------------------------------------------------------|
| `create()` | Creates a new WildFire antivirus profile                |
| `get()`    | Retrieves a WildFire antivirus profile by ID            |
| `update()` | Updates an existing WildFire antivirus profile          |
| `delete()` | Deletes a WildFire antivirus profile                    |
| `list()`   | Lists WildFire antivirus profiles with optional filters |
| `fetch()`  | Retrieves a single WildFire antivirus profile by name   |

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

## Creating WildFire Antivirus Profiles

The `create()` method allows you to create new WildFire antivirus profiles with proper error handling.

**Example: Basic Profile with Single Rule**

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import WildfireAntivirusProfile
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

wildfire_antivirus_profile = WildfireAntivirusProfile(client)

try:
    profile_data = {
        "name": "basic-profile",
        "description": "Basic WildFire profile",
        "folder": "Texas",
        "rules": [
            {
                "name": "basic-rule",
                "direction": "both",
                "analysis": "public-cloud",
                "application": ["web-browsing"],
                "file_type": ["pdf", "pe"]
            }
        ]
    }

    new_profile = wildfire_antivirus_profile.create(profile_data)
    print(f"Created profile: {new_profile.name}")

except NameNotUniqueError as e:
    print(f"Profile name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid profile data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

**Example: Profile with Multiple Rules and Exceptions**

<div class="termy">

<!-- termynal -->

```python
try:
    profile_data = {
        "name": "advanced-profile",
        "description": "Advanced WildFire profile",
        "folder": "Texas",
        "packet_capture": True,
        "rules": [
            {
                "name": "upload-rule",
                "direction": "upload",
                "analysis": "private-cloud",
                "application": ["ftp", "sftp"],
                "file_type": ["any"]
            },
            {
                "name": "download-rule",
                "direction": "download",
                "analysis": "public-cloud",
                "application": ["web-browsing"],
                "file_type": ["pdf", "doc"]
            }
        ],
        "mlav_exception": [
            {
                "name": "exception1",
                "filename": "trusted.exe",
                "description": "Trusted application"
            }
        ]
    }

    new_profile = wildfire_antivirus_profile.create(profile_data)
    print(f"Created profile: {new_profile.name}")

except InvalidObjectError as e:
    print(f"Invalid profile data: {e.message}")
    print(f"Error code: {e.error_code}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting WildFire Antivirus Profiles

Use the `get()` method to retrieve a WildFire antivirus profile by its ID.

<div class="termy">

<!-- termynal -->

```python
try:
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    profile = wildfire_antivirus_profile.get(profile_id)
    print(f"Profile Name: {profile.name}")
    print(f"Number of Rules: {len(profile.rules)}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid profile ID: {e.message}")
```

</div>

## Updating WildFire Antivirus Profiles

The `update()` method allows you to modify existing WildFire antivirus profiles using Pydantic models.

<div class="termy">

<!-- termynal -->

```python
try:
    # First fetch the existing profile
    profile = wildfire_antivirus_profile.fetch(
        name="basic-profile",
        folder="Texas"
    )

    # Update the profile attributes using Pydantic model
    profile.description = "Updated profile description"
    profile.rules[0].direction = "both"
    profile.rules[0].application = ["any"]
    profile.rules[0].file_type = ["any"]

    updated_profile = wildfire_antivirus_profile.update(profile)
    print(f"Updated profile: {updated_profile.name}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting WildFire Antivirus Profiles

Use the `delete()` method to remove a WildFire antivirus profile.

<div class="termy">

<!-- termynal -->

```python
try:
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    wildfire_antivirus_profile.delete(profile_id)
    print("Profile deleted successfully")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Profile still in use: {e.message}")
```

</div>

## Listing WildFire Antivirus Profiles

The `list()` method retrieves multiple WildFire antivirus profiles with optional filtering. You can filter the results
using the following kwargs:

- `rules`: List[str] - Filter by rule names (e.g., ['basic-rule', 'upload-rule'])

<div class="termy">

<!-- termynal -->

```python
try:
    # List all profiles in a folder
    profiles = wildfire_antivirus_profile.list(
        folder="Texas"
    )

    # List profiles with specific rules
    rule_profiles = wildfire_antivirus_profile.list(
        folder="Texas",
        rules=['basic-rule', 'upload-rule']
    )

    # Print the results
    for profile in profiles:
        print(f"Name: {profile.name}")
        for rule in profile.rules:
            print(f"  Rule: {rule.name}")
            print(f"  Direction: {rule.direction}")
            print(f"  Analysis: {rule.analysis}")
        print("---")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching WildFire Antivirus Profiles

The `fetch()` method retrieves a single WildFire antivirus profile by name from a specific container, returning a
Pydantic model.

<div class="termy">

<!-- termynal -->

```python
try:
    profile = wildfire_antivirus_profile.fetch(
        name="basic-profile",
        folder="Texas"
    )

    print(f"Found profile: {profile.name}")
    print(f"Current rules: {len(profile.rules)}")
    print(f"Description: {profile.description}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a WildFire antivirus profile with proper error handling:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import WildfireAntivirusProfile
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

    # Initialize WildFire antivirus profile object
    wildfire_antivirus_profile = WildfireAntivirusProfile(client)

    try:
        # Create new profile
        create_data = {
            "name": "test-profile",
            "description": "Test WildFire profile",
            "folder": "Texas",
            "rules": [
                {
                    "name": "test-rule",
                    "direction": "both",
                    "analysis": "public-cloud",
                    "application": ["web-browsing"],
                    "file_type": ["pdf", "pe"]
                }
            ]
        }

        new_profile = wildfire_antivirus_profile.create(create_data)
        print(f"Created profile: {new_profile.name}")

        # Fetch and update the profile
        try:
            fetched_profile = wildfire_antivirus_profile.fetch(
                name="test-profile",
                folder="Texas"
            )
            print(f"Found profile: {fetched_profile.name}")

            # Update the profile using Pydantic model
            fetched_profile.description = "Updated test profile"
            updated_profile = wildfire_antivirus_profile.update(fetched_profile)
            print(f"Updated description: {updated_profile.description}")

        except NotFoundError as e:
            print(f"Profile not found: {e.message}")

        # Clean up
        try:
            wildfire_antivirus_profile.delete(new_profile.id)
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

- [WildfireAntivirusProfileCreateModel](../../models/security_services/wildfire_antivirus_profile_models.md#Overview)
- [WildfireAntivirusProfileUpdateModel](../../models/security_services/wildfire_antivirus_profile_models.md#Overview)
- [WildfireAntivirusProfileResponseModel](../../models/security_services/wildfire_antivirus_profile_models.md#Overview)