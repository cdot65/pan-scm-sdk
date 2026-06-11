# GlobalProtect Forwarding Profile Regional and Custom Proxy Models

## Overview

The Forwarding Profile Regional and Custom Proxy models provide a structured way to manage proxy servers, connectivity preferences, and Prisma Access locations for GlobalProtect forwarding profiles in Palo Alto Networks' Strata Cloud Manager. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `ForwardingProfileRegionalAndCustomProxyBaseModel`: Base model with fields common to all operations
- `ForwardingProfileRegionalAndCustomProxyCreateModel`: Model for creating new proxies
- `ForwardingProfileRegionalAndCustomProxyUpdateModel`: Model for updating existing proxies (adds `id`)
- `ForwardingProfileRegionalAndCustomProxyResponseModel`: Response model for proxy operations (adds `id`)
- `RegionalProxyServer`: A proxy server definition (`fqdn`, `port`, `location`)
- `RegionalProxyConnectivityPreference`: A connectivity preference entry (`name`, `enabled`)
- `RegionalProxyPrismaAccessLocation`: A Prisma Access location entry (`name`, `locations`)
- `RegionalProxyType`: Enum for proxy types
- `RegionalProxyConnectivityName`: Enum for connectivity preference names
- `RegionalProxyFallbackOption`: Enum for fallback options
- `RegionalProxyLocationPreference`: Enum for location preferences

Request models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The response model uses `extra="ignore"` for forward compatibility.

## Attributes

| Attribute                 | Type                                        | Required | Default      | Description                                                                  |
|---------------------------|---------------------------------------------|----------|--------------|------------------------------------------------------------------------------|
| `name`                    | `str`                                       | Yes      | None         | Name of the proxy. Max length: 64 chars. Pattern: `^[0-9a-zA-Z._-]+$`         |
| `type`                    | `RegionalProxyType`                         | No       | `gp-and-pac` | Proxy type                                                                    |
| `description`             | `str`                                       | No       | None         | Description of the proxy. Max length: 1023 chars                              |
| `proxy_1`                 | `RegionalProxyServer`                       | No       | None         | Primary proxy server                                                          |
| `proxy_2`                 | `RegionalProxyServer`                       | No       | None         | Secondary proxy server                                                        |
| `connectivity_preference` | `List[RegionalProxyConnectivityPreference]` | No       | None         | Connectivity preference entries                                               |
| `fallback_option`         | `RegionalProxyFallbackOption`               | No       | None         | Fallback option                                                               |
| `location_preference`     | `RegionalProxyLocationPreference`           | No       | None         | Location preference                                                           |
| `prisma_access_locations` | `List[RegionalProxyPrismaAccessLocation]`   | No       | None         | Prisma Access locations (Americas, Europe, and Asia-Pacific)                  |
| `id`                      | `UUID`                                      | Yes*     | None         | UUID of the proxy                                                             |

\* Present in `UpdateModel` and `ResponseModel` only

### RegionalProxyServer

| Attribute  | Type  | Required | Description                                            |
|------------|-------|----------|--------------------------------------------------------|
| `fqdn`     | `str` | No       | Fully qualified domain name. Max length: 255 chars     |
| `port`     | `int` | No       | Proxy port (1-65535)                                   |
| `location` | `str` | No       | Proxy location                                         |

### RegionalProxyConnectivityPreference

| Attribute | Type                            | Required | Description                          |
|-----------|---------------------------------|----------|--------------------------------------|
| `name`    | `RegionalProxyConnectivityName` | Yes      | Connectivity preference name         |
| `enabled` | `bool`                          | No       | Whether the preference is enabled    |

### RegionalProxyPrismaAccessLocation

| Attribute   | Type        | Required | Description                                            |
|-------------|-------------|----------|--------------------------------------------------------|
| `name`      | `str`       | Yes      | Region name (one of 'americas', 'europe', 'apac')      |
| `locations` | `List[str]` | No       | List of locations in that region                       |

## Enumerations

### RegionalProxyType

| Value        | Description                       |
|--------------|-----------------------------------|
| `GP_AND_PAC` | GlobalProtect and PAC file proxy  |
| `ZTNA_AGENT` | ZTNA agent proxy                  |

### RegionalProxyConnectivityName

| Value    | Description       |
|----------|-------------------|
| `TUNNEL` | Tunnel            |
| `PROXY`  | Proxy             |
| `ADNS`   | ADNS              |
| `MASQUE` | MASQUE            |

### RegionalProxyFallbackOption

| Value       | Description |
|-------------|-------------|
| `FAIL_OPEN` | Fail open   |
| `FAIL_SAFE` | Fail safe   |

### RegionalProxyLocationPreference

| Value            | Description                          |
|------------------|--------------------------------------|
| `BEST_AVAILABLE` | Best available Prisma Access location |
| `SPECIFIC`       | Specific Prisma Access location       |

## Usage Example

```python
from scm.client import Scm
from scm.models.mobile_agent import (
    ForwardingProfileRegionalAndCustomProxyCreateModel,
)

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a regional and custom proxy using a model
proxy = ForwardingProfileRegionalAndCustomProxyCreateModel(
    name="emea-proxy",
    type="gp-and-pac",
    proxy_1={"fqdn": "proxy1.example.com", "port": 8080, "location": "Frankfurt"},
    fallback_option="fail-open",
)

# Convert the model to a dictionary for the API call
payload = proxy.model_dump(exclude_unset=True)
result = client.forwarding_profile_regional_and_custom_proxy.create(payload)
print(f"Created proxy: {result.id}")
```

## Related Documentation

- [Forwarding Profile Regional and Custom Proxies Configuration](../../config/mobile_agent/forwarding_profile_regional_and_custom_proxies.md)
- [Mobile Agent Models](index.md)
