# SDK Developer Documentation

Welcome to the SDK Developer Documentation for `pan-scm-sdk`. This section provides detailed information about the SDK's
configuration objects and data models used to interact with Palo Alto Networks Strata Cloud Manager.

## Contents

- [Auth](auth.md)
- [Client](client.md)
- Configuration
    - [BaseObject](config/base_object.md)
    - Deployment
        - [Remote Networks](config/deployment/remote_networks.md)
    - Network
        - [NAT Rules](config/network/nat_rules.md)
    - Objects
        - [Address](config/objects/address.md)
        - [Address Group](config/objects/address_group.md)
        - [Application](config/objects/application.md)
        - [Application Filters](config/objects/application_filters.md)
        - [Application Group](config/objects/application_group.md)
        - [Dynamic User Group](config/objects/dynamic_user_group.md)
        - [External Dynamic Lists](config/objects/external_dynamic_lists.md)
        - [HIP Object](config/objects/hip_object.md)
        - [HIP Profile](config/objects/hip_profile.md)
        - [HTTP Server Profiles](config/objects/http_server_profiles.md)
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
        - [Remote Networks](models/deployment/remote_networks_models.md)
    - Network
        - [NAT Rules](models/network/nat_rule_models.md)
    - Objects
        - [Address Models](models/objects/address_models.md)
        - [Address Group Models](models/objects/address_group_models.md)
        - [Application Models](models/objects/application_models.md)
        - [Application Filters Models](models/objects/application_filters_models.md)
        - [Application Group Models](models/objects/application_group_models.md)
        - [Dynamic User Group Models](models/objects/dynamic_user_group_models.md)
        - [External Dynamic Lists Models](models/objects/external_dynamic_lists_models.md)
        - [HIP Object Models](models/objects/hip_object_models.md)
        - [HIP Profile Models](models/objects/hip_profile_models.md)
        - [HTTP Server Profile Models](models/objects/http_server_profiles_models.md)
        - [Log Forwarding Profile Models](models/objects/log_forwarding_profile_models.md)
        - [Region Models](models/objects/region_models.md)
        - [Service Models](models/objects/service_models.md)
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

# ===== COMMIT CHANGES =====

# Commit all changes to apply them to the firewall
commit_result = client.commit(
    folders=["Texas"],
    description="Updated web-server address and removed NAT rule",
    sync=True  # Wait for commit to complete
)

# Check commit status
job_status = client.get_job_status(commit_result.job_id)
print(f"Commit job status: {job_status.data[0].status_str}")
```

## Available Client Services

The following table shows all services available through the unified client interface:

| Client Property                    | Class                            | Description                                    |
|------------------------------------|----------------------------------|------------------------------------------------|
| **Objects**                        |                                  |                                                |
| `address`                          | `Address`                        | Manages IP and FQDN address objects            |
| `address_group`                    | `AddressGroup`                   | Manages address group objects                  |
| `application`                      | `Application`                    | Manages custom application objects             |
| `application_filter`               | `ApplicationFilters`             | Manages application filter objects             |
| `application_group`                | `ApplicationGroup`               | Manages application group objects              |
| `dynamic_user_group`               | `DynamicUserGroup`               | Manages dynamic user group objects             |
| `external_dynamic_list`            | `ExternalDynamicLists`           | Manages external dynamic list objects          |
| `hip_object`                       | `HIPObject`                      | Manages host information profile objects       |
| `hip_profile`                      | `HIPProfile`                     | Manages host information profile group objects |
| `http_server_profile`              | `HTTPServerProfile`              | Manages HTTP server profile objects            |
| `log_forwarding_profile`           | `LogForwardingProfile`           | Manages Log Forwarding profile objects         |
| `region`                           | `Region`                         | Manages geographic region objects              |
| `service`                          | `Service`                        | Manages service objects                        |
| `service_group`                    | `ServiceGroup`                   | Manages service group objects                  |
| `tag`                              | `Tag`                            | Manages tag objects                            |
| **Network**                        |                                  |                                                |
| `nat_rule`                         | `NATRule`                        | Manages network address translation rules      |
| **Deployment**                     |                                  |                                                |
| `remote_network`                   | `RemoteNetworks`                 | Manages remote network connections             |
| **Security**                       |                                  |                                                |
| `security_rule`                    | `SecurityRule`                   | Manages security policy rules                  |
| `anti_spyware_profile`             | `AntiSpywareProfile`             | Manages anti-spyware security profiles         |
| `decryption_profile`               | `DecryptionProfile`              | Manages SSL decryption profiles                |
| `dns_security_profile`             | `DNSSecurityProfile`             | Manages DNS security profiles                  |
| `url_category`                     | `URLCategories`                  | Manages custom URL categories                  |
| `vulnerability_protection_profile` | `VulnerabilityProtectionProfile` | Manages vulnerability protection profiles      |
| `wildfire_antivirus_profile`       | `WildfireAntivirusProfile`       | Manages WildFire anti-virus profiles           |

Check out the [Client Module](client.md) documentation for more information on the unified client interface and the available
services.

For information about specific service objects, proceed to the [Configuration Objects](config/objects/index) section.

To learn more about the data models used by the SDK, proceed to the [Data Models](models/objects/index) section, which
explains how the Python dictionaries that are passed into the SDK are structured.
