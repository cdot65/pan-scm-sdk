# Network Data Models

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Common Model Patterns](#common-model-patterns)
4. [Usage Examples](#usage-examples)
5. [Models by Category](#models-by-category)
   1. [Network Interfaces](#network-interfaces)
   2. [Network Services](#network-services)
   3. [VPN Configuration](#vpn-configuration)
   4. [Other Network Models](#other-network-models)
   5. [Routing Configuration](#routing-configuration)
   6. [Routing Profile Models](#routing-profile-models)
6. [Best Practices](#best-practices)
7. [Related Documentation](#related-documentation)

## Overview {#Overview}
<span id="overview"></span>

The Strata Cloud Manager SDK uses Pydantic models for data validation and serialization of network configurations. These models ensure that the data being sent to and received from the Strata Cloud Manager API adheres to the expected structure and constraints. This section documents the models for network configuration resources.

## Model Types

For each network configuration, there are corresponding model types:

- **Create Models**: Used when creating new network resources (`{Object}CreateModel`)
- **Update Models**: Used when updating existing network resources (`{Object}UpdateModel`)
- **Response Models**: Used when parsing network data retrieved from the API (`{Object}ResponseModel`)
- **Base Models**: Common shared attributes for related network models (`{Object}BaseModel`)

## Common Model Patterns

Network models share common patterns:

- Container validation (exactly one of folder/snippet/device)
- UUID validation for identifiers
- Network address and service validation
- Translation configuration validation
- Rule positioning and ordering logic
- Discriminated union patterns for advanced configurations

## Usage Examples

```python
from scm.client import ScmClient
from scm.models.network import NatRuleCreateModel, NatRuleUpdateModel

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a new NAT rule using a model
nat_rule = NatRuleCreateModel(
   name="outbound-nat",
   source=["10.0.0.0/24"],
   destination=["any"],
   service="any",
   nat_type="ipv4",
   source_translation={
      "dynamic_ip_and_port": {
         "type": "dynamic_ip_and_port",
         "translated_address": ["192.168.1.100"]
      }
   },
   folder="NAT Rules"
)

# Convert the model to a dictionary for the API call
rule_dict = nat_rule.model_dump(exclude_unset=True)
result = client.nat_rule.create(rule_dict)

# Update an existing NAT rule using a model
update_rule = NatRuleUpdateModel(
   id=result.id,
   name="outbound-nat-updated",
   description="Updated outbound NAT rule",
   folder="NAT Rules"
)

update_dict = update_rule.model_dump(exclude_unset=True)
updated_result = client.nat_rule.update(update_dict)
```

## Models by Category

### Network Interfaces

- [Aggregate Interface Models](aggregate_interface_models.md) - Aggregate (bonded) ethernet interfaces with LACP
- [Ethernet Interface Models](ethernet_interface_models.md) - Physical ethernet interfaces (Layer 2/3/TAP modes)
- [Layer2 Subinterface Models](layer2_subinterface_models.md) - Layer 2 VLAN subinterfaces
- [Layer3 Subinterface Models](layer3_subinterface_models.md) - Layer 3 VLAN subinterfaces with IP addressing
- [Loopback Interface Models](loopback_interface_models.md) - Loopback interfaces
- [Tunnel Interface Models](tunnel_interface_models.md) - Tunnel interfaces for VPN
- [VLAN Interface Models](vlan_interface_models.md) - VLAN interfaces for inter-VLAN routing

### Network Services

- [DHCP Interface Models](dhcp_interface_models.md) - DHCP server and relay configurations on firewall interfaces
- [Interface Management Profile Models](interface_management_profile_models.md) - Interface management profiles for controlling management access

### VPN Configuration

- [IKE Crypto Profile Models](ike_crypto_profile_models.md) - Internet Key Exchange crypto profiles for VPN tunnels
- [IKE Gateway Models](ike_gateway_models.md) - Internet Key Exchange gateways for VPN tunnel endpoints
- [IPsec Crypto Profile Models](ipsec_crypto_profile_models.md) - IPsec crypto profiles for VPN tunnels
- [IPsec Tunnel Models](ipsec_tunnel_models.md) - IPsec tunnel configurations for site-to-site VPN

### Other Network Models

- [DNS Proxy Models](dns_proxy_models.md) - DNS proxy configurations with domain-specific rules and caching
- [NAT Rule Models](nat_rule_models.md) - Network Address Translation rules
- [PBF Rule Models](pbf_rule_models.md) - Policy-Based Forwarding rule configurations
- [QoS Profile Models](qos_profile_models.md) - Quality of Service profile configurations
- [QoS Rule Models](qos_rule_models.md) - QoS policy rule configurations with move operations
- [Security Zone Models](security_zone_models.md) - Security Zone configuration and management
- [Zone Protection Profile Models](zone_protection_profile_models.md) - Zone protection profiles for flood and scan protection

### Routing Configuration

- [Logical Router Models](logical_router_models.md) - Logical router models with VRF, BGP, OSPF, ECMP, and static routes

### Routing Profile Models

- [BGP Address Family Profile Models](bgp_address_family_profile_models.md) - BGP address family configuration models
- [BGP Auth Profile Models](bgp_auth_profile_models.md) - BGP MD5 authentication profile models
- [BGP Filtering Profile Models](bgp_filtering_profile_models.md) - BGP filtering profile models for route filtering
- [BGP Redistribution Profile Models](bgp_redistribution_profile_models.md) - BGP redistribution profile models
- [BGP Route Map Models](bgp_route_map_models.md) - BGP route map models with match/set criteria
- [BGP Route Map Redistribution Models](bgp_route_map_redistribution_models.md) - BGP route map redistribution models with protocol crossover patterns
- [OSPF Auth Profile Models](ospf_auth_profile_models.md) - OSPF authentication profile models
- [Route Access List Models](route_access_list_models.md) - Route access list models for route filtering
- [Route Prefix List Models](route_prefix_list_models.md) - Route prefix list models for prefix-based filtering

## Best Practices

1. **Model Validation**
   - Always validate network configuration data with models before sending to the API
   - Handle validation errors appropriately for network configurations
   - Use model_dump(exclude_unset=True) to avoid sending default values in network rules

2. **NAT Rule Configuration**
   - Ensure source and destination addresses are properly formatted
   - Validate that exactly one translation type is specified
   - Test NAT rules in a non-production environment first
   - Document NAT rules and their intended purpose

3. **Network Address Handling**
   - Validate IP addresses and subnets before creating rules
   - Use CIDR notation consistently for network addresses
   - Be aware of overlapping network definitions
   - Consider using address objects for frequently used networks

4. **Error Handling**
   - Catch and handle ValueError exceptions from network model validation
   - Check for common NAT configuration issues (missing translation, invalid addresses)
   - Validate that referenced services exist when used in NAT rules

## Related Documentation

- [Network Configuration](../../config/network/index.md) - Working with network configurations
- [NAT Rules Configuration](../../config/network/nat_rules.md) - NAT rule operations
- [Address Models](../objects/address_models.md) - Address models used in network configurations
