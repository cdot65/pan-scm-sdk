# Getting Started with Strata Cloud Manager SDK

This guide will help you get started with using the Strata Cloud Manager SDK for Python.

## Installation

Install the SDK using pip:

```bash
pip install pan-scm-sdk
```

Or with poetry:

```bash
poetry add pan-scm-sdk
```

## Authentication

To use the SDK, you need to authenticate with the Strata Cloud Manager. You can do this using OAuth2 client credentials flow.

```python
from scm import Scm

# Initialize the client
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id"
)

# The client will handle token acquisition and renewal automatically
```

## Basic Usage

Here's a simple example of listing address objects:

```python
# List all address objects
addresses = client.address.list()
print(f"Found {len(addresses)} address objects")

# Create a new address object
new_address = client.address.create({
    "name": "example-server",
    "folder": "Shared",
    "ip_netmask": "192.168.1.100/32",
    "description": "Example server created via SDK"
})
print(f"Created address object with ID: {new_address['id']}")

# Fetch a specific address object
address = client.address.fetch(id=new_address['id'])
print(f"Retrieved address: {address['name']}")

# Update an address object
client.address.update(id=address['id'], data={
    "description": "Updated description"
})
print("Address object updated")

# Delete an address object
client.address.delete(id=address['id'])
print("Address object deleted")
```

## Next Steps

- Check out the [Configuration Objects](configuration-objects.md) guide to learn more about managing different object types
- Review the [Data Models](data-models.md) guide to understand the structure of request and response data
- Explore the [API Reference](../sdk/index.md) for detailed information on all available methods
