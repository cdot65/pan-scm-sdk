# Dynamic User Group Models

## Overview {#Overview}

The Dynamic User Group models provide a structured way to manage dynamic user groups in Palo Alto Networks' Strata Cloud Manager. These models support defining user groups based on tag-based filters to dynamically associate users with specific groups for policy management. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

| Model                           | Purpose                                          |
|---------------------------------|--------------------------------------------------|
| `DynamicUserGroupBaseModel`     | Base model with common fields for all operations |
| `DynamicUserGroupCreateModel`   | Model for creating new dynamic user groups       |
| `DynamicUserGroupUpdateModel`   | Model for updating existing dynamic user groups  |
| `DynamicUserGroupResponseModel` | Model for API responses                          |

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute   | Type      | Required | Default | Description                                                                 |
|-------------|-----------|----------|---------|-----------------------------------------------------------------------------|
| name        | str       | Yes      | None    | Name of the dynamic user group. Max length: 63 chars. Must match pattern: ^[a-zA-Z\d\-_. ]+$ |
| filter      | str       | Yes      | None    | Tag-based filter for the dynamic user group. Max length: 2047 chars         |
| description | str       | No       | None    | Description of the dynamic user group. Max length: 1023 chars               |
| tag         | List[str] | No       | None    | List of tags. Each tag max length: 127 chars                                |
| folder      | str       | No*      | None    | Folder where dynamic user group is defined. Max length: 64 chars            |
| snippet     | str       | No*      | None    | Snippet where dynamic user group is defined. Max length: 64 chars           |
| device      | str       | No*      | None    | Device where dynamic user group is defined. Max length: 64 chars            |
| id          | UUID      | Yes**    | None    | UUID of the dynamic user group (response only)                              |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response model

## Exceptions

The Dynamic User Group models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When tag values are not unique in a list
    - When tag input is neither a string nor a list
    - When name pattern validation fails

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# This will raise a validation error
from scm.models.objects import DynamicUserGroupCreateModel

try:
    dug = DynamicUserGroupCreateModel(
        name="high-risk-users",
        filter="tag.criticality.high",
        folder="Security",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# This will also raise a validation error
try:
    dug = DynamicUserGroupCreateModel(
        name="high-risk-users",
        filter="tag.criticality.high"
        # Missing container
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Tag Validation

Tags must be unique and properly formatted:

```python
# This will raise a validation error for duplicate tags
try:
    dug = DynamicUserGroupCreateModel(
        name="high-risk-users",
        filter="tag.criticality.high",
        folder="Security",
        tag=["security", "security"]  # Duplicate tags not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"

# This will convert a single string tag to a list
dug = DynamicUserGroupCreateModel(
    name="high-risk-users",
    filter="tag.criticality.high",
    folder="Security",
    tag="security"  # Will be converted to ["security"]
)
print(dug.tag)  # ["security"]
```

## Usage Examples

### Creating a Dynamic User Group

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
dug_dict = {
    "name": "high-risk-users",
    "filter": "tag.criticality.high",
    "description": "Users with high risk classification",
    "folder": "Security",
    "tag": ["RiskManagement", "Security"]
}

response = client.dynamic_user_group.create(dug_dict)
```

### Creating a Dynamic User Group with a Complex Filter

```python
# Using dictionary
complex_dug_dict = {
    "name": "risky-contractors",
    "filter": "tag.user_type.contractor and (tag.criticality.high or tag.risk_score.gt.80)",
    "description": "High risk contractors",
    "folder": "Security",
    "tag": ["RiskManagement", "Contractors"]
}

response = client.dynamic_user_group.create(complex_dug_dict)
```

### Updating a Dynamic User Group

```python
# Fetch existing dynamic user group
existing = client.dynamic_user_group.fetch(name="high-risk-users", folder="Security")

# Modify attributes using dot notation
existing.description = "Updated user group for high risk classification"
existing.filter = "tag.criticality.high or tag.risk_score.gt.90"
existing.tag = ["RiskManagement", "Security", "HighPriority"]

# Pass modified object to update()
updated = client.dynamic_user_group.update(existing)
```

### Response Model

When retrieving dynamic user groups, the response will be validated against the `DynamicUserGroupResponseModel` schema:

```python
# Example of a response
response_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "high-risk-users",
    "filter": "tag.criticality.high or tag.risk_score.gt.90",
    "description": "Users with high risk classification",
    "folder": "Security",
    "tag": ["RiskManagement", "Security", "HighPriority"]
}

# Validating response data
from scm.models.objects import DynamicUserGroupResponseModel

response_model = DynamicUserGroupResponseModel(**response_data)
print(f"DUG ID: {response_model.id}")
print(f"Name: {response_model.name}")
print(f"Filter: {response_model.filter}")
print(f"Tags: {response_model.tag}")
```
