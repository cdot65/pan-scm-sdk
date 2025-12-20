# Folder Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Exceptions](#exceptions)
4. [Model Validators](#model-validators)
5. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Folder models provide a structured way to manage folder resources in Palo Alto Networks' Strata Cloud Manager.
These models represent folder hierarchies used to organize configuration objects. The models handle validation of
inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `FolderBaseModel`: Base model with fields common to all folder operations
- `FolderCreateModel`: Model for creating new folders
- `FolderUpdateModel`: Model for updating existing folders
- `FolderResponseModel`: Response model for folder operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### FolderBaseModel

| Attribute     | Type      | Required | Default | Description                                                |
|---------------|-----------|----------|---------|------------------------------------------------------------|
| name          | str       | Yes      | None    | The name of the folder                                     |
| parent        | str       | Yes      | None    | Name of the parent folder. Empty string for root folders   |
| description   | str       | No       | None    | Optional description of the folder                         |
| labels        | List[str] | No       | None    | Optional list of labels to apply to the folder             |
| snippets      | List[str] | No       | None    | Optional list of snippet IDs associated with the folder    |
| display_name  | str       | No       | None    | Display name for the folder/device                         |
| model         | str       | No       | None    | Device model, if present (e.g., 'PA-VM')                   |
| serial_number | str       | No       | None    | Device serial number, if present                           |
| type          | str       | No       | None    | Type of folder or device (e.g., 'on-prem', 'container')    |
| device_only   | bool      | No       | None    | True if this is a device-only entry                        |

### FolderCreateModel

Inherits all fields from `FolderBaseModel` without additional fields.

### FolderUpdateModel

Extends `FolderBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the folder  |

### FolderResponseModel

Extends `FolderBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the folder  |

## Exceptions

The Folder models can raise the following exceptions during validation:

- **ValueError**: Raised when field validation fails
- **ValidationError**: Raised by Pydantic when model validation fails

## Model Validators

### Parent Field Validation

The `FolderResponseModel` includes a validator for the parent field that allows empty strings for root folders:

```python
from scm.models.setup.folder import FolderResponseModel

# Root folder with empty parent
root_folder = FolderResponseModel(
    id="baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e",
    name="RootFolder",
    parent=""  # Empty string allowed for root folders
)

# Child folder with parent name
child_folder = FolderResponseModel(
    id="caf4dc4c-9ea2-4a3d-92bb-6f8a9e60822f",
    name="ChildFolder",
    parent="RootFolder"
)
```

## Usage Examples

### Creating a Folder

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
folder_data = {
    "name": "Engineering",
    "parent": "",  # Root folder
    "description": "Engineering team folder",
    "labels": ["team", "eng"]
}

response = client.folder.create(folder_data)
print(f"Created folder: {response.name} with ID: {response.id}")
```

### Creating a Child Folder

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a child folder under Engineering
child_folder = {
    "name": "Development",
    "parent": "Engineering",
    "description": "Development projects folder",
    "labels": ["development"]
}

response = client.folder.create(child_folder)
print(f"Created child folder: {response.name}")
```

### Updating a Folder

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing folder
existing = client.folder.fetch(name="Engineering")

# Modify attributes using dot notation
existing.description = "Updated Engineering folder"
existing.labels = ["engineering", "updated"]

# Pass modified object to update()
updated = client.folder.update(existing)
print(f"Updated folder: {updated.name}")
```

### Listing Folders

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List all folders
all_folders = client.folder.list()

for folder in all_folders:
    print(f"Folder: {folder.name}")
    print(f"Parent: {folder.parent}")
    print(f"Type: {folder.type}")

# Filter by parent
child_folders = client.folder.list(parent="Engineering")

# Filter by labels
labeled_folders = client.folder.list(labels=["engineering"])
```

### Fetching a Folder by Name

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch folder by name
folder = client.folder.fetch(name="Engineering")
if folder:
    print(f"Found folder: {folder.name}")
    print(f"ID: {folder.id}")
    print(f"Description: {folder.description}")
else:
    print("Folder not found")
```
