# Snippet Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Snippet models provide a structured way to manage snippet resources in Palo Alto Networks' Strata Cloud Manager.
These models represent reusable configuration elements that can be applied across multiple folders. The models handle
validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `SnippetBaseModel`: Base model with fields common to all snippet operations
- `SnippetCreateModel`: Model for creating new snippets
- `SnippetUpdateModel`: Model for updating existing snippets
- `SnippetResponseModel`: Response model for snippet operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### SnippetBaseModel

| Attribute     | Type      | Required | Default | Description                                |
|---------------|-----------|----------|---------|--------------------------------------------|
| name          | str       | Yes      | None    | Name of the snippet                        |
| description   | str       | No       | None    | Description of the snippet                 |
| labels        | List[str] | No       | None    | List of labels to apply to the snippet     |
| enable_prefix | bool      | No       | None    | Whether to enable prefix for this snippet  |

### SnippetCreateModel

Inherits all fields from `SnippetBaseModel` without additional fields.

### SnippetUpdateModel

Extends `SnippetBaseModel` by adding:

| Attribute | Type | Required | Default | Description                           |
|-----------|------|----------|---------|---------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the snippet  |

### SnippetResponseModel

Extends `SnippetBaseModel` by adding:

| Attribute    | Type                  | Required | Default | Description                                        |
|--------------|-----------------------|----------|---------|----------------------------------------------------|
| id           | UUID                  | Yes      | None    | The unique identifier of the snippet               |
| type         | str                   | No       | None    | Snippet type: 'predefined', 'custom', or 'readonly' |
| display_name | str                   | No       | None    | Display name of the snippet                        |
| last_update  | str                   | No       | None    | ISO timestamp of last update                       |
| created_in   | str                   | No       | None    | ISO timestamp of creation                          |
| folders      | List[FolderReference] | No       | None    | Folders the snippet is applied to                  |
| shared_in    | str                   | No       | None    | Sharing scope (e.g., 'local')                      |

## Supporting Models

### FolderReference

Reference to a folder that a snippet is applied to.

| Attribute | Type | Required | Default | Description                    |
|-----------|------|----------|---------|--------------------------------|
| id        | UUID | Yes      | None    | The UUID of the folder         |
| name      | str  | Yes      | None    | The name of the folder         |

## Exceptions

The Snippet models can raise the following exceptions during validation:

- **ValueError**: Raised when field validation fails (e.g., empty name)
- **ValidationError**: Raised by Pydantic when model validation fails

## Model Validators

### Name Validation

Both `SnippetBaseModel` and `FolderReference` include validators to ensure names are not empty:

```python
from scm.models.setup.snippet import SnippetCreateModel

# This will raise a validation error
try:
    snippet = SnippetCreateModel(name="")
except ValueError as e:
    print(f"Validation error: {e}")
    # Output: Snippet name cannot be empty
```

## Usage Examples

### Creating a Snippet

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
snippet_data = {
    "name": "Security Policy Snippet",
    "description": "Common security policy configurations",
    "labels": ["security", "policy"],
    "enable_prefix": True
}

response = client.snippet.create(snippet_data)
print(f"Created snippet: {response.name} with ID: {response.id}")
```

### Updating a Snippet

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing snippet
existing = client.snippet.fetch(name="Security Policy Snippet")

# Modify attributes using dot notation
existing.description = "Updated security policy configurations"
existing.labels = ["security", "updated"]

# Pass modified object to update()
updated = client.snippet.update(existing)
print(f"Updated snippet: {updated.name}")
```

### Listing Snippets

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List all snippets
all_snippets = client.snippet.list()

for snippet in all_snippets:
    print(f"Snippet: {snippet.name}")
    print(f"ID: {snippet.id}")
    print(f"Type: {snippet.type}")

# Filter by labels
security_snippets = client.snippet.list(labels=["security"])

# Filter by type
custom_snippets = client.snippet.list(types=["custom"])
```

### Fetching a Snippet by Name

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch snippet by name
snippet = client.snippet.fetch(name="Security Policy Snippet")
if snippet:
    print(f"Found snippet: {snippet.name}")
    print(f"ID: {snippet.id}")
    print(f"Type: {snippet.type}")

    # Access folder associations
    if snippet.folders:
        for folder in snippet.folders:
            print(f"Applied to folder: {folder.name} ({folder.id})")
else:
    print("Snippet not found")
```

