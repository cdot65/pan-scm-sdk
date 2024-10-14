# Strata Cloud Manager SDK

![Banner Image](https://raw.githubusercontent.com/cdot65/pan-scm-sdk/main/docs/images/logo.svg)

[![Build Status](https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pan-scm-sdk.svg)](https://badge.fury.io/py/pan-scm-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/pan-scm-sdk.svg)](https://pypi.org/project/pan-scm-sdk/)
[![License](https://img.shields.io/github/license/cdot65/pan-scm-sdk.svg)](https://github.com/cdot65/pan-scm-sdk/blob/main/LICENSE)

Python SDK for Palo Alto Networks Strata Cloud Manager.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
    - [Authentication](#authentication)
    - [Managing Address Objects](#managing-address-objects)
        - [Listing Addresses](#listing-addresses)
        - [Creating an Address](#creating-an-address)
    - [Managing Address Groups](#managing-address-groups)
        - [Listing Address Groups](#listing-address-groups)
        - [Creating an Address Group](#creating-an-address-group)
    - [Managing Applications](#managing-applications)
        - [Listing Applications](#listing-applications)
        - [Creating an Application](#creating-an-application)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- **OAuth2 Authentication**: Securely authenticate with the Strata Cloud Manager API using OAuth2 client credentials
  flow.
- **Resource Management**: Create, read, update, and delete configuration objects such as addresses, address groups, and
  applications.
- **Data Validation**: Utilize Pydantic models for data validation and serialization.
- **Exception Handling**: Comprehensive error handling with custom exceptions for API errors.
- **Extensibility**: Designed for easy extension to support additional resources and endpoints.

## Installation

**Requirements**:

- Python 3.10 or higher

Install the package via pip:

```bash
pip install pan-scm-sdk
```

## Usage

### Authentication

Before interacting with the SDK, you need to authenticate using your Strata Cloud Manager credentials.

```python
from scm.client import Scm

# Initialize the API client with your credentials
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# The SCM client is now ready to use
```

### Managing Address Objects

#### Listing Addresses

```python
from scm.config.objects import Address

# Create an Address instance
address = Address(scm)

# List addresses in a specific folder
addresses = address.list(folder='Prisma Access')

# Iterate through the addresses
for addr in addresses:
    print(f"Address Name: {addr.name}, IP: {addr.ip_netmask or addr.fqdn}")
```

#### Creating an Address

```python
# Define a new address object
address_data = {
    "name": "test123",
    "fqdn": "test123.example.com",
    "description": "Created via pan-scm-sdk",
    "folder": "Prisma Access",
}

# Create the address in Strata Cloud Manager
new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")
```

### Managing Address Groups

#### Listing Address Groups

```python
from scm.config.objects import AddressGroup

# Create an AddressGroup instance
address_group = AddressGroup(scm)

# List address groups in a specific folder
address_groups = address_group.list(folder='Prisma Access')

# Iterate through the address groups
for ag in address_groups:
    print(f"Address Group Name: {ag.name}, Description: {ag.description}")
```

#### Creating an Address Group

```python
# Define a new address group
address_group_data = {
    "name": "example-group",
    "description": "This is a test address group",
    "static": ["Branch-test1", "Branch-test2"],
    "folder": "Prisma Access",
}

# Create the address group in Strata Cloud Manager
new_address_group = address_group.create(address_group_data)
print(f"Created address group with ID: {new_address_group.id}")
```

### Managing Applications

#### Listing Applications

```python
from scm.config.objects import Application

# Create an Application instance
application = Application(scm)

# List applications in a specific folder
applications = application.list(folder='Prisma Access')

# Iterate through the applications
for app in applications:
    print(f"Application Name: {app.name}, Category: {app.category}")
```

#### Creating an Application

```python
# Define a new application
application_data = {
    "name": "test123",
    "category": "collaboration",
    "subcategory": "internet-conferencing",
    "technology": "client-server",
    "risk": 1,
    "description": "Created via pan-scm-sdk",
    "ports": ["tcp/80,443", "udp/3478"],
    "folder": "Prisma Access",
    "evasive": False,
    "pervasive": False,
    "excessive_bandwidth_use": False,
    "used_by_malware": False,
    "transfers_files": False,
    "has_known_vulnerabilities": True,
    "tunnels_other_apps": False,
    "prone_to_misuse": False,
    "no_certifications": False,
}

# Create the application in Strata Cloud Manager
new_application = application.create(application_data)
print(f"Created application with ID: {new_application.id}")
```

### Managing Services

#### Listing Services

```python
from scm.config.objects import Service

# Create a Service instance
service = Service(scm)

# List services in a specific folder
services = service.list(folder='Prisma Access')

# Iterate through the services
for svc in services:
    protocol = 'TCP' if svc.protocol.tcp else 'UDP'
    ports = svc.protocol.tcp.port if svc.protocol.tcp else svc.protocol.udp.port
    print(f"Service Name: {svc.name}, Protocol: {protocol}, Ports: {ports}")
```

#### Creating a Service

```python
# Define a new service
service_data = {
    "name": "dns-service",
    "protocol": {
        "udp": {
            "port": "53",
            "override": {
                "timeout": 60,
            },
        }
    },
    "description": "DNS service",
    "folder": "Prisma Access",
}

# Create the service in Strata Cloud Manager
new_service = service.create(service_data)
print(f"Created service with ID: {new_service.id}")
```

---

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Ensure your code adheres to the project's coding standards and includes tests where appropriate.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for details.

## Support

For support and questions, please refer to the [SUPPORT.md](./SUPPORT.md) file in this repository.

---

*Detailed documentation is available on our [GitHub Pages site](https://cdot65.github.io/pan-scm-sdk/).*