# HIP Object Models

## Overview {#Overview}

The HIP Object models provide a structured way to manage Host Information Profile (HIP) objects in Palo Alto Networks'
Strata Cloud Manager. These models support comprehensive host profiling including host information, network details,
security products, mobile device management, certificate validation, and custom checks.

### Models

| Model                    | Purpose                                          |
|--------------------------|--------------------------------------------------|
| `HIPObjectBaseModel`     | Base model with common fields for all operations |
| `HIPObjectCreateModel`   | Model for creating new HIP objects               |
| `HIPObjectUpdateModel`   | Model for updating existing HIP objects          |
| `HIPObjectResponseModel` | Model for API responses                          |

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute        | Type                 | Required | Default | Description                                                            |
|------------------|----------------------|----------|---------|------------------------------------------------------------------------|
| name             | str                  | Yes      | None    | Name of HIP object. Max length: 31 chars. Pattern: ^[ a-zA-Z0-9.\-_]+$ |
| description      | str                  | No       | None    | Description of the HIP object. Max length: 255 chars                   |
| host_info        | HostInfoModel        | No       | None    | Host information criteria                                              |
| network_info     | NetworkInfoModel     | No       | None    | Network information criteria                                           |
| patch_management | PatchManagementModel | No       | None    | Patch management criteria                                              |
| disk_encryption  | DiskEncryptionModel  | No       | None    | Disk encryption criteria                                               |
| mobile_device    | MobileDeviceModel    | No       | None    | Mobile device criteria                                                 |
| certificate      | CertificateModel     | No       | None    | Certificate criteria                                                   |
| custom_checks    | CustomChecksModel    | No       | None    | Custom checks criteria (registry keys, process list, plist)            |
| folder           | str                  | No*      | None    | Folder where object is defined. Max length: 64 chars                   |
| snippet          | str                  | No*      | None    | Snippet where object is defined. Max length: 64 chars                  |
| device           | str                  | No*      | None    | Device where object is defined. Max length: 64 chars                   |
| id               | UUID                 | Yes**    | None    | UUID of the HIP object (response only)                                 |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response model

## Exceptions

The HIP Object models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When name pattern validation fails
    - When field length limits are exceeded
    - When invalid patterns are provided for fields

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.objects import HIPObjectCreateModel

# This will raise a validation error
try:
    hip = HIPObjectCreateModel(
        name="windows-policy",
        folder="Shared",
        device="fw01",  # Can't specify both folder and device
        host_info={
            "criteria": {
                "os": {"contains": {"Microsoft": "All"}}
            }
        }
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

## Usage Examples

### Creating a Windows Host Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
windows_profile = {
    "name": "windows-workstation",
    "description": "Windows workstation profile",
    "folder": "Shared",
    "host_info": {
        "criteria": {
            "os": {"contains": {"Microsoft": "All"}},
            "domain": {"contains": "company.local"}
        }
    },
    "patch_management": {
        "criteria": {
            "is_installed": True,
            "is_enabled": "yes",
            "missing_patches": {
                "severity": 3,
                "check": "has-none"
            }
        }
    }
}

response = client.hip_object.create(windows_profile)
```

### Creating a Mobile Device Profile

```python
# Using dictionary
mobile_profile = {
    "name": "mobile-device",
    "description": "Mobile device profile",
    "folder": "Mobile",
    "mobile_device": {
        "criteria": {
            "jailbroken": False,
            "disk_encrypted": True,
            "passcode_set": True,
            "applications": {
                "has_malware": False,
                "has_unmanaged_app": False
            }
        }
    }
}

response = client.hip_object.create(mobile_profile)
```

### Creating a Custom Checks Profile

```python
# Using dictionary with custom checks for Windows registry and process list
custom_checks_profile = {
    "name": "custom-security-checks",
    "description": "Custom security checks for Windows endpoints",
    "folder": "Shared",
    "custom_checks": {
        "criteria": {
            "process_list": [
                {"name": "antivirus.exe", "running": True},
                {"name": "malware.exe", "running": False}
            ],
            "registry_key": [
                {
                    "name": "HKEY_LOCAL_MACHINE\\SOFTWARE\\SecurityApp",
                    "registry_value": [
                        {"name": "Enabled", "value_data": "1"}
                    ]
                }
            ]
        }
    }
}

response = client.hip_object.create(custom_checks_profile)
```

### Updating a HIP Object

```python
# Fetch existing HIP object
existing = client.hip_object.fetch(name="windows-workstation", folder="Shared")

# Modify attributes using dot notation
existing.description = "Updated Windows workstation profile"
if existing.host_info and existing.host_info.criteria:
    existing.host_info.criteria.managed = True

# Pass modified object to update()
updated = client.hip_object.update(existing)
```

## Best Practices

1. **Profile Management**
    - Use descriptive names for profiles
    - Document profile purposes
    - Group related criteria
    - Keep profiles focused
    - Review and update regularly

2. **Container Management**
    - Always specify exactly one container type
    - Use consistent container names
    - Validate container existence
    - Group related configurations

3. **Security**
    - Set appropriate patch requirements
    - Enable disk encryption checks
    - Validate mobile device security
    - Check certificate validity
    - Monitor compliance status

4. **Performance**
    - Use efficient criteria combinations
    - Avoid overly complex rules
    - Monitor evaluation times
    - Test profile impacts
    - Optimize rule ordering

## Related Models

- HostInfoModel
- NetworkInfoModel
- PatchManagementModel
- DiskEncryptionModel
- MobileDeviceModel
- CertificateModel
- CustomChecksModel (includes ProcessListItemModel, RegistryKeyModel, RegistryValueModel, PlistModel, PlistKeyModel)

These related models are defined within the same file and described in the Attributes section above.
