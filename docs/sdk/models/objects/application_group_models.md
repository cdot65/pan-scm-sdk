# Application Group Models

## Overview

The Application Group models provide a structured way to manage application groups in Palo Alto Networks' Strata Cloud
Manager. These models support grouping applications together and defining them within folders, snippets, or devices. The
models
handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute | Type      | Required | Default | Description                                                                                  |
|-----------|-----------|----------|---------|----------------------------------------------------------------------------------------------|
| name      | str       | Yes      | None    | Name of the application group. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
| members   | List[str] | Yes      | None    | List of application names. Min length: 1, Max length: 1024                                   |
| folder    | str       | No*      | None    | Folder where group is defined. Max length: 64 chars                                          |
| snippet   | str       | No*      | None    | Snippet where group is defined. Max length: 64 chars                                         |
| device    | str       | No*      | None    | Device where group is defined. Max length: 64 chars                                          |
| id        | UUID      | Yes**    | None    | UUID of the application group (response only)                                                |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

## Exceptions

The Application Group models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When members list is empty or exceeds maximum length
    - When name or container fields don't match required patterns

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.objects import ApplicationGroup

# Error: multiple containers specified
try:
    app_group_dict = {
        "name": "invalid-group",
        "members": ["app1", "app2"],
        "folder": "Shared",
        "device": "fw01"  # Can't specify both folder and device
    }
    app_group = ApplicationGroup(api_client)
    response = app_group.create(app_group_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
from scm.models.objects import ApplicationGroupCreateModel

# Error: no container specified
try:
    app_group = ApplicationGroupCreateModel(
        name="invalid-group",
        members=["app1", "app2"]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

## Usage Examples

### Creating an Application Group

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.objects import ApplicationGroup

app_group_dict = {
    "name": "web-apps",
    "members": ["http", "https", "web-browsing"],
    "folder": "Shared",
}

app_group = ApplicationGroup(api_client)
response = app_group.create(app_group_dict)

# Using model directly
from scm.models.objects import ApplicationGroupCreateModel

app_group = ApplicationGroupCreateModel(
    name="web-apps",
    members=["http", "https", "web-browsing"],
    folder="Shared"
)

payload = app_group.model_dump(exclude_unset=True)
response = app_group.create(payload)
```

</div>

### Creating an Application Group in a Snippet

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
snippet_group_dict = {
    "name": "database-apps",
    "members": ["mysql", "postgresql", "mongodb"],
    "snippet": "Database Config"
}

response = app_group.create(snippet_group_dict)

# Using model directly
snippet_group = ApplicationGroupCreateModel(
    name="database-apps",
    members=["mysql", "postgresql", "mongodb"],
    snippet="Database Config"
)

payload = snippet_group.model_dump(exclude_unset=True)
response = app_group.create(payload)
```

</div>

### Updating an Application Group

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "web-apps-updated",
    "members": ["http", "https", "web-browsing", "ssl"],
}

response = app_group.update(update_dict)

# Using model directly
from scm.models.objects import ApplicationGroupUpdateModel

update_group = ApplicationGroupUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="web-apps-updated",
    members=["http", "https", "web-browsing", "ssl"]
)

payload = update_group.model_dump(exclude_unset=True)
response = app_group.update(payload)
```

</div>