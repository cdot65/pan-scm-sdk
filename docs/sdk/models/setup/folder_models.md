# Folder Models

## Table of Contents

1. [Overview](#overview)
2. [Models](#models)
    - [FolderBaseModel](#folderbasemodel)
    - [FolderCreateModel](#foldercreatemodel)
    - [FolderUpdateModel](#folderupdatemodel)
    - [FolderResponseModel](#folderresponsemodel)
3. [Model Validation Rules](#model-validation-rules)
4. [Usage Examples](#usage-examples)
    - [Creating Model Instances](#creating-model-instances)
    - [Model Validation](#model-validation)
    - [Model Serialization](#model-serialization)
    - [API Integration Examples](#api-integration-examples)

## Overview

This page documents the Pydantic models used for folder operations in the Strata Cloud Manager SDK. These models provide structured data validation and serialization for folder creation, updates, and API responses.

## Models

### FolderBaseModel

The base model for folder resources containing common fields.

```python
class FolderBaseModel(BaseModel):
    name: str
    parent: str
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    snippets: Optional[List[str]] = None
    display_name: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    type: Optional[str] = None
    device_only: Optional[bool] = None
```

### FolderCreateModel

Model for creating new folder resources.

```python
class FolderCreateModel(FolderBaseModel):
    # Inherits all fields from FolderBaseModel without additional fields
    pass
```

### FolderUpdateModel

Model for updating existing folder resources.

```python
class FolderUpdateModel(FolderBaseModel):
    id: UUID
```

### FolderResponseModel

Model for folder responses from the API.

```python
class FolderResponseModel(FolderBaseModel):
    id: UUID
    @field_validator("parent")
    @classmethod
    def validate_parent(cls, v: str) -> str:
        """
        Validate parent field. Empty string is allowed for root folders.
        """
        # Allow empty string for root folders
        return v
```

## Model Validation Rules

| Field           | Validation Rules                                           |
|-----------------|------------------------------------------------------------|
| `name`          | Non-empty string, max 255 characters                       |
| `parent`        | String, empty string for root folders                      |
| `id`            | Valid UUID format (required in response and update models) |
| `description`   | Optional text description                                  |
| `labels`        | Optional list of string labels                             |
| `snippets`      | Optional list of snippet IDs (usually UUIDs as strings)    |
| `display_name`  | Optional string                                            |
| `model`         | Optional string                                            |
| `serial_number` | Optional string                                            |
| `type`          | Optional string                                            |
| `device_only`   | Optional boolean                                           |

The `FolderResponseModel` includes a validator for the parent field:

```python
@field_validator("parent")
@classmethod
def validate_parent(cls, v: str) -> str:
    """
    Validate parent field. Empty string is allowed for root folders.
    """
    # Allow empty string for root folders
    return v
```

## Usage Examples

### Creating Model Instances

```python
from uuid import UUID
from scm.models.setup.folder import (
    FolderBaseModel,
    FolderCreateModel,
    FolderUpdateModel,
    FolderResponseModel
)

# Create a base folder model
base_folder = FolderBaseModel(
    name="Projects",
    parent="",  # Root folder
    description="Main projects folder",
    labels=["root", "projects"],
    display_name="Projects (Root)",
)

# Create a folder creation model
create_folder = FolderCreateModel(
    name="Development",
    parent="Projects",
    description="Development projects folder",
    labels=["development"]
)

# Create a folder update model
update_folder = FolderUpdateModel(
    id=UUID("baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e"),
    name="Development",
    parent="Projects",
    description="Updated folder",
    labels=["dev", "updated"]
)

# Parse a folder API response
response = FolderResponseModel(
    id=UUID("baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e"),
    name="Engineering",
    parent="root",
    display_name="Engineering",
    model="PA-VM",
    serial_number="0123456789",
    type="container",
    device_only=False
)
```

### Model Validation

```python
from pydantic_core import ValidationError
try:
    FolderCreateModel(name="", parent="root")
except ValidationError as e:
    print("Validation error:", e)
```

### Model Serialization

```python
folder = FolderResponseModel(
    id=UUID("baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e"),
    name="Engineering",
    parent="root"
)
# Convert to dict
folder_dict = folder.model_dump()
# Convert to JSON
folder_json = folder.model_dump_json()
```

### API Integration Examples

```python
from scm.config.setup.folder import Folder
folders = Folder(client)

# Create and send a folder
new_folder = FolderCreateModel(
    name="QA",
    parent="Engineering",
    description="Quality Assurance folder"
)
created = folders.create(new_folder.model_dump(exclude_unset=True))

# Update a folder
update = FolderUpdateModel(
    id=created.id,
    name="QA",
    parent="Engineering",
    description="QA and Testing"
)
folders.update(update)
```
