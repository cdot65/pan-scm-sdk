# GlobalProtect Forwarding Profile Destinations Configuration Object

Manages GlobalProtect destinations (FQDN and IP address groups) referenced by forwarding profile rules in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `ForwardingProfileDestinations` class inherits from `BaseObject` and provides CRUD operations for GlobalProtect destination objects. Destinations are UUID-addressed resources under the `Mobile Users` folder.

### Methods

| Method     | Description                          | Parameters                                       | Return Type                                        |
|------------|--------------------------------------|--------------------------------------------------|----------------------------------------------------|
| `create()` | Creates a new destination            | `data: Dict[str, Any]`, `folder: str`            | `ForwardingProfileDestinationResponseModel`        |
| `get()`    | Retrieves a destination by ID        | `object_id: Union[str, UUID]`                    | `ForwardingProfileDestinationResponseModel`        |
| `update()` | Updates an existing destination      | `object_id: Union[str, UUID]`, `data: Dict[str, Any]` | `ForwardingProfileDestinationResponseModel`   |
| `delete()` | Deletes a destination                | `object_id: Union[str, UUID]`                    | `None`                                             |
| `list()`   | Lists destinations with filtering    | `folder: str`, `name: Optional[str]`, `**filters` | `List[ForwardingProfileDestinationResponseModel]` |
| `fetch()`  | Gets a destination by name and folder | `name: str`, `folder: str`                      | `ForwardingProfileDestinationResponseModel`        |

### Model Attributes

| Attribute      | Type                        | Required | Default | Description                                                     |
|----------------|-----------------------------|----------|---------|-----------------------------------------------------------------|
| `name`         | str                         | Yes      | None    | Name of the destination (max 64 chars, `[0-9a-zA-Z._-]`)        |
| `description`  | str                         | No       | None    | Description of the destination (max 1023 chars)                  |
| `fqdn`         | List[DestinationFqdnEntry]  | No       | None    | FQDN entries (wildcards and at most one trailing `$` supported) |
| `ip_addresses` | List[DestinationIpEntry]    | No       | None    | IP address entries (wildcards and CIDR notation supported)      |

Each FQDN or IP entry has a required `name` and an optional `port` (1-65535).

:::note
The `folder` is sent as a query parameter (only `"Mobile Users"` is valid), not in the
request body. `create()` accepts `folder` either as a keyword argument or as a key in `data`.
:::

### Exceptions

| Exception                    | HTTP Code | Description                                 |
|------------------------------|-----------|---------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid destination data or folder value    |
| `MissingQueryParameterError` | 400       | Missing required parameters                 |
| `ObjectNotPresentError`      | 404       | Destination not found                       |
| `AuthenticationError`        | 401       | Authentication failed                       |
| `ServerError`                | 500       | Internal server error                       |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

destinations = client.forwarding_profile_destination
```

## Methods

### List Destinations

```python
destinations = client.forwarding_profile_destination.list()

for destination in destinations:
    print(f"Name: {destination.name}, ID: {destination.id}")
```

**Controlling pagination with max_limit:**

```python
client.forwarding_profile_destination.max_limit = 1000

destinations = client.forwarding_profile_destination.list()
```

### Fetch a Destination

```python
destination = client.forwarding_profile_destination.fetch(
    name="internal-destinations", folder="Mobile Users"
)
print(f"Found destination: {destination.name} ({destination.id})")
```

### Create a Destination

```python
destination_config = {
    "name": "internal-destinations",
    "description": "Internal corporate destinations",
    "fqdn": [
        {"name": "*.example.com"},
        {"name": "intranet.example.com", "port": 8443},
    ],
    "ip_addresses": [
        {"name": "10.0.0.0/8"},
        {"name": "192.168.1.*", "port": 443},
    ],
}
new_destination = client.forwarding_profile_destination.create(destination_config)
```

### Get a Destination

```python
destination = client.forwarding_profile_destination.get(
    "123e4567-e89b-12d3-a456-426655440000"
)
print(f"Destination: {destination.name}")
```

### Update a Destination

```python
updated = client.forwarding_profile_destination.update(
    "123e4567-e89b-12d3-a456-426655440000",
    {
        "name": "internal-destinations",
        "fqdn": [{"name": "*.corp.example.com"}],
    },
)
print(f"Updated destination: {updated.name}")
```

### Delete a Destination

```python
client.forwarding_profile_destination.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Related Documentation

- [Forwarding Profile Destination Models](../../models/mobile_agent/forwarding_profile_destinations_models.md)
- [Forwarding Profiles](forwarding_profiles.md)
- [Mobile Agent Overview](index.md)
