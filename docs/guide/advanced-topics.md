# Advanced Topics

This guide covers advanced features and techniques for working with the Strata Cloud Manager SDK.

## Pagination

When listing objects, the API may return paginated results. The SDK provides methods to handle pagination automatically or manually.

### Automatic Pagination

By default, the SDK's list methods handle pagination automatically and return all results:

```python
# Get all address objects (automatically handling pagination)
all_addresses = client.address.list()
```

### Manual Pagination

You can also control pagination manually:

```python
# Get the first page of results with a specific limit
first_page = client.address.list(limit=50)

# If you need to implement your own pagination logic
offset = 0
limit = 50
all_results = []

while True:
    page = client.address.list(offset=offset, limit=limit)
    all_results.extend(page)
    
    if len(page) < limit:
        # Reached the end of results
        break
        
    offset += limit
```

## Advanced Filtering

The SDK supports filtering results using the OData syntax:

### Basic Filters

```python
# Filter by name
filtered = client.address.list(filter="name eq 'web-server'")

# Filter by folder
filtered = client.address.list(filter="folder eq 'Shared'")
```

### Compound Filters

```python
# Multiple conditions (AND)
filtered = client.address.list(filter="name eq 'web-server' and folder eq 'Shared'")

# Multiple conditions (OR)
filtered = client.address.list(filter="name eq 'web-server' or name eq 'db-server'")
```

### Filter Operators

```python
# Contains
filtered = client.address.list(filter="contains(name, 'server')")

# Starts with
filtered = client.address.list(filter="startswith(name, 'web')")

# Numeric comparisons
filtered = client.nat_rules.list(filter="destinationPort gt 1000")
```

## Performance Optimization

### Requesting Specific Fields

To reduce response size and improve performance, you can specify which fields to return:

```python
# Only retrieve specific fields
addresses = client.address.list(fields="id,name,ip_netmask")
```

### Batch Operations

For multiple operations, it's more efficient to use batch processing:

```python
# Create multiple objects efficiently
objects_to_create = [
    {"name": "server1", "folder": "Shared", "ip_netmask": "192.168.1.100/32"},
    {"name": "server2", "folder": "Shared", "ip_netmask": "192.168.1.101/32"},
    {"name": "server3", "folder": "Shared", "ip_netmask": "192.168.1.102/32"}
]

for obj in objects_to_create:
    client.address.create(obj)

# Then commit once
client.candidate_push({
    "description": "Adding multiple server addresses",
    "admin_name": "admin"
})
```

## Error Handling and Retries

### Custom Retry Logic

For operations that might fail temporarily, you can implement retry logic:

```python
import time
from scm.exceptions import ApiError

def retry_operation(operation_func, max_retries=3, retry_delay=2):
    retries = 0
    while retries < max_retries:
        try:
            return operation_func()
        except ApiError as e:
            if e.status_code in [429, 503]:  # Rate limit or service unavailable
                retries += 1
                if retries < max_retries:
                    time.sleep(retry_delay * retries)  # Exponential backoff
                else:
                    raise
            else:
                raise

# Usage example
def create_address():
    return client.address.create({
        "name": "example",
        "folder": "Shared",
        "ip_netmask": "192.168.1.100/32"
    })

new_address = retry_operation(create_address)
```

### Debugging API Interactions

For troubleshooting, you can enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Working with Custom Token URLs

The SDK supports specifying a custom token URL for environments that use different authentication endpoints:

```python
from scm import Scm

# Initialize with a custom token URL
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id",
    token_url="https://custom-auth-endpoint.example.com/oauth2/token"
)
```

## Next Steps

- Explore the [API Reference](../sdk/index.md) for detailed information on all available methods
- Check the [GitHub repository](https://github.com/cdot65/pan-scm-sdk) for examples and updates