# Network Configuration Objects

## Table of Contents

1. [Overview](#overview)
2. [Available Network Objects](#available-network-objects)
3. [Common Features](#common-features)
4. [Usage Example](#usage-example)

## Overview

This section covers the configuration of network features provided by the Palo Alto Networks Strata Cloud Manager SDK. Each configuration object corresponds to a resource in the Strata Cloud Manager and provides methods for CRUD (Create, Read, Update, Delete) operations.

## Available Network Objects

- [IKE Crypto Profiles](ike_crypto_profile.md) - Configure Internet Key Exchange crypto profiles for VPN tunnels
- [IKE Gateways](ike_gateway.md) - Configure Internet Key Exchange gateways for VPN tunnel endpoints
- [NAT Rules](nat_rules.md) - Configure Network Address Translation rules for traffic handling
- [Security Zones](security_zone.md) - Configure Security Zones for network segmentation

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

<div class="termy">

<!-- termynal -->
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

</div>

Select an object from the list above to view detailed documentation, including methods, parameters, and examples.