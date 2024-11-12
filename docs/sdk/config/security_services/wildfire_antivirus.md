# WildFire Antivirus Profile Configuration Object

The `WildfireAntivirusProfile` class provides functionality to manage WildFire antivirus profiles in Palo Alto Networks'
Strata
Cloud Manager. WildFire profiles define settings for malware analysis, file inspection, and threat detection using both
cloud
and local analysis capabilities.

## Overview

WildFire antivirus profiles in Strata Cloud Manager allow you to:

- Configure rules for file analysis in WildFire cloud
- Define direction-based scanning (upload, download, or both)
- Specify application and file type filters
- Set up MLAV (Machine Learning Anti-Virus) exceptions
- Configure threat exceptions for known cases
- Organize profiles within folders, snippets, or devices

## Methods

| Method     | Description                                             |
|------------|---------------------------------------------------------|
| `create()` | Creates a new WildFire antivirus profile                |
| `get()`    | Retrieves a WildFire antivirus profile by ID            |
| `update()` | Updates an existing WildFire antivirus profile          |
| `delete()` | Deletes a WildFire antivirus profile                    |
| `list()`   | Lists WildFire antivirus profiles with optional filters |
| `fetch()`  | Retrieves a single WildFire antivirus profile by name   |

## Creating WildFire Antivirus Profiles

The `create()` method allows you to define new WildFire antivirus profiles. You must specify a name, rules, and exactly
one
container type (folder, snippet, or device).

**Example: Basic Profile with Single Rule**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "basic-profile",
    "description": "Basic WildFire profile",
    "folder": "Shared",
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
print(f"Created profile: {new_profile['name']}")
```

</div>

**Example: Profile with Multiple Rules and Exceptions**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "advanced-profile",
    "description": "Advanced WildFire profile",
    "folder": "Shared",
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
print(f"Created profile: {new_profile['name']}")
```

</div>

## Getting WildFire Antivirus Profiles

Use the `get()` method to retrieve a WildFire antivirus profile by its ID.

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile = wildfire_antivirus_profile.get(profile_id)
print(f"Profile Name: {profile['name']}")
print(f"Number of Rules: {len(profile['rules'])}")
```

</div>

## Updating WildFire Antivirus Profiles

The `update()` method allows you to modify existing WildFire antivirus profiles.

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
            "direction": "both",
            "analysis": "public-cloud",
            "application": ["any"],
            "file_type": ["any"]
        }
    ],
    "threat_exception": [
        {
            "name": "exception1",
            "notes": "Known false positive"
        }
    ]
}

updated_profile = wildfire_antivirus_profile.update(update_data)
print(f"Updated profile: {updated_profile['name']}")
```

</div>

## Deleting WildFire Antivirus Profiles

Use the `delete()` method to remove a WildFire antivirus profile.

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
wildfire_antivirus_profile.delete(profile_id)
print("Profile deleted successfully")
```

</div>

## Listing WildFire Antivirus Profiles

The `list()` method retrieves multiple WildFire antivirus profiles with optional filtering. You can filter the results
using the
following kwargs:

- `rules`: List[str] - Filter by rule names (e.g., ['basic-rule', 'upload-rule'])

<div class="termy">

<!-- termynal -->

```python
# List all profiles in a folder
profiles = wildfire_antivirus_profile.list(
    folder="Shared"
)

# List profiles with specific rules
rule_profiles = wildfire_antivirus_profile.list(
    folder="Shared",
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
```

</div>

## Fetching WildFire Antivirus Profiles

The `fetch()` method retrieves a single WildFire antivirus profile by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
profile = wildfire_antivirus_profile.fetch(
    name="basic-profile",
    folder="Shared"
)

print(f"Found profile: {profile['name']}")
print(f"Current rules: {len(profile['rules'])}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a WildFire antivirus profile:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import WildfireAntivirusProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize WildFire antivirus profile object
wildfire_antivirus_profile = WildfireAntivirusProfile(client)

# Create new profile
create_data = {
    "name": "test-profile",
    "description": "Test WildFire profile",
    "folder": "Shared",
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
print(f"Created profile: {new_profile['name']}")

# Fetch the profile by name
fetched_profile = wildfire_antivirus_profile.fetch(
    name="test-profile",
    folder="Shared"
)

# Modify the fetched profile
fetched_profile["description"] = "Updated test profile"
fetched_profile["rules"].append({
    "name": "additional-rule",
    "direction": "upload",
    "analysis": "private-cloud",
    "application": ["ftp"],
    "file_type": ["any"]
})

# Update using the modified object
updated_profile = wildfire_antivirus_profile.update(fetched_profile)
print(f"Updated profile: {updated_profile['name']}")
print(f"New description: {updated_profile['description']}")

# List all profiles
profiles = wildfire_antivirus_profile.list(folder="Shared")
for profile in profiles:
    print(f"Listed profile: {profile['name']}")

# Clean up
wildfire_antivirus_profile.delete(new_profile['id'])
print("Profile deleted successfully")
```

</div>

## Related Models

- [WildfireAntivirusProfileCreateModel](../../models/security/wildfire_antivirus_profile_models.md#wildfireantivirusprofilecreatemodel)
- [WildfireAntivirusProfileUpdateModel](../../models/security/wildfire_antivirus_profile_models.md#wildfireantivirusprofileupdatemodel)
- [WildfireAntivirusProfileResponseModel](../../models/security/wildfire_antivirus_profile_models.md#wildfireantivirusprofileresponsemodel)