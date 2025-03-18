# Working with Configuration Objects

The Strata Cloud Manager SDK provides a unified interface for working with various configuration objects in the Palo Alto Networks ecosystem.

## Object Categories

The SDK organizes configuration objects into several categories:

### Network Objects

- [Address](../sdk/config/objects/address.md)
- [Address Group](../sdk/config/objects/address_group.md)
- [Service](../sdk/config/objects/service.md)
- [Service Group](../sdk/config/objects/service_group.md)
- [Tag](../sdk/config/objects/tag.md)

### Applications

- [Application](../sdk/config/objects/application.md)
- [Application Group](../sdk/config/objects/application_group.md)
- [Application Filter](../sdk/config/objects/application_filters.md)

### Security Services

- [Security Rules](../sdk/config/security_services/security_rule.md)
- [Anti-Spyware Profile](../sdk/config/security_services/anti_spyware_profile.md)
- [DNS Security Profile](../sdk/config/security_services/dns_security_profile.md)
- [Vulnerability Protection Profile](../sdk/config/security_services/vulnerability_protection_profile.md)
- [WildFire Antivirus Profile](../sdk/config/security_services/wildfire_antivirus.md)

### Network Configuration

- [Security Zone](../sdk/config/network/security_zone.md)
- [NAT Rules](../sdk/config/network/nat_rules.md)
- [IKE Gateway](../sdk/config/network/ike_gateway.md)
- [IKE Crypto Profile](../sdk/config/network/ike_crypto_profile.md)
- [IPsec Crypto Profile](../sdk/config/network/ipsec_crypto_profile.md)

### Prisma Access Deployment

- [Bandwidth Allocations](../sdk/config/deployment/bandwidth_allocations.md)
- [BGP Routing](../sdk/config/deployment/bgp_routing.md)
- [Internal DNS Servers](../sdk/config/deployment/internal_dns_servers.md)
- [Network Locations](../sdk/config/deployment/network_locations.md)
- [Remote Networks](../sdk/config/deployment/remote_networks.md)
- [Service Connections](../sdk/config/deployment/service_connections.md)

### Mobile Agent

- [Authentication Settings](../sdk/config/mobile_agent/auth_settings.md)
- [Agent Versions](../sdk/config/mobile_agent/agent_versions.md)

## Common Operations

All configuration objects support the following common operations:

### List

Retrieves a list of objects:

```python
# List all objects
all_items = client.address.list()

# List with filtering
filtered_items = client.address.list(filter="name eq 'example'")

# List with limit
limited_items = client.address.list(limit=10)
```

### Fetch

Retrieves a specific object by ID:

```python
# Fetch by ID
object = client.address.fetch(id="12345")
```

### Create

Creates a new object:

```python
# Create a new object
new_object = client.address.create({
    "name": "example",
    "folder": "Shared",
    # Other required fields
})
```

### Update

Updates an existing object:

```python
# Update an object
client.address.update(id="12345", data={
    "description": "Updated description"
})
```

### Delete

Deletes an object:

```python
# Delete an object
client.address.delete(id="12345")
```

## Next Steps

- Learn about [Data Models](data-models.md) to understand how to structure request and response data
- Explore [Operations](operations.md) to learn about candidate configurations and job monitoring
- Check out [Advanced Topics](advanced-topics.md) for pagination, filtering, and error handling