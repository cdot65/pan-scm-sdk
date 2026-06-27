# GlobalProtect Forwarding Profiles Configuration Object

Manages GlobalProtect forwarding profiles for controlling how mobile agent traffic is forwarded (PAC file, GlobalProtect proxy, or ZTNA agent) in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `ForwardingProfiles` class inherits from `BaseObject` and provides CRUD operations for GlobalProtect forwarding profile objects. Forwarding profiles are UUID-addressed resources under the `Mobile Users` folder.

### Methods

| Method     | Description                          | Parameters                                       | Return Type                             |
|------------|--------------------------------------|--------------------------------------------------|-----------------------------------------|
| `create()` | Creates a new forwarding profile     | `data: Dict[str, Any]`, `folder: str`            | `ForwardingProfileResponseModel`        |
| `get()`    | Retrieves a profile by ID            | `object_id: Union[str, UUID]`                    | `ForwardingProfileResponseModel`        |
| `update()` | Updates an existing profile          | `object_id: Union[str, UUID]`, `data: Dict[str, Any]` | `ForwardingProfileResponseModel`   |
| `delete()` | Deletes a forwarding profile         | `object_id: Union[str, UUID]`                    | `None`                                  |
| `list()`   | Lists profiles with filtering        | `folder: str`, `name: Optional[str]`, `**filters` | `List[ForwardingProfileResponseModel]` |
| `fetch()`  | Gets a profile by name and folder    | `name: str`, `folder: str`                       | `ForwardingProfileResponseModel`        |

### Model Attributes

| Attribute           | Type             | Required | Default | Description                                                       |
|---------------------|------------------|----------|---------|-------------------------------------------------------------------|
| `name`              | str              | Yes      | None    | Name of the forwarding profile (max 64 chars, `[0-9a-zA-Z._-]`)   |
| `description`       | str              | No       | None    | Description of the profile (max 1023 chars)                        |
| `definition_method` | DefinitionMethod | No       | rules   | How the profile is defined: `rules` or `pac-file`                  |
| `type`              | Union            | No       | None    | Profile type config: `pac_file`, `global_protect_proxy`, or `ztna_agent` |

:::note
The `folder` is sent as a query parameter (only `"Mobile Users"` is valid), not in the
request body. `create()` accepts `folder` either as a keyword argument or as a key in `data`.
:::

### Exceptions

| Exception                    | HTTP Code | Description                                 |
|------------------------------|-----------|---------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or folder value        |
| `MissingQueryParameterError` | 400       | Missing required parameters                 |
| `ObjectNotPresentError`      | 404       | Forwarding profile not found                |
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

forwarding_profiles = client.forwarding_profile
```

## Methods

### List Forwarding Profiles

```python
profiles = client.forwarding_profile.list()

for profile in profiles:
    print(f"Name: {profile.name}, ID: {profile.id}, Method: {profile.definition_method}")
```

**Controlling pagination with max_limit:**

```python
client.forwarding_profile.max_limit = 1000

profiles = client.forwarding_profile.list()
```

### Fetch a Forwarding Profile

```python
profile = client.forwarding_profile.fetch(name="corp-forwarding", folder="Mobile Users")
print(f"Found forwarding profile: {profile.name} ({profile.id})")
```

### Create a Forwarding Profile

```python
# Rules-based profile with ZTNA agent forwarding
profile_config = {
    "name": "corp-forwarding",
    "description": "Corporate ZTNA forwarding profile",
    "definition_method": "rules",
    "type": {
        "ztna_agent": {
            "forwarding_rules": [
                {
                    "name": "internal-apps",
                    "traffic_type": "dns-and-network-traffic",
                    "enabled": True,
                    "user_locations": "Any",
                    "destinations": "internal-destinations",
                    "connectivity": "direct",
                }
            ],
            "block_rule": {
                "block_all_other_unmatched_outbound_connections": False,
                "allow_icmp_for_troubleshooting": True,
            },
        }
    },
}
new_profile = client.forwarding_profile.create(profile_config)

# GlobalProtect proxy profile
proxy_config = {
    "name": "gp-proxy-forwarding",
    "type": {
        "global_protect_proxy": {
            "forwarding_rules": [
                {"name": "default-rule", "connectivity": "direct"},
            ],
        }
    },
}
proxy_profile = client.forwarding_profile.create(proxy_config, folder="Mobile Users")
```

### Get a Forwarding Profile

```python
profile = client.forwarding_profile.get("123e4567-e89b-12d3-a456-426655440000")
print(f"Profile: {profile.name}")
```

### Update a Forwarding Profile

```python
updated = client.forwarding_profile.update(
    "123e4567-e89b-12d3-a456-426655440000",
    {
        "name": "corp-forwarding",
        "description": "Updated description",
    },
)
print(f"Updated profile: {updated.name}")
```

### Delete a Forwarding Profile

```python
client.forwarding_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Related Documentation

- [Forwarding Profile Models](../../models/mobile_agent/forwarding_profiles_models.md)
- [Forwarding Profile Destinations](forwarding_profile_destinations.md)
- [Mobile Agent Overview](index.md)
