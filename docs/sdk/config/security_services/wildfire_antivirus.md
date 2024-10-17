# WildFire Antivirus Profile Configuration Object

The `WildfireAntivirusProfile` class is used to manage WildFire Antivirus Profile objects in the Strata Cloud Manager.
It provides methods to create, retrieve, update, delete, and list WildFire Antivirus Profile objects.

---

## Importing the WildfireAntivirusProfile Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.security import WildfireAntivirusProfile
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> WildfireAntivirusProfileResponseModel`

Creates a new WildFire Antivirus Profile object.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the WildFire Antivirus Profile object data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "test_profile",
    "description": "Created via pan-scm-sdk",
    "folder": "Prisma Access",
    "rules": [
        {
            "name": "rule1",
            "direction": "both",
            "analysis": "public-cloud"
        }
    ]
}

new_profile = wildfire_antivirus_profile.create(profile_data)
print(f"Created WildFire Antivirus Profile with ID: {new_profile.id}")
```

</div>

### `get(object_id: str) -> WildfireAntivirusProfileResponseModel`

Retrieves a WildFire Antivirus Profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the WildFire Antivirus Profile object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile_object = wildfire_antivirus_profile.get(profile_id)
print(f"Profile Name: {profile_object.name}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> WildfireAntivirusProfileResponseModel`

Updates an existing WildFire Antivirus Profile object.

**Parameters:**

- `object_id` (str): The UUID of the WildFire Antivirus Profile object.
- `data` (Dict[str, Any]): A dictionary containing the updated WildFire Antivirus Profile data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated description",
    "rules": [
        {
            "name": "updated_rule",
            "direction": "upload",
            "analysis": "private-cloud"
        }
    ]
}

updated_profile = wildfire_antivirus_profile.update(profile_id, update_data)
print(f"Updated WildFire Antivirus Profile with ID: {updated_profile.id}")
```

</div>

### `delete(object_id: str) -> None`

Deletes a WildFire Antivirus Profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the WildFire Antivirus Profile object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
wildfire_antivirus_profile.delete(profile_id)
print(f"Deleted WildFire Antivirus Profile with ID: {profile_id}")
```

</div>

###
`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, offset: Optional[int] = None, limit: Optional[int] = None, name: Optional[str] = None, **filters) -> List[WildfireAntivirusProfileResponseModel]`

Lists WildFire Antivirus Profile objects, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list profiles from.
- `snippet` (Optional[str]): The snippet to list profiles from.
- `device` (Optional[str]): The device to list profiles from.
- `offset` (Optional[int]): The pagination offset.
- `limit` (Optional[int]): The pagination limit.
- `name` (Optional[str]): Filter profiles by name.
- `**filters`: Additional filters.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profiles = wildfire_antivirus_profile.list(folder='Prisma Access', limit=10)

for profile in profiles:
    print(f"Profile Name: {profile.name}, ID: {profile.id}")
```

</div>

---

## Usage Examples

### Example 1: Creating a WildFire Antivirus Profile

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "example_profile",
    "description": "Example WildFire Antivirus Profile",
    "folder": "Prisma Access",
    "packet_capture": True,
    "rules": [
        {
            "name": "rule1",
            "direction": "both",
            "analysis": "public-cloud",
            "application": ["web-browsing", "ssl"],
            "file_type": ["pe", "pdf"]
        }
    ]
}

new_profile = wildfire_antivirus_profile.create(profile_data)
print(f"Created profile: {new_profile.name} with ID: {new_profile.id}")
```

</div>

### Example 2: Updating a WildFire Antivirus Profile

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated WildFire Antivirus Profile",
    "packet_capture": False,
    "rules": [
        {
            "name": "updated_rule",
            "direction": "upload",
            "analysis": "private-cloud",
            "application": ["any"],
            "file_type": ["any"]
        }
    ]
}

updated_profile = wildfire_antivirus_profile.update(new_profile.id, update_data)
print(f"Updated profile: {updated_profile.name}")
```

</div>

### Example 3: Listing WildFire Antivirus Profiles with Filters

<div class="termy">

<!-- termynal -->

```python
profiles = wildfire_antivirus_profile.list(
    folder='Prisma Access',
    limit=5,
    name='example'
)

for profile in profiles:
    print(f"Profile: {profile.name}, Description: {profile.description}")
```

</div>

### Example 4: Creating a Profile with MLAV Exceptions

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "mlav_exception_profile",
    "folder": "Shared",
    "rules": [
        {
            "name": "default_rule",
            "direction": "both",
            "analysis": "public-cloud"
        }
    ],
    "mlav_exception": [
        {
            "name": "exception1",
            "description": "MLAV exception example",
            "filename": "test_file.exe"
        }
    ]
}

new_profile = wildfire_antivirus_profile.create(profile_data)
print(f"Created profile with MLAV exception: {new_profile.name}")
```

</div>

### Example 5: Updating a Profile with Threat Exceptions

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "threat_exception": [
        {
            "name": "threat_exception1",
            "notes": "Example threat exception"
        }
    ]
}

updated_profile = wildfire_antivirus_profile.update(new_profile.id, update_data)
print(f"Updated profile with threat exception: {updated_profile.name}")
```

</div>

### Example 6: Creating a Profile in a Snippet

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "snippet_profile",
    "description": "Profile in a snippet",
    "snippet": "Example Snippet",
    "rules": [
        {
            "name": "snippet_rule",
            "direction": "download",
            "analysis": "public-cloud"
        }
    ]
}

new_profile = wildfire_antivirus_profile.create(profile_data)
print(f"Created profile in snippet: {new_profile.name}")
```

</div>

---

## Full Example: Creating and Managing a WildFire Antivirus Profile

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import WildfireAntivirusProfile

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create a WildfireAntivirusProfile instance
wildfire_antivirus_profile = WildfireAntivirusProfile(scm)

# Create a new WildFire Antivirus Profile
profile_data = {
    "name": "comprehensive_profile",
    "description": "Comprehensive WildFire Antivirus Profile",
    "folder": "Prisma Access",
    "packet_capture": True,
    "rules": [
        {
            "name": "rule1",
            "direction": "both",
            "analysis": "public-cloud",
            "application": ["web-browsing", "ssl"],
            "file_type": ["pe", "pdf"]
        },
        {
            "name": "rule2",
            "direction": "upload",
            "analysis": "private-cloud",
            "application": ["ftp", "sftp"],
            "file_type": ["any"]
        }
    ],
    "mlav_exception": [
        {
            "name": "mlav_exception1",
            "description": "MLAV exception for specific file",
            "filename": "allowed_file.exe"
        }
    ],
    "threat_exception": [
        {
            "name": "threat_exception1",
            "notes": "Exception for known false positive"
        }
    ]
}

new_profile = wildfire_antivirus_profile.create(profile_data)
print(f"Created comprehensive profile: {new_profile.name} with ID: {new_profile.id}")

# Retrieve the created profile
retrieved_profile = wildfire_antivirus_profile.get(new_profile.id)
print(f"Retrieved profile: {retrieved_profile.name}")

# Update the profile
update_data = {
    "description": "Updated comprehensive WildFire Antivirus Profile",
    "packet_capture": False,
    "rules": [
        {
            "name": "updated_rule",
            "direction": "both",
            "analysis": "public-cloud",
            "application": ["any"],
            "file_type": ["any"]
        }
    ]
}

updated_profile = wildfire_antivirus_profile.update(new_profile.id, update_data)
print(f"Updated profile: {updated_profile.name}")

# List profiles
profiles = wildfire_antivirus_profile.list(folder='Prisma Access', limit=10)
print("List of profiles:")
for profile in profiles:
    print(f"- {profile.name} (ID: {profile.id})")

# Delete the profile
wildfire_antivirus_profile.delete(new_profile.id)
print(f"Deleted profile: {new_profile.name}")
```

</div>

---

## Related Models

- [WildfireAntivirusProfileRequestModel](../../models/security_services/wildfire_antivirus_profile_models.md#WildfireAntivirusProfileRequestModel)
- [WildfireAntivirusProfileResponseModel](../../models/security_services/wildfire_antivirus_profile_models.md#WildfireAntivirusProfileResponseModel)
