# Anti-Spyware Profile Configuration Object

The `AntiSpywareProfile` class is used to manage anti-spyware profile objects in the Strata Cloud Manager. It provides
methods to create, retrieve, update, delete, and list anti-spyware profile objects.

---

## Importing the AntiSpywareProfile Class

```python
from scm.config.security import AntiSpywareProfile
```

## Methods

### `create(data: Dict[str, Any]) -> AntiSpywareProfileResponseModel`

Creates a new anti-spyware profile object.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the anti-spyware profile object data.

**Example:**

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

### `get(object_id: str) -> AntiSpywareProfileResponseModel`

Retrieves an anti-spyware profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the anti-spyware profile object.

**Example:**

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile_object = anti_spyware_profile.get(profile_id)
print(f"Anti-Spyware Profile Name: {profile_object.name}")
```

### `update(object_id: str, data: Dict[str, Any]) -> AntiSpywareProfileResponseModel`

Updates an existing anti-spyware profile object.

**Parameters:**

- `object_id` (str): The UUID of the anti-spyware profile object.
- `data` (Dict[str, Any]): A dictionary containing the updated anti-spyware profile data.

**Example:**

```python
update_data = {
    "description": "Updated anti-spyware profile description",
}

updated_profile = anti_spyware_profile.update(profile_id, update_data)
print(f"Updated anti-spyware profile with ID: {updated_profile.id}")
```

### `delete(object_id: str) -> None`

Deletes an anti-spyware profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the anti-spyware profile object.

**Example:**

```python
anti_spyware_profile.delete(profile_id)
print(f"Deleted anti-spyware profile with ID: {profile_id}")
```

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

```python
profiles = anti_spyware_profile.list(folder='Prisma Access', limit=10)

for profile in profiles:
    print(f"Anti-Spyware Profile Name: {profile.name}, ID: {profile.id}")
```

---

## Usage Example

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

# List anti-spyware profiles
profiles = anti_spyware_profile.list(folder='Prisma Access', limit=10)
for profile in profiles:
    print(f"Anti-Spyware Profile Name: {profile.name}, ID: {profile.id}")
```

---

## Related Models

- [AntiSpywareProfileRequestModel](../../models/security_services/anti_spyware_profile_models.md#AntiSpywareProfileRequestModel)
- [AntiSpywareProfileResponseModel](../../models/security_services/anti_spyware_profile_models.md#AntiSpywareProfileResponseModel)

