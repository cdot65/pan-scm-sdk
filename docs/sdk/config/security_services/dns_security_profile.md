# DNS Security Profile Configuration Object

The `DNSSecurityProfile` class provides functionality to manage DNS Security profiles in Palo Alto Networks' Strata
Cloud Manager.
DNS Security profiles define policies for protecting against DNS-based threats, including botnet domains, malware, and
phishing
attempts.

## Overview

DNS Security profiles in Strata Cloud Manager allow you to:

- Configure actions for different DNS security categories
- Define custom blocklists and allowlists
- Set up sinkhole configurations for malicious domains
- Specify whitelist entries for trusted domains
- Control packet capture and logging behavior
- Organize profiles within folders, snippets, or devices

## Methods

| Method     | Description                                       |
|------------|---------------------------------------------------|
| `create()` | Creates a new DNS Security profile                |
| `get()`    | Retrieves a DNS Security profile by ID            |
| `update()` | Updates an existing DNS Security profile          |
| `delete()` | Deletes a DNS Security profile                    |
| `list()`   | Lists DNS Security profiles with optional filters |
| `fetch()`  | Retrieves a single DNS Security profile by name   |

## Creating DNS Security Profiles

The `create()` method allows you to define new DNS Security profiles. You must specify a name and exactly one container
type (folder, snippet, or device).

**Example: Basic Profile with DNS Security Categories**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "basic-profile",
    "description": "Basic DNS Security profile",
    "folder": "Shared",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "grayware",
                "action": "block",
                "log_level": "medium",
                "packet_capture": "single-packet"
            }
        ]
    }
}

new_profile = dns_security_profile.create(profile_data)
print(f"Created profile: {new_profile['name']}")
```

</div>

**Example: Profile with Custom Lists and Sinkhole**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "advanced-profile",
    "description": "Advanced DNS Security profile",
    "folder": "Shared",
    "botnet_domains": {
        "lists": [
            {
                "name": "custom-blocklist",
                "action": {"block": {}},
                "packet_capture": "single-packet"
            }
        ],
        "sinkhole": {
            "ipv4_address": "pan-sinkhole-default-ip",
            "ipv6_address": "::1"
        }
    }
}

new_profile = dns_security_profile.create(profile_data)
print(f"Created profile: {new_profile['name']}")
```

</div>

## Getting DNS Security Profiles

Use the `get()` method to retrieve a DNS Security profile by its ID.

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile = dns_security_profile.get(profile_id)
print(f"Profile Name: {profile['name']}")
print(f"Description: {profile['description']}")
```

</div>

## Updating DNS Security Profiles

The `update()` method allows you to modify existing DNS Security profiles.

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "description": "Updated DNS Security profile",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "malware",
                "action": "sinkhole",
                "log_level": "critical",
                "packet_capture": "extended-capture"
            }
        ]
    }
}

updated_profile = dns_security_profile.update(update_data)
print(f"Updated profile: {updated_profile['name']}")
```

</div>

## Deleting DNS Security Profiles

Use the `delete()` method to remove a DNS Security profile.

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
dns_security_profile.delete(profile_id)
print("Profile deleted successfully")
```

</div>

## Listing DNS Security Profiles

The `list()` method retrieves multiple DNS Security profiles with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all profiles in a folder
profiles = dns_security_profile.list(
    folder="Shared",
    limit=10,
    offset=0
)

for profile in profiles:
    print(f"Name: {profile['name']}")

# List profiles with name filter
filtered_profiles = dns_security_profile.list(
    folder="Shared",
    name="basic"
)

for profile in filtered_profiles:
    print(f"Filtered profile: {profile['name']}")
```

</div>

## Fetching DNS Security Profiles

The `fetch()` method retrieves a single DNS Security profile by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
profile = dns_security_profile.fetch(
    name="basic-profile",
    folder="Shared"
)

print(f"Found profile: {profile['name']}")
print(f"Current settings: {profile['botnet_domains']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a DNS Security profile:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DNSSecurityProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize DNS Security profile object
dns_security_profile = DNSSecurityProfile(client)

# Create new profile
create_data = {
    "name": "test-profile",
    "description": "Test DNS Security profile",
    "folder": "Shared",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "grayware",
                "action": "block",
                "log_level": "medium"
            }
        ]
    }
}

new_profile = dns_security_profile.create(create_data)
print(f"Created profile: {new_profile['name']}")

# Fetch the profile by name
fetched_profile = dns_security_profile.fetch(
    name="test-profile",
    folder="Shared"
)

# Modify the fetched profile
fetched_profile["description"] = "Updated test profile"
fetched_profile["botnet_domains"]["dns_security_categories"].append({
    "name": "malware",
    "action": "sinkhole",
    "log_level": "critical",
    "packet_capture": "extended-capture"
})

# Update using the modified object
updated_profile = dns_security_profile.update(fetched_profile)
print(f"Updated profile: {updated_profile['name']}")
print(f"New description: {updated_profile['description']}")

# List all profiles
profiles = dns_security_profile.list(folder="Shared")
for profile in profiles:
    print(f"Listed profile: {profile['name']}")

# Clean up
dns_security_profile.delete(new_profile['id'])
print("Profile deleted successfully")
```

</div>

## Related Models

- [DNSSecurityProfileCreateModel](../../models/security/dns_security_profile_models.md#dnssecurityprofilecreatemodel)
- [DNSSecurityProfileUpdateModel](../../models/security/dns_security_profile_models.md#dnssecurityprofileupdatemodel)
- [DNSSecurityProfileResponseModel](../../models/security/dns_security_profile_models.md#dnssecurityprofileresponsemodel)