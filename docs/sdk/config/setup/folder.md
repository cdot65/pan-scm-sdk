# Folder Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Folder Model Attributes](#folder-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Folder Objects](#creating-folder-objects)
    - [Retrieving Folders](#retrieving-folders)
    - [Fetching a Folder by Name](#fetching-a-folder-by-name)
    - [Updating Folders](#updating-folders)
    - [Listing Folders](#listing-folders)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Working with Folder Hierarchies](#working-with-folder-hierarchies)
    - [Deleting Folders](#deleting-folders)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Full Script Examples](#full-script-examples)
10. [Related Models](#related-models)

## Overview

The `Folder` class provides functionality to manage folder objects in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting folder objects, which are used to organize resources in a hierarchical structure.

## Core Methods

| Method     | Description                  | Parameters                      | Return Type                     |
|------------|------------------------------|----------------------------------|---------------------------------|
| `create()` | Creates a new folder         | `data: Dict[str, Any]`           | `FolderResponseModel`           |
| `get()`    | Retrieves a folder by ID     | `folder_id: Union[str, UUID]`    | `FolderResponseModel`           |
| `update()` | Updates an existing folder   | `folder: FolderUpdateModel`      | `FolderResponseModel`           |
| `delete()` | Deletes a folder             | `folder_id: Union[str, UUID]`    | `None`                          |
| `list()`   | Lists folders with filtering | `**filters`                      | `List[FolderResponseModel]`     |
| `fetch()`  | Gets a folder by its name    | `name: str`                      | `Optional[FolderResponseModel]` |

## Folder Model Attributes

| Attribute       | Type                | Required | Default | Description                                                           |
|-----------------|---------------------|----------|---------|-----------------------------------------------------------------------|
| `name`          | str                 | Yes      | None    | Name of the folder                                                    |
| `parent`        | str                 | Yes      | None    | Name of the parent folder (not the ID). Empty string for root folders |
| `id`            | UUID                | Yes*     | None    | Unique identifier (*response/update only)                             |
| `description`   | str                 | No       | None    | Optional description of the folder                                    |
| `labels`        | List[str]           | No       | None    | Optional list of labels to apply to the folder                        |
| `snippets`      | List[str]           | No       | None    | Optional list of snippet IDs associated with the folder               |
| `display_name`  | str                 | No       | None    | Display name for the folder/device, if present                        |
| `model`         | str                 | No       | None    | Device model, if present (e.g., 'PA-VM')                              |
| `serial_number` | str                 | No       | None    | Device serial number, if present                                      |
| `type`          | str                 | No       | None    | Type of folder or device (e.g., 'on-prem', 'container', 'cloud')      |
| `device_only`   | bool                | No       | None    | True if this is a device-only entry                                   |

\* Only required for response and update models

### Filter Parameters

The `list()` method supports the following filters:

| Parameter       | Type       | Description                                      |
|-----------------|------------|--------------------------------------------------|
| `labels`        | List[str]  | Filter by labels (server-side, comma-joined)     |
| `type`          | str        | Filter by folder type (server-side)              |
| `parent`        | str        | Filter by parent folder name (server-side)       |
| `snippets`      | List[str]  | Filter by snippets (client-side, any match)      |
| `model`         | str        | Filter by device model (client-side, exact)      |
| `serial_number` | str        | Filter by serial number (client-side, exact)     |
| `device_only`   | bool       | Filter device-only entries (client-side)         |

## Exceptions

| Exception                | HTTP Code | Description                                   |
|--------------------------|-----------|-----------------------------------------------|
| `InvalidObjectError`     | 400       | Invalid folder data or format                 |
| `ObjectNotPresentError`  | 404       | Requested folder not found                    |
| `APIError`               | Various   | General API communication error               |
| `AuthenticationError`    | 401       | Authentication failed                         |
| `ServerError`            | 500       | Internal server error                         |

## Basic Configuration

The Folder service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Folder service directly through the client
# No need to create a separate Folder instance
folders = client.folder
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.setup.folder import Folder

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Folder object explicitly
folders = Folder(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Folder Objects
```python
folder_data = {
    "name": "Engineering",
    "parent": "root",
    "description": "Engineering team folder",
    "labels": ["team", "eng"],
    "snippets": [],
}
created = folders.create(folder_data)
print(created.id, created.name)
```

### Retrieving Folders
```python
folder = folders.get("baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e")
print(folder.name, folder.parent)
```

### Fetching a Folder by Name
```python
folder_by_name = folders.fetch("Engineering")
if folder_by_name:
    print(folder_by_name.id)
```

### Updating Folders

```python
# Fetch existing folder
existing = client.folder.fetch(name="Engineering")

# Modify attributes using dot notation
existing.description = "Updated description"
existing.labels = ["updated", "engineering"]

# Pass modified object to update()
updated = client.folder.update(existing)
print(updated.description)
```

### Listing Folders
```python
all_folders = folders.list()
folders_with_label = folders.list(labels=["eng"])
folders_of_type = folders.list(type="container")
```

### Filtering Responses
```python
# Filter folders by labels
eng_folders = folders.list(labels=["eng"])
# Filter folders by type
container_folders = folders.list(type="container")
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
client.folder.max_limit = 100

# List all folders - auto-paginates through results
all_folders = client.folder.list()

# The folders are fetched in chunks according to the max_limit setting.
```

### Working with Folder Hierarchies
```python
# List all folders with a specific parent
child_folders = folders.list(parent="root")
```

### Deleting Folders
```python
folders.delete("baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e")
```

## Error Handling

```python
from scm.exceptions import ObjectNotPresentError, InvalidObjectError
try:
    folders.get("nonexistent-id")
except ObjectNotPresentError:
    print("Folder not found!")

try:
    folders.create({"name": "", "parent": "root"})
except InvalidObjectError as e:
    print("Validation error:", e)
```

## Best Practices
- Always check for required fields (`name`, `parent`) before creating or updating folders.
- Use client-side filtering for fields not supported by server-side API filtering (e.g., `name`).
- Handle exceptions for robust automation.
- Use pagination (`max_limit`) for large folder sets.

## Full Script Examples

See the test suite in `tests/scm/config/setup/test_folder.py` for comprehensive usage and edge cases.

## Related Models

- [FolderBaseModel](../../models/setup/folder_models.md#Overview)
- [FolderCreateModel](../../models/setup/folder_models.md#Overview)
- [FolderUpdateModel](../../models/setup/folder_models.md#Overview)
- [FolderResponseModel](../../models/setup/folder_models.md#Overview)
