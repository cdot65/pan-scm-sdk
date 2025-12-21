# Service Group Models

## Overview {#Overview}

The Service Group models provide a structured way to manage service group objects in Palo Alto Networks' Strata Cloud Manager. These models support creating and managing collections of services with a static list of service references. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `ServiceGroupBaseModel`: Base model with fields common to all service group operations
- `ServiceGroupCreateModel`: Model for creating new service groups
- `ServiceGroupUpdateModel`: Model for updating existing service groups
- `ServiceGroupResponseModel`: Response model for service group operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute | Type      | Required | Default | Description                                                                   |
|-----------|-----------|----------|---------|-------------------------------------------------------------------------------|
| name      | str       | Yes      | None    | Name of the service group. Max length: 63 chars. Pattern: `^[a-zA-Z0-9_ \.-]+$` |
| members   | List[str] | Yes      | None    | List of service members (1-1024 items). Must be unique.                       |
| tag       | List[str] | No       | None    | List of tags. Must be unique.                                                 |
| folder    | str       | No*      | None    | Folder where service group is defined. Max length: 64 chars                   |
| snippet   | str       | No*      | None    | Snippet where service group is defined. Max length: 64 chars                  |
| device    | str       | No*      | None    | Device where service group is defined. Max length: 64 chars                   |
| id        | UUID      | Yes**    | None    | UUID of the service group (response only)                                     |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response model

## Exceptions

The Service Group models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When tag or member values are not unique in a list
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.objects import ServiceGroupCreateModel

# This will raise a validation error
try:
    service_group = ServiceGroupCreateModel(
        name="invalid-group",
        members=["service1", "service2"],
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Tag and Member Validation

Tags and members must be unique and can be provided as a single string (auto-converted to list):

```python
from scm.models.objects import ServiceGroupCreateModel

# This will raise a validation error for duplicate tags
try:
    service_group = ServiceGroupCreateModel(
        name="invalid-group",
        members=["service1", "service2"],
        folder="Texas",
        tag=["web", "web"]  # Duplicate tags not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"

# This will convert a single string tag to a list
service_group = ServiceGroupCreateModel(
    name="valid-group",
    members=["service1", "service2"],
    folder="Texas",
    tag="web"  # Will be converted to ["web"]
)
```

## Usage Examples

### Creating a Service Group

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
service_group_data = {
    "name": "web-services",
    "members": ["HTTP", "HTTPS", "HTTP-ALT"],
    "folder": "Texas",
    "tag": ["web", "production"]
}

response = client.service_group.create(service_group_data)
print(f"Created service group: {response.name} (ID: {response.id})")
```

### Creating a Service Group in a Snippet

```python
# Create a service group in a snippet
service_group_data = {
    "name": "database-services",
    "members": ["MySQL", "PostgreSQL", "MongoDB"],
    "snippet": "Database Configs",
    "tag": ["database"]
}

response = client.service_group.create(service_group_data)
print(f"Created service group: {response.name}")
```

### Updating a Service Group

```python
# Fetch existing service group
existing = client.service_group.fetch(name="web-services", folder="Texas")

# Modify attributes using dot notation
existing.members = ["HTTP", "HTTPS", "HTTP-ALT", "HTTP2"]
existing.tag = ["web", "production", "updated"]

# Pass modified object to update()
updated = client.service_group.update(existing)
print(f"Updated service group: {updated.name}")
print(f"Members: {', '.join(updated.members)}")
```

### Working with Response Models

```python
# List and process service groups
groups = client.service_group.list(folder="Texas")

for group in groups:
    print(f"Group: {group.name} (ID: {group.id})")
    print(f"  Members: {', '.join(group.members)}")
    if group.tag:
        print(f"  Tags: {', '.join(group.tag)}")
```

## Best Practices

### Member Management
- Use descriptive member names that reference existing service objects
- Members must be references to existing service or service group objects in SCM
- Avoid using predefined service names like 'HTTP' or 'HTTPS' directly
- Keep member lists organized and documented

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for service groups
- Organize service groups logically by function or application

### Validation
- Handle validation errors appropriately in your application
- Ensure all members and tags are unique within their lists
- Validate that referenced services exist before creating groups
