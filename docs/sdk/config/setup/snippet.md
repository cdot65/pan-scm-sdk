# Snippet Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Snippet Model Attributes](#snippet-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Snippets](#creating-snippets)
    - [Retrieving Snippets](#retrieving-snippets)
    - [Fetching a Snippet by Name](#fetching-a-snippet-by-name)
    - [Updating Snippets](#updating-snippets)
    - [Listing Snippets](#listing-snippets)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Snippets](#deleting-snippets)
7. [Folder Associations](#folder-associations)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Snippet` class manages snippet objects in Palo Alto Networks' Strata Cloud Manager. It provides methods for creating, retrieving, updating, and deleting snippets, which are reusable configuration elements. The API supports advanced filtering, pagination, and (planned) folder associations.

## Core Methods

| Method                  | Description                           | Parameters                              | Return Type                      |
|-------------------------|---------------------------------------|-----------------------------------------|----------------------------------|
| `create()`              | Creates a new snippet                 | `data: Dict[str, Any]`                  | `SnippetResponseModel`           |
| `get()`                 | Retrieves a snippet by ID             | `object_id: Union[str, UUID]`           | `SnippetResponseModel`           |
| `update()`              | Updates an existing snippet           | `snippet: SnippetUpdateModel`           | `SnippetResponseModel`           |
| `delete()`              | Deletes a snippet                     | `object_id: Union[str, UUID]`           | `None`                           |
| `list()`                | Lists snippets with filtering         | `**filters`                             | `List[SnippetResponseModel]`     |
| `fetch()`               | Gets a snippet by its name            | `name: str`                             | `Optional[SnippetResponseModel]` |
| `associate_folder()`    | Associates a snippet with a folder    | `snippet_id`, `folder_id`               | `SnippetResponseModel`           |
| `disassociate_folder()` | Disassociates a snippet from a folder | `snippet_id`, `folder_id`               | `SnippetResponseModel`           |

## Snippet Model Attributes

| Attribute       | Type                            | Required | Default | Description                                      |
|-----------------|---------------------------------|----------|---------|--------------------------------------------------|
| `name`          | str                             | Yes      | None    | Name of the snippet                              |
| `id`            | UUID                            | Yes*     | None    | Unique identifier (*response/update only)        |
| `description`   | str                             | No       | None    | Optional description of the snippet              |
| `labels`        | List[str]                       | No       | None    | Optional list of labels to apply to the snippet  |
| `enable_prefix` | bool                            | No       | None    | Whether to enable prefix for this snippet        |
| `type`          | str                             | No       | None    | Snippet type: 'predefined', 'custom', 'readonly' |
| `display_name`  | str                             | No       | None    | Display name for the snippet                     |
| `last_update`   | str                             | No       | None    | Timestamp of last update                         |
| `created_in`    | str                             | No       | None    | Timestamp of creation                            |
| `folders`       | List[FolderReference]           | No       | None    | Folders the snippet is applied to                |
| `shared_in`     | str                             | No       | None    | Sharing scope (e.g., 'local')                    |

\* Only required for response and update models

### Filter Parameters

The `list()` method supports the following filters:

| Parameter | Type       | Description                              |
|-----------|------------|------------------------------------------|
| `labels`  | List[str]  | Filter by labels (server-side)           |
| `types`   | List[str]  | Filter by snippet type (server-side)     |

## Exceptions

| Exception               | HTTP Code | Description                                       |
|-------------------------|-----------|---------------------------------------------------|
| `InvalidObjectError`    | 400       | Invalid snippet data or format                    |
| `ObjectNotPresentError` | 404       | Requested snippet not found                       |
| `APIError`              | Various   | General API communication error                   |
| `NotImplementedError`   | 501       | Feature not yet implemented (folder associations) |
| `AuthenticationError`   | 401       | Authentication failed                             |
| `ServerError`           | 500       | Internal server error                             |

## Basic Configuration

The Snippet service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Snippet service directly through the client
# No need to create a separate Snippet instance
snippets = client.snippet
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.setup.snippet import Snippet

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Snippet object explicitly
snippets = Snippet(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Snippets
```python
snippet_data = {
    "name": "Security Policy Snippet",
    "description": "Common security policy configurations",
    "labels": ["security", "policy"],
    "enable_prefix": True
}
created = snippets.create(snippet_data)
print(created.id, created.name)
```

### Retrieving Snippets
```python
snippet = snippets.get("12345678-1234-1234-1234-123456789012")
print(snippet.name, snippet.type)
```

### Fetching a Snippet by Name
```python
snippet_by_name = snippets.fetch("Security Policy Snippet")
if snippet_by_name:
    print(snippet_by_name.id)
```

### Updating Snippets

```python
# Fetch existing snippet
existing = client.snippet.fetch(name="Security Policy Snippet")

# Modify attributes using dot notation
existing.description = "Updated security policy configs"
existing.labels = ["security", "updated"]

# Pass modified object to update()
updated = client.snippet.update(existing)
print(f"Updated snippet: {updated.name}")
```

### Listing Snippets
```python
all_snippets = snippets.list()
security_snippets = snippets.list(labels=["security"])
custom_snippets = snippets.list(types=["custom"])
```

### Filtering Responses
```python
# Filter snippets by type
custom_snippets = snippets.list(types=["custom"])
# Filter snippets by labels
security_snippets = snippets.list(labels=["security"])
```

### Controlling Pagination with max_limit

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.snippet.max_limit = 100

# List all snippets - auto-paginates through results
all_snippets = client.snippet.list()

# The snippets are fetched in chunks according to the max_limit setting.
```

### Deleting Snippets
```python
snippets.delete("12345678-1234-1234-1234-123456789012")
```

## Folder Associations

The API supports associating snippets with folders, but this may not be fully implemented yet:
```python
try:
    updated_snippet = snippets.associate_folder(snippet_id, folder_id)
    print("Associated snippet with folder")
    result = snippets.disassociate_folder(snippet_id, folder_id)
    print("Disassociated snippet from folder")
except NotImplementedError as e:
    print(f"Folder association not yet implemented: {e}")
```

## Error Handling
```python
from scm.exceptions import ObjectNotPresentError, InvalidObjectError
try:
    snippets.get("nonexistent-id")
except ObjectNotPresentError:
    print("Snippet not found!")

try:
    snippets.create({"name": "", "description": "Invalid"})
except InvalidObjectError as e:
    print("Validation error:", e)
```

## Best Practices
- Always provide a non-empty `name` when creating or updating snippets.
- Use labels to organize and filter snippets.
- Handle exceptions for robust automation.
- Use pagination (`max_limit`) for large snippet sets.

## Full Script Examples
See the test suite in `tests/scm/config/setup/test_snippet.py` for comprehensive usage and edge cases.

## Related Models

- [SnippetBaseModel](../../models/setup/snippet_models.md#Overview)
- [SnippetCreateModel](../../models/setup/snippet_models.md#Overview)
- [SnippetUpdateModel](../../models/setup/snippet_models.md#Overview)
- [SnippetResponseModel](../../models/setup/snippet_models.md#Overview)
- [FolderReference](../../models/setup/snippet_models.md#Overview)
