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

### Managing Objects

> **NOTE**: Please refer to the [GitHub Pages documentation site](https://cdot65.github.io/pan-scm-sdk/) for all
> examples

#### Unified Client Access Pattern (Recommended)

Starting with version 0.3.13, you can use a unified client access pattern to work with resources:

```python
from scm.client import Scm

# Create an authenticated session with SCM
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access services directly through the client object
# No need to create separate service instances

# === ADDRESS OBJECTS ===

# List addresses in a specific folder
addresses = client.address.list(folder='Texas')
for addr in addresses:
    print(f"Found address: {addr.name}, Type: {'IP' if addr.ip_netmask else 'FQDN'}")

# Fetch a specific address
web_server = client.address.fetch(name="web-server", folder="Texas")
print(f"Web server details: {web_server.name}, {web_server.ip_netmask}")

# Update an address
web_server.description = "Updated via SDK"
updated_addr = client.address.update(web_server)
print(f"Updated address description: {updated_addr.description}")

# === SECURITY RULES ===

# Fetch a security rule by name
security_rule = client.security_rule.fetch(name="allow-outbound", folder="Texas")
print(f"Security rule: {security_rule.name}")
print(f"  Action: {security_rule.action}")
print(f"  Source zones: {security_rule.source_zone}")
print(f"  Destination zones: {security_rule.destination_zone}")

# === NAT RULES ===

# List NAT rules with source zone filtering
nat_rules = client.nat_rule.list(
    folder="Texas",
    source_zone=["trust"]
)
print(f"Found {len(nat_rules)} NAT rules with source zone 'trust'")

# Delete a NAT rule
if nat_rules:
    client.nat_rule.delete(nat_rules[0].id)
    print(f"Deleted NAT rule: {nat_rules[0].name}")
    
    # Commit the changes
    commit_job = client.commit(
        folders=["Texas"], 
        description="Deleted NAT rule",
        sync=True
    )
    print(f"Commit job status: {client.get_job_status(commit_job.job_id).data[0].status_str}")
```

### Available Client Services

The unified client provides access to the following services through attribute-based access:

| Client Property | Class | Description |
|----------------|-------|-------------|
| **Objects** | | |
| `address` | `Address` | Manages IP and FQDN address objects |
| `address_group` | `AddressGroup` | Manages address group objects |
| `application` | `Application` | Manages custom application objects |
| `application_filter` | `ApplicationFilters` | Manages application filter objects |
| `application_group` | `ApplicationGroup` | Manages application group objects |
| `dynamic_user_group` | `DynamicUserGroup` | Manages dynamic user group objects |
| `external_dynamic_list` | `ExternalDynamicLists` | Manages external dynamic list objects |
| `hip_object` | `HIPObject` | Manages host information profile objects |
| `hip_profile` | `HIPProfile` | Manages host information profile group objects |
| `http_server_profile` | `HTTPServerProfile` | Manages HTTP server profile objects |
| `service` | `Service` | Manages service objects |
| `service_group` | `ServiceGroup` | Manages service group objects |
| `tag` | `Tag` | Manages tag objects |
| **Network** | | |
| `nat_rule` | `NATRule` | Manages network address translation rules |
| **Deployment** | | |
| `remote_network` | `RemoteNetworks` | Manages remote network connections |
| **Security** | | |
| `security_rule` | `SecurityRule` | Manages security policy rules |
| `anti_spyware_profile` | `AntiSpywareProfile` | Manages anti-spyware security profiles |
| `decryption_profile` | `DecryptionProfile` | Manages SSL decryption profiles |
| `dns_security_profile` | `DNSSecurityProfile` | Manages DNS security profiles |
| `url_category` | `URLCategories` | Manages custom URL categories |
| `vulnerability_protection_profile` | `VulnerabilityProtectionProfile` | Manages vulnerability protection profiles |
| `wildfire_antivirus_profile` | `WildfireAntivirusProfile` | Manages WildFire anti-virus profiles |

#### Traditional Access Pattern (Legacy Support)

You can also use the traditional pattern where you explicitly create service instances:

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

# Create the address in Strata Cloud Manager (unified client approach)
new_address = api_client.address.create(address_data)
print(f"Created address with ID: {new_address.id}")

# Or using the traditional approach
address_service = Address(api_client)
new_address = address_service.create(address_data)
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