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
    - [Managing Objects](#managing-objects)
        - [Creating an Address](#creating-an-address)
- [Development](#development)
    - [Setup](#setup)
    - [Code Quality](#code-quality)
    - [Pre-commit Hooks](#pre-commit-hooks)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- **Flexible Authentication**:
  - OAuth2 client credentials flow for standard authentication
  - Bearer token support for scenarios with pre-acquired tokens
- **Resource Management**: Create, read, update, and delete configuration objects such as addresses, address groups,
  applications, regions, internal DNS servers, and more.
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

Before interacting with the SDK, you need to authenticate using one of the following methods:

#### Method 1: OAuth2 Client Credentials (Standard)

```python
from scm.client import Scm

# Initialize the API client with OAuth2 client credentials
api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# The SCM client is now ready to use
```

#### Method 2: Bearer Token Authentication

If you already have a valid OAuth token, you can use it directly:

```python
from scm.client import Scm

# Initialize the API client with a pre-acquired bearer token
api_client = Scm(
    access_token="your_bearer_token"
)

# The SCM client is now ready to use
```

> **NOTE**: When using bearer token authentication, token refresh is your responsibility. For commit operations with bearer token auth, you must explicitly provide the `admin` parameter.
```python
# Example of commit with bearer token authentication
api_client.commit(
    folders=["Texas"],
    description="Configuration changes",
    admin=["admin@example.com"],  # Required when using bearer token
    sync=True
)
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

# === INTERNAL DNS SERVERS ===

# Create a new internal DNS server
dns_server = client.internal_dns_server.create({
    "name": "main-dns-server",
    "domain_name": ["example.com", "internal.example.com"],
    "primary": "192.168.1.10",
    "secondary": "192.168.1.11"
})
print(f"Created DNS server: {dns_server.name} with ID: {dns_server.id}")

# List all internal DNS servers
dns_servers = client.internal_dns_server.list()
for server in dns_servers:
    print(f"DNS Server: {server.name}, Primary: {server.primary}")

# === NETWORK LOCATIONS ===

# List all network locations
locations = client.network_location.list()
print(f"Found {len(locations)} network locations")

# Filter locations by continent
us_locations = client.network_location.list(continent="North America")
print(f"Found {len(us_locations)} locations in North America")

# Fetch a specific location
west_coast = client.network_location.fetch("us-west-1")
print(f"Location: {west_coast.display} ({west_coast.value})")
print(f"Region: {west_coast.region}, Coordinates: {west_coast.latitude}, {west_coast.longitude}")

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

| Client Property                    | Description                                                   |
|------------------------------------|---------------------------------------------------------------|
| **Objects**                        |                                                               |
| `address`                          | IP addresses, CIDR ranges, and FQDNs for security policies    |
| `address_group`                    | Static or dynamic collections of address objects              |
| `application`                      | Custom application definitions and signatures                 |
| `application_filter`               | Filters for identifying applications by characteristics       |
| `application_group`                | Logical groups of applications for policy application         |
| `auto_tag_action`                  | Automated tag assignment based on traffic and security events |
| `dynamic_user_group`               | User groups with dynamic membership criteria                  |
| `external_dynamic_list`            | Externally managed lists of IPs, URLs, or domains             |
| `hip_object`                       | Host information profile match criteria                       |
| `hip_profile`                      | Endpoint security compliance profiles                         |
| `http_server_profile`              | HTTP server configurations for logging and monitoring         |
| `log_forwarding_profile`           | Configurations for forwarding logs to external systems        |
| `quarantined_device`               | Management of devices blocked from network access             |
| `region`                           | Geographic regions for policy control                         |
| `schedule`                         | Time-based policies and access control                        |
| `service`                          | Protocol and port definitions for network services            |
| `service_group`                    | Collections of services for simplified policy management      |
| `syslog_server_profile`            | Syslog server configurations for centralized logging          |
| `tag`                              | Resource classification and organization labels               |
| **Mobile Agent**                   |                                                               |
| `auth_setting`                     | GlobalProtect authentication settings                         |
| `agent_version`                    | GlobalProtect agent versions (read-only)                      |
| **Network**                        |                                                               |
| `ike_crypto_profile`               | IKE crypto profiles for VPN tunnel encryption                 |
| `ike_gateway`                      | IKE gateways for VPN tunnel endpoints                         |
| `ipsec_crypto_profile`             | IPsec crypto profiles for VPN tunnel encryption               |
| `nat_rule`                         | Network address translation policies for traffic routing      |
| `security_zone`                    | Security zones for network segmentation                       |
| **Deployment**                     |                                                               |
| `bandwidth_allocation`             | Bandwidth allocation management for network capacity planning |
| `bgp_routing`                      | BGP routing configuration for network connectivity            |
| `internal_dns_server`              | Internal DNS server configurations for domain resolution      |
| `network_location`                 | Geographic network locations for service connectivity         |
| `remote_network`                   | Secure branch and remote site connectivity configurations     |
| `service_connection`               | Service connections to cloud service providers                |
| **Security**                       |                                                               |
| `security_rule`                    | Core security policies controlling network traffic            |
| `anti_spyware_profile`             | Protection against spyware, C2 traffic, and data exfiltration |
| `decryption_profile`               | SSL/TLS traffic inspection configurations                     |
| `dns_security_profile`             | Protection against DNS-based threats and tunneling            |
| `url_category`                     | Custom URL categorization for web filtering                   |
| `vulnerability_protection_profile` | Defense against known CVEs and exploit attempts               |
| `wildfire_antivirus_profile`       | Cloud-based malware analysis and zero-day protection          |
| **Setup**                          |                                                               |
| `device`                           | Device resources and management                               |
| `folder`                           | Folder organization and hierarchy                             |
| `label`                            | Resource classification and simple key-value object labels    |
| `snippet`                          | Reusable configuration snippets                               |
| `variable`                         | Typed variables with flexible container scoping               |

#### Traditional Access Pattern (Legacy Support)

You can also use the traditional pattern where you explicitly create service instances:

```python
from scm.client import Scm
from scm.config.objects import Address
from scm.config.deployment import InternalDnsServers, NetworkLocations

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

# Create an InternalDnsServers instance
dns_servers = InternalDnsServers(api_client)

# List all internal DNS servers
all_dns_servers = dns_servers.list()
for server in all_dns_servers:
    print(f"DNS Server: {server.name}, Primary: {server.primary}")

# Create a NetworkLocations instance
network_locations = NetworkLocations(api_client)

# List all network locations
locations = network_locations.list()
for loc in locations:
    print(f"Location: {loc.display} ({loc.value}), Region: {loc.region}")
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

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/cdot65/pan-scm-sdk.git
   cd pan-scm-sdk
   ```

2. Install dependencies and pre-commit hooks:
   ```bash
   make setup
   ```

   Alternatively, you can install manually:
   ```bash
   poetry install
   poetry run pre-commit install
   ```

### Code Quality

This project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Run linting checks
make lint

# Format code
make format

# Auto-fix linting issues when possible
make fix
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality before committing:

```bash
# Run pre-commit hooks on all files
make pre-commit-all
```

The following checks run automatically before each commit:
- ruff linting and formatting
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON syntax checking
- Large file detection
- Python syntax validation
- Merge conflict detection
- Private key detection

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/your-feature`).
3. Make your changes, ensuring all linting and tests pass.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to your branch (`git push origin feature/your-feature`).
6. Open a Pull Request.

Ensure your code adheres to the project's coding standards and includes tests where appropriate.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for details.

## Support

For support and questions, please refer to the [SUPPORT.md](./SUPPORT.md) file in this repository.

---

*Detailed documentation is available on our [GitHub Pages documentation site](https://cdot65.github.io/pan-scm-sdk/).*
