# GlobalProtect Forwarding Profile User Locations Configuration Object

Manages GlobalProtect forwarding profile user locations in Palo Alto Networks Strata Cloud Manager. User locations define location matching criteria (internal host detection or IP address lists) referenced by forwarding profiles.

## Class Overview

The `ForwardingProfileUserLocations` class inherits from `BaseObject` and provides CRUD operations for GlobalProtect forwarding profile user location objects.

### Methods

| Method     | Description                       | Parameters                                                  | Return Type                                        |
|------------|-----------------------------------|--------------------------------------------------------------|----------------------------------------------------|
| `create()` | Creates a new user location       | `data: Dict[str, Any]`, `folder: str`                        | `ForwardingProfileUserLocationResponseModel`       |
| `get()`    | Retrieves a user location by ID   | `object_id: Union[str, UUID]`                                | `ForwardingProfileUserLocationResponseModel`       |
| `update()` | Updates an existing user location | `user_location: ForwardingProfileUserLocationUpdateModel`    | `ForwardingProfileUserLocationResponseModel`       |
| `delete()` | Deletes a user location           | `object_id: Union[str, UUID]`                                | `None`                                             |
| `list()`   | Lists user locations              | `folder: str`, `name: Optional[str]`                         | `List[ForwardingProfileUserLocationResponseModel]` |
| `fetch()`  | Gets a user location by name      | `name: str`, `folder: str`                                   | `ForwardingProfileUserLocationResponseModel`       |

### Model Attributes

| Attribute     | Type               | Required | Default | Description                                      |
|---------------|--------------------|----------|---------|--------------------------------------------------|
| `name`        | str                | Yes      | None    | Name of the user location (max 64 chars)         |
| `choice`      | UserLocationChoice | Yes      | None    | Location matching criteria (exactly one option)  |
| `description` | str                | No       | None    | Description of the user location (max 1023)      |
| `id`          | UUID               | Yes*     | None    | UUID of the user location                        |

\* Present in update and response models only. The `folder` ("Mobile Users") is passed as a query parameter on `create()` and `list()`, not as a model field.

The `choice` field accepts exactly one of:

- `internal_host_detection` — `ip_address` and/or `fqdn` used to detect the internal network
- `ip_addresses` — a list of IP address entries (`name` per entry, IPv4 with optional wildcards or CIDR)

### Exceptions

| Exception                    | HTTP Code | Description                       |
|------------------------------|-----------|-----------------------------------|
| `InvalidObjectError`         | 400       | Invalid data, folder, or response |
| `MissingQueryParameterError` | 400       | Missing required parameters       |
| `ObjectNotPresentError`      | 404       | User location not found           |
| `AuthenticationError`        | 401       | Authentication failed             |
| `ServerError`                | 500       | Internal server error             |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

user_locations = client.forwarding_profile_user_location
```

## Methods

### List User Locations

```python
all_locations = client.forwarding_profile_user_location.list()

for location in all_locations:
    print(f"Name: {location.name}")
```

### Fetch a User Location

```python
location = client.forwarding_profile_user_location.fetch(
    name="branch-offices",
    folder="Mobile Users",
)
print(f"Found user location: {location.name}")
```

### Create a User Location

```python
# Using internal host detection
ihd_config = {
    "name": "corporate-network",
    "description": "Detect users on the corporate network",
    "choice": {
        "internal_host_detection": {
            "ip_address": "10.0.0.1",
            "fqdn": "internal.example.com",
        }
    },
}
new_location = client.forwarding_profile_user_location.create(ihd_config)

# Using IP address entries
ip_config = {
    "name": "branch-offices",
    "choice": {
        "ip_addresses": [
            {"name": "10.1.0.0/16"},
            {"name": "10.2.0.0/16"},
        ]
    },
}
branch_location = client.forwarding_profile_user_location.create(ip_config)
```

### Update a User Location

```python
from scm.models.mobile_agent import ForwardingProfileUserLocationUpdateModel

existing = client.forwarding_profile_user_location.fetch(name="branch-offices")

update_model = ForwardingProfileUserLocationUpdateModel(
    id=existing.id,
    name=existing.name,
    choice={"ip_addresses": [{"name": "10.1.0.0/16"}]},
)
updated = client.forwarding_profile_user_location.update(update_model)
```

### Delete a User Location

```python
client.forwarding_profile_user_location.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Related Documentation

- [Forwarding Profile User Location Models](../../models/mobile_agent/forwarding_profile_user_locations_models.md)
- [Mobile Agent Configuration](index.md)
