# DNS Security Profile Configuration Object

The `DNSSecurityProfile` class provides functionality to manage DNS Security profiles in Palo Alto Networks' Strata
Cloud Manager. DNS Security profiles define policies for protecting against DNS-based threats, including botnet domains,
malware, and phishing attempts.

## Overview

DNS Security profiles in Strata Cloud Manager allow you to:

- Configure actions for different DNS security categories
- Define custom blocklists and allowlists
- Set up sinkhole configurations for malicious domains
- Specify whitelist entries for trusted domains
- Control packet capture and logging behavior
- Organize profiles within folders, snippets, or devices

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during profile
management.

## Methods

| Method     | Description                                       |
|------------|---------------------------------------------------|
| `create()` | Creates a new DNS Security profile                |
| `get()`    | Retrieves a DNS Security profile by ID            |
| `update()` | Updates an existing DNS Security profile          |
| `delete()` | Deletes a DNS Security profile                    |
| `list()`   | Lists DNS Security profiles with optional filters |
| `fetch()`  | Retrieves a single DNS Security profile by name   |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when profile data is invalid or malformed
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
- `SessionTimeoutError`: When the API session times out

## Creating DNS Security Profiles

The `create()` method allows you to create new DNS Security profiles with proper error handling.

**Example: Basic Profile with DNS Security Categories**

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DNSSecurityProfile
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

dns_security_profiles = DNSSecurityProfile(client)

try:
    profile_data = {
        'name': 'new-test',
        'description': 'Best practice dns security profile',
        'botnet_domains': {
            'dns_security_categories': [
                {
                    'name': 'pan-dns-sec-grayware',
                    'action': 'sinkhole',
                    'log_level': 'default',
                    'packet_capture': 'disable'
                },
                {
                    'name': 'pan-dns-sec-malware',
                    'action': 'sinkhole',
                    'log_level': 'default',
                    'packet_capture': 'disable'
                }
            ],
            'sinkhole': {
                'ipv4_address': 'pan-sinkhole-default-ip',
                'ipv6_address': '::1'
            }
        },
        'folder': 'Texas'
    }

    new_profile = dns_security_profiles.create(profile_data)
    print(f"Created profile: {new_profile.name}")

except NameNotUniqueError as e:
    print(f"Profile name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid profile data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

**Example: Profile with Custom Lists and Sinkhole**

<div class="termy">

<!-- termynal -->

```python
try:
    profile_data = {
        'name': 'test-profile',
        'description': 'Custom DNS security profile',
        'botnet_domains': {
            'lists': [
                {
                    'name': 'default-paloalto-dns',
                    'packet_capture': 'single-packet',
                    'action': {
                        'sinkhole': {}
                    }
                }
            ],
            'sinkhole': {
                'ipv4_address': 'pan-sinkhole-default-ip',
                'ipv6_address': '::1'
            },
            'whitelist': [
                {
                    'name': 'trusted-domain.com',
                    'description': 'Trusted domain'
                }
            ]
        },
        'folder': 'Texas'
    }

    new_profile = dns_security_profiles.create(profile_data)
    print(f"Created profile: {new_profile.name}")

except InvalidObjectError as e:
    print(f"Invalid profile data: {e.message}")
    print(f"Error code: {e.error_code}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting DNS Security Profiles

Use the `get()` method to retrieve a DNS Security profile by its ID.

<div class="termy">

<!-- termynal -->

```python
try:
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    profile = dns_security_profiles.get(profile_id)
    print(f"Profile Name: {profile.name}")
    print(f"Description: {profile.description}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
```

</div>

## Updating DNS Security Profiles

The `update()` method allows you to modify existing DNS Security profiles.

<div class="termy">

<!-- termynal -->

```python
try:
    profile = dns_security_profiles.fetch(folder='Texas', name='test dns security')
    profile['description'] = "Updated description"

    updated_profile = dns_security_profiles.update(profile)
    print(f"Updated profile: {updated_profile.name}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting DNS Security Profiles

Use the `delete()` method to remove a DNS Security profile.

<div class="termy">

<!-- termynal -->

```python
try:
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    dns_security_profiles.delete(profile_id)
    print("Profile deleted successfully")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Profile still in use: {e.message}")
```

</div>

## Listing DNS Security Profiles

The `list()` method retrieves multiple DNS Security profiles with optional filtering. You can filter the results using
the following kwargs:

- `dns_security_categories`: List[str] - Filter by DNS security category names (
  e.g., ['pan-dns-sec-malware', 'pan-dns-sec-phishing'])

<div class="termy">

<!-- termynal -->

```python
try:
    # List all profiles in a folder
    profiles = dns_security_profiles.list(folder="Texas")

    # List profiles with specific DNS security categories
    malware_profiles = dns_security_profiles.list(
        folder="Texas",
        dns_security_categories=['pan-dns-sec-malware']
    )

    # List profiles with multiple category matches
    filtered_profiles = dns_security_profiles.list(
        folder="Texas",
        dns_security_categories=['pan-dns-sec-malware', 'pan-dns-sec-phishing']
    )

    # Print the results
    for profile in profiles:
        print(f"Name: {profile.name}")
        if profile.botnet_domains and profile.botnet_domains.dns_security_categories:
            print("Categories:", [cat.name for cat in profile.botnet_domains.dns_security_categories])

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching DNS Security Profiles

The `fetch()` method retrieves a single DNS Security profile by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
try:
    profile = dns_security_profiles.fetch(
        name="test asdf",
        folder="Texas"
    )

    print(f"Found profile: {profile['name']}")
    print(f"Current settings: {profile['botnet_domains']}")

except NotFoundError as e:
    print(f"Profile not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a DNS Security profile with proper error handling:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DNSSecurityProfile
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

    # Initialize DNS Security profile object
    dns_security_profiles = DNSSecurityProfile(client)

    try:
        # Create new profile
        profile_data = {
            'name': 'test-profile',
            'description': 'Test DNS security profile',
            'botnet_domains': {
                'dns_security_categories': [
                    {
                        'name': 'pan-dns-sec-malware',
                        'action': 'sinkhole',
                        'log_level': 'default',
                        'packet_capture': 'disable'
                    }
                ],
                'sinkhole': {
                    'ipv4_address': 'pan-sinkhole-default-ip',
                    'ipv6_address': '::1'
                }
            },
            'folder': 'Texas'
        }

        new_profile = dns_security_profiles.create(profile_data)
        print(f"Created profile: {new_profile.name}")

        # Fetch and update the profile
        try:
            fetched_profile = dns_security_profiles.fetch(
                name="test-profile",
                folder="Texas"
            )
            print(f"Found profile: {fetched_profile['name']}")

            # Update the profile
            fetched_profile["description"] = "Updated test profile"
            updated_profile = dns_security_profiles.update(fetched_profile)
            print(f"Updated description: {updated_profile.description}")

        except NotFoundError as e:
            print(f"Profile not found: {e.message}")

        # Clean up
        try:
            dns_security_profiles.delete(new_profile.id)
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

- [DNSSecurityProfileCreateModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [DNSSecurityProfileUpdateModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [DNSSecurityProfileResponseModel](../../models/security_services/dns_security_profile_models.md#Overview)