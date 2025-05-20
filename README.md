# Strata Cloud Manager SDK

![Banner Image](https://raw.githubusercontent.com/cdot65/pan-scm-sdk/main/docs/images/logo.svg)
[![codecov](https://codecov.io/github/cdot65/pan-scm-sdk/graph/badge.svg?token=BB39SMLYFP)](https://codecov.io/github/cdot65/pan-scm-sdk)
[![Build Status](https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pan-scm-sdk.svg)](https://badge.fury.io/py/pan-scm-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/pan-scm-sdk.svg)](https://pypi.org/project/pan-scm-sdk/)
[![License](https://img.shields.io/github/license/cdot65/pan-scm-sdk.svg)](https://github.com/cdot65/pan-scm-sdk/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/cdot65/pan-scm-sdk)

Python SDK for Palo Alto Networks Strata Cloud Manager.

> **NOTE**: Please refer to the [GitHub Pages documentation site](https://cdot65.github.io/pan-scm-sdk/) for all
> examples

## Table of Contents

- [Strata Cloud Manager SDK](#strata-cloud-manager-sdk)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Development Guidelines](#development-guidelines)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Authentication](#authentication)
      - [Method 1: OAuth2 Client Credentials passed into a ScmClient instance](#method-1-oauth2-client-credentials-passed-into-a-scmclient-instance)
      - [Method 2: Bearer Token Authentication](#method-2-bearer-token-authentication)
    - [TLS Certificate Verification Control](#tls-certificate-verification-control)
    - [Available Client Services](#available-client-services)
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

## Development Guidelines

For developers working on this SDK:

- **Service File Standards**: See `SDK_STYLING_GUIDE.md` for comprehensive service file guidelines
- **Model Standards**: See `CLAUDE_MODELS.md` for Pydantic model patterns and conventions
- **Templates**: Use `SDK_SERVICE_TEMPLATE.py` as a starting point for new services
- **Claude Code Integration**: Reference `CLAUDE.md` for AI-assisted development guidelines

## Installation

**Requirements**:

- Python 3.10 or higher

Install the package via pip:

```bash
pip install pan-scm-sdk
```

## Usage

### TLS Certificate Verification Control

By default, the SDK verifies TLS certificates for all HTTPS requests. You can bypass TLS verification (for development or testing) by setting the `verify_ssl` flag to `False` when initializing `Scm` or `ScmClient`:

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="...",
    client_secret="...",
    tsg_id="...",
    verify_ssl=False,  # WARNING: disables TLS verification!
)
```

> **Warning:** Disabling TLS verification is insecure and exposes you to man-in-the-middle attacks. Only use `verify_ssl=False` in trusted development environments.

### Authentication

Before interacting with the SDK, you need to authenticate:

#### Method 1: OAuth2 Client Credentials passed into a ScmClient instance

```python
from scm.client import ScmClient

# Initialize the API client with OAuth2 client credentials
api_client = ScmClient(
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

### Available Client Services

The unified client provides access to the following services through attribute-based access:

| Client Property                    | Description                                                   |
| ---------------------------------- | ------------------------------------------------------------- |
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

---

## Development

Before starting development, please review:

- `SDK_STYLING_GUIDE.md` - Comprehensive guide for writing consistent SDK code
- `CLAUDE_MODELS.md` - Guidelines for creating Pydantic models
- `SDK_SERVICE_TEMPLATE.py` - Template for new service files
- `WINDSURF_RULES.md` - Overall project standards

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

_Detailed documentation is available on our [GitHub Pages documentation site](https://cdot65.github.io/pan-scm-sdk/)._
