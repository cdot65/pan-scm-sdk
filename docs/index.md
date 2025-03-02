---
hide:
  - navigation
---

<style>
.md-content .md-typeset h1 { display: none; }
</style>

<p align="center">
    <a href="https://paloaltonetworks.com"><img src="https://github.com/cdot65/pan-scm-sdk/blob/main/docs/images/logo.svg?raw=true" alt="PaloAltoNetworks"></a>
</p>
<p align="center">
    <em><code>pan-scm-sdk</code>: Python SDK to manage Palo Alto Networks Strata Cloud Manager</em>
</p>
<p align="center">
<a href="https://github.com/cdot65/pan-scm-sdk/graphs/contributors" target="_blank">
    <img src="https://img.shields.io/github/contributors/cdot65/pan-scm-sdk.svg?style=for-the-badge" alt="Contributors">
</a>
<a href="https://github.com/cdot65/pan-scm-sdk/network/members" target="_blank">
    <img src="https://img.shields.io/github/forks/cdot65/pan-scm-sdk.svg?style=for-the-badge" alt="Forks">
</a>
<a href="https://github.com/cdot65/pan-scm-sdk/stargazers" target="_blank">
    <img src="https://img.shields.io/github/stars/cdot65/pan-scm-sdk.svg?style=for-the-badge" alt="Stars">
</a>
<a href="https://github.com/cdot65/pan-scm-sdk/issues" target="_blank">
    <img src="https://img.shields.io/github/issues/cdot65/pan-scm-sdk.svg?style=for-the-badge" alt="Issues">
</a>
<a href="https://github.com/cdot65/pan-scm-sdk/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/cdot65/pan-scm-sdk.svg?style=for-the-badge" alt="License">
</a>
</p>

---

**Documentation
**: <a href="https://cdot65.github.io/pan-scm-sdk/" target="_blank">https://cdot65.github.io/pan-scm-sdk/</a>

**Source Code
**: <a href="https://github.com/cdot65/pan-scm-sdk" target="_blank">https://github.com/cdot65/pan-scm-sdk</a>

---

`pan-scm-sdk` is a Python SDK for Palo Alto Networks Strata Cloud Manager.

## Installation

**Requirements**:

- Python 3.10 or higher

Install the package via pip:

<div class="termy">

<!-- termynal -->

```bash
$ pip install pan-scm-sdk
```

</div>

## Quick Example

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm

# Initialize the unified client (handles all object types through a single interface)
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Work with Address objects
addresses = client.address.list(folder="Texas")
print(f"Found {len(addresses)} addresses")

# Fetch a specific address
my_address = client.address.fetch(name="web-server", folder="Texas")
print(f"Address details: {my_address.name}, {my_address.ip_netmask}")

# Update the address
my_address.description = "Updated via unified client"
updated_address = client.address.update(my_address)

# Work with Security Rules
security_rule = client.security_rule.fetch(name="allow-web", folder="Texas")
print(f"Security rule: {security_rule.name}, Action: {security_rule.action}")

# Work with NAT Rules - list with filtering
nat_rules = client.nat_rule.list(
    folder="Texas",
    source_zone=["trust"]
)
print(f"Found {len(nat_rules)} NAT rules with source zone 'trust'")

# Delete a NAT rule
if nat_rules:
    client.nat_rule.delete(nat_rules[0].id)
    print(f"Deleted NAT rule: {nat_rules[0].name}")

# Make configuration changes
client.commit(
    folders=["Texas"],
    description="Updated address and removed NAT rule",
    sync=True
)
```

</div>

## Available Services

The unified client provides access to the following services through its attribute-based interface:

| Client Property                    | Description                                    |
|------------------------------------|------------------------------------------------|
| **Objects**                        |                                                |
| `address`                          | Manages IP and FQDN address objects            |
| `address_group`                    | Manages address group objects                  |
| `application`                      | Manages custom application objects             |
| `application_filter`               | Manages application filter objects             |
| `application_group`                | Manages application group objects              |
| `dynamic_user_group`               | Manages dynamic user group objects             |
| `external_dynamic_list`            | Manages external dynamic list objects          |
| `hip_object`                       | Manages host information profile objects       |
| `hip_profile`                      | Manages host information profile group objects |
| `http_server_profile`              | Manages HTTP server profile objects            |
| `log_forwarding_profile`           | Manages Log Forwarding profile objects         |
| `quarantined_devices`              | Manages Quarantined Devices                    |
| `region`                           | Manages geographic region objects              |
| `schedules`                        | Manages schedule objects                       |
| `service`                          | Manages service objects                        |
| `service_group`                    | Manages service group objects                  |
| `syslog_server_profile`            | Manages SYSLOG server profiles                 |
| `tag`                              | Manages tag objects                            |
| **Network**                        |                                                |
| `nat_rule`                         | Manages network address translation rules      |
| **Deployment**                     |                                                |
| `remote_network`                   | Manages remote network connections             |
| **Security**                       |                                                |
| `security_rule`                    | Manages security policy rules                  |
| `anti_spyware_profile`             | Manages anti-spyware security profiles         |
| `decryption_profile`               | Manages SSL decryption profiles                |
| `dns_security_profile`             | Manages DNS security profiles                  |
| `url_category`                     | Manages custom URL categories                  |
| `vulnerability_protection_profile` | Manages vulnerability protection profiles      |
| `wildfire_antivirus_profile`       | Manages WildFire anti-virus profiles           |

For more detailed usage instructions and examples, refer to the [User Guide](about/introduction.md).

---

## Contributing

Contributions are welcome and greatly appreciated. Visit the [Contributing](about/contributing.md) page for guidelines
on how to contribute.

## License

This project is licensed under the Apache 2.0 License - see the [License](about/license.md) page for details.
