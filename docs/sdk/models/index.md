# Data Models

Welcome to the Data Models documentation for `pan-scm-sdk`. This section provides detailed information about the
Pydantic models used to validate and structure data when interacting with the Strata Cloud Manager API.

## What Are Data Models?

Data Models are **Pydantic classes** that define the schema and validation rules for configuration objects. They ensure
that data passed to and received from the API conforms to expected formats, types, and constraints.

Use this section when you need to:

- **Understand field constraints** - Learn what values are allowed for each field (patterns, lengths, enums)
- **Validate configurations** - Pre-validate data before sending to the API
- **Type annotations** - Get proper IDE autocompletion and type checking
- **Build configuration dictionaries** - Know exactly what fields are required vs optional

## Model Types

Each resource has three model types:

| Model Type | Purpose | Example |
|------------|---------|---------|
| `CreateModel` | Validates data for creating new resources | `AddressCreateModel` |
| `UpdateModel` | Validates data for updating existing resources (includes `id`) | `AddressUpdateModel` |
| `ResponseModel` | Represents data returned from the API | `AddressResponseModel` |

## Example Usage

```python
from scm.models.objects.address import AddressCreateModel

# Validate configuration before API call
try:
    config = AddressCreateModel(
        name="web-server",
        ip_netmask="10.0.1.100/32",
        folder="Texas",
        description="Primary web server"
    )
    print(f"Valid config: {config.model_dump()}")
except ValueError as e:
    print(f"Validation error: {e}")
```

## Categories

### Deployment
Models for Prisma Access deployment configuration:
- [Bandwidth Allocations](deployment/bandwidth_allocation_models.md)
- [BGP Routing](deployment/bgp_routing_models.md)
- [Internal DNS Servers](deployment/internal_dns_servers_models.md)
- [Network Locations](deployment/network_locations.md)
- [Remote Networks](deployment/remote_networks_models.md)
- [Service Connections](deployment/service_connections_models.md)

### Mobile Agent
Models for GlobalProtect mobile agent configuration:
- [Authentication Settings](mobile_agent/auth_settings_models.md)
- [Agent Versions](mobile_agent/agent_versions_models.md)

### Network
Models for network infrastructure:
- [IKE Crypto Profiles](network/ike_crypto_profile_models.md)
- [IKE Gateways](network/ike_gateway_models.md)
- [IPsec Crypto Profiles](network/ipsec_crypto_profile_models.md)
- [NAT Rules](network/nat_rule_models.md)
- [Security Zones](network/security_zone_models.md)

### Objects
Models for reusable policy objects:
- [Addresses](objects/address_models.md)
- [Address Groups](objects/address_group_models.md)
- [Applications](objects/application_models.md)
- [Application Filters](objects/application_filters_models.md)
- [Application Groups](objects/application_group_models.md)
- [Auto Tag Actions](objects/auto_tag_actions_models.md)
- [Dynamic User Groups](objects/dynamic_user_group_models.md)
- [External Dynamic Lists](objects/external_dynamic_lists_models.md)
- [HIP Objects](objects/hip_object_models.md)
- [HIP Profiles](objects/hip_profile_models.md)
- [HTTP Server Profiles](objects/http_server_profiles_models.md)
- [Log Forwarding Profiles](objects/log_forwarding_profile_models.md)
- [Quarantined Devices](objects/quarantined_devices_models.md)
- [Regions](objects/region_models.md)
- [Schedules](objects/schedules_models.md)
- [Services](objects/service_models.md)
- [Service Groups](objects/service_group_models.md)
- [Syslog Server Profiles](objects/syslog_server_profiles_models.md)
- [Tags](objects/tag_models.md)

### Operations
Models for operational tasks:
- [Candidate Push](operations/candidate_push.md)
- [Jobs](operations/jobs.md)

### Security Services
Models for security profiles and policies:
- [Anti-Spyware Profiles](security_services/anti_spyware_profile_models.md)
- [Decryption Profiles](security_services/decryption_profile_models.md)
- [DNS Security Profiles](security_services/dns_security_profile_models.md)
- [Security Rules](security_services/security_rule_models.md)
- [URL Categories](security_services/url_categories_models.md)
- [Vulnerability Protection Profiles](security_services/vulnerability_protection_profile_models.md)
- [WildFire Antivirus Profiles](security_services/wildfire_antivirus_profile_models.md)

### Setup
Models for organizational containers:
- [Folders](setup/folder_models.md)
- [Labels](setup/label_models.md)
- [Snippets](setup/snippet_models.md)
- [Devices](setup/device_models.md)
- [Variables](setup/variable_models.md)

### Insights
Models for Prisma Access Insights:
- [Alerts](insights/alerts_models.md)

---

## Relationship to SDK Reference

The **Data Models** define *what* data looks like, while the **[SDK Reference](../index.md)** documents *how* to
perform operations. For example:

- Use `AddressCreateModel` (Data Models) to understand required fields
- Use `client.address.create()` (SDK Reference) to actually create the address

```python
from scm.client import Scm

client = Scm(client_id="...", client_secret="...", tsg_id="...")

# The dictionary you pass follows AddressCreateModel schema
client.address.create({
    "name": "web-server",        # Required: str, max 63 chars
    "ip_netmask": "10.0.1.100",  # One of: ip_netmask, ip_range, ip_wildcard, fqdn
    "folder": "Texas",           # Required: one container type
})
```
