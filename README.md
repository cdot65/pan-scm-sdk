# Strata Cloud Manager SDK

![Banner Image](https://raw.githubusercontent.com/cdot65/pan-scm-sdk/main/docs/images/logo.svg)
[![codecov](https://codecov.io/github/cdot65/pan-scm-sdk/graph/badge.svg?token=BB39SMLYFP)](https://codecov.io/github/cdot65/pan-scm-sdk)
[![Build Status](https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pan-scm-sdk.svg)](https://badge.fury.io/py/pan-scm-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/pan-scm-sdk.svg)](https://pypi.org/project/pan-scm-sdk/)
[![License](https://img.shields.io/github/license/cdot65/pan-scm-sdk.svg)](https://github.com/cdot65/pan-scm-sdk/blob/main/LICENSE)

Python SDK for Palo Alto Networks Strata Cloud Manager.

> **NOTE**: Please refer to the [GitHub Pages documentation site](https://cdot65.github.io/pan-scm-sdk/) for all
> examples

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
    - [Authentication](#authentication)
    - [Managing Address Objects](#managing-address-objects)
        - [Listing Addresses](#listing-addresses)
        - [Creating an Address](#creating-an-address)
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
api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# The SCM client is now ready to use
```

### Managing Address Objects

> **NOTE**: Please refer to the [GitHub Pages documentation site](https://cdot65.github.io/pan-scm-sdk/) for all
> examples

#### Listing Addresses

```python
from scm.client import Scm
from scm.config.objects import Address

# Create an authenticated session with SCM
api_client = Scm(
    client_id="this is an example",
    client_secret="this is an example",
    tsg_id="this is an example"
)

# Create an Address instance by passing the SCM instance into it
address = Address(api_client)

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
    "folder": "Texas",
}

# Create the address in Strata Cloud Manager
new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")
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

*Detailed documentation is available on our [GitHub Pages documentation site](https://cdot65.github.io/pan-scm-sdk/).*