# Internal DNS Servers Configuration Object

Manages internal DNS server objects for domain name resolution in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `InternalDnsServers` class inherits from `BaseObject` and provides CRUD operations for internal DNS server configurations.

### Methods

| Method     | Description                              | Parameters                                  | Return Type                             |
|------------|------------------------------------------|---------------------------------------------|-----------------------------------------|
| `create()` | Creates a new internal DNS server object | `data: Dict[str, Any]`                      | `InternalDnsServersResponseModel`       |
| `get()`    | Retrieves a DNS server by ID             | `object_id: str`                            | `InternalDnsServersResponseModel`       |
| `update()` | Updates an existing DNS server           | `dns_server: InternalDnsServersUpdateModel` | `InternalDnsServersResponseModel`       |
| `delete()` | Deletes a DNS server                     | `object_id: str`                            | `None`                                  |
| `list()`   | Lists DNS servers with filtering         | `name: str`, `**filters`                    | `List[InternalDnsServersResponseModel]` |
| `fetch()`  | Gets DNS server by name                  | `name: str`                                 | `InternalDnsServersResponseModel`       |

### Model Attributes

| Attribute     | Type          | Required | Default | Description                            |
|---------------|---------------|----------|---------|----------------------------------------|
| `name`        | str           | Yes      | None    | Name of the DNS server (max 63 chars)  |
| `id`          | UUID          | Yes*     | None    | Unique identifier (*response only)     |
| `domain_name` | List[str]     | Yes      | None    | List of DNS domain names               |
| `primary`     | IPvAnyAddress | Yes      | None    | IP address of the primary DNS server   |
| `secondary`   | IPvAnyAddress | No       | None    | IP address of the secondary DNS server |

\* Only required for response models

### Exceptions

| Exception                    | HTTP Code | Description                       |
|------------------------------|-----------|-----------------------------------|
| `InvalidObjectError`         | 400       | Invalid DNS server data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters       |
| `ObjectNotPresentError`      | 404       | DNS server not found              |
| `AuthenticationError`        | 401       | Authentication failed             |
| `ServerError`                | 500       | Internal server error             |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

dns_servers = client.internal_dns_server
```

## Methods

### List Internal DNS Servers

```python
all_dns_servers = client.internal_dns_server.list()

for dns in all_dns_servers:
    print(f"Name: {dns.name}, Primary DNS: {dns.primary}")
```

**Filtering responses:**

```python
# Filter by name
filtered_dns_servers = client.internal_dns_server.list(name="main")

# Filter by primary IP address
primary_ip_filter = client.internal_dns_server.list(primary="192.168.1.10")

# Combine multiple filters
combined_filter = client.internal_dns_server.list(
    primary="192.168.1.10",
    domain_name="example"
)
```

**Controlling pagination with max_limit:**

```python
client.internal_dns_server.max_limit = 4000

all_dns_servers = client.internal_dns_server.list()
```

### Fetch an Internal DNS Server

```python
dns_server = client.internal_dns_server.fetch(name="main-dns-server")
print(f"Found DNS server: {dns_server.name}")
print(f"Domain names: {dns_server.domain_name}")
```

### Create an Internal DNS Server

```python
dns_server_config = {
    "name": "main-dns-server",
    "domain_name": ["example.com", "internal.example.com"],
    "primary": "192.168.1.10",
    "secondary": "192.168.1.11"
}
dns_server = client.internal_dns_server.create(dns_server_config)
print(f"Created DNS server: {dns_server.name} with ID: {dns_server.id}")
```

### Update an Internal DNS Server

```python
existing_dns_server = client.internal_dns_server.fetch(name="main-dns-server")

existing_dns_server.domain_name = ["example.com", "internal.example.com", "new-domain.example.com"]
existing_dns_server.secondary = "192.168.1.12"

updated_dns_server = client.internal_dns_server.update(existing_dns_server)
```

### Delete an Internal DNS Server

```python
client.internal_dns_server.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get an Internal DNS Server by ID

```python
dns_server_by_id = client.internal_dns_server.get("123e4567-e89b-12d3-a456-426655440000")
print(f"Retrieved DNS server: {dns_server_by_id.name}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    description="Updated internal DNS servers",
    sync=True,
    timeout=300
)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ObjectNotPresentError
)

try:
    dns_config = {
        "name": "test-dns-server",
        "domain_name": ["example.com"],
        "primary": "192.168.1.10"
    }
    new_dns_server = client.internal_dns_server.create(dns_config)

except InvalidObjectError as e:
    print(f"Invalid DNS server data: {e.message}")
except ObjectNotPresentError as e:
    print(f"DNS server not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Internal DNS Server Models](../../models/deployment/internal_dns_servers_models.md#Overview)
- [Deployment Overview](index.md)
- [API Client](../../client.md)
