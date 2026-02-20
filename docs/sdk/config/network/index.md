# Network Configuration Objects

## Table of Contents

1. [Overview](#overview)
2. [Available Network Objects](#available-network-objects)
3. [Common Features](#common-features)
4. [Usage Example](#usage-example)

## Overview

This section covers the configuration of network features provided by the Palo Alto Networks Strata Cloud Manager SDK. Each configuration object corresponds to a resource in the Strata Cloud Manager and provides methods for CRUD (Create, Read, Update, Delete) operations.

## Available Network Objects

### Network Interfaces

- [Aggregate Interfaces](aggregate_interface.md) - Configure aggregate (bonded) ethernet interfaces with LACP
- [Ethernet Interfaces](ethernet_interface.md) - Configure physical ethernet interfaces (Layer 2, Layer 3, TAP modes)
- [Layer2 Subinterfaces](layer2_subinterface.md) - Configure Layer 2 VLAN subinterfaces
- [Layer3 Subinterfaces](layer3_subinterface.md) - Configure Layer 3 VLAN subinterfaces with IP addressing
- [Loopback Interfaces](loopback_interface.md) - Configure loopback interfaces for management and services
- [Tunnel Interfaces](tunnel_interface.md) - Configure tunnel interfaces for VPN connections
- [VLAN Interfaces](vlan_interface.md) - Configure VLAN interfaces for inter-VLAN routing

### VPN Configuration

- [IKE Crypto Profiles](ike_crypto_profile.md) - Configure Internet Key Exchange crypto profiles for VPN tunnels
- [IKE Gateways](ike_gateway.md) - Configure Internet Key Exchange gateways for VPN tunnel endpoints
- [IPsec Crypto Profiles](ipsec_crypto_profile.md) - Configure IPsec crypto profiles for VPN tunnels
- [IPsec Tunnels](ipsec_tunnel.md) - Configure IPsec tunnels for encrypted site-to-site VPN connectivity

### Other Network Objects

- [DHCP Interfaces](dhcp_interface.md) - Configure DHCP server and relay on firewall interfaces
- [Interface Management Profiles](interface_management_profile.md) - Configure management service access on interfaces
- [NAT Rules](nat_rules.md) - Configure Network Address Translation rules for traffic handling
- [Security Zones](security_zone.md) - Configure Security Zones for network segmentation
- [Zone Protection Profiles](zone_protection_profile.md) - Configure zone-level protection against floods, scans, and packet-based attacks

### Routing Configuration

- [Logical Router](logical_router.md) - Configure logical routers with VRF, BGP, OSPF, ECMP, and static routes

### Routing Profiles

- [BGP Address Family Profile](bgp_address_family_profile.md) - Configure BGP address family settings for peer groups
- [BGP Auth Profile](bgp_auth_profile.md) - Configure BGP MD5 authentication profiles
- [BGP Filtering Profile](bgp_filtering_profile.md) - Configure BGP filtering profiles for route filtering
- [BGP Redistribution Profile](bgp_redistribution_profile.md) - Configure BGP route redistribution between protocols
- [BGP Route Map](bgp_route_map.md) - Configure BGP route maps for import/export policy control
- [BGP Route Map Redistribution](bgp_route_map_redistribution.md) - Configure BGP route map redistribution with protocol crossover patterns
- [OSPF Auth Profile](ospf_auth_profile.md) - Configure OSPF authentication profiles
- [Route Access List](route_access_list.md) - Configure route access lists for route filtering
- [Route Prefix List](route_prefix_list.md) - Configure route prefix lists for prefix-based filtering

## Common Features

All network configuration objects provide standard operations:

- Create new network configurations
- Read existing network objects
- Update network properties
- Delete network objects
- List and filter network objects with pagination support

The network objects also enforce:

- Container validation (folder/device/snippet)
- Data validation with detailed error messages
- Consistent API patterns across all network object types

## Usage Example

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a NAT rule
client.nat_rule.create({
   "name": "outbound-nat",
   "nat_type": "ipv4",
   "source": ["10.0.0.0/24"],
   "destination": ["any"],
   "service": "any",
   "source_translation": {
      "dynamic_ip_and_port": {
         "type": "dynamic_ip_and_port",
         "translated_address": ["192.168.1.100"]
      }
   },
   "folder": "NAT Rules"
})

# List NAT rules
nat_rules = client.nat_rule.list(folder="NAT Rules")

# Print the results
for rule in nat_rules:
   print(f"NAT Rule: {rule.name}, Type: {rule.nat_type}")
```

Select an object from the list above to view detailed documentation, including methods, parameters, and examples.
