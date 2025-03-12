# HIP Object Models

## Overview

The HIP Object models provide a structured way to manage Host Information Profile (HIP) objects in Palo Alto Networks'
Strata Cloud Manager. These models support comprehensive host profiling including host information, network details,
security products, mobile device management, and certificate validation.

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

<div class="termy">

<!-- termynal -->
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

</div>

## Usage Examples

### Creating a Windows Host Profile

<div class="termy">

<!-- termynal -->
```python
from scm.config.objects import HIPObject

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

hip_object = HIPObject(api_client)
response = hip_object.create(windows_profile)
```

</div>

### Creating a Mobile Device Profile

<div class="termy">

<!-- termynal -->
```python
# Using model directly
from scm.models.objects import (
    HIPObjectCreateModel,
    MobileDeviceModel,
    MobileDeviceCriteriaModel,
    MobileApplicationsModel
)

mobile_profile = HIPObjectCreateModel(
    name="mobile-device",
    description="Mobile device profile",
    folder="Mobile",
    mobile_device=MobileDeviceModel(
        criteria=MobileDeviceCriteriaModel(
            jailbroken=False,
            disk_encrypted=True,
            passcode_set=True,
            applications=MobileApplicationsModel(
                has_malware=False,
                has_unmanaged_app=False
            )
        )
    )
)

payload = mobile_profile.model_dump(exclude_unset=True)
response = hip_object.create(payload)
```

</div>

### Updating a HIP Object

<div class="termy">

<!-- termynal -->
```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "windows-workstation-updated",
    "description": "Updated Windows workstation profile",
    "host_info": {
        "criteria": {
            "os": {"contains": {"Microsoft": "All"}},
            "domain": {"contains": "company.local"},
            "managed": True
        }
    }
}

response = hip_object.update(update_dict)
```

</div>

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

- [HostInfoModel](../../models/objects/hip_object_models.md#Overview)
- [NetworkInfoModel](../../models/objects/hip_object_models.md#Overview)
- [PatchManagementModel](../../models/objects/hip_object_models.md#Overview)
- [DiskEncryptionModel](../../models/objects/hip_object_models.md#Overview)
- [MobileDeviceModel](../../models/objects/hip_object_models.md#Overview)
- [CertificateModel](../../models/objects/hip_object_models.md#Overview)
