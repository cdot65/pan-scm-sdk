# Folder Configuration Object

Manages folder objects for organizing resources in a hierarchical structure in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `Folder` class inherits from `BaseObject` and provides CRUD operations for folder objects used to organize resources hierarchically.

### Methods

| Method     | Description                  | Parameters                    | Return Type             |
|------------|------------------------------|-------------------------------|-------------------------|
| `create()` | Creates a new folder         | `data: Dict[str, Any]`        | `FolderResponseModel`   |
| `get()`    | Retrieves a folder by ID     | `folder_id: Union[str, UUID]` | `FolderResponseModel`   |
| `update()` | Updates an existing folder   | `folder: FolderUpdateModel`   | `FolderResponseModel`   |
| `delete()` | Deletes a folder             | `folder_id: Union[str, UUID]` | `None`                  |
| `list()`   | Lists folders with filtering | `**filters`                   | `List[FolderResponseModel]` |
| `fetch()`  | Gets a folder by its name    | `name: str`                   | `FolderResponseModel`   |

### Model Attributes

| Attribute       | Type      | Required | Default | Description                                                           |
|-----------------|-----------|----------|---------|-----------------------------------------------------------------------|
| `name`          | str       | Yes      | None    | Name of the folder                                                    |
| `parent`        | str       | Yes      | None    | Name of the parent folder (not the ID). Empty string for root folders |
| `id`            | UUID      | Yes*     | None    | Unique identifier (*response/update only)                             |
| `description`   | str       | No       | None    | Optional description of the folder                                    |
| `labels`        | List[str] | No       | None    | Optional list of labels                                               |
| `snippets`      | List[str] | No       | None    | Optional list of snippet IDs associated with the folder               |
| `display_name`  | str       | No       | None    | Display name for the folder/device                                    |
| `model`         | str       | No       | None    | Device model (e.g., 'PA-VM')                                          |
| `serial_number` | str       | No       | None    | Device serial number                                                  |
| `type`          | str       | No       | None    | Folder or device type (e.g., 'on-prem', 'container', 'cloud')         |
| `device_only`   | bool      | No       | None    | True if this is a device-only entry                                   |

\* Only required for response and update models

### Exceptions

| Exception              | HTTP Code | Description                   |
|------------------------|-----------|-------------------------------|
| `InvalidObjectError`   | 400       | Invalid folder data or format |
| `ObjectNotPresentError`| 404       | Requested folder not found    |
| `APIError`             | Various   | General API communication error |
| `AuthenticationError`  | 401       | Authentication failed         |
| `ServerError`          | 500       | Internal server error         |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

folders = client.folder
```

## Methods

### List Folders

```python
all_folders = client.folder.list()

for folder in all_folders:
    print(f"Folder: {folder.name}, Parent: {folder.parent}")
```

**Filtering responses:**

```python
# Filter by labels (server-side)
eng_folders = client.folder.list(labels=["eng"])

# Filter by type (server-side)
container_folders = client.folder.list(type="container")

# Filter by parent (server-side)
child_folders = client.folder.list(parent="root")

# Filter by snippets (client-side)
snippet_folders = client.folder.list(snippets=["snippet-id"])
```

**Controlling pagination with max_limit:**

```python
client.folder.max_limit = 100

all_folders = client.folder.list()
```

### Fetch a Folder

```python
folder = client.folder.fetch("Engineering")
if folder:
    print(f"Found folder: {folder.name}, ID: {folder.id}")
```

### Create a Folder

```python
folder_data = {
    "name": "Engineering",
    "parent": "root",
    "description": "Engineering team folder",
    "labels": ["team", "eng"],
}
created = client.folder.create(folder_data)
print(f"Created folder: {created.id}")
```

### Update a Folder

```python
existing = client.folder.fetch(name="Engineering")

existing.description = "Updated description"
existing.labels = ["updated", "engineering"]

updated = client.folder.update(existing)
```

### Delete a Folder

```python
client.folder.delete("baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e")
```

### Get a Folder by ID

```python
folder = client.folder.get("baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e")
print(f"Folder: {folder.name}, Parent: {folder.parent}")
```

## Error Handling

```python
from scm.exceptions import ObjectNotPresentError, InvalidObjectError

try:
    folder = client.folder.get("nonexistent-id")
except ObjectNotPresentError:
    print("Folder not found!")

try:
    client.folder.create({"name": "", "parent": "root"})
except InvalidObjectError as e:
    print(f"Validation error: {e}")
```

## Related Topics

- [Folder Models](../../models/setup/folder_models.md#Overview)
- [Setup Overview](index.md)
- [API Client](../../client.md)
