# Security Zones

This document provides examples and guidance for using the Security Zones functionality in the Palo Alto Networks Strata Cloud Manager (SCM) SDK.

## Overview

Security Zones are a fundamental component of network security in PAN-OS, allowing you to segment your network into security zones and apply different security policies to traffic moving between zones.

The Security Zone module in the SCM SDK provides a comprehensive set of operations to manage security zones:

- Create new security zones
- Retrieve security zones by ID or name
- Update existing security zones
- List and filter security zones
- Delete security zones

## Prerequisites

Before using the Security Zone module, ensure you have:

1. A valid SCM API client ID and secret
2. Appropriate permissions to manage security zones in SCM
3. The SCM SDK installed (`pip install pan-scm-sdk`)

## Basic Usage

### Authentication

```python
from scm.auth import OAuth2
from scm.client import Client
from scm.config.network import SecurityZone

# Set up authentication
auth = OAuth2(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://api.strata.paloaltonetworks.com/api/oauth2/token",
)

# Initialize client
client = Client(
    api_url="https://api.strata.paloaltonetworks.com",
    auth=auth,
)

# Create security zone instance
security_zone = SecurityZone(client)
```

### Creating a Security Zone

```python
# Define a new security zone
zone_data = {
    "name": "trusted-zone",
    "folder": "My Folder",  # You must specify one of folder, snippet, or device
    "enable_user_identification": True,
    "enable_device_identification": False,
    "network": {
        "layer3": ["ethernet1/1", "ethernet1/2"],
        "zone_protection_profile": "default",
        "enable_packet_buffer_protection": True
    },
    "user_acl": {
        "include_list": ["user1", "user2"],
        "exclude_list": []
    }
}

# Create the security zone
created_zone = security_zone.create(zone_data)
print(f"Created security zone: {created_zone.name} (ID: {created_zone.id})")
```

### Retrieving a Security Zone

```python
# Get by ID
zone_by_id = security_zone.get("123e4567-e89b-12d3-a456-426655440000")

# Get by name (requires specifying a container: folder, snippet, or device)
zone_by_name = security_zone.fetch(name="trusted-zone", folder="My Folder")
```

### Updating a Security Zone

```python
# Update an existing security zone
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",  # Required for updates
    "name": "trusted-zone",
    "folder": "My Folder",
    "enable_user_identification": True,
    "enable_device_identification": True,  # Changed to True
    "network": {
        "layer3": ["ethernet1/1", "ethernet1/2", "ethernet1/3"],  # Added another interface
        "zone_protection_profile": "enhanced",  # Changed profile
        "enable_packet_buffer_protection": True
    }
}

# Update method requires a SecurityZoneUpdateModel instance
from scm.models.network import SecurityZoneUpdateModel
update_model = SecurityZoneUpdateModel(**update_data)
updated_zone = security_zone.update(update_model)
```

### Listing Security Zones

```python
# List all zones in a folder
zones = security_zone.list(folder="My Folder")

# List with filtering
filtered_zones = security_zone.list(
    folder="My Folder",
    enable_user_identification=True,
    network_type=["layer3"]
)

# Advanced filtering
zones_with_exclusions = security_zone.list(
    folder="My Folder",
    exclude_folders=["Template Folder"],
    exact_match=True
)
```

### Deleting a Security Zone

```python
# Delete a security zone by ID
security_zone.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Security Zone Network Types

Security zones can be associated with different types of network interfaces. The SDK supports the following network interface types, and you must specify exactly one type in the network configuration:

- `tap`: For tap interfaces
- `virtual_wire`: For virtual wire interfaces
- `layer2`: For Layer 2 interfaces
- `layer3`: For Layer 3 interfaces
- `tunnel`: For tunnel interfaces
- `external`: For external interfaces

Example with different network types:

```python
# Layer 3 zone
layer3_zone = {
    "name": "L3-Zone",
    "folder": "My Folder",
    "network": {
        "layer3": ["ethernet1/1", "ethernet1/2"]
    }
}

# Layer 2 zone
layer2_zone = {
    "name": "L2-Zone",
    "folder": "My Folder",
    "network": {
        "layer2": ["ethernet1/3", "ethernet1/4"]
    }
}
```

## Additional Configuration Options

### Zone Protection and DoS Protection

```python
zone_with_protection = {
    "name": "protected-zone",
    "folder": "My Folder",
    "dos_profile": "custom-dos-profile",
    "dos_log_setting": "dos-logging",
    "network": {
        "layer3": ["ethernet1/1"],
        "zone_protection_profile": "custom-zone-protection",
        "log_setting": "network-logging"
    }
}
```

### User and Device ACLs

Control which users and devices can access resources in a zone:

```python
zone_with_acls = {
    "name": "acl-zone",
    "folder": "My Folder",
    "enable_user_identification": True,
    "enable_device_identification": True,
    "user_acl": {
        "include_list": ["finance-users", "it-admin"],
        "exclude_list": ["contractors"]
    },
    "device_acl": {
        "include_list": ["corporate-laptops"],
        "exclude_list": ["byod-devices", "iot-devices"]
    },
    "network": {
        "layer3": ["ethernet1/1"]
    }
}
```

## Best Practices

1. Always specify exactly one container (folder, snippet, or device) for all operations
2. Use unique, descriptive names for your security zones
3. When updating zones, fetch the current configuration first to avoid unintentional changes
4. Consider organizing related zones in the same folder
5. Use zone protection profiles for critical zones that face untrusted networks

## Error Handling

The SDK provides detailed error messages to help troubleshoot issues:

```python
try:
    security_zone.create(zone_data)
except Exception as e:
    print(f"Error creating security zone: {str(e)}")
```

## Additional Resources

- See the full example script at `examples/scm/config/network/security_zone.py`
- For API details, refer to the SCM API documentation
- Review the SDK documentation for complete details on all available methods and parameters