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
    - [Creating Address Objects](#creating-address-objects)
    - [Listing Addresses](#listing-addresses)
    - [Updating an Address](#updating-an-address)
    - [Deleting an Address](#deleting-an-address)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- **OAuth2 Authentication**: Securely authenticate with the Strata Cloud Manager API using OAuth2 client credentials
  flow.
- **Resource Management**: Create, read, update, and delete configuration objects such as addresses.
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
from pan_scm_sdk.client import APIClient

# Initialize the API client with your credentials
api_client = APIClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# The api_client is now ready to use
```

### Creating Address Objects

```python
from pan_scm_sdk.resources.address import AddressClient
from pan_scm_sdk.models.address import Address

# Create an AddressClient instance
address_client = AddressClient(api_client)

# Define a new address object
address = Address(
    name="MyAddress",
    ip_netmask="192.168.1.1/32",
    folder="Shared",
)

# Create the address in Strata Cloud Manager
created_address = address_client.create_address(address)
print(f"Created address with ID: {created_address.id}")
```

### Listing Addresses

```python
# List addresses with optional filtering
addresses = address_client.list_addresses(limit=10)
for addr in addresses:
    print(f"Address ID: {addr.id}, Name: {addr.name}, IP: {addr.ip_netmask}")
```

### Updating an Address

```python
# Retrieve an existing address
address_id = "123e4567-e89b-12d3-a456-426655440000"
address = address_client.get_address(address_id)

# Update the address properties
address.description = "Updated description"

# Send the update to Strata Cloud Manager
updated_address = address_client.update_address(address_id, address)
print(f"Updated address with ID: {updated_address.id}")
```

### Deleting an Address

```python
# Delete an address by ID
address_id = "123e4567-e89b-12d3-a456-426655440000"
address_client.delete_address(address_id)
print(f"Deleted address with ID: {address_id}")
```

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