# GlobalProtect Tunnel Profiles Models

## Overview

The GlobalProtect Tunnel Profiles models provide a structured way to manage tunnel settings for mobile users in Palo Alto Networks' Strata Cloud Manager. These models cover split tunneling configuration, authentication override cookies, and tunnel source restrictions. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `TunnelProfileBaseModel`: Base model with fields common to all tunnel profile operations
- `TunnelProfileCreateModel`: Model for creating new tunnel profiles
- `TunnelProfileUpdateModel`: Model for updating existing tunnel profiles (addressed by name)
- `TunnelProfileResponseModel`: Response model for tunnel profile operations
- `AuthenticationOverride`: Authentication override configuration
- `AcceptCookie`: Accept cookie configuration for authentication override
- `CookieLifetime`: Cookie lifetime bounds (days/hours/minutes)
- `SourceAddress`: Source IP addresses and regions
- `SplitTunneling`: Split tunneling routes, applications, and domains
- `SplitTunnelingDomains`: Domain list container for include/exclude domains
- `SplitTunnelingDomainEntry`: Single domain entry with optional ports
- `TunnelOperatingSystem`: Enum for available operating systems

All request models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The response model uses `extra="ignore"` to tolerate additional fields returned by the API.

## Attributes

| Attribute                           | Type                        | Required | Default | Description                                               |
|-------------------------------------|-----------------------------|----------|---------|-----------------------------------------------------------|
| `name`                              | `str`                       | Yes      | None    | Name of the tunnel profile. Length: 1-31 chars            |
| `authentication_override`           | `AuthenticationOverride`    | No       | None    | Authentication cookie override configuration              |
| `no_direct_access_to_local_network` | `bool`                      | No       | None    | Disable direct access to the local network                |
| `os`                                | `List[TunnelOperatingSystem]` | No     | None    | Operating systems the profile applies to                  |
| `retrieve_framed_ip_address`        | `bool`                      | No       | None    | Retrieve framed IP address from the authentication server |
| `source_address`                    | `SourceAddress`             | No       | None    | Source IP addresses and regions                           |
| `source_user`                       | `List[str]`                 | No       | None    | Source users the profile applies to                       |
| `split_tunneling`                   | `SplitTunneling`            | No       | None    | Split tunneling configuration                             |

The response model additionally exposes `folder` (`Optional[str]`) when returned by the API.

### Nested Model Attributes

**CookieLifetime**

| Attribute             | Type  | Constraints | Description                |
|-----------------------|-------|-------------|----------------------------|
| `lifetime_in_days`    | `int` | 1-365       | Cookie lifetime in days    |
| `lifetime_in_hours`   | `int` | 1-72        | Cookie lifetime in hours   |
| `lifetime_in_minutes` | `int` | 1-59        | Cookie lifetime in minutes |

**SplitTunneling**

| Attribute              | Type                    | Description                          |
|------------------------|-------------------------|--------------------------------------|
| `access_route`         | `List[str]`             | Routes included in the tunnel        |
| `exclude_access_route` | `List[str]`             | Routes excluded from the tunnel      |
| `exclude_applications` | `List[str]`             | Applications excluded from tunnel    |
| `exclude_domains`      | `SplitTunnelingDomains` | Domains excluded from the tunnel     |
| `include_applications` | `List[str]`             | Applications included in the tunnel  |
| `include_domains`      | `SplitTunnelingDomains` | Domains included in the tunnel       |

**SplitTunnelingDomainEntry**

| Attribute | Type        | Constraints       | Description          |
|-----------|-------------|-------------------|----------------------|
| `name`    | `str`       |                   | The domain name      |
| `ports`   | `List[int]` | each port 1-65535 | Ports for the domain |

## Enumerations

### TunnelOperatingSystem

| Value         | Description              |
|---------------|--------------------------|
| `ANDROID`     | Android devices          |
| `CHROME`      | Chrome OS devices        |
| `IOT`         | Internet of Things devices |
| `LINUX`       | Linux systems            |
| `MAC`         | macOS systems            |
| `WINDOWS`     | Windows systems          |
| `WINDOWS_UWP` | Windows UWP applications |
| `IOS`         | iOS devices              |

:::note
Unlike the authentication settings `OperatingSystem` enum, tunnel profiles do not support `Any`, `Browser`, or `Satellite` values.
:::

## Usage Example

```python
from scm.client import Scm
from scm.models.mobile_agent.tunnel_profiles import (
    TunnelProfileCreateModel,
    TunnelOperatingSystem,
)

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a tunnel profile using a model
tunnel_profile = TunnelProfileCreateModel(
   name="windows-tunnel",
   os=[TunnelOperatingSystem.WINDOWS],
   no_direct_access_to_local_network=True,
   split_tunneling={
       "access_route": ["10.0.0.0/8"],
       "exclude_domains": {"list": [{"name": "example.com", "ports": [443]}]},
   },
)

# Convert the model to a dictionary for the API call
profile_dict = tunnel_profile.model_dump(exclude_unset=True)
result = client.tunnel_profile.create(profile_dict)
print(f"Created tunnel profile: {result.name}")
```

## Related Topics

- [Tunnel Profiles Configuration](../../config/mobile_agent/tunnel_profiles.md)
- [Mobile Agent Overview](index.md)
