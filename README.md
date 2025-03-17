# pan-scm-sdk

[![Python](https://img.shields.io/pypi/pyversions/pan-scm-sdk.svg)](https://pypi.org/project/pan-scm-sdk/)
[![PyPI](https://img.shields.io/pypi/v/pan-scm-sdk.svg)](https://pypi.org/project/pan-scm-sdk/)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://cdot65.github.io/pan-scm-sdk/)
[![License](https://img.shields.io/github/license/cdot65/pan-scm-sdk.svg)](https://github.com/cdot65/pan-scm-sdk)

A Python SDK for interacting with Palo Alto Networks Strata Cloud Manager.

## Documentation

For detailed documentation, visit [https://cdot65.github.io/pan-scm-sdk/](https://cdot65.github.io/pan-scm-sdk/).

## Features

- Authentication with OAuth 2.0
- API client for Strata Cloud Manager
- Support for configuration management
- Support for deployment operations
- Support for security operations
- Support for monitoring and reporting

## Key Service Features

The SDK provides support for managing many different service types:

| Category         | Services                                                   |
|------------------|-----------------------------------------------------------|
| Objects          | Address, Address Group, Applications, Service, Tags, etc.  |
| Network          | IKE/IPsec profiles, NAT Rules, Security Zones              |
| Mobile Agent     | Authentication Settings, Agent Versions                    |
| Deployment       | Remote Networks, Bandwidth Allocations, DNS Servers, etc.  |
| Security         | Security Rules, Anti-Spyware Profiles, URL Categories, etc.|

## Installation

```bash
pip install pan-scm-sdk
```

## Quickstart

```python
from scm.client import Scm

# Initialize the unified client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List addresses
addresses = client.address.list(folder="Texas")
for addr in addresses:
    print(f"Name: {addr.name}, Value: {addr.ip_netmask or addr.fqdn}")

# Create an address
new_address = client.address.create({
    "name": "webserver",
    "ip_netmask": "10.0.1.100",
    "description": "Primary web server",
    "folder": "Texas"
})

# Commit changes
client.commit(
    folders=["Texas"],
    description="Added webserver address",
    sync=True
)
```

## License

This project is licensed under the terms of the Apache 2.0 license.
