# GlobalProtect Infrastructure Settings Models

## Overview

The GlobalProtect Infrastructure Settings models provide a structured way to manage the network infrastructure configuration for mobile users in Palo Alto Networks' Strata Cloud Manager: DNS servers, IP pools, the portal hostname, WINS, UDP query retries, and static IP pools. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `InfrastructureSettingsBaseModel`: Base model with fields common to all infrastructure settings operations
- `InfrastructureSettingsCreateModel`: Model for creating new infrastructure settings
- `InfrastructureSettingsUpdateModel`: Model for updating existing infrastructure settings (addressed by name, not ID)
- `InfrastructureSettingsResponseModel`: Response model, adds the read-only `id` field

Supporting models:

- `DnsServerEntry`: DNS server entry (`dns_suffix`, `internal_dns_match`, public DNS servers)
- `InternalDnsMatch` / `DnsServerSelection`: Internal DNS resolution rules
- `PublicDnsServer`: Primary/secondary public DNS server
- `EnableWins` / `EnableWinsYes` / `WinsServerEntry`: WINS configuration (`yes`/`no` choice)
- `IpPool`: IP pool entry
- `PortalHostname` / `CustomDomain` / `DefaultDomain`: Portal hostname configuration
- `UdpQueries` / `UdpQueryRetries`: UDP query retry configuration
- `StaticIpPool` / `UserGroup`: Static IP pool entries

Request models use `extra="forbid"`; the response model uses `extra="ignore"`.

!!! note
    The `folder` ("Mobile Users") is a query parameter on this endpoint, not a body
    field, so it does not appear on these models. The service class handles it.

## Attributes

| Attribute         | Type                   | Required | Default | Description                                          |
|-------------------|------------------------|----------|---------|------------------------------------------------------|
| `name`            | `str`                  | Yes      | None    | Name of the infrastructure settings                  |
| `dns_servers`     | `List[DnsServerEntry]` | Yes      | None    | DNS server entries                                   |
| `ip_pools`        | `List[IpPool]`         | Yes      | None    | IP pools for mobile users                            |
| `portal_hostname` | `PortalHostname`       | Yes      | None    | Portal hostname (custom or default domain)           |
| `enable_wins`     | `EnableWins`           | No       | None    | WINS configuration (`yes`/`no` choice)               |
| `ipv6`            | `bool`                 | No       | None    | Whether IPv6 is enabled                              |
| `udp_queries`     | `UdpQueries`           | No       | None    | UDP query retry configuration                        |
| `static_ip_pools` | `List[StaticIpPool]`   | No       | None    | Static IP pools                                      |
| `id`              | `UUID`                 | Yes**    | None    | UUID of the resource                                 |

\** Response model only (read-only field)

### StaticIpPool Attributes

| Attribute     | Type              | Required | Description                                          |
|---------------|-------------------|----------|------------------------------------------------------|
| `name`        | `str`             | No       | Pool entry name (max 128 chars)                      |
| `pool_type`   | `"Static-IP"`     | No       | Pool type (only `Static-IP` is valid)                |
| `ip_pool`     | `List[str]`       | No       | IP subnets (CIDR)                                    |
| `theatres`    | `List[str]`       | No       | IP pools on theatres                                 |
| `users`       | `List[str]`       | No       | IP pools on users                                    |
| `user_groups` | `List[UserGroup]` | No       | IP pools on user groups (DN max 320 chars)           |

### UdpQueryRetries Attributes

| Attribute  | Type  | Constraints | Description                                          |
|------------|-------|-------------|------------------------------------------------------|
| `attempts` | `int` | 1-30        | Maximum retries before trying the next name server   |
| `interval` | `int` | 1-30        | Time in seconds for another request to be sent       |

## Exceptions

The Infrastructure Settings models can raise the following exceptions during validation:

- **ValueError / ValidationError**: Raised in several scenarios:
    - When required fields (`name`, `dns_servers`, `ip_pools`, `portal_hostname`) are missing
    - When `pool_type` is not `"Static-IP"`
    - When `attempts` or `interval` are outside the 1-30 range
    - When unknown fields are passed to request models (`extra="forbid"`)

## Usage Examples

### Creating an Infrastructure Settings Model

```python
from scm.models.mobile_agent import InfrastructureSettingsCreateModel

infra = InfrastructureSettingsCreateModel(
    name="mobile-users-infra",
    dns_servers=[
        {
            "name": "dns-config",
            "dns_suffix": ["example.com"],
            "primary_public_dns": {"dns_server": "8.8.8.8"},
        }
    ],
    ip_pools=[{"name": "ip-pool-1", "ip_pool": ["10.10.0.0/16"]}],
    portal_hostname={"default_domain": {"hostname": "acme"}},
)

payload = infra.model_dump(exclude_unset=True)
```

### Static IP Pools

```python
from scm.models.mobile_agent import StaticIpPool

pool = StaticIpPool(
    name="branch-pool",
    pool_type="Static-IP",
    ip_pool=["10.1.0.0/24"],
    user_groups=[{"name": "cn=engineering,dc=example,dc=com", "directory": "ldap"}],
)
```

## Related Documentation

- [Infrastructure Settings Configuration](../../config/mobile_agent/infrastructure_settings.md)
- [Mobile Agent Models Overview](index.md)
