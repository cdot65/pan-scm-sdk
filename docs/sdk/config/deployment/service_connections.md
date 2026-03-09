# Service Connections Configuration Object

Manages service connection objects for establishing connectivity to cloud service providers in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `ServiceConnection` class inherits from `BaseObject` and provides CRUD operations for service connection objects.

### Methods

| Method     | Description                              | Parameters                                         | Return Type                            |
|------------|------------------------------------------|----------------------------------------------------|----------------------------------------|
| `create()` | Creates a new service connection         | `data: Dict[str, Any]`                             | `ServiceConnectionResponseModel`       |
| `get()`    | Retrieves a service connection by ID     | `object_id: str`                                   | `ServiceConnectionResponseModel`       |
| `update()` | Updates an existing service connection   | `service_connection: ServiceConnectionUpdateModel` | `ServiceConnectionResponseModel`       |
| `delete()` | Deletes a service connection             | `object_id: str`                                   | `None`                                 |
| `list()`   | Lists service connections with filtering | `name: Optional[str]`, `**filters`                 | `List[ServiceConnectionResponseModel]` |
| `fetch()`  | Gets service connection by name          | `name: str`                                        | `ServiceConnectionResponseModel`       |

### Model Attributes

| Attribute                | Type              | Required | Default             | Description                               |
|--------------------------|-------------------|----------|---------------------|-------------------------------------------|
| `name`                   | str               | Yes      | None                | Name of service connection (max 63 chars) |
| `id`                     | UUID              | Yes*     | None                | Unique identifier (*response only)        |
| `folder`                 | str               | No       | Service Connections | Folder containing the service connection  |
| `ipsec_tunnel`           | str               | Yes      | None                | IPsec tunnel for the service connection   |
| `onboarding_type`        | OnboardingType    | No       | classic             | Onboarding type                           |
| `region`                 | str               | Yes      | None                | Region for the service connection         |
| `backup_SC`              | str               | No       | None                | Backup service connection                 |
| `bgp_peer`               | BgpPeerModel      | No       | None                | BGP peer configuration                    |
| `nat_pool`               | str               | No       | None                | NAT pool                                  |
| `no_export_community`    | NoExportCommunity | No       | None                | No export community configuration         |
| `protocol`               | ProtocolModel     | No       | None                | Protocol configuration                    |
| `qos`                    | QosModel          | No       | None                | QoS configuration                         |
| `secondary_ipsec_tunnel` | str               | No       | None                | Secondary IPsec tunnel                    |
| `source_nat`             | bool              | No       | None                | Enable source NAT                         |
| `subnets`                | List[str]         | No       | None                | Subnets for the service connection        |

\* Only required for response models

### Exceptions

| Exception                    | HTTP Code | Description                               |
|------------------------------|-----------|-------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid service connection data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters               |
| `ObjectNotPresentError`      | 404       | Service connection not found              |
| `AuthenticationError`        | 401       | Authentication failed                     |
| `ServerError`                | 500       | Internal server error                     |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

service_connections = client.service_connection
```

## Methods

### List Service Connections

```python
all_connections = client.service_connection.list()

for conn in all_connections:
    print(f"Service Connection: {conn.name}, Region: {conn.region}")
```

**Filtering responses:**

```python
# Filter by name
filtered_connections = client.service_connection.list(name="aws")

# Filter by region
us_east_connections = client.service_connection.list(region="us-east-1")
```

**Controlling pagination with max_limit:**

```python
client.service_connection.max_limit = 500

all_connections = client.service_connection.list()
```

### Fetch a Service Connection

```python
service_connection = client.service_connection.fetch(name="aws-service-connection")
print(f"Found service connection: {service_connection.name}")
```

### Create a Service Connection

```python
service_connection_config = {
    "name": "aws-service-connection",
    "ipsec_tunnel": "aws-ipsec-tunnel",
    "region": "us-east-1",
    "onboarding_type": "classic",
    "subnets": ["10.0.0.0/24", "192.168.1.0/24"],
    "bgp_peer": {
        "local_ip_address": "192.168.1.1",
        "peer_ip_address": "192.168.1.2",
    },
    "protocol": {
        "bgp": {
            "enable": True,
            "peer_as": "65000",
        }
    },
    "source_nat": True,
}
service_connection = client.service_connection.create(service_connection_config)
```

### Update a Service Connection

```python
existing_connection = client.service_connection.fetch(name="aws-service-connection")

existing_connection.subnets = ["10.0.0.0/24", "192.168.1.0/24", "172.16.0.0/24"]
existing_connection.source_nat = False

updated_connection = client.service_connection.update(existing_connection)
```

### Delete a Service Connection

```python
client.service_connection.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a Service Connection by ID

```python
service_connection_by_id = client.service_connection.get(service_connection.id)
print(f"Retrieved service connection: {service_connection_by_id.name}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Service Connections"],
    description="Added new service connection",
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
    service_connection_config = {
        "name": "test-connection",
        "ipsec_tunnel": "test-tunnel",
        "region": "us-east-1",
        "onboarding_type": "classic",
        "subnets": ["10.0.0.0/24"]
    }
    new_connection = client.service_connection.create(service_connection_config)
    result = client.commit(
        folders=["Service Connections"],
        description="Added test service connection",
        sync=True
    )
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid service connection data: {e.message}")
except ObjectNotPresentError as e:
    print(f"Service connection not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Service Connection Models](../../models/deployment/service_connections_models.md#Overview)
- [Deployment Overview](index.md)
- [API Client](../../client.md)
