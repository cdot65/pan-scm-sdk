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
from scm.client import Scm

# Initialize the SCM client with your credentials
scm = Scm(
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

The SDK provides classes to manage various configuration objects. Below are examples of how to use the SDK to manage
addresses, address groups, and applications.

### Managing Addresses

<div class="termy">

<!-- termynal -->

```python
from scm.config.objects import Address

# Create an Address instance
address = Address(scm)

# Create a new address
address_data = {
    "name": "test-address",
    "fqdn": "test.example.com",
    "description": "Created via pan-scm-sdk",
    "folder": "Prisma Access",
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")

# List addresses
addresses = address.list(folder='Prisma Access')
for addr in addresses:
    print(f"Address Name: {addr.name}, IP: {addr.ip_netmask or addr.fqdn}")
```

</div>

### Managing Address Groups

<div class="termy">

<!-- termynal -->

```python
from scm.config.objects import AddressGroup

# Create an AddressGroup instance
address_group = AddressGroup(scm)

# Create a new address group
address_group_data = {
    "name": "example-group",
    "description": "Test address group",
    "static": ["test-address"],
    "folder": "Prisma Access",
}

new_group = address_group.create(address_group_data)
print(f"Created address group with ID: {new_group.id}")

# List address groups
groups = address_group.list(folder='Prisma Access')
for group in groups:
    print(f"Address Group Name: {group.name}")
```

</div>

### Managing Applications

<div class="termy">

<!-- termynal -->

```python
from scm.config.objects import Application

# Create an Application instance
application = Application(scm)

# Create a new application
application_data = {
    "name": "test-app",
    "category": "collaboration",
    "subcategory": "internet-conferencing",
    "technology": "client-server",
    "risk": 1,
    "description": "Created via pan-scm-sdk",
    "ports": ["tcp/80,443"],
    "folder": "Prisma Access",
}

new_application = application.create(application_data)
print(f"Created application with ID: {new_application.id}")

# List applications
applications = application.list(folder='Prisma Access')
for app in applications:
    print(f"Application Name: {app.name}, Category: {app.category}")
```

</div>

## Next Steps

- Explore the [SDK Developer Documentation](../sdk/index.md) for detailed information on classes and methods.
- Refer to the [Usage Examples](examples.md) for more practical examples.
