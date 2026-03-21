# DNS Proxy

The `DnsProxy` class manages DNS proxy configuration objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete DNS proxy configurations. These configurations enable DNS proxy services on firewall interfaces, allowing you to define default DNS servers, domain-specific server rules, static DNS entries, caching behavior, and TCP/UDP query settings.

## Class Overview

```python
from scm.client import Scm

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the DNS Proxy service directly through the client
dns_proxies = client.dns_proxy
```

| Method     | Description                                                    | Parameters                                                                                                                       | Return Type                     |
|------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| `create()` | Creates a new DNS proxy configuration                          | `data: Dict[str, Any]`                                                                                                           | `DnsProxyResponseModel`         |
| `get()`    | Retrieves a DNS proxy by its unique ID                         | `object_id: str`                                                                                                                 | `DnsProxyResponseModel`         |
| `update()` | Updates an existing DNS proxy configuration                    | `proxy: DnsProxyUpdateModel`                                                                                                     | `DnsProxyResponseModel`         |
| `list()`   | Lists DNS proxies with optional filtering                      | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[DnsProxyResponseModel]`   |
| `fetch()`  | Fetches a single DNS proxy by name within a container          | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `DnsProxyResponseModel`         |
| `delete()` | Deletes a DNS proxy by its ID                                  | `object_id: str`                                                                                                                 | `None`                          |

### DNS Proxy Model Attributes

| Attribute        | Type                           | Required | Default | Description                                                       |
|------------------|--------------------------------|----------|---------|-------------------------------------------------------------------|
| `name`           | str                            | Yes      | None    | DNS proxy name. Max 31 chars                                      |
| `id`             | UUID                           | Yes*     | None    | Unique identifier (*response/update only)                         |
| `enabled`        | bool                           | No       | None    | Enable DNS proxy                                                  |
| `default`        | DnsProxyDefaultServer          | No       | None    | Default DNS server configuration                                  |
| `interface`      | List[str]                      | No       | None    | Interfaces on which to enable DNS proxy service                   |
| `domain_servers` | List[DnsProxyDomainServer]     | No       | None    | DNS proxy rules (domain servers). API alias: `domain-servers`     |
| `static_entries` | List[DnsProxyStaticEntry]      | No       | None    | Static domain name mappings. API alias: `static-entries`          |
| `tcp_queries`    | DnsProxyTcpQueries             | No       | None    | TCP queries configuration. API alias: `tcp-queries`               |
| `udp_queries`    | DnsProxyUdpQueries             | No       | None    | UDP queries configuration. API alias: `udp-queries`               |
| `cache`          | DnsProxyCache                  | No       | None    | DNS cache configuration                                           |
| `folder`         | str                            | No**     | None    | Folder location. Max 64 chars                                     |
| `snippet`        | str                            | No**     | None    | Snippet location. Max 64 chars                                    |
| `device`         | str                            | No**     | None    | Device location. Max 64 chars                                     |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

!!! note
    Several fields use aliases to map between Python attribute names (using underscores) and the API's hyphenated field names. For example, `domain_servers` maps to `domain-servers` in the API, `static_entries` maps to `static-entries`, `tcp_queries` maps to `tcp-queries`, and `udp_queries` maps to `udp-queries`. The SDK handles this mapping automatically when serializing and deserializing data.

### Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | DNS proxy name already exists                                                 |
| `ObjectNotPresentError`      | 404       | DNS proxy not found                                                           |
| `ReferenceNotZeroError`      | 409       | DNS proxy still referenced by other objects                                   |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Methods

### List DNS Proxies

```python
# List all DNS proxies in a folder
proxies = client.dns_proxy.list(
   folder="Texas"
)

# Process results
for proxy in proxies:
   print(f"Name: {proxy.name}, Enabled: {proxy.enabled}")
```

#### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters,
you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control
which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return proxies defined exactly in 'Texas'
exact_proxies = client.dns_proxy.list(
   folder='Texas',
   exact_match=True
)

for proxy in exact_proxies:
   print(f"Exact match: {proxy.name} in {proxy.folder}")

# Exclude all proxies from the 'All' folder
no_all_proxies = client.dns_proxy.list(
   folder='Texas',
   exclude_folders=['All']
)

for proxy in no_all_proxies:
   assert proxy.folder != 'All'
   print(f"Filtered out 'All': {proxy.name}")
```

#### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import Scm

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.dns_proxy.max_limit = 4000

# List all proxies - auto-paginates through results
all_proxies = client.dns_proxy.list(folder='Texas')
```

### Fetch a DNS Proxy

```python
# Fetch by name and folder
proxy = client.dns_proxy.fetch(
   name="corp-dns-proxy",
   folder="Texas"
)
print(f"Found proxy: {proxy.name}")

# Get by ID
proxy_by_id = client.dns_proxy.get(proxy.id)
print(f"Retrieved proxy: {proxy_by_id.name}")
```

### Create a DNS Proxy

```python
from scm.client import Scm

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a basic DNS proxy with default server
proxy_data = {
   "name": "corp-dns-proxy",
   "enabled": True,
   "default": {
      "primary": "8.8.8.8",
      "secondary": "8.8.4.4"
   },
   "interface": ["ethernet1/1"],
   "folder": "Texas"
}

new_proxy = client.dns_proxy.create(proxy_data)
print(f"Created DNS proxy with ID: {new_proxy.id}")

# Create a DNS proxy with domain-specific rules and caching
advanced_proxy = {
   "name": "advanced-dns-proxy",
   "enabled": True,
   "default": {
      "primary": "10.0.0.1",
      "secondary": "10.0.0.2"
   },
   "interface": ["ethernet1/1", "ethernet1/2"],
   "domain-servers": [
      {
         "name": "internal-domains",
         "domain-name": ["*.corp.example.com", "*.internal.example.com"],
         "primary": "10.1.0.1",
         "secondary": "10.1.0.2",
         "cacheable": True
      }
   ],
   "static-entries": [
      {
         "name": "app-server",
         "domain": "app.corp.example.com",
         "address": ["10.2.0.100"]
      }
   ],
   "cache": {
      "enabled": True,
      "cache-edns": False,
      "max-ttl": {
         "enabled": True,
         "time-to-live": 3600
      }
   },
   "folder": "Texas"
}

adv_proxy = client.dns_proxy.create(advanced_proxy)
print(f"Created advanced DNS proxy with ID: {adv_proxy.id}")
```

### Update a DNS Proxy

```python
# Fetch existing proxy
existing_proxy = client.dns_proxy.fetch(
   name="corp-dns-proxy",
   folder="Texas"
)

# Update the default DNS servers
existing_proxy.default = {
   "primary": "1.1.1.1",
   "secondary": "1.0.0.1"
}

# Perform update
updated_proxy = client.dns_proxy.update(existing_proxy)
```

### Delete a DNS Proxy

```python
# Delete by ID
proxy_id = "123e4567-e89b-12d3-a456-426655440000"
client.dns_proxy.delete(proxy_id)
```

## Use Cases

#### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated DNS proxy configurations",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

#### Monitoring Jobs

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   NameNotUniqueError,
   ObjectNotPresentError,
   ReferenceNotZeroError
)

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create DNS proxy
   proxy_config = {
      "name": "test-dns-proxy",
      "enabled": True,
      "default": {
         "primary": "8.8.8.8"
      },
      "interface": ["ethernet1/1"],
      "folder": "Texas"
   }

   new_proxy = client.dns_proxy.create(proxy_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added DNS proxy",
      sync=True
   )

   # Check job status
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid proxy data: {e.message}")
except NameNotUniqueError as e:
   print(f"Proxy name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Proxy not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Proxy still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Related Topics

- [DnsProxyBaseModel](../../models/network/dns_proxy_models.md#Overview)
- [DnsProxyCreateModel](../../models/network/dns_proxy_models.md#Overview)
- [DnsProxyUpdateModel](../../models/network/dns_proxy_models.md#Overview)
- [DnsProxyResponseModel](../../models/network/dns_proxy_models.md#Overview)
