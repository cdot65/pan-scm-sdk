# Internal DNS Servers Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Internal DNS Servers Model Attributes](#internal-dns-servers-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Internal DNS Servers](#creating-internal-dns-servers)
    - [Retrieving Internal DNS Servers](#retrieving-internal-dns-servers)
    - [Updating Internal DNS Servers](#updating-internal-dns-servers)
    - [Listing Internal DNS Servers](#listing-internal-dns-servers)
    - [Filtering Internal DNS Servers](#filtering-internal-dns-servers)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Internal DNS Servers](#deleting-internal-dns-servers)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Full Script Examples](#full-script-examples)
10. [Related Models](#related-models)

## Overview

The `InternalDnsServers` class provides functionality to manage internal DNS server objects in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting internal DNS server configurations.

## Core Methods

| Method     | Description                              | Parameters                                  | Return Type                             |
|------------|------------------------------------------|---------------------------------------------|-----------------------------------------|
| `create()` | Creates a new internal DNS server object | `data: Dict[str, Any]`                      | `InternalDnsServersResponseModel`       |
| `get()`    | Retrieves a DNS server by ID             | `object_id: str`                            | `InternalDnsServersResponseModel`       |
| `update()` | Updates an existing DNS server           | `dns_server: InternalDnsServersUpdateModel` | `InternalDnsServersResponseModel`       |
| `delete()` | Deletes a DNS server                     | `object_id: str`                            | `None`                                  |
| `list()`   | Lists DNS servers with filtering         | `name: str`, `**filters`                    | `List[InternalDnsServersResponseModel]` |
| `fetch()`  | Gets DNS server by name                  | `name: str`                                 | `InternalDnsServersResponseModel`       |

## Internal DNS Servers Model Attributes

| Attribute      | Type           | Required | Description                                   |
|----------------|----------------|----------|-----------------------------------------------|
| `name`         | str            | Yes      | Name of the DNS server (max 63 chars)         |
| `id`           | UUID           | Yes*     | Unique identifier (*response only)            |
| `domain_name`  | List[str]      | Yes      | List of DNS domain names                      |
| `primary`      | IPvAnyAddress  | Yes      | IP address of the primary DNS server          |
| `secondary`    | IPvAnyAddress  | No       | IP address of the secondary DNS server        |

## Exceptions

| Exception                    | HTTP Code | Description                         |
|------------------------------|-----------|-------------------------------------|
| `InvalidObjectError`         | 400       | Invalid DNS server data or format   |
| `MissingQueryParameterError` | 400       | Missing required parameters         |
| `ObjectNotPresentError`      | 404       | DNS server not found                |
| `AuthenticationError`        | 401       | Authentication failed               |
| `ServerError`                | 500       | Internal server error               |

## Basic Configuration

The Internal DNS Servers service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Internal DNS Servers service directly through the client
# No need to create a separate InternalDnsServers instance
dns_servers = client.internal_dns_servers
```

</div>

### Traditional Service Instantiation (Legacy)

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.deployment import InternalDnsServers

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize InternalDnsServers object explicitly
dns_servers = InternalDnsServers(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Internal DNS Servers

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Prepare DNS server configuration
dns_server_config = {
   "name": "main-dns-server",
   "domain_name": ["example.com", "internal.example.com"],
   "primary": "192.168.1.10",
   "secondary": "192.168.1.11"
}

# Create the DNS server object using the unified client interface
dns_server = client.internal_dns_servers.create(dns_server_config)

print(f"Created DNS server: {dns_server.name} with ID: {dns_server.id}")
```

</div>

### Retrieving Internal DNS Servers

<div class="termy">

<!-- termynal -->

```python
# Fetch by name
dns_server = client.internal_dns_servers.fetch(name="main-dns-server")
print(f"Found DNS server: {dns_server.name}")
print(f"Domain names: {dns_server.domain_name}")
print(f"Primary DNS: {dns_server.primary}")
print(f"Secondary DNS: {dns_server.secondary}")

# Get by ID
dns_server_id = "123e4567-e89b-12d3-a456-426655440000"
dns_server_by_id = client.internal_dns_servers.get(dns_server_id)
print(f"Retrieved DNS server: {dns_server_by_id.name}")
```

</div>

### Updating Internal DNS Servers

<div class="termy">

<!-- termynal -->

```python
from scm.models.deployment import InternalDnsServersUpdateModel

# Fetch existing DNS server
existing_dns_server = client.internal_dns_servers.fetch(name="main-dns-server")

# Create update model with ID and only fields to update
update_model = InternalDnsServersUpdateModel(
    id=existing_dns_server.id,
    domain_name=["example.com", "internal.example.com", "new-domain.example.com"],
    secondary="192.168.1.12"  # Update the secondary DNS server
)

# Perform update
updated_dns_server = client.internal_dns_servers.update(update_model)

print(f"Updated DNS server: {updated_dns_server.name}")
print(f"Updated domain names: {updated_dns_server.domain_name}")
print(f"Updated secondary DNS: {updated_dns_server.secondary}")
```

</div>

### Listing Internal DNS Servers

<div class="termy">

<!-- termynal -->

```python
# List all DNS servers
all_dns_servers = client.internal_dns_servers.list()

# Process results
for dns in all_dns_servers:
   print(f"Name: {dns.name}, Primary DNS: {dns.primary}")

# Filter by name
filtered_dns_servers = client.internal_dns_servers.list(name="main")

# Process filtered results
for dns in filtered_dns_servers:
   print(f"Filtered DNS server: {dns.name}")
   print(f"Domain names: {dns.domain_name}")
```

</div>

### Filtering Internal DNS Servers

<div class="termy">

<!-- termynal -->

```python
# Filter by primary IP address
primary_ip_filter = client.internal_dns_servers.list(primary="192.168.1.10")
print(f"DNS servers with primary IP 192.168.1.10: {len(primary_ip_filter)}")

# Filter by domain name (partial match)
domain_filter = client.internal_dns_servers.list(domain_name="example")
print(f"DNS servers with 'example' in domain name: {len(domain_filter)}")

# Combine multiple filters
combined_filter = client.internal_dns_servers.list(
    primary="192.168.1.10",
    domain_name="example"
)
print(f"DNS servers matching both filters: {len(combined_filter)}")

# Process filtered results
for dns in combined_filter:
    print(f"Filtered DNS server: {dns.name}")
    print(f"Primary IP: {dns.primary}")
    print(f"Domain names: {dns.domain_name}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved.

**Example:**

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.config.deployment import InternalDnsServers

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Create a custom InternalDnsServers instance with max_limit
dns_servers_service = InternalDnsServers(client, max_limit=4000)
all_dns_servers = dns_servers_service.list()

# Option 2: Use the unified client interface directly
# This will use the default max_limit (2500)
all_dns_servers = client.internal_dns_servers.list()

# Both options will auto-paginate through all available objects.
# The DNS servers are fetched in chunks according to the max_limit.
```

</div>

### Deleting Internal DNS Servers

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
dns_server_id = "123e4567-e89b-12d3-a456-426655440000"
client.internal_dns_servers.delete(dns_server_id)
print(f"Deleted DNS server with ID: {dns_server_id}")

# Fetch by name, then delete by ID
dns_server = client.internal_dns_servers.fetch(name="main-dns-server")
client.internal_dns_servers.delete(dns_server.id)
print(f"Deleted DNS server: {dns_server.name}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

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
   # Create DNS server configuration
   dns_config = {
      "name": "test-dns-server",
      "domain_name": ["example.com"],
      "primary": "192.168.1.10"
   }

   # Create the DNS server using the unified client interface
   new_dns_server = client.internal_dns_servers.create(dns_config)
   print(f"Created DNS server: {new_dns_server.name}")

   # Try to retrieve non-existent DNS server
   try:
      non_existent = client.internal_dns_servers.fetch(name="non-existent-server")
   except ObjectNotPresentError as e:
      print(f"DNS server not found: {e.message}")

except InvalidObjectError as e:
   print(f"Invalid DNS server data: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
except Exception as e:
   print(f"Unexpected error: {str(e)}")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.internal_dns_servers`) for streamlined code
    - Create a single client instance and reuse it across your application
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Data Validation**
    - Always provide all required fields: `name`, `domain_name`, and `primary`
    - Ensure domain_name is a valid list of domain names
    - Validate IP addresses before creating or updating
    - Use appropriate error handling for validation failures

3. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

4. **Performance**
    - Reuse client instances
    - Use appropriate pagination for list operations
    - Implement proper retry mechanisms for network failures
    - Cache frequently accessed objects

5. **Security**
    - Follow the principle of least privilege
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication handling

## Full Script Examples

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

def create_dns_server():
    """Create a new internal DNS server."""
    try:
        # Prepare DNS server configuration
        dns_config = {
            "name": "main-dns-server",
            "domain_name": ["example.com", "internal.example.com"],
            "primary": "192.168.1.10",
            "secondary": "192.168.1.11"
        }
        
        # Create the DNS server
        dns_server = client.internal_dns_servers.create(dns_config)
        print(f"Created DNS server: {dns_server.name} with ID: {dns_server.id}")
        return dns_server.id
    except InvalidObjectError as e:
        print(f"Invalid DNS server data: {e.message}")
        return None

def update_dns_server(dns_id):
    """Update an existing internal DNS server."""
    from scm.models.deployment import InternalDnsServersUpdateModel
    
    try:
        # Create update model
        update_model = InternalDnsServersUpdateModel(
            id=dns_id,
            domain_name=["example.com", "internal.example.com", "new-domain.example.com"],
            secondary="192.168.1.12"
        )
        
        # Perform update
        updated = client.internal_dns_servers.update(update_model)
        print(f"Updated DNS server: {updated.name}")
        print(f"Updated domain names: {updated.domain_name}")
        print(f"Updated secondary DNS: {updated.secondary}")
    except ObjectNotPresentError as e:
        print(f"DNS server not found: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid update data: {e.message}")

def list_dns_servers():
    """List all internal DNS servers."""
    dns_servers = client.internal_dns_servers.list()
    print(f"Found {len(dns_servers)} DNS servers:")
    for dns in dns_servers:
        print(f"  - {dns.name}: Primary={dns.primary}, Domains={dns.domain_name}")

def delete_dns_server(dns_id):
    """Delete an internal DNS server by ID."""
    try:
        client.internal_dns_servers.delete(dns_id)
        print(f"Deleted DNS server with ID: {dns_id}")
    except ObjectNotPresentError as e:
        print(f"DNS server not found: {e.message}")

def main():
    """Main function to demonstrate DNS server operations."""
    # Create a new DNS server
    dns_id = create_dns_server()
    if not dns_id:
        return
    
    # Update the DNS server
    update_dns_server(dns_id)
    
    # List all DNS servers
    list_dns_servers()
    
    # Delete the DNS server
    delete_dns_server(dns_id)

if __name__ == "__main__":
    main()
```

## Related Models

- [InternalDnsServersCreateModel](../../models/deployment/internal_dns_servers_models.md#Overview)
- [InternalDnsServersUpdateModel](../../models/deployment/internal_dns_servers_models.md#Overview)
- [InternalDnsServersResponseModel](../../models/deployment/internal_dns_servers_models.md#Overview)
