# Snippet Configuration Object

Manages reusable configuration snippet objects in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `Snippet` class inherits from `BaseObject` and provides CRUD operations for snippet objects, which are reusable configuration elements. It also supports folder association and disassociation.

### Methods

| Method                  | Description                           | Parameters                    | Return Type              |
|-------------------------|---------------------------------------|-------------------------------|--------------------------|
| `create()`              | Creates a new snippet                 | `data: Dict[str, Any]`        | `SnippetResponseModel`   |
| `get()`                 | Retrieves a snippet by ID             | `object_id: Union[str, UUID]` | `SnippetResponseModel`   |
| `update()`              | Updates an existing snippet           | `snippet: SnippetUpdateModel` | `SnippetResponseModel`   |
| `delete()`              | Deletes a snippet                     | `object_id: Union[str, UUID]` | `None`                   |
| `list()`                | Lists snippets with filtering         | `**filters`                   | `List[SnippetResponseModel]` |
| `fetch()`               | Gets a snippet by its name            | `name: str`                   | `SnippetResponseModel`   |
| `associate_folder()`    | Associates a snippet with a folder    | `snippet_id`, `folder_id`     | `SnippetResponseModel`   |
| `disassociate_folder()` | Disassociates a snippet from a folder | `snippet_id`, `folder_id`     | `SnippetResponseModel`   |

### Model Attributes

| Attribute       | Type                  | Required | Default | Description                                       |
|-----------------|-----------------------|----------|---------|---------------------------------------------------|
| `name`          | str                   | Yes      | None    | Name of the snippet                               |
| `id`            | UUID                  | Yes*     | None    | Unique identifier (*response/update only)         |
| `description`   | str                   | No       | None    | Optional description                              |
| `labels`        | List[str]             | No       | None    | Optional list of labels                           |
| `enable_prefix` | bool                  | No       | None    | Whether to enable prefix for this snippet         |
| `type`          | str                   | No       | None    | Snippet type: 'predefined', 'custom', 'readonly'  |
| `display_name`  | str                   | No       | None    | Display name for the snippet                      |
| `last_update`   | str                   | No       | None    | Timestamp of last update                          |
| `created_in`    | str                   | No       | None    | Timestamp of creation                             |
| `folders`       | List[FolderReference] | No       | None    | Folders the snippet is applied to                 |
| `shared_in`     | str                   | No       | None    | Sharing scope (e.g., 'local')                     |

\* Only required for response and update models

### Exceptions

| Exception              | HTTP Code | Description                    |
|------------------------|-----------|--------------------------------|
| `InvalidObjectError`   | 400       | Invalid snippet data or format |
| `ObjectNotPresentError`| 404       | Requested snippet not found    |
| `APIError`             | Various   | General API communication error |
| `NotImplementedError`  | 501       | Feature not yet implemented    |
| `AuthenticationError`  | 401       | Authentication failed          |
| `ServerError`          | 500       | Internal server error          |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

snippets = client.snippet
```

## Methods

### List Snippets

```python
all_snippets = client.snippet.list()
security_snippets = client.snippet.list(labels=["security"])
custom_snippets = client.snippet.list(types=["custom"])
```

**Controlling pagination with max_limit:**

```python
client.snippet.max_limit = 100

all_snippets = client.snippet.list()
```

### Fetch a Snippet

```python
snippet = client.snippet.fetch("Security Policy Snippet")
if snippet:
    print(f"Found snippet: {snippet.name}, ID: {snippet.id}")
```

### Create a Snippet

```python
snippet_data = {
    "name": "Security Policy Snippet",
    "description": "Common security policy configurations",
    "labels": ["security", "policy"],
    "enable_prefix": True
}
created = client.snippet.create(snippet_data)
print(f"Created snippet: {created.id}")
```

### Update a Snippet

```python
existing = client.snippet.fetch(name="Security Policy Snippet")

existing.description = "Updated security policy configs"
existing.labels = ["security", "updated"]

updated = client.snippet.update(existing)
```

### Delete a Snippet

```python
client.snippet.delete("12345678-1234-1234-1234-123456789012")
```

### Get a Snippet by ID

```python
snippet = client.snippet.get("12345678-1234-1234-1234-123456789012")
print(f"Snippet: {snippet.name}, Type: {snippet.type}")
```

## Use Cases

### Folder Associations

```python
try:
    updated_snippet = client.snippet.associate_folder(snippet_id, folder_id)
    print("Associated snippet with folder")
    result = client.snippet.disassociate_folder(snippet_id, folder_id)
    print("Disassociated snippet from folder")
except NotImplementedError as e:
    print(f"Folder association not yet implemented: {e}")
```

## Error Handling

```python
from scm.exceptions import ObjectNotPresentError, InvalidObjectError

try:
    snippet = client.snippet.get("nonexistent-id")
except ObjectNotPresentError:
    print("Snippet not found!")

try:
    client.snippet.create({"name": "", "description": "Invalid"})
except InvalidObjectError as e:
    print(f"Validation error: {e}")
```

## Related Topics

- [Snippet Models](../../models/setup/snippet_models.md#Overview)
- [Setup Overview](index.md)
- [API Client](../../client.md)
