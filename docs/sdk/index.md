# Services

Service classes provide CRUD operations for managing Strata Cloud Manager configurations. Each service maps to a resource type and is accessed through the unified client.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Every resource follows the same pattern
client.address.create({"name": "web-server", "ip_netmask": "10.0.1.100/32", "folder": "Texas"})
client.address.list(folder="Texas")
client.address.fetch(name="web-server", folder="Texas")
client.address.update(address_object)
client.address.delete(address_id)
```

!!! note "Looking for field schemas and validation rules?"
    See the **[Data Models](models/index.md)** section to understand what fields are required, allowed values,
    and validation constraints for each resource type.

---

## Service Categories

- **[Deployment](config/deployment/index.md)** - Prisma Access infrastructure (bandwidth, BGP, DNS, remote networks)
- **[Identity](config/identity/index.md)** - Authentication and server profiles (LDAP, RADIUS, SAML, TACACS+, Kerberos)
- **[Mobile Agent](config/mobile_agent/index.md)** - GlobalProtect agent configuration
- **[Network](config/network/index.md)** - Interfaces, VPN profiles, NAT rules, routing, security zones
- **[Objects](config/objects/index.md)** - Reusable policy objects (addresses, services, tags, HIP)
- **[Security Services](config/security_services/index.md)** - Security profiles and rules
- **[Setup](config/setup/index.md)** - Organizational containers (folders, snippets, devices)
- **[Insights](insights/index.md)** - Prisma Access Insights alerts

## Related Documentation

- **[Auth](auth.md)** - OAuth2 authentication flow
- **[Client](client.md)** - Unified client interface and service registration
- **[BaseObject](config/base_object.md)** - Base class for all service classes
- **[Data Models](models/index.md)** - Pydantic schemas for validating configuration data
- **[Exceptions](exceptions.md)** - Error handling and exception types
