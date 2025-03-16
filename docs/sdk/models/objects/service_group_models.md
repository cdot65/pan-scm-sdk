# Service Group Models

## Overview

The Service Group models provide a structured way to manage service group objects in Palo Alto Networks' Strata Cloud Manager.
These models support creating and managing collections of services with either a static list of service references or
dynamically via tags. The models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute    | Type      | Required | Default | Description                                                                       |
|--------------|-----------|----------|---------|-----------------------------------------------------------------------------------|
| name         | str       | Yes      | None    | Name of the service group. Max length: 63 chars. Pattern: ^[a-zA-Z0-9_ \.-]+$     |
| description  | str       | No       | None    | Description of the service group. Max length: 1023 chars                          |
| members      | List[str] | No*      | None    | List of service members (for static service groups)                               |
| dynamic      | Dict      | No*      | None    | Dynamic service group configuration with filter expression                         |
| tag          | List[str] | No       | None    | List of tags                                                                       |
| folder       | str       | No**     | None    | Folder where service group is defined. Max length: 64 chars                        |
| snippet      | str       | No**     | None    | Snippet where service group is defined. Max length: 64 chars                       |
| device       | str       | No**     | None    | Device where service group is defined. Max length: 64 chars                        |
| id           | UUID      | Yes***   | None    | UUID of the service group (response only)                                         |

\* Either members or dynamic must be provided, but not both
\** Exactly one container type (folder/snippet/device) must be provided for create operations
\*** Only required for response model

## Exceptions

The Service Group models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When neither or both members and dynamic are provided
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When tag values are not unique in a list
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Service Group Type Validation

The models enforce that either members or dynamic configuration must be provided, but not both:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
from scm.models.objects import ServiceGroupCreateModel

# Error: both members and dynamic provided
try:
    service_group = ServiceGroupCreateModel(
        name="invalid-group",
        members=["service1", "service2"],
        dynamic={"filter": "'tag1' and 'tag2'"},
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'members' or 'dynamic' must be provided."

# Error: neither members nor dynamic provided
try:
    service_group = ServiceGroupCreateModel(
        name="invalid-group",
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'members' or 'dynamic' must be provided."
```

</div>

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
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

</div>

## Usage Examples

### Creating a Static Service Group

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.objects import ServiceGroup

static_dict = {
    "name": "web-services",
    "description": "Common web services",
    "members": ["HTTP", "HTTPS", "HTTP-ALT"],
    "folder": "Texas",
    "tag": ["web", "production"]
}

service_group = ServiceGroup(api_client)
response = service_group.create(static_dict)

# Using model directly
from scm.models.objects import ServiceGroupCreateModel

static_group = ServiceGroupCreateModel(
    name="web-services",
    description="Common web services",
    members=["HTTP", "HTTPS", "HTTP-ALT"],
    folder="Texas",
    tag=["web", "production"]
)

payload = static_group.model_dump(exclude_unset=True)
response = service_group.create(payload)
```

</div>

### Creating a Dynamic Service Group

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
dynamic_dict = {
    "name": "database-services",
    "description": "Database services",
    "dynamic": {
        "filter": "'database' and 'production'"
    },
    "folder": "Texas",
    "tag": ["database"]
}

response = service_group.create(dynamic_dict)

# Using model directly
from scm.models.objects import ServiceGroupCreateModel, DynamicServiceGroupFilter

dynamic_group = ServiceGroupCreateModel(
    name="database-services",
    description="Database services",
    dynamic=DynamicServiceGroupFilter(
        filter="'database' and 'production'"
    ),
    folder="Texas",
    tag=["database"]
)

payload = dynamic_group.model_dump(exclude_unset=True)
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
    "description": "Updated web services",
    "members": ["HTTP", "HTTPS", "HTTP-ALT", "HTTP2"],
    "tag": ["web", "production", "updated"]
}

response = service_group.update(update_dict)

# Using model directly
from scm.models.objects import ServiceGroupUpdateModel

update_group = ServiceGroupUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="web-services-updated",
    description="Updated web services",
    members=["HTTP", "HTTPS", "HTTP-ALT", "HTTP2"],
    tag=["web", "production", "updated"]
)

payload = update_group.model_dump(exclude_unset=True)
response = service_group.update(payload)
```

</div>
