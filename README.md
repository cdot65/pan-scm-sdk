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
- **Resource Management**: Create, read, update, and delete configuration objects such as addresses, address groups, 
  applications, regions, and more.
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

| Client Property                    | Description                                                     |
|------------------------------------|-----------------------------------------------------------------|
| **Objects**                        |                                                                 |
| `address`                          | IP addresses, CIDR ranges, and FQDNs for security policies      |
| `address_group`                    | Static or dynamic collections of address objects                |
| `application`                      | Custom application definitions and signatures                   |
| `application_filter`               | Filters for identifying applications by characteristics         |
| `application_group`                | Logical groups of applications for policy application           |
| `dynamic_user_group`               | User groups with dynamic membership criteria                    |
| `external_dynamic_list`            | Externally managed lists of IPs, URLs, or domains               |
| `hip_object`                       | Host information profile match criteria                         |
| `hip_profile`                      | Endpoint security compliance profiles                           |
| `http_server_profile`              | HTTP server configurations for logging and monitoring           |
| `log_forwarding_profile`           | Configurations for forwarding logs to external systems          |
| `quarantined_device`               | Management of devices blocked from network access               |
| `region`                           | Geographic regions for policy control                           |
| `schedule`                         | Time-based policies and access control                          |
| `service`                          | Protocol and port definitions for network services              |
| `service_group`                    | Collections of services for simplified policy management        |
| `syslog_server_profile`            | Syslog server configurations for centralized logging            |
| `tag`                              | Resource classification and organization labels                 |
| **Network**                        |                                                                 |
| `nat_rule`                         | Network address translation policies for traffic routing        |
| `security_zone`                    | Security zones for network segmentation                         |
| **Deployment**                     |                                                                 |
| `remote_network`                   | Secure branch and remote site connectivity configurations       |
| **Security**                       |                                                                 |
| `security_rule`                    | Core security policies controlling network traffic              |
| `anti_spyware_profile`             | Protection against spyware, C2 traffic, and data exfiltration   |
| `decryption_profile`               | SSL/TLS traffic inspection configurations                       |
| `dns_security_profile`             | Protection against DNS-based threats and tunneling              |
| `url_category`                     | Custom URL categorization for web filtering                     |
| `vulnerability_protection_profile` | Defense against known CVEs and exploit attempts                 |
| `wildfire_antivirus_profile`       | Cloud-based malware analysis and zero-day protection            |

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