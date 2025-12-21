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

```bash
$ pip install pan-scm-sdk
```

## Quick Example

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

# Work with Internal DNS Servers
dns_server = client.internal_dns_server.create({
    "name": "main-dns-server",
    "domain_name": ["example.com", "internal.example.com"],
    "primary": "192.168.1.10",
    "secondary": "192.168.1.11"
})
print(f"Created DNS server: {dns_server.name}")

# List all DNS servers
dns_servers = client.internal_dns_server.list()
print(f"Found {len(dns_servers)} DNS servers")

# Work with BGP Routing
bgp_settings = client.bgp_routing.get()
print(f"Current BGP routing: {bgp_settings.backbone_routing}")

# Update BGP routing preferences
client.bgp_routing.update({
    "routing_preference": {"hot_potato_routing": {}},
    "backbone_routing": "asymmetric-routing-with-load-share",
    "accept_route_over_SC": True,
    "outbound_routes_for_services": ["10.0.0.0/8"]
})
print("Updated BGP routing settings")

# Work with Network Locations
locations = client.network_location.list()
print(f"Found {len(locations)} network locations")

us_locations = client.network_location.list(continent="North America")
print(f"Found {len(us_locations)} locations in North America")

west_coast = client.network_location.fetch("us-west-1")
print(f"Location: {west_coast.display} ({west_coast.value})")

# Work with GlobalProtect Agent Versions (read-only)
agent_versions = client.agent_version.list()
print(f"Found {len(agent_versions)} GlobalProtect agent versions")

# Filter for specific versions
filtered_versions = client.agent_version.list(version="5.3")
print(f"Found {len(filtered_versions)} versions containing '5.3'")

# Work with Security Rules
security_rule = client.security_rule.fetch(name="allow-web", folder="Texas")
print(f"Security rule: {security_rule.name}, Action: {security_rule.action}")

# Work with NAT Rules - list with filtering
nat_rules = client.nat_rule.list(
    folder="Texas",
    source_zone=["trust"]
)
print(f"Found {len(nat_rules)} NAT rules with source zone 'trust'")

# Work with Security Zones
security_zones = client.security_zone.list(folder="Texas")
print(f"Found {len(security_zones)} security zones")

# Work with Bandwidth Allocations
bandwidth_allocations = client.bandwidth_allocation.list()
print(f"Found {len(bandwidth_allocations)} bandwidth allocations")

# Create a new bandwidth allocation
new_allocation = client.bandwidth_allocation.create({
    "name": "test-region",
    "allocated_bandwidth": 100,
    "spn_name_list": ["spn1", "spn2"],
    "qos": {
        "enabled": True,
        "customized": True,
        "profile": "test-profile",
        "guaranteed_ratio": 0.5
    }
})
print(f"Created bandwidth allocation: {new_allocation.name}")

# Delete a NAT rule
if nat_rules:
    client.nat_rule.delete(nat_rules[0].id)
    print(f"Deleted NAT rule: {nat_rules[0].name}")

# Work with Prisma Access Insights - Alerts
# List recent high-severity alerts
high_severity_alerts = client.insights.alerts.list(
    severity=["critical", "high"],
    status=["Raised"],
    start_time=7  # Last 7 days
)
print(f"Found {len(high_severity_alerts)} high-severity alerts")

# Get alert statistics by severity
alert_stats = client.insights.alerts.get_statistics(
    time_range=30,
    group_by="severity"
)
for stat in alert_stats:
    print(f"{stat.severity}: {stat.count} alerts")

# Generate alert timeline
timeline = client.insights.alerts.get_timeline(
    time_range=7,
    interval="day",
    status="Raised"
)
for point in timeline:
    print(f"Day {point.state}: {point.count} alerts")

# Make configuration changes
client.commit(
    folders=["Texas"],
    description="Updated address, DNS servers, BGP routing, and removed NAT rule",
    sync=True
)
```

For more detailed usage instructions and examples, refer to the [User Guide](about/introduction.md).

---

## Documentation Guide

This documentation is organized into two main developer sections:

### SDK Reference

**[Go to SDK Reference →](sdk/index.md)**

Service classes for performing CRUD operations on Strata Cloud Manager resources.

Use when you need to:

- Create, read, update, or delete configurations
- List and filter resources
- See method signatures and usage examples

### Data Models

**[Go to Data Models →](sdk/models/index.md)**

Pydantic schemas that define validation rules and field constraints.

Use when you need to:

- Understand required vs optional fields
- Check allowed values and patterns
- Pre-validate configurations before API calls

---

## Contributing

Contributions are welcome and greatly appreciated. Visit the [Contributing](about/contributing.md) page for guidelines
on how to contribute.

## License

This project is licensed under the Apache 2.0 License - see the [License](about/license.md) page for details.
