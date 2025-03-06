# Comprehensive Security Zones SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage security zones across a wide range of real-world enterprise scenarios.

## Overview

The `security_zone.py` script showcases enterprise-ready security zone configurations addressing common network segmentation needs, including:

1. **Security Zone Types**:
   - Layer 3 security zones - for traditional routed interfaces
   - Layer 2 security zones - for switching environments
   - Virtual Wire zones - for transparent deployments
   - TAP zones - for passive monitoring
   - External zones - for external networks
   - Tunnel zones - for VPN and tunneled traffic

2. **Security Features**:
   - User identification - for User-ID integration
   - Device identification - for device-based policies
   - Zone protection profiles - for dedicated zone security
   - Packet buffer protection - for enhanced security

3. **Access Control Lists**:
   - User ACLs - for controlling user access
   - Device ACLs - for controlling device access

4. **Operational Functions**:
   - Creation of various zone types
   - Retrieval by ID and name
   - Updating existing zones
   - Listing and filtering zones
   - Deletion and cleanup

## Prerequisites

Before running the examples, you need:

1. A Strata Cloud Manager account with appropriate permissions
2. Your SCM API credentials (client ID, client secret, and TSG ID)
3. Python 3.10 or higher
4. The PAN-SCM-SDK package installed (`pip install pan-scm-sdk`)
5. A folder configuration in your SCM environment (or modify the script)

## Script Organization

The script is organized into modular sections that each demonstrate specific security zone operations:

### Setup and Authentication
- Initializing the SDK client
- Setting up logging and environment variables

### Core Operations
- Creating a security zone with Layer 3 interfaces
- Retrieving a security zone by ID
- Retrieving a security zone by name
- Updating an existing security zone
- Listing and filtering security zones
- Deleting a security zone

## Real-World Security Zone Examples

The example script demonstrates these common real-world security zone patterns:

### 1. Basic Layer 3 Security Zone

```python
zone_data = {
    "name": "example-zone",
    "folder": "Example Folder",
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
```

### 2. DMZ Security Zone

```python
dmz_zone = {
    "name": "dmz-zone",
    "folder": "Example Folder",
    "enable_user_identification": False,
    "enable_device_identification": False,
    "network": {
        "layer3": ["ethernet1/7", "ethernet1/8"],
        "zone_protection_profile": "strict",
    }
}
```

### 3. Guest Network Zone with Layer 2

```python
guest_zone = {
    "name": "guest-zone",
    "folder": "Example Folder",
    "enable_user_identification": True,
    "network": {
        "layer2": ["ethernet1/3", "ethernet1/4"],
        "log_setting": "guest-logging"
    }
}
```

### 4. Virtual Wire Zone for Transparent Deployment

```python
virtual_wire_zone = {
    "name": "vwire-zone",
    "folder": "Example Folder",
    "network": {
        "virtual_wire": ["ethernet1/5", "ethernet1/6"]
    }
}
```

## Running the Example

Follow these steps to run the example:

1. Set up authentication credentials in one of the following ways:

   **Option A: Using environment variables**
   ```bash
   export SCM_CLIENT_ID=your-oauth2-client-id
   export SCM_CLIENT_SECRET=your-oauth2-client-secret
   export SCM_TOKEN_URL=https://api.strata.paloaltonetworks.com/api/oauth2/token
   export SCM_API_URL=https://api.strata.paloaltonetworks.com
   ```

   **Option B: Modifying the script**
   - Edit the script and replace the environment variable references with your actual credentials

2. Run the script:
   ```bash
   python security_zone.py
   ```

3. Examine the output to understand:
   - The zone creation process
   - How to retrieve zones by ID and name
   - How to update existing zones
   - How to list and filter zones
   - How to delete zones

## Security Zone Model Structure

The examples demonstrate the proper structure for security zone configurations:

### Basic Security Zone Structure

```python
{
    "name": "zone-name",               # Required: Name of the security zone
    "folder": "folder-name",           # Required: One of folder, snippet, or device
    "enable_user_identification": bool, # Optional: Enable User-ID
    "enable_device_identification": bool, # Optional: Enable Device-ID
    "dos_profile": "profile-name",     # Optional: DoS protection profile
    "dos_log_setting": "log-setting",  # Optional: DoS log setting
    "network": {                       # Network configuration
        # Only one of the following can be specified:
        "layer3": ["ethernet1/1"],     # Layer 3 interfaces
        "layer2": ["ethernet1/2"],     # Layer 2 interfaces
        "virtual_wire": ["ethernet1/3"], # Virtual wire interfaces
        "tap": ["ethernet1/4"],        # TAP interfaces
        "tunnel": {},                  # Tunnel configuration
        "external": ["ethernet1/5"],   # External interfaces
        
        # Additional network options:
        "zone_protection_profile": "profile-name", # Optional
        "enable_packet_buffer_protection": bool,   # Optional
        "log_setting": "log-setting"               # Optional
    },
    "user_acl": {                      # Optional: User access control
        "include_list": ["user1"],     # Users to include
        "exclude_list": ["user2"]      # Users to exclude
    },
    "device_acl": {                    # Optional: Device access control
        "include_list": ["device1"],   # Devices to include
        "exclude_list": ["device2"]    # Devices to exclude
    }
}
```

## Best Practices for Security Zones

1. **Zone Design**
   - Create zones based on security requirements, not just network topology
   - Use descriptive names that indicate the security level or purpose
   - Document zone purpose in comments or documentation
   - Limit the number of zones to maintain manageable policies

2. **Interface Assignment**
   - Assign interfaces to zones based on their security requirements
   - Consider creating dedicated management zones
   - Separate high-security and low-security interfaces into different zones

3. **User and Device Identification**
   - Enable User-ID only for zones where user-based policies are needed
   - Enable Device-ID only for zones where device-based policies are needed
   - Configure appropriate ACLs to limit scope for performance reasons

4. **Zone Protection**
   - Apply zone protection profiles to untrusted zones
   - Configure packet buffer protection for critical zones
   - Use appropriate logging settings for security monitoring

5. **Zone Naming Conventions**
   - Use consistent naming conventions (e.g., "trust", "untrust", "dmz")
   - Consider including location or environment information in zone names
   - Use prefixes or suffixes to indicate zone type or purpose

## Additional Resources

- For complete SDK documentation, visit the [SCM SDK Documentation](https://cdot65.github.io/pan-scm-sdk/)
- For detailed API information, refer to the Strata Cloud Manager API documentation
- For additional examples, explore other scripts in the `examples` directory