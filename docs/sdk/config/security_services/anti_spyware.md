# Anti-Spyware Profile Configuration Object

The `AntiSpywareProfile` class is used to manage anti-spyware profile objects in the Strata Cloud Manager. It provides
methods to create, retrieve, update, delete, and list anti-spyware profile objects.

---

## Creating an API client object

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm

api_client = Scm(
    client_id="this-is-a-placeholder",
    client_secret="this-is-a-placeholder",
    tsg_id="this-is-a-placeholder",
)
```

</div>

## Importing the AntiSpywareProfile Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.security import AntiSpywareProfile

anti_spyware_profile = AntiSpywareProfile(api_client)
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> AntiSpywareProfileResponseModel`

Creates a new anti-spyware profile object.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the anti-spyware profile object data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "test_profile",
    "description": "Test anti-spyware profile",
    "folder": "Prisma Access",
    "rules": [
        {
            "name": "rule1",
            "severity": ["critical", "high"],
            "category": "spyware",
            "action": {"alert": {}}
        }
    ]
}

new_profile = anti_spyware_profile.create(profile_data)
print(f"Created anti-spyware profile with ID: {new_profile.id}")
```

</div>

### `get(object_id: str) -> AntiSpywareProfileResponseModel`

Retrieves an anti-spyware profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the anti-spyware profile object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile_object = anti_spyware_profile.get(profile_id)
print(f"Anti-Spyware Profile Name: {profile_object.name}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> AntiSpywareProfileResponseModel`

Updates an existing anti-spyware profile object.

**Parameters:**

- `object_id` (str): The UUID of the anti-spyware profile object.
- `data` (Dict[str, Any]): A dictionary containing the updated anti-spyware profile data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "name": "Updated name",
    "folder": "Prisma Access",
    "description": "Updated anti-spyware profile description",
    "rules": [
        {
            "name": "updated_rule",
            "severity": ["high"],
            "category": "dns-security",
            "action": {"block_ip": {"track_by": "source", "duration": 300}}
        }
    ]
}

updated_profile = anti_spyware_profile.update(profile_id, update_data)
print(f"Updated anti-spyware profile with ID: {updated_profile.id}")
```

</div>

### `delete(object_id: str) -> None`

Deletes an anti-spyware profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the anti-spyware profile object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
anti_spyware_profile.delete(profile_id)
print(f"Deleted anti-spyware profile with ID: {profile_id}")
```

</div>

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, offset: Optional[int] = None, limit: Optional[int] = None, name: Optional[str] = None, **filters) -> List[AntiSpywareProfileResponseModel]`

Lists anti-spyware profile objects, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list anti-spyware profiles from.
- `snippet` (Optional[str]): The snippet to list anti-spyware profiles from.
- `device` (Optional[str]): The device to list anti-spyware profiles from.
- `offset` (Optional[int]): The offset for pagination.
- `limit` (Optional[int]): The limit for pagination.
- `name` (Optional[str]): Filter profiles by name.
- `**filters`: Additional filters.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profiles = anti_spyware_profile.list(folder='Prisma Access', limit=10)

for profile in profiles:
    print(f"Anti-Spyware Profile Name: {profile.name}, ID: {profile.id}")
```

</div>

---

## Usage Examples

### Example 1: Creating a profile with multiple rules

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "multi_rule_profile",
    "description": "Profile with multiple rules",
    "folder": "Prisma Access",
    "rules": [
        {
            "name": "rule1",
            "severity": ["critical", "high"],
            "category": "spyware",
            "action": {"alert": {}}
        },
        {
            "name": "rule2",
            "severity": ["medium"],
            "category": "dns-security",
            "action": {"drop": {}}
        }
    ]
}

new_profile = anti_spyware_profile.create(profile_data)
print(f"Created profile with ID: {new_profile.id}")
```

</div>

### Example 2: Updating a profile with threat exceptions

> Note: There is currently a schema validation error if an update is made with either `threat_name` or `category` set to
> the value of `any`, it suggests that a minimum of four characters is required and that `any` is not a valid category

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "name": "updated profile",
    "description": "Profile with multiple rules",
    "folder": "Prisma Access",
    "rules": [
        {
            "name": "rule1",
            "severity": ["critical", "high"],
            "category": "spyware",
            "action": {"alert": {}}
        },
        {
            "name": "rule2",
            "severity": ["medium"],
            "category": "dns-security",
            "action": {"drop": {}}
        }
    ],
    "threat_exception": [
        {
            "name": "10001",
            "packet_capture": "single-packet",
            "action": {"allow": {}},
            "exempt_ip": [{"name": "10.0.0.1"}]
        }
    ]
}

updated_profile = anti_spyware_profile.update(profile_id, update_data)
print(f"Updated profile with ID: {updated_profile.id}")
```

</div>

### Example 3: Listing profiles with filters

<div class="termy">

<!-- termynal -->

```python
filtered_profiles = anti_spyware_profile.list(
    folder='Prisma Access',
    limit=5,
    name='updated profile',
)

for profile in filtered_profiles:
    print(f"Filtered Profile: {profile.name}")
```

</div>

### Example 4: Creating a profile with MICA engine settings

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "mica_profile",
    "description": "Profile with MICA engine settings",
    "folder": "Prisma Access",
    "mica_engine_spyware_enabled": [
        {
            "name": "HTTP Command and Control detector",
            "inline_policy_action": "alert"
        },
        {
            "name": "HTTP2 Command and Control detector",
            "inline_policy_action": "reset-both"
        }
    ],
    "rules": [
        {
            "name": "mica_rule",
            "severity": ["any"],
            "category": "any",
            "action": {"reset_both": {}}
        }
    ]
}

new_profile = anti_spyware_profile.create(profile_data)
print(f"Created MICA profile with ID: {new_profile.id}")
```

</div>

### Example 5: Updating a profile with inline exceptions

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "inline_exception_edl_url": ["http://example.com/edl1", "http://example.com/edl2"],
    "inline_exception_ip_address": ["192.168.1.1", "192.168.1.2"]
}

updated_profile = anti_spyware_profile.update(profile_id, update_data)
print(f"Updated profile with inline exceptions, ID: {updated_profile.id}")
```

</div>

### Example 6: Creating a profile in a snippet

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "snippet_profile",
    "description": "Profile in a snippet",
    "snippet": "cdot.io Best Practices",
    "rules": [
        {
            "name": "snippet_rule",
            "severity": ["high"],
            "category": "command-and-control",
            "action": {"reset_both": {}}
        }
    ]
}

new_profile = anti_spyware_profile.create(profile_data)
print(f"Created profile in snippet with ID: {new_profile.id}")
```

</div>

---

## Full Example

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import AntiSpywareProfile

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an AntiSpywareProfile instance
anti_spyware_profile = AntiSpywareProfile(scm)

# Create a new anti-spyware profile
profile_data = {
    "name": "comprehensive_profile",
    "description": "A comprehensive anti-spyware profile",
    "folder": "Prisma Access",
    "cloud_inline_analysis": True,
    "mica_engine_spyware_enabled": [
        {
            "name": "HTTP Command and Control detector",
            "inline_policy_action": "alert"
        }
    ],
    "rules": [
        {
            "name": "rule1",
            "severity": ["critical", "high"],
            "category": "spyware",
            "action": {"alert": {}}
        },
        {
            "name": "rule2",
            "severity": ["medium"],
            "category": "dns-security",
            "action": {"drop": {}}
        }
    ],
    "threat_exception": [
        {
            "name": "10001",
            "packet_capture": "single-packet",
            "action": {"allow": {}},
            "exempt_ip": [{"name": "10.0.0.1"}]
        }
    ]
}

new_profile = anti_spyware_profile.create(profile_data)
print(f"Created comprehensive anti-spyware profile with ID: {new_profile.id}")

# List anti-spyware profiles
profiles = anti_spyware_profile.list(folder='Prisma Access', limit=10)
for profile in profiles:
    print(f"Anti-Spyware Profile Name: {profile.name}, ID: {profile.id}")

# Update the profile
update_data = {
    "description": "Updated comprehensive anti-spyware profile",
    "rules": [
        {
            "name": "updated_rule",
            "severity": ["high"],
            "category": "command-and-control",
            "action": {"block_ip": {"track_by": "source", "duration": 300}}
        }
    ]
}

updated_profile = anti_spyware_profile.update(new_profile.id, update_data)
print(f"Updated anti-spyware profile with ID: {updated_profile.id}")

# Delete the profile
anti_spyware_profile.delete(new_profile.id)
print(f"Deleted anti-spyware profile with ID: {new_profile.id}")
```

</div>

---

## Related Models

- [AntiSpywareProfileRequestModel](../../models/security_services/anti_spyware_profile_models.md#AntiSpywareProfileRequestModel)
- [AntiSpywareProfileResponseModel](../../models/security_services/anti_spyware_profile_models.md#AntiSpywareProfileResponseModel)
