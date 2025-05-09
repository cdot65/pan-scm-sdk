# SDK Developer Documentation

Welcome to the SDK Developer Documentation for `pan-scm-sdk`. This section provides detailed information about the SDK's
configuration objects and data models used to interact with Palo Alto Networks Strata Cloud Manager.

## Contents

- [Auth](auth.md)
- [Client](client.md)
- Configuration
    - [BaseObject](config/base_object.md)
    - Deployment
        - [Bandwidth Allocation](config/deployment/bandwidth_allocations.md)
        - [BGP Routing](config/deployment/bgp_routing.md)
        - [Internal DNS Server](config/deployment/internal_dns_servers.md)
        - [Network Location](config/deployment/network_locations.md)
        - [Remote Network](config/deployment/remote_networks.md)
        - [Service Connection](config/deployment/service_connections.md)
    - Mobile Agent
        - [Authentication Setting](config/mobile_agent/auth_settings.md)
        - [Agent Version](config/mobile_agent/agent_versions.md)
    - Network
        - [IKE Crypto Profiles](config/network/ike_crypto_profile.md)
        - [IKE Gateways](config/network/ike_gateway.md)
        - [IPsec Crypto Profiles](config/network/ipsec_crypto_profile.md)
        - [NAT Rules](config/network/nat_rules.md)
        - [Security Zones](config/network/security_zone.md)
    - Objects
        - [Address](config/objects/address.md)
        - [Address Group](config/objects/address_group.md)
        - [Application](config/objects/application.md)
        - [Application Filter](config/objects/application_filters.md)
        - [Application Group](config/objects/application_group.md)
        - [Dynamic User Group](config/objects/dynamic_user_group.md)
        - [External Dynamic List](config/objects/external_dynamic_lists.md)
        - [HIP Object](config/objects/hip_object.md)
        - [HIP Profile](config/objects/hip_profile.md)
        - [HTTP Server Profile](config/objects/http_server_profiles.md)
        - [Log Forwarding Profile](config/objects/log_forwarding_profile.md)
        - [Quarantined Device](config/objects/quarantined_devices.md)
        - [Region](config/objects/region.md)
        - [Schedule](config/objects/schedules.md)
        - [Syslog Server Profile](config/objects/syslog_server_profiles.md)
        - [Service](config/objects/service.md)
        - [Service Group](config/objects/service_group.md)
        - [Tag](config/objects/tag.md)
    - Security Services
        - [Anti-Spyware Profile](config/security_services/anti_spyware_profile.md)
        - [Decryption Profile](config/security_services/decryption_profile.md)
        - [DNS Security Profile](config/security_services/dns_security_profile.md)
        - [Security Rule](config/security_services/security_rule.md)
        - [URL Categories](config/security_services/url_categories.md)
        - [Vulnerability Protection Profile](config/security_services/vulnerability_protection_profile.md)
        - [Wildfire Antivirus Profile](config/security_services/wildfire_antivirus.md)
    - Setup
        - [Folder](config/setup/folder.md)
        - [Device](config/setup/device.md)
        - [Label](config/setup/label.md)
        - [Snippet](config/setup/snippet.md)
        - [Variable](config/setup/variable.md)
- Data Models
    - Deployment
        - [Bandwidth Allocation Models](models/deployment/bandwidth_allocation_models.md)
        - [BGP Routing Models](models/deployment/bgp_routing_models.md)
        - [Internal DNS Server Models](models/deployment/internal_dns_servers_models.md)
        - [Network Location Models](models/deployment/network_locations.md)
        - [Remote Network Models](models/deployment/remote_networks_models.md)
        - [Service Connection Models](models/deployment/service_connections_models.md)
    - Mobile Agent
        - [Authentication Setting Models](models/mobile_agent/auth_settings_models.md)
        - [Agent Version Models](models/mobile_agent/agent_versions_models.md)
    - Network
        - [IKE Crypto Profile Models](models/network/ike_crypto_profile_models.md)
        - [IKE Gateway Models](models/network/ike_gateway_models.md)
        - [IPsec Crypto Profile Models](models/network/ipsec_crypto_profile_models.md)
        - [NAT Rules Models](models/network/nat_rule_models.md)
        - [Security Zone Models](models/network/security_zone_models.md)
    - Objects
        - [Address Models](models/objects/address_models.md)
        - [Address Group Models](models/objects/address_group_models.md)
        - [Application Models](models/objects/application_models.md)
        - [Application Filter Models](models/objects/application_filters_models.md)
        - [Application Group Models](models/objects/application_group_models.md)
        - [Dynamic User Group Models](models/objects/dynamic_user_group_models.md)
        - [External Dynamic List Models](models/objects/external_dynamic_lists_models.md)
        - [HIP Object Models](models/objects/hip_object_models.md)
        - [HIP Profile Models](models/objects/hip_profile_models.md)
        - [HTTP Server Profile Models](models/objects/http_server_profiles_models.md)
        - [Log Forwarding Profile Models](models/objects/log_forwarding_profile_models.md)
        - [Quarantined Device Models](models/objects/quarantined_devices_models.md)
        - [Region Models](models/objects/region_models.md)
        - [Schedule Models](models/objects/schedules_models.md)
        - [Service Models](models/objects/service_models.md)
        - [Service Group Models](models/objects/service_group_models.md)
        - [Syslog Server Profile Models](models/objects/syslog_server_profiles_models.md)
        - [Tag Models](models/objects/tag_models.md)
    - Operations
        - [Candidate Push Models](models/operations/candidate_push.md)
        - [Jobs Models](models/operations/jobs.md)
    - Security Services
        - [Anti-Spyware Profile Models](models/security_services/anti_spyware_profile_models.md)
        - [Decryption Profile Models](models/security_services/decryption_profile_models.md)
        - [DNS Security Profile Models](models/security_services/dns_security_profile_models.md)
        - [Security Rule Models](models/security_services/security_rule_models.md)
        - [URL Categories Models](models/security_services/url_categories_models.md)
        - [Vulnerability Protection Profile Models](models/security_services/vulnerability_protection_profile_models.md)
        - [WildFire Antivirus Profile Models](models/security_services/wildfire_antivirus_profile_models.md)
    - Setup
        - [Models Setup](models/setup/index.md): Folder, Label, Snippet, Device, Variable models
        - [Folder Models](models/setup/folder_models.md)
        - [Label Models](models/setup/label_models.md)
        - [Snippet Models](models/setup/snippet_models.md)
        - [Variable Models](models/setup/variable_models.md)
- [Exceptions](exceptions.md)

---

## Introduction

The `pan-scm-sdk` provides a set of classes and models to simplify interaction with the Strata Cloud Manager API. By
utilizing this SDK, developers can programmatically manage configurations, ensuring consistency and efficiency.

Starting with version 0.3.14, the SDK supports a unified client interface that allows you to access all service objects
directly through the client instance using attribute-based access. This provides a more intuitive and streamlined
developer
experience. Here's a comprehensive example showing how to use the unified client with multiple object types:

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
|------------------------------------|---------------------------------------------------------------|
| **Objects**                        |                                                               |
| `address`                          | IP addresses, CIDR ranges, and FQDNs for security policies    |
| `address_group`                    | Static or dynamic collections of address objects              |
| `application`                      | Custom application definitions and signatures                 |
| `application_filter`               | Filters for identifying applications by characteristics       |
| `application_group`                | Logical groups of applications for policy application         |
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
| **Network**                        |                                                               |
| `ike_crypto_profile`               | IKE crypto profiles for VPN tunnels                           |
| `ike_gateway`                      | IKE gateway configurations for VPN tunnel endpoints           |
| `ipsec_crypto_profile`             | IPsec crypto profiles for VPN tunnel encryption               |
| `nat_rule`                         | Network address translation policies for traffic routing      |
| `security_zone`                    | Security zones for network segmentation                       |
| **Mobile Agent**                   |                                                               |
| `auth_setting`                     | GlobalProtect authentication settings by operating system     |
| `agent_version`                    | Available GlobalProtect agent versions (read-only)            |
| **Deployment**                     |                                                               |
| `bandwidth_allocation`             | Bandwidth allocation settings for regions and service nodes   |
| `bgp_routing`                      | Global BGP routing preferences and behaviors                  |
| `internal_dns_server`              | DNS server configurations for domain resolution               |
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
| `folder`                           | Folder management for organizing configurations               |

Check out the [Client Module](client.md) documentation for more information on the unified client interface and the
available
services.

For information about specific service objects, proceed to the [Configuration Objects](config/objects/index.md) section.

To learn more about the data models used by the SDK, proceed to the [Data Models](models/objects/index.md) section,
which
explains how the Python dictionaries that are passed into the SDK are structured.
