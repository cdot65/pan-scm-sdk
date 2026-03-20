---
hide:
  - navigation
---

<style>
.md-content .md-typeset h1 { display: none; }
</style>

<p align="center">
    <a href="https://paloaltonetworks.com"><img src="images/logo.svg" alt="PaloAltoNetworks" class="hero-logo"></a>
</p>
<p align="center">
    <em><code>pan-scm-sdk</code>: Python SDK for Palo Alto Networks Strata Cloud Manager</em>
</p>
<p align="center" style="display: flex; justify-content: center; align-items: center; gap: 4px; flex-wrap: wrap;">
<a href="https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml" target="_blank">
    <img src="https://github.com/cdot65/pan-scm-sdk/actions/workflows/ci.yml/badge.svg" alt="Build Status" style="height: 20px;">
</a>
<a href="https://codecov.io/github/cdot65/pan-scm-sdk" target="_blank">
    <img src="https://codecov.io/github/cdot65/pan-scm-sdk/graph/badge.svg?token=BB39SMLYFP" alt="codecov" style="height: 20px;">
</a>
<a href="https://pypi.org/project/pan-scm-sdk/" target="_blank">
    <img src="https://img.shields.io/pypi/v/pan-scm-sdk.svg?style=flat" alt="PyPI version" style="height: 20px;">
</a>
<a href="https://pypi.org/project/pan-scm-sdk/" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/pan-scm-sdk.svg?style=flat" alt="Python versions" style="height: 20px;">
</a>
<a href="https://github.com/cdot65/pan-scm-sdk/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/cdot65/pan-scm-sdk.svg?style=flat" alt="License" style="height: 20px;">
</a>
</p>

---

Manage 80+ Strata Cloud Manager resource types — addresses, security rules, NAT rules, network interfaces, and more — through a simple, unified Python client with full CRUD support, Pydantic validation, and automatic pagination.

## Installation

```bash
pip install pan-scm-sdk
```

Requires Python 3.10+.

## Quick Start

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an address object
client.address.create({
    "name": "web-server",
    "ip_netmask": "10.0.1.100/32",
    "folder": "Texas",
})

# List addresses
for addr in client.address.list(folder="Texas"):
    print(addr.name)
```

Explore the full API across all resource types in the [Services](sdk/index.md) documentation.

---

## Documentation Guide

### Services

**[Go to Services →](sdk/index.md)**

Service classes for performing CRUD operations on Strata Cloud Manager resources. Use when you need method signatures, usage examples, and filtering options.

### Data Models

**[Go to Data Models →](sdk/models/index.md)**

Pydantic schemas that define validation rules, required vs optional fields, and allowed values. Use when you need to pre-validate configurations before API calls.

### User Guide

**[Go to User Guide →](about/introduction.md)**

Authentication options, TLS configuration, commit workflows, and detailed walkthroughs for common tasks.

---

## Contributing

Contributions are welcome. Visit the [Contributing](about/contributing.md) page for guidelines.

## License

Apache 2.0 — see the [License](about/license.md) page for details.
