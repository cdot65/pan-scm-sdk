# DNS Proxy Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Sub-Models](#sub-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The DNS Proxy models provide a structured way to represent and validate DNS proxy configuration data for Palo Alto Networks' Strata Cloud Manager. These models manage DNS proxy settings including default servers, domain-specific rules, static entries, caching behavior, and TCP/UDP query configurations.

### Models

The module provides the following Pydantic models:

- `DnsProxyBaseModel`: Base model with fields common to all DNS proxy operations
- `DnsProxyCreateModel`: Model for creating new DNS proxy configurations
- `DnsProxyUpdateModel`: Model for updating existing DNS proxy configurations
- `DnsProxyResponseModel`: Response model for DNS proxy operations

### Sub-Models

The module also provides several sub-models for nested configuration:

- `DnsProxyDefaultServer`: Default DNS server configuration
- `DnsProxyDomainServer`: DNS proxy rule (domain server) entry
- `DnsProxyStaticEntry`: Static domain name mapping entry
- `DnsProxyTcpQueries`: TCP queries configuration
- `DnsProxyUdpQueries`: UDP queries configuration
- `DnsProxyUdpRetries`: UDP query retry configuration
- `DnsProxyCacheMaxTtl`: Cache max TTL configuration
- `DnsProxyCache`: DNS cache configuration

The `DnsProxyBaseModel` and `DnsProxyCreateModel` / `DnsProxyUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `DnsProxyResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

### Field Aliases

Several fields in the DNS Proxy models use aliases to map between Python attribute names (underscores) and the API's hyphenated field names. The following aliases are defined:

| Python Attribute      | API Field Name         | Model                  |
|-----------------------|------------------------|------------------------|
| `domain_servers`      | `domain-servers`       | DnsProxyBaseModel      |
| `static_entries`      | `static-entries`       | DnsProxyBaseModel      |
| `tcp_queries`         | `tcp-queries`          | DnsProxyBaseModel      |
| `udp_queries`         | `udp-queries`          | DnsProxyBaseModel      |
| `domain_name`         | `domain-name`          | DnsProxyDomainServer   |
| `max_pending_requests`| `max-pending-requests` | DnsProxyTcpQueries     |
| `time_to_live`        | `time-to-live`         | DnsProxyCacheMaxTtl    |
| `cache_edns`          | `cache-edns`           | DnsProxyCache          |
| `max_ttl`             | `max-ttl`              | DnsProxyCache          |

All models use `populate_by_name=True`, so you can use either the Python attribute name or the API field name when constructing model instances.

## Model Attributes

### DnsProxyBaseModel

This is the base model containing fields common to all DNS proxy operations.

| Attribute        | Type                           | Required | Default | Description                                                       |
|------------------|--------------------------------|----------|---------|-------------------------------------------------------------------|
| name             | str                            | Yes      | None    | DNS proxy name. Max 31 chars.                                     |
| enabled          | bool                           | No       | None    | Enable DNS proxy.                                                 |
| default          | DnsProxyDefaultServer          | No       | None    | Default DNS server configuration.                                 |
| interface        | List[str]                      | No       | None    | Interfaces on which to enable DNS proxy service.                  |
| domain_servers   | List[DnsProxyDomainServer]     | No       | None    | DNS proxy rules (domain servers). Alias: `domain-servers`.        |
| static_entries   | List[DnsProxyStaticEntry]      | No       | None    | Static domain name mappings. Alias: `static-entries`.             |
| tcp_queries      | DnsProxyTcpQueries             | No       | None    | TCP queries configuration. Alias: `tcp-queries`.                  |
| udp_queries      | DnsProxyUdpQueries             | No       | None    | UDP queries configuration. Alias: `udp-queries`.                  |
| cache            | DnsProxyCache                  | No       | None    | DNS cache configuration.                                          |
| folder           | str                            | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.    |
| snippet          | str                            | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.   |
| device           | str                            | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.    |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### DnsProxyCreateModel

Inherits all fields from `DnsProxyBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### DnsProxyUpdateModel

Extends `DnsProxyBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the DNS proxy             |

### DnsProxyResponseModel

Extends `DnsProxyBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the DNS proxy             |

> **Note:** The `DnsProxyResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Sub-Models

### DnsProxyDefaultServer

Default DNS server configuration.

| Attribute   | Type              | Required | Default | Description                                           |
|-------------|-------------------|----------|---------|-------------------------------------------------------|
| inheritance | Dict[str, Any]    | No       | None    | Inheritance settings with 'source' (dynamic interface)|
| primary     | str               | Yes      | None    | Primary DNS name server IP address.                   |
| secondary   | str               | No       | None    | Secondary DNS name server IP address.                 |

### DnsProxyDomainServer

DNS proxy rule (domain server) entry for domain-specific DNS resolution.

| Attribute   | Type        | Required | Default | Description                                           |
|-------------|-------------|----------|---------|-------------------------------------------------------|
| name        | str         | Yes      | None    | Proxy rule name.                                      |
| cacheable   | bool        | No       | None    | Enable caching for this DNS proxy rule.               |
| domain_name | List[str]   | No       | None    | Domain names that will be matched. Alias: `domain-name`.|
| primary     | str         | Yes      | None    | Primary DNS server IP address.                        |
| secondary   | str         | No       | None    | Secondary DNS server IP address.                      |

### DnsProxyStaticEntry

Static domain name mapping entry for direct name-to-address resolution.

| Attribute | Type        | Required | Default | Description                                           |
|-----------|-------------|----------|---------|-------------------------------------------------------|
| name      | str         | Yes      | None    | Static entry name. Max 31 chars.                      |
| domain    | str         | Yes      | None    | Fully qualified domain name. Max 255 chars.           |
| address   | List[str]   | Yes      | None    | Resolved IP addresses.                                |

### DnsProxyTcpQueries

TCP queries configuration.

| Attribute            | Type | Required | Default | Description                                                |
|----------------------|------|----------|---------|------------------------------------------------------------|
| enabled              | bool | Yes      | None    | Turn on forwarding of TCP DNS queries.                     |
| max_pending_requests | int  | No       | None    | Upper limit on concurrent TCP DNS requests (64-256). Alias: `max-pending-requests`.|

### DnsProxyUdpQueries

UDP queries configuration.

| Attribute | Type              | Required | Default | Description                              |
|-----------|-------------------|----------|---------|------------------------------------------|
| retries   | DnsProxyUdpRetries| No       | None    | Retry configuration for UDP queries.     |

### DnsProxyUdpRetries

UDP query retry configuration.

| Attribute | Type | Required | Default | Description                                                |
|-----------|------|----------|---------|------------------------------------------------------------|
| interval  | int  | No       | None    | Time in seconds for another request to be sent (1-30).     |
| attempts  | int  | No       | None    | Maximum number of retries before trying next server (1-30).|

### DnsProxyCacheMaxTtl

Cache max TTL configuration.

| Attribute    | Type | Required | Default | Description                                                        |
|--------------|------|----------|---------|--------------------------------------------------------------------|
| enabled      | bool | Yes      | None    | Enable max TTL for this DNS object.                                |
| time_to_live | int  | No       | None    | Time in seconds after which entry is cleared (60-86400). Alias: `time-to-live`.|

### DnsProxyCache

DNS cache configuration.

| Attribute  | Type                | Required | Default | Description                                           |
|------------|---------------------|----------|---------|-------------------------------------------------------|
| enabled    | bool                | Yes      | None    | Turn on caching for this DNS object.                  |
| cache_edns | bool                | No       | None    | Cache EDNS UDP response. Alias: `cache-edns`.         |
| max_ttl    | DnsProxyCacheMaxTtl | No       | None    | Maximum TTL configuration. Alias: `max-ttl`.          |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a proxy (`DnsProxyCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.
- When the `name` field exceeds the maximum length of 31 characters.
- When `max_pending_requests` in `DnsProxyTcpQueries` is outside the range of 64-256.
- When `interval` or `attempts` in `DnsProxyUdpRetries` is outside the range of 1-30.
- When `time_to_live` in `DnsProxyCacheMaxTtl` is outside the range of 60-86400.

## Model Validators

### Container Validation in `DnsProxyCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a DNS Proxy

#### Using a Dictionary

```python
from scm.models.network import DnsProxyCreateModel

proxy_data = {
    "name": "corp-dns-proxy",
    "enabled": True,
    "default": {
        "primary": "8.8.8.8",
        "secondary": "8.8.4.4"
    },
    "interface": ["ethernet1/1"],
    "folder": "Networking",
}

# Validate and create model instance
proxy = DnsProxyCreateModel(**proxy_data)
payload = proxy.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import DnsProxyCreateModel
from scm.models.network.dns_proxy import (
    DnsProxyDefaultServer,
    DnsProxyDomainServer,
    DnsProxyCache,
    DnsProxyCacheMaxTtl,
)

# Create DNS proxy with sub-models
proxy = DnsProxyCreateModel(
    name="advanced-dns-proxy",
    enabled=True,
    default=DnsProxyDefaultServer(
        primary="10.0.0.1",
        secondary="10.0.0.2"
    ),
    domain_servers=[
        DnsProxyDomainServer(
            name="internal-rule",
            domain_name=["*.corp.example.com"],
            primary="10.1.0.1",
            cacheable=True
        )
    ],
    cache=DnsProxyCache(
        enabled=True,
        cache_edns=False,
        max_ttl=DnsProxyCacheMaxTtl(
            enabled=True,
            time_to_live=3600
        )
    ),
    folder="Networking",
)
payload = proxy.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Using Hyphenated Field Names (API Aliases)

```python
from scm.models.network import DnsProxyCreateModel

# You can use the hyphenated API field names thanks to populate_by_name=True
proxy_data = {
    "name": "alias-example",
    "enabled": True,
    "default": {
        "primary": "8.8.8.8"
    },
    "domain-servers": [
        {
            "name": "internal",
            "domain-name": ["*.internal.com"],
            "primary": "10.0.0.1"
        }
    ],
    "tcp-queries": {
        "enabled": True,
        "max-pending-requests": 128
    },
    "cache": {
        "enabled": True,
        "cache-edns": True,
        "max-ttl": {
            "enabled": True,
            "time-to-live": 7200
        }
    },
    "folder": "Networking",
}

proxy = DnsProxyCreateModel(**proxy_data)
payload = proxy.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a DNS Proxy

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing proxy
existing = client.dns_proxy.fetch(name="corp-dns-proxy", folder="Networking")

# Update the default DNS servers
existing.default = {"primary": "1.1.1.1", "secondary": "1.0.0.1"}

# Pass modified object to update()
updated = client.dns_proxy.update(existing)
print(f"Updated proxy: {updated.name}")
```
