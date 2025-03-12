# Getting Started with pan-scm-sdk

Welcome to the `pan-scm-sdk`! This guide will walk you through the initial setup and basic usage of the SDK to interact
with Palo Alto Networks Strata Cloud Manager.

## Installation

**Requirements**:

- Python 3.10 or higher

Install the package via pip:

<div class="termy">

<!-- termynal -->

```bash
$ pip install pan-scm-sdk
```

</div>

## Authentication

Before using the SDK, you need to authenticate with Strata Cloud Manager using your client credentials.

**Example:**

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize the SCM client with your credentials
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# The SCM client is now ready to use
```

</div>

- `client_id`: Your OAuth2 client ID.
- `client_secret`: Your OAuth2 client secret.
- `tsg_id`: Your Tenant Service Group ID.

## Basic Usage

The SDK provides two ways to interact with Strata Cloud Manager: the unified client interface (recommended) and the traditional service instantiation pattern.

### Unified Client Interface (Recommended)

Starting with version 0.3.14, you can access all service objects directly through the client instance. This approach is more intuitive and streamlined:

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize the client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create a new address using the unified client interface
address_data = {
    "name": "test-address",
    "fqdn": "test.example.com",
    "description": "Created via unified client",
    "folder": "Texas",
}

new_address = client.address.create(address_data)
print(f"Created address with ID: {new_address.id}")

# List addresses
addresses = client.address.list(folder='Prisma Access')
for addr in addresses:
    print(f"Address Name: {addr.name}, IP: {addr.ip_netmask or addr.fqdn}")

# Create a tag
tag_data = {
    "name": "Development",
    "color": "blue",
    "folder": "Texas"
}
new_tag = client.tag.create(tag_data)
print(f"Created tag: {new_tag.name}")

# Create a security rule
rule_data = {
    "name": "allow-dev-traffic",
    "folder": "Texas",
    "source": {"address": ["test-address"]},
    "destination": {"address": ["any"]},
    "application": ["web-browsing"],
    "service": ["application-default"],
    "action": "allow",
    "tag": ["Development"]
}
new_rule = client.security_rule.create(rule_data)
print(f"Created rule: {new_rule.name}")

# Commit changes
result = client.commit(
    folders=["Texas"],
    description="Added new objects via unified client",
    sync=True
)
print(f"Commit job ID: {result.job_id}")
```

</div>

### Traditional Service Instantiation (Legacy)

You can also use the traditional pattern where service objects are explicitly instantiated. While this approach is still supported for backward compatibility, it's recommended to use the unified client interface for new development.

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address, AddressGroup, Application

# Initialize the client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create service instances manually
address = Address(client)
address_group = AddressGroup(client)
application = Application(client)

# Create a new address
address_data = {
    "name": "test-address",
    "fqdn": "test.example.com",
    "description": "Created via pan-scm-sdk",
    "folder": "Texas",
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")

# List addresses
addresses = address.list(folder='Prisma Access')
for addr in addresses:
    print(f"Address Name: {addr.name}, IP: {addr.ip_netmask or addr.fqdn}")
```

</div>

!!! warning
    Using the traditional approach requires manually creating service instances for each service type you want to use, which can lead to code duplication and more complex management. It also doesn't automatically handle token refreshing across all service instances.

## Common Operations

### Managing Address Objects

<div class="termy">

<!-- termynal -->

```python
# Create an IP/Netmask address
ip_address_data = {
    "name": "internal-network",
    "ip_netmask": "192.168.1.0/24",
    "description": "Internal network segment",
    "folder": "Texas",
    "tag": ["Network", "Internal"]
}
ip_address = client.address.create(ip_address_data)

# Update an address
ip_address.description = "Updated network description"
updated_address = client.address.update(ip_address)

# Fetch address by name
found_address = client.address.fetch(name="internal-network", folder="Texas")

# Delete an address
client.address.delete(ip_address.id)
```

</div>

### Managing Tags

<div class="termy">

<!-- termynal -->

```python
# Create tags with different colors
tags_to_create = [
    {"name": "Production", "color": "red", "folder": "Texas"},
    {"name": "Testing", "color": "green", "folder": "Texas"},
    {"name": "Development", "color": "blue", "folder": "Texas"}
]

for tag_data in tags_to_create:
    tag = client.tag.create(tag_data)
    print(f"Created tag: {tag.name} with color: {tag.color}")

# List all tags
all_tags = client.tag.list(folder="Texas")
for tag in all_tags:
    print(f"Tag: {tag.name}, Color: {tag.color}")
```

</div>

### Managing Security Rules

<div class="termy">

<!-- termynal -->

```python
# Create a security rule
rule_data = {
    "name": "allow-internal-web",
    "folder": "Texas",
    "description": "Allow internal web browsing",
    "source": {"address": ["internal-network"]},
    "destination": {"address": ["any"]},
    "application": ["web-browsing", "ssl"],
    "service": ["application-default"],
    "action": "allow",
    "log_setting": None,
    "log_start": False,
    "log_end": True,
    "disabled": False,
    "tag": ["Production"]
}

rule = client.security_rule.create(rule_data)
print(f"Created rule: {rule.name}")

# List security rules
rules = client.security_rule.list(folder="Texas")
for r in rules:
    print(f"Rule: {r.name}, Action: {r.action}")
```

</div>

### Committing Changes

<div class="termy">

<!-- termynal -->

```python
# Commit changes with synchronous waiting
result = client.commit(
    folders=["Texas"],
    description="Configuration changes via SDK",
    sync=True,
    timeout=300
)

if result.success:
    print(f"Successfully committed changes. Job ID: {result.job_id}")
else:
    print(f"Commit failed: {result.error_message}")

# Check the status of a specific job
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")
```

</div>

## Error Handling

Always implement proper error handling in your code to manage API errors gracefully:

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import (
    APIError,
    AuthenticationError,
    InvalidObjectError,
    NameNotUniqueError,
    ObjectNotPresentError
)

try:
    # Attempt to create an address
    address_data = {
        "name": "example-server",
        "fqdn": "server.example.com",
        "folder": "Texas"
    }

    new_address = client.address.create(address_data)
    print(f"Created address: {new_address.name}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except NameNotUniqueError as e:
    print(f"Address name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid address data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
except APIError as e:
    print(f"API error: {e.message}")
```

</div>

## Next Steps

- Explore the [SDK Reference Documentation](../sdk/index.md) for detailed information on all available services and methods.
- Check out the [Client Module](../sdk/client.md) documentation for more information on the unified client interface.
- Refer to the [examples directory](https://github.com/cdot65/pan-scm-sdk/tree/main/examples) for complete script examples.
