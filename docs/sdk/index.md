# SDK Developer Documentation

Welcome to the SDK Developer Documentation for `pan-scm-sdk`. This section provides detailed information about the SDK's
configuration objects and data models used to interact with Palo Alto Networks Strata Cloud Manager.

## Contents

- [Auth](auth.md)
- [Client](client.md)
- Configuration
    - [BaseObject](config/base_object.md)
    - Deployment
        - [Bandwidth Allocations](config/deployment/bandwidth_allocations.md)
        - [BGP Routing](config/deployment/bgp_routing.md)
        - [Internal DNS Servers](config/deployment/internal_dns_servers.md)
        - [Network Locations](config/deployment/network_locations.md)
        - [Remote Networks](config/deployment/remote_networks.md)
        - [Service Connections](config/deployment/service_connections.md)
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
        - [Anti-Spyware Profile](config/security_services/anti_spyware_profile)
        - [Decryption Profile](config/security_services/decryption_profile.md)
        - [DNS Security Profile](config/security_services/dns_security_profile.md)
        - [Security Rule](config/security_services/security_rule.md)
        - [URL Categories](config/security_services/url_categories.md)
        - [Vulnerability Protection Profile](config/security_services/vulnerability_protection_profile.md)
        - [Wildfire Antivirus Profile](config/security_services/wildfire_antivirus.md)
- Data Models
    - Deployment
        - [Bandwidth Allocation Models](models/deployment/bandwidth_allocation_models.md)
        - [BGP Routing Models](models/deployment/bgp_routing_models.md)
        - [Internal DNS Servers Models](models/deployment/internal_dns_servers_models.md)
        - [Network Locations Models](models/deployment/network_locations.md)
        - [Remote Networks Models](models/deployment/remote_networks_models.md)
        - [Service Connections Models](models/deployment/service_connections_models.md)
    - Network
        - [IKE Crypto Profile Models](models/network/ike_crypto_profile_models.md)
        - [IKE Gateway Models](models/network/ike_gateway_models.md)
        - [IPsec Crypto Profile Models](models/network/ipsec_crypto_profile_models.md)
        - [NAT Rules Models](models/network/nat_rule_models.md)
        - [Security Zones Models](models/network/security_zone_models.md)
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
        - [Syslog Server Profile Models](models/objects/syslog_server_profiles_models.md)
        - [Service Group Models](models/objects/service_group_models.md)
        - [Tag Models](models/objects/tag_models.md)
    - Operations
        - [Candidate Push (commit) Models](models/operations/candidate_push.md)
        - [Jobs Models](models/operations/jobs.md)
    - Security Services
        - [Anti-Spyware Profile Models](models/security_services/anti_spyware_profile_models.md)
        - [Decryption Profile Models](models/security_services/decryption_profile_models.md)
        - [DNS Security Profile Models](models/security_services/dns_security_profile_models.md)
        - [Security Rule Models](models/security_services/security_rule_models.md)
        - [URL Categories Models](models/security_services/url_categories_models.md)
        - [Vulnerability Protection Profile Models](models/security_services/vulnerability_protection_profile_models.md)
        - [Wildfire Antivirus Profile Models](models/security_services/wildfire_antivirus_profile_models.md)
- [Exceptions](exceptions.md)

---

## Introduction

The `pan-scm-sdk` provides a set of classes and models to simplify interaction with the Strata Cloud Manager API. By
utilizing this SDK, developers can programmatically manage configurations, ensuring consistency and efficiency.

Starting with version 0.3.14, the SDK supports a unified client interface that allows you to access all service objects
directly through the client instance using attribute-based access. This provides a more intuitive and streamlined developer
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
dns_server = client.internal_dns_servers.create({
    "name": "main-dns-server",
    "domain_name": ["example.com", "internal.example.com"],
    "primary": "192.168.1.10",
    "secondary": "192.168.1.11"
})
print(f"Created DNS server: {dns_server.name} with ID: {dns_server.id}")

# List all DNS servers
dns_servers = client.internal_dns_servers.list()
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

# ===== WORKING WITH NETWORK LOCATIONS =====

# List all network locations
locations = client.network_location.list()
print(f"Found {len(locations)} network locations")

# Filter locations by continent
us_locations = client.network_location.list(continent="North America")
print(f"Found {len(us_locations)} locations in North America")

# Fetch a specific location by value
west_coast = client.network_location.fetch("us-west-1")
print(f"Location: {west_coast.display} ({west_coast.value})")
print(f"Region: {west_coast.region}, Coordinates: {west_coast.latitude}, {west_coast.longitude}")

# ===== COMMIT CHANGES =====

# Commit all changes to apply them to the firewall
commit_result = client.commit(
    folders=["Texas"],
    description="Updated web-server address and BGP routing settings",
    sync=True  # Wait for commit to complete
)

# Check commit status
job_status = client.get_job_status(commit_result.job_id)
print(f"Commit job status: {job_status.data[0].status_str}")
```

## Available Client Services

The following table shows all services available through the unified client interface:

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
| `ike_crypto_profile`               | IKE crypto profiles for VPN tunnels                            |
| `ike_gateway`                      | IKE gateway configurations for VPN tunnel endpoints             |
| `ipsec_crypto_profile`             | IPsec crypto profiles for VPN tunnel encryption                 |
| `nat_rule`                         | Network address translation policies for traffic routing        |
| `security_zone`                    | Security zones for network segmentation                         |
| **Deployment**                     |                                                                 |
| `bandwidth_allocation`             | Bandwidth allocation settings for regions and service nodes     |
| `bgp_routing`                      | Global BGP routing preferences and behaviors                    |
| `internal_dns_servers`             | DNS server configurations for domain resolution                 |
| `network_location`                 | Geographic network locations for service connectivity           |
| `remote_network`                   | Secure branch and remote site connectivity configurations       |
| `service_connection`               | Service connections to cloud service providers                  |
| **Security**                       |                                                                 |
| `security_rule`                    | Core security policies controlling network traffic              |
| `anti_spyware_profile`             | Protection against spyware, C2 traffic, and data exfiltration   |
| `decryption_profile`               | SSL/TLS traffic inspection configurations                       |
| `dns_security_profile`             | Protection against DNS-based threats and tunneling              |
| `url_category`                     | Custom URL categorization for web filtering                     |
| `vulnerability_protection_profile` | Defense against known CVEs and exploit attempts                 |
| `wildfire_antivirus_profile`       | Cloud-based malware analysis and zero-day protection            |

Check out the [Client Module](client.md) documentation for more information on the unified client interface and the available
services.

For information about specific service objects, proceed to the [Configuration Objects](config/objects/index) section.

To learn more about the data models used by the SDK, proceed to the [Data Models](models/objects/index) section, which
explains how the Python dictionaries that are passed into the SDK are structured.