# Strata Cloud Manager SDK

<p align="center">
  <a href="https://cdot65.github.io/pan-scm-sdk/">
    <img src="https://raw.githubusercontent.com/cdot65/pan-scm-sdk/main/docs/images/logo.svg" alt="pan-scm-sdk" width="200">
  </a>
</p>

<p align="center">
  <a href="https://codecov.io/github/cdot65/pan-scm-sdk"><img src="https://codecov.io/github/cdot65/pan-scm-sdk/graph/badge.svg?token=BB39SMLYFP" alt="codecov"></a>
  <a href="https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml"><img src="https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml/badge.svg" alt="Build Status"></a>
  <a href="https://pypi.org/project/pan-scm-sdk/"><img src="https://img.shields.io/pypi/v/pan-scm-sdk.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/pan-scm-sdk/"><img src="https://img.shields.io/pypi/pyversions/pan-scm-sdk.svg" alt="Python versions"></a>
  <a href="https://github.com/cdot65/pan-scm-sdk/blob/main/LICENSE"><img src="https://img.shields.io/github/license/cdot65/pan-scm-sdk.svg" alt="License"></a>
</p>

Python SDK for Palo Alto Networks Strata Cloud Manager. Provides OAuth2-authenticated CRUD operations on firewall configuration objects — addresses, security rules, NAT rules, and 80+ resource types — via a unified client interface.

## Installation

```bash
pip install pan-scm-sdk
```

Requires Python 3.10+.

## Quick Start

```python
from scm.client import Scm

# Initialize with OAuth2 credentials
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an address object
client.address.create({
    "name": "web-server",
    "ip_netmask": "10.0.1.100/32",
    "description": "Production web server",
    "folder": "Texas",
})

# List all addresses in a folder
addresses = client.address.list(folder="Texas")
for addr in addresses:
    print(f"{addr.name}: {addr.ip_netmask or addr.fqdn}")
```

## Documentation

For comprehensive guides, API reference, and examples for all 80+ supported resources, visit the full documentation site:

**[https://cdot65.github.io/pan-scm-sdk/](https://cdot65.github.io/pan-scm-sdk/)**

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Run quality checks (`make quality`) and tests (`make test`)
4. Open a Pull Request

## License

Apache 2.0 &mdash; see [LICENSE](./LICENSE) for details.
