# SDK Reference

Welcome to the SDK Reference for `pan-scm-sdk`. This section documents the **service classes** that provide CRUD
operations for managing Strata Cloud Manager configurations.

## What Is the SDK Reference?

The SDK Reference documents **service classes** - Python classes that handle API communication for each resource type.
Use these classes to create, read, update, delete, and list configuration objects.

Use this section when you need to:

- **Perform CRUD operations** - Create, read, update, delete resources
- **List and filter resources** - Query configurations with various filters
- **Understand method signatures** - Know what parameters each method accepts
- **See usage examples** - Copy working code patterns

!!! note "Looking for field schemas and validation rules?"
    See the **[Data Models](models/index.md)** section to understand what fields are required, allowed values,
    and validation constraints for each resource type.

---

## Quick Start

The SDK uses a unified client interface to access all service objects:

```python
from scm.client import Scm

# Initialize the unified client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# ===== WORKING WITH ADDRESS OBJECTS =====

# List all addresses in a folder
addresses = client.address.list(folder="Texas")
print(f"Found {len(addresses)} addresses in Texas folder")

# Fetch a specific address by name
web_server = client.address.fetch(name="web-server", folder="Texas")
print(f"Address details - Name: {web_server.name}, IP: {web_server.ip_netmask or web_server.fqdn}")

# Update the description of the address
web_server.description = "Primary web server updated via unified client"
updated_address = client.address.update(web_server)
print(f"Updated address description: {updated_address.description}")

# ===== WORKING WITH BGP ROUTING =====

# Get current BGP routing settings
bgp_settings = client.bgp_routing.get()
print(f"Current BGP backbone routing: {bgp_settings.backbone_routing}")

# Update BGP routing preferences
client.bgp_routing.update({
    "routing_preference": {"hot_potato_routing": {}},
    "backbone_routing": "asymmetric-routing-with-load-share",
    "accept_route_over_SC": True,
    "outbound_routes_for_services": ["10.0.0.0/8", "172.16.0.0/12"],
})
print("Updated BGP routing settings")

# ===== WORKING WITH INTERNAL DNS SERVERS =====

# Create a new internal DNS server
dns_server = client.internal_dns_server.create({
    "name": "main-dns-server",
    "domain_name": ["example.com", "internal.example.com"],
    "primary": "192.168.1.10",
    "secondary": "192.168.1.11"
})
print(f"Created DNS server: {dns_server.name} with ID: {dns_server.id}")

# List all DNS servers
dns_servers = client.internal_dns_server.list()
print(f"Found {len(dns_servers)} DNS servers")

# ===== WORKING WITH SECURITY RULES =====

# Fetch a specific security rule
security_rule = client.security_rule.fetch(name="allow-web-traffic", folder="Texas")
print(f"Security rule: {security_rule.name}")
print(f"  Source zones: {security_rule.source_zone}")
print(f"  Destination zones: {security_rule.destination_zone}")
print(f"  Action: {security_rule.action}")

# ===== WORKING WITH NAT RULES =====

# List NAT rules with filtering (source zone = "trust")
filtered_nat_rules = client.nat_rule.list(
    folder="Texas",
    source_zone=["trust"]
)
print(f"Found {len(filtered_nat_rules)} NAT rules with source zone 'trust'")

# Delete a NAT rule if any were found
if filtered_nat_rules:
    rule_to_delete = filtered_nat_rules[0].id
    rule_name = filtered_nat_rules[0].name
    client.nat_rule.delete(rule_to_delete)
    print(f"Deleted NAT rule '{rule_name}' (ID: {rule_to_delete})")

# ===== WORKING WITH BANDWIDTH ALLOCATIONS =====

# List all bandwidth allocations
allocations = client.bandwidth_allocation.list()
print(f"Found {len(allocations)} bandwidth allocations")

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

# ===== WORKING WITH AUTHENTICATION SETTINGS =====

# List all authentication settings
auth_settings = client.auth_setting.list()
print(f"Found {len(auth_settings)} authentication settings")

# Create new authentication settings for Windows
windows_auth = client.auth_setting.create({
    "name": "windows_auth",
    "authentication_profile": "windows-profile",
    "os": "Windows",
    "user_credential_or_client_cert_required": True,
    "folder": "Mobile Users"
})
print(f"Created authentication settings: {windows_auth.name}")

# Move authentication settings to the top of evaluation order
client.auth_setting.move({
    "name": "windows_auth",
    "where": "top"
})
print("Moved Windows authentication settings to the top")

# ===== WORKING WITH AGENT VERSIONS =====

# List all available GlobalProtect agent versions
agent_versions = client.agent_version.list()
print(f"Found {len(agent_versions)} GlobalProtect agent versions")

# Filter for specific versions
filtered_versions = client.agent_version.list(version="5.3")
print(f"Found {len(filtered_versions)} versions containing '5.3'")

# Fetch a specific version
try:
    version = client.agent_version.fetch("5.3.0")
    print(f"Found specific version: {version}")
except Exception as e:
    print(f"Version not found: {str(e)}")

# ===== WORKING WITH INSIGHTS ALERTS =====

# List recent critical alerts
critical_alerts = client.insights.alerts.list(
    severity=["critical"],
    status=["Raised"],
    start_time=7  # Last 7 days
)
print(f"Found {len(critical_alerts)} critical alerts")

# Get alert statistics
stats = client.insights.alerts.get_statistics(
    time_range=30,
    group_by="severity"
)
for stat in stats:
    print(f"{stat.severity}: {stat.count} alerts")

# Generate alert timeline
timeline = client.insights.alerts.get_timeline(
    time_range=7,
    interval="hour",
    status="Raised"
)
print(f"Generated {len(timeline)} timeline points")

# ===== COMMIT CHANGES =====

# Commit all changes to apply them to the firewall
commit_result = client.commit(
    folders=["Texas", "Mobile Users"],
    description="Updated configurations via unified client",
    sync=True  # Wait for commit to complete
)

# Check commit status
job_status = client.get_job_status(commit_result.job_id)
print(f"Commit job status: {job_status.data[0].status_str}")
```

## Available Client Services

The following table shows all services available through the unified client interface:

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
| `auth_setting`                     | GlobalProtect authentication settings by operating system     |
| `agent_version`                    | Available GlobalProtect agent versions (read-only)            |
| **Network**                        |                                                               |
| `aggregate_interface`              | Aggregated ethernet interfaces with LACP support              |
| `ethernet_interface`               | Physical ethernet interface configurations                    |
| `ike_crypto_profile`               | IKE crypto profiles for VPN tunnels                           |
| `ike_gateway`                      | IKE gateway configurations for VPN tunnel endpoints           |
| `ipsec_crypto_profile`             | IPsec crypto profiles for VPN tunnel encryption               |
| `layer2_subinterface`              | Layer 2 VLAN subinterfaces for switching                      |
| `layer3_subinterface`              | Layer 3 VLAN subinterfaces for routing                        |
| `loopback_interface`               | Loopback interfaces for management and routing                |
| `nat_rule`                         | Network address translation policies for traffic routing      |
| `security_zone`                    | Security zones for network segmentation                       |
| `tunnel_interface`                 | Tunnel interfaces for VPN and overlay networks                |
| `vlan_interface`                   | VLAN interfaces for network segmentation                      |
| **Deployment**                     |                                                               |
| `bandwidth_allocation`             | Bandwidth allocation settings for regions and service nodes   |
| `bgp_routing`                      | Global BGP routing preferences and behaviors                  |
| `internal_dns_server`              | DNS server configurations for domain resolution               |
| `network_location`                 | Geographic network locations for service connectivity         |
| `remote_network`                   | Secure branch and remote site connectivity configurations     |
| `service_connection`               | Service connections to cloud service providers                |
| **Security**                       |                                                               |
| `anti_spyware_profile`             | Protection against spyware, C2 traffic, and data exfiltration |
| `decryption_profile`               | SSL/TLS traffic inspection configurations                     |
| `dns_security_profile`             | Protection against DNS-based threats and tunneling            |
| `security_rule`                    | Core security policies controlling network traffic            |
| `url_category`                     | Custom URL categorization for web filtering                   |
| `vulnerability_protection_profile` | Defense against known CVEs and exploit attempts               |
| `wildfire_antivirus_profile`       | Cloud-based malware analysis and zero-day protection          |
| **Insights**                       |                                                               |
| `alerts`                           | Security and operational alerts from Prisma Access            |
| **Setup**                          |                                                               |
| `device`                           | Device resources and management                               |
| `folder`                           | Folder organization and hierarchy                             |
| `label`                            | Resource classification and simple key-value object labels    |
| `snippet`                          | Reusable configuration snippets                               |
| `variable`                         | Typed variables with flexible container scoping               |

Check out the [Client Module](client.md) documentation for more information on the unified client interface.

## Service Categories

- **[Deployment](config/deployment/index.md)** - Prisma Access infrastructure (bandwidth, BGP, DNS, remote networks)
- **[Mobile Agent](config/mobile_agent/index.md)** - GlobalProtect agent configuration
- **[Network](config/network/index.md)** - VPN profiles, NAT rules, security zones
- **[Objects](config/objects/index.md)** - Reusable policy objects (addresses, services, tags)
- **[Security Services](config/security_services/index.md)** - Security profiles and rules
- **[Setup](config/setup/index.md)** - Organizational containers (folders, snippets, devices)
- **[Insights](insights/index.md)** - Prisma Access Insights alerts

## Related Documentation

- **[Data Models](models/index.md)** - Pydantic schemas for validating configuration data
- **[Exceptions](exceptions.md)** - Error handling and exception types
