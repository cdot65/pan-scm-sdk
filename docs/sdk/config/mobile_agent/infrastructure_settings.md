# GlobalProtect Infrastructure Settings Configuration Object

Manages GlobalProtect infrastructure settings (DNS servers, IP pools, portal hostname, WINS, and static IP pools) for mobile users in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `InfrastructureSettings` class inherits from `BaseObject` and provides CRUD operations for GlobalProtect infrastructure settings objects.

!!! note
    This resource has no `/{id}` API paths. Objects are addressed by `name` within the
    `Mobile Users` folder, both passed as query parameters. `create()` and `update()`
    send the folder as a query parameter alongside the JSON payload, and `delete()`
    addresses the object by `name` and `folder`.

### Methods

| Method     | Description                                  | Parameters                                  | Return Type                                       |
|------------|----------------------------------------------|---------------------------------------------|---------------------------------------------------|
| `create()` | Creates new infrastructure settings          | `data: Dict[str, Any]`, `folder: str`       | `Optional[InfrastructureSettingsResponseModel]`   |
| `update()` | Updates existing settings (by name in body)  | `data: Dict[str, Any]`, `folder: str`       | `Optional[InfrastructureSettingsResponseModel]`   |
| `delete()` | Deletes settings by name and folder          | `name: str`, `folder: str`                  | `None`                                            |
| `list()`   | Lists settings (name required by the API)    | `name: str`, `folder: str`, `**filters`     | `List[InfrastructureSettingsResponseModel]`       |
| `fetch()`  | Gets settings by name and folder             | `name: str`, `folder: str`                  | `InfrastructureSettingsResponseModel`             |

!!! note
    The API returns `201 Created` / `200 OK` with an empty body for `create()` and
    `update()`, in which case these methods return `None`.

### Model Attributes

| Attribute         | Type                | Required | Default | Description                                      |
|-------------------|---------------------|----------|---------|--------------------------------------------------|
| `name`            | str                 | Yes      | None    | Name of the infrastructure settings              |
| `dns_servers`     | List[DnsServerEntry]| Yes      | None    | DNS server entries                               |
| `ip_pools`        | List[IpPool]        | Yes      | None    | IP pools for mobile users                        |
| `portal_hostname` | PortalHostname      | Yes      | None    | Portal hostname (custom or default domain)       |
| `enable_wins`     | EnableWins          | No       | None    | WINS configuration (`yes`/`no` choice)           |
| `ipv6`            | bool                | No       | None    | Whether IPv6 is enabled                          |
| `udp_queries`     | UdpQueries          | No       | None    | UDP query retry configuration                    |
| `static_ip_pools` | List[StaticIpPool]  | No       | None    | Static IP pools (theatres, users, user groups)   |
| `id`              | UUID                | Response | None    | UUID of the resource (response only)             |

### Exceptions

| Exception                    | HTTP Code | Description                                 |
|------------------------------|-----------|---------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid settings data or folder value       |
| `MissingQueryParameterError` | 400       | Missing required parameters (e.g. `name`)   |
| `ObjectNotPresentError`      | 404       | Infrastructure settings not found           |
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

infrastructure_settings = client.infrastructure_settings
```

## Methods

### List Infrastructure Settings

The API requires the `name` query parameter for this endpoint.

```python
settings = client.infrastructure_settings.list(name="mobile-users-infra")

for setting in settings:
    print(f"Name: {setting.name}, IPv6: {setting.ipv6}")
```

### Fetch Infrastructure Settings

```python
infra = client.infrastructure_settings.fetch(name="mobile-users-infra", folder="Mobile Users")
print(f"Found infrastructure settings: {infra.name}")
```

### Create Infrastructure Settings

```python
infra_config = {
    "name": "mobile-users-infra",
    "dns_servers": [
        {
            "name": "dns-config",
            "dns_suffix": ["example.com"],
            "primary_public_dns": {"dns_server": "8.8.8.8"},
            "secondary_public_dns": {"dns_server": "8.8.4.4"},
        }
    ],
    "ip_pools": [
        {
            "name": "ip-pool-1",
            "ip_pool": ["10.10.0.0/16"],
        }
    ],
    "portal_hostname": {
        "default_domain": {"hostname": "acme"},
    },
    "ipv6": False,
}

client.infrastructure_settings.create(infra_config)
```

### Update Infrastructure Settings

The object is addressed by the `name` field in the payload; there is no ID-based update.

```python
infra_config = {
    "name": "mobile-users-infra",
    "dns_servers": [
        {
            "name": "dns-config",
            "primary_public_dns": {"dns_server": "1.1.1.1"},
        }
    ],
    "ip_pools": [
        {
            "name": "ip-pool-1",
            "ip_pool": ["10.20.0.0/16"],
        }
    ],
    "portal_hostname": {
        "custom_domain": {
            "hostname": "vpn.example.com",
            "cname": "vpn.example.com.gp.prismaaccess.com",
        },
    },
}

client.infrastructure_settings.update(infra_config)
```

### Delete Infrastructure Settings

```python
client.infrastructure_settings.delete(name="mobile-users-infra", folder="Mobile Users")
```

## Related Documentation

- [Infrastructure Settings Models](../../models/mobile_agent/infrastructure_settings_models.md)
- [Mobile Agent Overview](index.md)
