# Objects Configuration Objects

## Table of Contents

1. [Overview](#overview)
2. [Address Objects](#address-objects)
3. [Service Objects](#service-objects)
4. [Application Objects](#application-objects)
5. [Group Objects](#group-objects)
6. [Profile Objects](#profile-objects)
7. [Miscellaneous Objects](#miscellaneous-objects)

## Overview

This section covers the configuration objects provided by the Palo Alto Networks Strata Cloud Manager SDK. Each configuration object corresponds to a resource in the Strata Cloud Manager and provides methods for CRUD (Create, Read, Update, Delete) operations.

## Address Objects

- [Address](address.md) - IP addresses, ranges, and FQDNs for use in security policies
- [Address Group](address_group.md) - Collections of addresses for simplified policy management

## Service Objects

- [Service](service.md) - Port and protocol definitions for network service access
- [Service Group](service_group.md) - Collections of services for simplified policy management

## Application Objects

- [Application](application.md) - Custom application definitions for fine-grained control
- [Application Filters](application_filters.md) - Filters to identify applications based on characteristics
- [Application Group](application_group.md) - Collections of applications for simplified policy management

## Group Objects

- [Dynamic User Group](dynamic_user_group.md) - User groups based on dynamic membership criteria
- [External Dynamic Lists](external_dynamic_lists.md) - Lists of IPs, URLs, or domains from external sources

## Profile Objects

- [HIP Object](hip_object.md) - Host Information Profile objects for endpoint matching
- [HIP Profile](hip_profile.md) - Host Information Profile definitions for security policy enforcement
- [HTTP Server Profiles](http_server_profiles.md) - HTTP server configurations for log forwarding
- [Log Forwarding Profile](log_forwarding_profile.md) - Profiles for forwarding logs to external systems

## Miscellaneous Objects

- [Tag](tag.md) - Tags for resource organization and policy application

## Common Features

All configuration objects provide standard operations:

- Create new objects
- Read existing objects
- Update object properties
- Delete objects
- List and filter objects with pagination support

The objects also enforce:

- Container validation (folder/device/snippet)
- Data validation with detailed error messages
- Consistent API patterns across all object types

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

# Access any object type directly through the client
# Create an address object
client.address.create({
   "name": "webserver",
   "ip_netmask": "10.0.1.100",
   "description": "Primary web server",
   "folder": "Shared"
})

# List address objects with filtering
results = client.address.list(
   folder="Shared",
   exact_match=True
)

# Print the results
for address in results:
   print(f"Address: {address.name}, Value: {address.ip_netmask}")
```

</div>

Select an object from the sections above to view detailed documentation, including methods, parameters, and examples.