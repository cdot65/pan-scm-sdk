# HIP Profile Models

## Overview {#Overview}

The HIP Profile models provide a structured way to manage Host Information Profile (HIP) profiles in Palo Alto Networks'
Strata Cloud Manager. These models define the match criteria expressions used to associate HIP objects with policy rules,
enabling dynamic security policy enforcement based on host posture assessments.

## Attributes

| Attribute        | Type                 | Required | Default | Description                                                            |
|------------------|----------------------|----------|---------|------------------------------------------------------------------------|
| name             | str                  | Yes      | None    | Name of HIP profile. Max length: 31 chars. Pattern: ^[a-zA-Z\d\-_. ]+$ |
| match            | str                  | Yes      | None    | Match expression for the profile. Max length: 2048 chars               |
| description      | str                  | No       | None    | Description of the HIP profile. Max length: 255 chars                  |
| folder           | str                  | No*      | None    | Folder where profile is defined. Max length: 64 chars                  |
| snippet          | str                  | No*      | None    | Snippet where profile is defined. Max length: 64 chars                 |
| device           | str                  | No*      | None    | Device where profile is defined. Max length: 64 chars                  |
| id               | UUID                 | Yes**    | None    | UUID of the HIP profile (required for update/response)                 |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for update and response models

## Exceptions

The HIP Profile models can raise the following exceptions during validation:

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
from scm.models.objects import HIPProfileCreateModel

# This will raise a validation error
try:
    profile = HIPProfileCreateModel(
        name="windows-profile",
        match='"is-win"',
        folder="Shared",
        device="fw01",  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

## Usage Examples

### Creating a Basic HIP Profile

```python
from scm.config.objects import HIPProfile

# Using dictionary
basic_profile = {
    "name": "windows-workstation",
    "description": "Windows workstation profile",
    "folder": "Shared",
    "match": '"is-win"'  # Single HIP object reference
}

hip_profile = HIPProfile(api_client)
response = hip_profile.create(basic_profile)
```

### Creating a Complex HIP Profile with Boolean Operators

```python
# Using model directly
from scm.models.objects import HIPProfileCreateModel

complex_profile = HIPProfileCreateModel(
    name="secure-workstation",
    description="Secure Windows workstation profile",
    folder="Shared",
    match='"is-win" and "is-firewall-enabled" and "is-antivirus-running"'
)

payload = complex_profile.model_dump(exclude_unset=True)
response = hip_profile.create(payload)
```

### Creating a HIP Profile with Negative Match

```python
# Negative match (NOT operator)
negative_profile = {
    "name": "non-windows-hosts",
    "description": "All non-Windows hosts",
    "folder": "Shared",
    "match": 'not ("is-win")'  # NOT operator with parentheses
}

response = hip_profile.create(negative_profile)
```

### Updating a HIP Profile

```python
from scm.models.objects import HIPProfileUpdateModel
from uuid import UUID

# Using model directly
update_model = HIPProfileUpdateModel(
    id=UUID("123e4567-e89b-12d3-a456-426655440000"),
    name="secure-workstation",
    description="Updated secure Windows workstation profile",
    match='"is-win" and "is-firewall-enabled" and "is-antivirus-running" and "is-disk-encrypted"'
)

response = hip_profile.update(update_model)
```

## Match Expression Syntax

The `match` field supports a powerful expression language for defining HIP profile match criteria:

```python
# Basic object reference - use double quotes around object names
match = '"is-win"'

# Boolean AND operation
match = '"is-win" and "is-firewall-enabled"'

# Boolean OR operation
match = '"is-win" or "is-mac"'

# Boolean NOT operation
match = 'not ("is-win")'

# Combining operators with parentheses
match = '("is-win" or "is-mac") and "is-firewall-enabled"'

# Complex nested expressions
match = '("is-win" and "is-firewall-enabled") or ("is-mac" and "is-mac-firewall-enabled")'
```

## Best Practices

1. **Match Expression Design**
    - Use quoted object names (e.g., `"is-win"`)
    - Maintain clear boolean logic with parentheses
    - Verify HIP objects exist before referencing them
    - Keep expressions simple and maintainable
    - Test expressions against expected hosts

2. **Container Management**
    - Always specify exactly one container type
    - Use consistent container names
    - Validate container existence
    - Group related profiles

3. **Performance**
    - Keep match expressions concise
    - Avoid overly complex expressions
    - Test profile evaluation performance
    - Consider impact on policy processing

4. **Security**
    - Document profile purposes
    - Review profiles regularly
    - Use clear naming conventions
    - Consider least privilege principles
    - Validate match expressions

## Related Models

- HIP Objects - See [HIP Object Models](../../models/objects/hip_object_models.md)
