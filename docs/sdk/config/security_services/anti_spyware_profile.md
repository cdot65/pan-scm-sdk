# Anti-Spyware Profile Configuration Object

The `AntiSpywareProfile` class provides functionality to manage anti-spyware profiles in Palo Alto Networks' Strata
Cloud Manager.
Anti-spyware profiles define threat detection and prevention settings for identifying and blocking spyware,
command-and-control
traffic, and other malicious activities.

## Overview

Anti-spyware profiles in Strata Cloud Manager allow you to:

- Define rules for different threat severities and categories
- Configure actions for detected threats (alert, block, reset connections)
- Set up threat exceptions for specific cases
- Enable cloud-based inline analysis
- Configure MICA engine spyware detection
- Organize profiles within folders, snippets, or devices

## Methods

| Method     | Description                                         |
|------------|-----------------------------------------------------|
| `create()` | Creates a new anti-spyware profile                  |
| `get()`    | Retrieves an anti-spyware profile by ID             |
| `update()` | Updates an existing anti-spyware profile            |
| `delete()` | Deletes an anti-spyware profile                     |
| `list()`   | Lists anti-spyware profiles with optional filtering |
| `fetch()`  | Retrieves a single anti-spyware profile by name     |

## Creating Anti-Spyware Profiles

The `create()` method allows you to define new anti-spyware profiles. You must specify a name, rules, and exactly one
container type (folder, snippet, or device).

**Example: Basic Profile with Single Rule**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "basic-profile",
    "description": "Basic anti-spyware profile",
    "folder": "Shared",
    "rules": [
        {
            "name": "block-critical",
            "severity": ["critical"],
            "category": "spyware",
            "action": {"block_ip": {"track_by": "source", "duration": 300}}
        }
    ]
}

new_profile = anti_spyware_profile.create(profile_data)
print(f"Created profile: {new_profile['name']}")
```

</div>

**Example: Profile with Multiple Rules and MICA Engine**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "advanced-profile",
    "description": "Advanced anti-spyware profile",
    "folder": "Shared",
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

new_profile = anti_spyware_profile.create(profile_data)
print(f"Created profile: {new_profile['name']}")
```

</div>

## Getting Anti-Spyware Profiles

Use the `get()` method to retrieve an anti-spyware profile by its ID.

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile = anti_spyware_profile.get(profile_id)
print(f"Profile Name: {profile['name']}")
print(f"Number of Rules: {len(profile['rules'])}")
```

</div>

## Updating Anti-Spyware Profiles

The `update()` method allows you to modify existing anti-spyware profiles.

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "description": "Updated profile description",
    "folder": "Shared",
    "rules": [
        {
            "name": "updated-rule",
            "severity": ["critical", "high"],
            "category": "spyware",
            "action": {"reset_both": {}}
        }
    ],
    "threat_exception": [
        {
            "name": "exception-1",
            "packet_capture": "single-packet",
            "action": {"allow": {}},
            "exempt_ip": [{"name": "10.0.0.1"}]
        }
    ]
}

updated_profile = anti_spyware_profile.update(update_data)
print(f"Updated profile: {updated_profile['name']}")
```

</div>

## Deleting Anti-Spyware Profiles

Use the `delete()` method to remove an anti-spyware profile.

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
anti_spyware_profile.delete(profile_id)
print("Profile deleted successfully")
```

</div>

## Listing Anti-Spyware Profiles

The `list()` method retrieves multiple anti-spyware profiles with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all profiles in a folder
profiles = anti_spyware_profile.list(
    folder="Shared",
    limit=10,
    offset=0
)

for profile in profiles:
    print(f"Name: {profile['name']}")
    print(f"Rules: {len(profile['rules'])}")
    print("---")

# List profiles with name filter
filtered_profiles = anti_spyware_profile.list(
    folder="Shared",
    name="basic"
)

for profile in filtered_profiles:
    print(f"Filtered profile: {profile['name']}")
```

</div>

## Fetching Anti-Spyware Profiles

The `fetch()` method retrieves a single anti-spyware profile by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
profile = anti_spyware_profile.fetch(
    name="basic-profile",
    folder="Shared"
)

print(f"Found profile: {profile['name']}")
print(f"Current rules: {len(profile['rules'])}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an anti-spyware profile:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import AntiSpywareProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize anti-spyware profile object
anti_spyware_profile = AntiSpywareProfile(client)

# Create new profile
create_data = {
    "name": "test-profile",
    "description": "Test anti-spyware profile",
    "folder": "Shared",
    "rules": [
        {
            "name": "test-rule",
            "severity": ["critical"],
            "category": "spyware",
            "action": {"alert": {}}
        }
    ]
}

new_profile = anti_spyware_profile.create(create_data)
print(f"Created profile: {new_profile['name']}")

# Fetch the profile by name
fetched_profile = anti_spyware_profile.fetch(
    name="test-profile",
    folder="Shared"
)

# Modify the fetched profile
fetched_profile["description"] = "Updated test profile"
fetched_profile["rules"].append({
    "name": "additional-rule",
    "severity": ["high"],
    "category": "command-and-control",
    "action": {"reset_both": {}}
})

# Update using the modified object
updated_profile = anti_spyware_profile.update(fetched_profile)
print(f"Updated profile: {updated_profile['name']}")
print(f"New description: {updated_profile['description']}")

# List all profiles
profiles = anti_spyware_profile.list(folder="Shared")
for profile in profiles:
    print(f"Listed profile: {profile['name']}")

# Clean up
anti_spyware_profile.delete(new_profile['id'])
print("Profile deleted successfully")
```

</div>

## Related Models

- [AntiSpywareProfileRequestModel](../../models/security/anti_spyware_profile_models.md#antispywareprofilerequest)
- [AntiSpywareProfileUpdateModel](../../models/security/anti_spyware_profile_models.md#antispywareprofileupdate)
- [AntiSpywareProfileResponseModel](../../models/security/anti_spyware_profile_models.md#antispywareprofileresponse)