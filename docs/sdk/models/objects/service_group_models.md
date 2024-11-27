# Service Group Models

## Overview

The Service Group models provide a structured way to manage service groups in Palo Alto Networks' Strata Cloud Manager.
These models support grouping network services together and defining them within folders, snippets, or devices. The
models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute | Type      | Required | Default | Description                                                                              |
|-----------|-----------|----------|---------|------------------------------------------------------------------------------------------|
| name      | str       | Yes      | None    | Name of the service group. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
| members   | List[str] | Yes      | None    | List of service names. Min length: 1, Max length: 1024                                   |
| tag       | List[str] | No       | None    | List of tags. Each tag max length: 64 chars                                              |
| folder    | str       | No*      | None    | Folder where group is defined. Max length: 64 chars                                      |
| snippet   | str       | No*      | None    | Snippet where group is defined. Max length: 64 chars                                     |
| device    | str       | No*      | None    | Device where group is defined. Max length: 64 chars                                      |
| id        | UUID      | Yes**    | None    | UUID of the service group (response only)                                                |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

## Exceptions

The Service Group models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When members list is empty or exceeds maximum length
    - When tag values are not unique in a list
    - When tag input is neither a string nor a list
    - When name or container fields don't match required patterns

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->
```python
# Using dictionary
from scm.config.objects import ServiceGroup

# Error: multiple containers specified
try:
    service_group_dict = {
        "name": "invalid-group",
        "members": ["service1", "service2"],
        "folder": "Shared",
        "device": "fw01"  # Can't specify both folder and device
    }
    service_group = ServiceGroup(api_client)
    response = service_group.create(service_group_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
from scm.models.objects import ServiceGroupCreateModel

# Error: no container specified
try:
    service_group = ServiceGroupCreateModel(
        name="invalid-group",
        members=["service1", "service2"]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

### Tag Validation

Tags must be unique and properly formatted:

<div class="termy">

<!-- termynal -->
```python
# This will raise a validation error for duplicate tags
try:
    service_group = ServiceGroupCreateModel(
        name="invalid-group",
        members=["service1"],
        folder="Shared",
        tag=["web", "web"]  # Duplicate tags not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"

# This will convert a single string tag to a list
service_group = ServiceGroupCreateModel(
    name="valid-group",
    members=["service1"],
    folder="Shared",
    tag="web"  # Will be converted to ["web"]
)
```

</div>

## Usage Examples

### Creating a Service Group

<div class="termy">

<!-- termynal -->
```python
# Using dictionary
from scm.config.objects import ServiceGroup

service_group_dict = {
    "name": "web-services",
    "members": ["http", "https", "web-browsing"],
    "folder": "Shared",
    "tag": ["web", "production"]
}

service_group = ServiceGroup(api_client)
response = service_group.create(service_group_dict)

# Using model directly
from scm.models.objects import ServiceGroupCreateModel

service_group = ServiceGroupCreateModel(
    name="web-services",
    members=["http", "https", "web-browsing"],
    folder="Shared",
    tag=["web", "production"]
)

payload = service_group.model_dump(exclude_unset=True)
response = service_group.create(payload)
```

</div>

### Creating a Service Group in a Snippet

<div class="termy">

<!-- termynal -->
```python
# Using dictionary
snippet_group_dict = {
    "name": "database-services",
    "members": ["mysql", "postgresql", "mongodb"],
    "snippet": "Database Config",
    "tag": ["database", "internal"]
}

response = service_group.create(snippet_group_dict)

# Using model directly
snippet_group = ServiceGroupCreateModel(
    name="database-services",
    members=["mysql", "postgresql", "mongodb"],
    snippet="Database Config",
    tag=["database", "internal"]
)

payload = snippet_group.model_dump(exclude_unset=True)
response = service_group.create(payload)
```

</div>

### Updating a Service Group

<div class="termy">

<!-- termynal -->
```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "web-services-updated",
    "members": ["http", "https", "web-browsing", "ssl"],
    "tag": ["web", "production", "updated"]
}

response = service_group.update(update_dict)

# Using model directly
from scm.models.objects import ServiceGroupUpdateModel

update_group = ServiceGroupUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="web-services-updated",
    members=["http", "https", "web-browsing", "ssl"],
    tag=["web", "production", "updated"]
)

payload = update_group.model_dump(exclude_unset=True)
response = service_group.update(payload)
```

</div>