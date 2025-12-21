# Application Group Models

## Overview {#Overview}

The Application Group models provide a structured way to manage application groups in Palo Alto Networks' Strata Cloud
Manager. These models support grouping applications together and defining them within folders, snippets, or devices. The
models handle validation of inputs and outputs when interacting with the SCM API.

### Models

| Model                           | Purpose                                          |
|---------------------------------|--------------------------------------------------|
| `ApplicationGroupBaseModel`     | Base model with common fields for all operations |
| `ApplicationGroupCreateModel`   | Model for creating new application groups        |
| `ApplicationGroupUpdateModel`   | Model for updating existing application groups   |
| `ApplicationGroupResponseModel` | Model for API responses                          |

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute | Type      | Required | Default | Description                                                                                  |
|-----------|-----------|----------|---------|----------------------------------------------------------------------------------------------|
| name      | str       | Yes      | None    | Name of the application group. Max length: 31 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
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

```python
# Using dictionary
from scm.config.objects import ApplicationGroup

# Error: multiple containers specified
try:
    app_group_dict = {
        "name": "invalid-group",
        "members": ["app1", "app2"],
        "folder": "Texas",
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

## Usage Examples

### Creating an Application Group

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
app_group_dict = {
    "name": "web-apps",
    "members": ["http", "https", "web-browsing"],
    "folder": "Texas",
}

response = client.application_group.create(app_group_dict)
```

### Creating an Application Group in a Snippet

```python
# Using dictionary
snippet_group_dict = {
    "name": "database-apps",
    "members": ["mysql", "postgresql", "mongodb"],
    "snippet": "Database Config"
}

response = client.application_group.create(snippet_group_dict)
```

### Updating an Application Group

```python
# Fetch existing group
existing = client.application_group.fetch(name="web-apps", folder="Texas")

# Modify attributes using dot notation
existing.members = ["http", "https", "web-browsing", "ssl"]

# Pass modified object to update()
updated = client.application_group.update(existing)
```
