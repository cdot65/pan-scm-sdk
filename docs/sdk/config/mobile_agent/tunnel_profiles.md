# GlobalProtect Tunnel Profiles Configuration Object

Manages GlobalProtect tunnel settings (tunnel profiles) for mobile users in Palo Alto Networks Strata Cloud Manager. Tunnel profiles control split tunneling behavior, authentication override cookies, and tunnel source restrictions for the GlobalProtect agent.

!!! note
    The SCM UI refers to this resource as "Tunnel Settings". The underlying API endpoint is `/tunnel-profiles`.

## Class Overview

The `TunnelProfiles` class inherits from `BaseObject` and provides CRUD operations for GlobalProtect tunnel profile objects. Tunnel profiles are addressed **by name** within the `Mobile Users` folder — the API exposes no ID-based endpoints for this resource.

### Methods

| Method     | Description                            | Parameters                                  | Return Type                        |
|------------|----------------------------------------|---------------------------------------------|------------------------------------|
| `create()` | Creates a new tunnel profile           | `data: Dict[str, Any]`, `folder: str`       | `TunnelProfileResponseModel`       |
| `update()` | Updates a tunnel profile by name       | `data: Dict[str, Any]`, `folder: str`       | `TunnelProfileResponseModel`       |
| `delete()` | Deletes a tunnel profile by name       | `name: str`, `folder: str`                  | `None`                             |
| `list()`   | Lists tunnel profiles with filtering   | `folder: str`, `name: Optional[str]`        | `List[TunnelProfileResponseModel]` |
| `fetch()`  | Gets a tunnel profile by name          | `name: str`, `folder: str`                  | `TunnelProfileResponseModel`       |

`folder` defaults to `"Mobile Users"` on all methods, which is the only value accepted by the API.

### Model Attributes

| Attribute                           | Type                         | Required | Default | Description                                                  |
|-------------------------------------|------------------------------|----------|---------|--------------------------------------------------------------|
| `name`                              | str                          | Yes      | None    | Name of the tunnel profile (1-31 chars)                      |
| `authentication_override`           | AuthenticationOverride       | No       | None    | Authentication cookie override configuration                 |
| `no_direct_access_to_local_network` | bool                         | No       | None    | Disable direct access to the local network                   |
| `os`                                | List[TunnelOperatingSystem]  | No       | None    | Operating systems the profile applies to                     |
| `retrieve_framed_ip_address`        | bool                         | No       | None    | Retrieve framed IP address from the authentication server    |
| `source_address`                    | SourceAddress                | No       | None    | Source IP addresses and regions the profile applies to       |
| `source_user`                       | List[str]                    | No       | None    | Source users the profile applies to                          |
| `split_tunneling`                   | SplitTunneling               | No       | None    | Split tunneling routes, applications, and domains            |

### Exceptions

| Exception                    | HTTP Code | Description                          |
|------------------------------|-----------|--------------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or folder value |
| `MissingQueryParameterError` | 400       | Missing required parameters          |
| `NameNotUniqueError`         | 409       | Tunnel profile name already exists   |
| `ObjectNotPresentError`      | 404       | Tunnel profile not found             |
| `AuthenticationError`        | 401       | Authentication failed                |
| `ServerError`                | 500       | Internal server error                |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

tunnel_profiles = client.tunnel_profile
```

## Methods

### Create Tunnel Profile

```python
profile_config = {
    "name": "windows-tunnel",
    "os": ["Windows", "Mac"],
    "no_direct_access_to_local_network": True,
    "split_tunneling": {
        "access_route": ["10.0.0.0/8"],
        "exclude_domains": {
            "list": [{"name": "example.com", "ports": [443]}]
        },
    },
}

new_profile = client.tunnel_profile.create(profile_config)
print(f"Created tunnel profile: {new_profile.name}")
```

### List Tunnel Profiles

```python
all_profiles = client.tunnel_profile.list()

for profile in all_profiles:
    print(f"Name: {profile.name}, OS: {profile.os}")
```

**Controlling pagination with max_limit:**

```python
client.tunnel_profile.max_limit = 1000

all_profiles = client.tunnel_profile.list()
```

### Fetch Tunnel Profile

```python
profile = client.tunnel_profile.fetch(name="windows-tunnel", folder="Mobile Users")
print(f"Split tunneling: {profile.split_tunneling}")
```

### Update Tunnel Profile

Tunnel profiles are addressed by name in the request body — there is no ID:

```python
update_config = {
    "name": "windows-tunnel",
    "retrieve_framed_ip_address": True,
}

updated_profile = client.tunnel_profile.update(update_config)
print(f"Updated tunnel profile: {updated_profile.name}")
```

### Delete Tunnel Profile

```python
client.tunnel_profile.delete(name="windows-tunnel")
```

## Complete Example

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError
)

try:
    profile_config = {
        "name": "corp-tunnel",
        "os": ["Windows"],
        "authentication_override": {
            "accept_cookie": {
                "cookie_lifetime": {"lifetime_in_hours": 24},
                "generate_cookie": True,
            }
        },
        "split_tunneling": {
            "access_route": ["10.0.0.0/8", "172.16.0.0/12"],
        },
    }
    new_profile = client.tunnel_profile.create(profile_config)
    result = client.commit(
        folders=["Mobile Users"],
        description="Added GlobalProtect tunnel profile",
        sync=True
    )
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid tunnel profile data: {e.message}")
except NameNotUniqueError as e:
    print(f"Tunnel profile name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Tunnel profile not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Tunnel Profiles Models](../../models/mobile_agent/tunnel_profiles_models.md#Overview)
- [Mobile Agent Overview](index.md)
- [API Client](../../client.md)
