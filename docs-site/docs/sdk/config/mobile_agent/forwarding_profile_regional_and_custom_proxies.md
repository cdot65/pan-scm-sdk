# GlobalProtect Forwarding Profile Regional and Custom Proxies Configuration Object

Manages GlobalProtect forwarding profile regional and custom proxies in Palo Alto Networks Strata Cloud Manager. Regional and custom proxies define proxy servers, connectivity preferences, and Prisma Access locations referenced by forwarding profiles.

## Class Overview

The `ForwardingProfileRegionalAndCustomProxies` class inherits from `BaseObject` and provides CRUD operations for GlobalProtect forwarding profile regional and custom proxy objects.

### Methods

| Method     | Description                   | Parameters                                                                          | Return Type                                                   |
|------------|-------------------------------|--------------------------------------------------------------------------------------|----------------------------------------------------------------|
| `create()` | Creates a new proxy           | `data: Dict[str, Any]`, `folder: str`                                                | `ForwardingProfileRegionalAndCustomProxyResponseModel`         |
| `get()`    | Retrieves a proxy by ID       | `object_id: Union[str, UUID]`                                                        | `ForwardingProfileRegionalAndCustomProxyResponseModel`         |
| `update()` | Updates an existing proxy     | `regional_and_custom_proxy: ForwardingProfileRegionalAndCustomProxyUpdateModel`      | `ForwardingProfileRegionalAndCustomProxyResponseModel`         |
| `delete()` | Deletes a proxy               | `object_id: Union[str, UUID]`                                                        | `None`                                                         |
| `list()`   | Lists proxies                 | `folder: str`, `name: Optional[str]`                                                 | `List[ForwardingProfileRegionalAndCustomProxyResponseModel]`   |
| `fetch()`  | Gets a proxy by name          | `name: str`, `folder: str`                                                           | `ForwardingProfileRegionalAndCustomProxyResponseModel`         |

### Model Attributes

| Attribute                 | Type                                        | Required | Default      | Description                                          |
|---------------------------|---------------------------------------------|----------|--------------|------------------------------------------------------|
| `name`                    | str                                         | Yes      | None         | Name of the proxy (max 64 chars)                     |
| `type`                    | RegionalProxyType                           | No       | `gp-and-pac` | Proxy type (`gp-and-pac` or `ztna-agent`)            |
| `description`             | str                                         | No       | None         | Description of the proxy (max 1023)                  |
| `proxy_1`                 | RegionalProxyServer                         | No       | None         | Primary proxy server (fqdn, port, location)          |
| `proxy_2`                 | RegionalProxyServer                         | No       | None         | Secondary proxy server (fqdn, port, location)        |
| `connectivity_preference` | List[RegionalProxyConnectivityPreference]   | No       | None         | Connectivity preferences (tunnel/proxy/adns/masque)  |
| `fallback_option`         | RegionalProxyFallbackOption                 | No       | None         | `fail-open` or `fail-safe`                           |
| `location_preference`     | RegionalProxyLocationPreference             | No       | None         | `best-available-pa-location` or `specific-pa-location` |
| `prisma_access_locations` | List[RegionalProxyPrismaAccessLocation]     | No       | None         | Prisma Access locations per region                   |
| `id`                      | UUID                                        | Yes*     | None         | UUID of the proxy                                    |

\* Present in update and response models only. The `folder` ("Mobile Users") is passed as a query parameter on `create()` and `list()`, not as a model field.

### Exceptions

| Exception                    | HTTP Code | Description                          |
|------------------------------|-----------|--------------------------------------|
| `InvalidObjectError`         | 400       | Invalid data, folder, or response    |
| `MissingQueryParameterError` | 400       | Missing required parameters          |
| `ObjectNotPresentError`      | 404       | Regional and custom proxy not found  |
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

proxies = client.forwarding_profile_regional_and_custom_proxy
```

## Methods

### List Regional and Custom Proxies

```python
all_proxies = client.forwarding_profile_regional_and_custom_proxy.list()

for proxy in all_proxies:
    print(f"Name: {proxy.name}, Type: {proxy.type}")
```

### Fetch a Regional and Custom Proxy

```python
proxy = client.forwarding_profile_regional_and_custom_proxy.fetch(
    name="emea-proxy",
    folder="Mobile Users",
)
print(f"Found proxy: {proxy.name}")
```

### Create a Regional and Custom Proxy

```python
proxy_config = {
    "name": "emea-proxy",
    "type": "gp-and-pac",
    "description": "EMEA regional proxy",
    "proxy_1": {
        "fqdn": "proxy1.example.com",
        "port": 8080,
        "location": "Frankfurt",
    },
    "connectivity_preference": [
        {"name": "tunnel", "enabled": True},
        {"name": "proxy", "enabled": True},
    ],
    "fallback_option": "fail-open",
    "location_preference": "specific-pa-location",
    "prisma_access_locations": [
        {"name": "europe", "locations": ["frankfurt", "paris"]},
    ],
}
new_proxy = client.forwarding_profile_regional_and_custom_proxy.create(proxy_config)
print(f"Created proxy with ID: {new_proxy.id}")
```

### Update a Regional and Custom Proxy

```python
from scm.models.mobile_agent import ForwardingProfileRegionalAndCustomProxyUpdateModel

existing = client.forwarding_profile_regional_and_custom_proxy.fetch(name="emea-proxy")

update_model = ForwardingProfileRegionalAndCustomProxyUpdateModel(
    id=existing.id,
    name=existing.name,
    fallback_option="fail-safe",
)
updated = client.forwarding_profile_regional_and_custom_proxy.update(update_model)
```

### Delete a Regional and Custom Proxy

```python
client.forwarding_profile_regional_and_custom_proxy.delete(
    "123e4567-e89b-12d3-a456-426655440000"
)
```

## Related Documentation

- [Forwarding Profile Regional and Custom Proxy Models](../../models/mobile_agent/forwarding_profile_regional_and_custom_proxies_models.md)
- [Mobile Agent Configuration](index.md)
