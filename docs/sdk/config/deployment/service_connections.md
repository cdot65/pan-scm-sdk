# Service Connections Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Service Connection Model Attributes](#service-connection-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Service Connections](#creating-service-connections)
    - [Retrieving Service Connections](#retrieving-service-connections)
    - [Updating Service Connections](#updating-service-connections)
    - [Listing Service Connections](#listing-service-connections)
    - [Filtering Service Connections](#filtering-service-connections)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Service Connections](#deleting-service-connections)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `ServiceConnection` class provides functionality to manage service connection objects in Palo Alto Networks' Strata Cloud Manager. This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting service connection objects
which are used to establish connectivity to cloud service providers.

## Core Methods

| Method     | Description                              | Parameters                                         | Return Type                            |
|------------|------------------------------------------|----------------------------------------------------|----------------------------------------|
| `create()` | Creates a new service connection         | `data: Dict[str, Any]`                             | `ServiceConnectionResponseModel`       |
| `get()`    | Retrieves a service connection by ID     | `object_id: str`                                   | `ServiceConnectionResponseModel`       |
| `update()` | Updates an existing service connection   | `service_connection: ServiceConnectionUpdateModel` | `ServiceConnectionResponseModel`       |
| `delete()` | Deletes a service connection             | `object_id: str`                                   | `None`                                 |
| `list()`   | Lists service connections with filtering | `name: Optional[str]`, `**filters`                 | `List[ServiceConnectionResponseModel]` |
| `fetch()`  | Gets service connection by name          | `name: str`                                        | `ServiceConnectionResponseModel`       |

## Service Connection Model Attributes

| Attribute                | Type              | Required | Default             | Description                               |
|--------------------------|-------------------|----------|---------------------|-------------------------------------------|
| `name`                   | str               | Yes      | None                | Name of service connection (max 63 chars) |
| `id`                     | UUID              | Yes*     | None                | Unique identifier (*response only)        |
| `folder`                 | str               | No       | Service Connections | Folder containing the service connection  |
| `ipsec_tunnel`           | str               | Yes      | None                | IPsec tunnel for the service connection   |
| `onboarding_type`        | OnboardingType    | No       | classic             | Onboarding type for the service connection|
| `region`                 | str               | Yes      | None                | Region for the service connection         |
| `backup_SC`              | str               | No       | None                | Backup service connection                 |
| `bgp_peer`               | BgpPeerModel      | No       | None                | BGP peer configuration                    |
| `nat_pool`               | str               | No       | None                | NAT pool for the service connection       |
| `no_export_community`    | NoExportCommunity | No       | None                | No export community configuration         |
| `protocol`               | ProtocolModel     | No       | None                | Protocol configuration                    |
| `qos`                    | QosModel          | No       | None                | QoS configuration                         |
| `secondary_ipsec_tunnel` | str               | No       | None                | Secondary IPsec tunnel                    |
| `source_nat`             | bool              | No       | None                | Enable source NAT                         |
| `subnets`                | List[str]         | No       | None                | Subnets for the service connection        |

## Exceptions

| Exception                    | HTTP Code | Description                               |
|------------------------------|-----------|-------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid service connection data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters               |
| `ObjectNotPresentError`      | 404       | Service connection not found              |
| `AuthenticationError`        | 401       | Authentication failed                     |
| `ServerError`                | 500       | Internal server error                     |

## Basic Configuration

The Service Connection service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Service Connection service directly through the client
# No need to create a separate ServiceConnection instance
service_connections = client.service_connection
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.deployment import ServiceConnection

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize ServiceConnection object explicitly
service_connections = ServiceConnection(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Service Connections

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Prepare service connection configuration
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

# Create the service connection
service_connection = client.service_connection.create(service_connection_config)
print(f"Service connection created: {service_connection.name}")
```

### Retrieving Service Connections

```python
# Fetch by name
service_connection = client.service_connection.fetch(name="aws-service-connection")
print(f"Found service connection: {service_connection.name}")

# Get by ID
service_connection_by_id = client.service_connection.get(service_connection.id)
print(f"Retrieved service connection: {service_connection_by_id.name}")
```

### Updating Service Connections

```python
# Fetch existing service connection
existing_connection = client.service_connection.fetch(name="aws-service-connection")

# Update specific attributes
existing_connection.subnets = ["10.0.0.0/24", "192.168.1.0/24", "172.16.0.0/24"]
existing_connection.source_nat = False

# Perform update
updated_connection = client.service_connection.update(existing_connection)
print(f"Updated service connection subnets: {updated_connection.subnets}")
```

### Listing Service Connections

```python
# List all service connections
all_connections = client.service_connection.list()
print(f"Found {len(all_connections)} service connections")

# Process results
for conn in all_connections:
   print(f"Service Connection: {conn.name}, Region: {conn.region}")
```

### Filtering Service Connections

```python
# List service connections with name filter
filtered_connections = client.service_connection.list(name="aws")

# List service connections with region filter
us_east_connections = client.service_connection.list(region="us-east-1")

# Process results
for conn in us_east_connections:
   print(f"Service Connection in US East: {conn.name}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 200. The API itself imposes a maximum allowed value of 1000. If you set `max_limit` higher than 1000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.service_connection.max_limit = 500

# List all service connections - auto-paginates through results
all_connections = client.service_connection.list()

# The connections are fetched in chunks according to the max_limit.
# All results are returned as a single list.
```

### Deleting Service Connections

```python
# Delete by ID
service_connection_id = "123e4567-e89b-12d3-a456-426655440000"
client.service_connection.delete(service_connection_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Service Connections"],
   "description": "Added new service connection",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

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
from scm.client import ScmClient
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   ObjectNotPresentError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create service connection configuration
   service_connection_config = {
      "name": "test-connection",
      "ipsec_tunnel": "test-tunnel",
      "region": "us-east-1",
      "onboarding_type": "classic",
      "subnets": ["10.0.0.0/24", "192.168.1.0/24"]
   }

   # Create the service connection
   new_connection = client.service_connection.create(service_connection_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Service Connections"],
      description="Added test service connection",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid service connection data: {e.message}")
except ObjectNotPresentError as e:
   print(f"Service connection not found: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.service_connection`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

3. **BGP Configuration**
    - When using BGP, ensure all required parameters are provided
    - Validate ASNs and IP addresses before creation
    - Test connectivity after configuration

4. **Performance**
    - Reuse client instances
    - Use appropriate pagination for list operations
    - Implement proper retry mechanisms for network operations

5. **Security**
    - Follow the least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication handling

## Full Script Examples

Refer to the [unified_client_example.py](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/unified_client_example.py) for more examples.

## Related Models

- [ServiceConnectionBaseModel](../../models/deployment/service_connections_models.md#Overview)
- [ServiceConnectionCreateModel](../../models/deployment/service_connections_models.md#Overview)
- [ServiceConnectionUpdateModel](../../models/deployment/service_connections_models.md#Overview)
- [ServiceConnectionResponseModel](../../models/deployment/service_connections_models.md#Overview)
- [BgpPeerModel](../../models/deployment/service_connections_models.md#Overview)
- [BgpProtocolModel](../../models/deployment/service_connections_models.md#Overview)
- [ProtocolModel](../../models/deployment/service_connections_models.md#Overview)
- [QosModel](../../models/deployment/service_connections_models.md#Overview)
- [OnboardingType](../../models/deployment/service_connections_models.md#Overview)
- [NoExportCommunity](../../models/deployment/service_connections_models.md#Overview)
