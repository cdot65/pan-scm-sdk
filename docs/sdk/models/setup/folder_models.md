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

This page documents the Pydantic models used for folder operations in the Strata Cloud Manager SDK. These models provide
structured data validation and serialization for folder creation, updates, and API responses.

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
```

## Model Validation Rules

| Field         | Validation Rules                                               |
|---------------|---------------------------------------------------------------|
| `name`        | Non-empty string, max 255 characters                          |
| `parent`      | String, empty string for root folders                         |
| `id`          | Valid UUID format (required in response and update models)    |
| `description` | Optional text description                                     |
| `labels`      | Optional list of string labels                                |
| `snippets`    | Optional list of snippet IDs (usually UUIDs as strings)       |

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
from typing import List, Optional
from scm.models.setup.folder_models import (
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
    labels=["root", "projects"]
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
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Development-Updated",
    parent="Projects",
    description="Updated development folder",
    labels=["development", "updated"]
)

# Create a folder response model
response_folder = FolderResponseModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Development",
    parent="Projects",
    description="Development projects folder",
    labels=["development"],
    snippets=["87654321-4321-4321-4321-210987654321"]
)
```

### Model Validation

```python
from pydantic import ValidationError
from scm.models.setup.folder_models import FolderCreateModel

try:
    # This will fail validation (empty name)
    invalid_folder = FolderCreateModel(
        name="",
        parent="Projects",
        description="Invalid folder model"
    )
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    # This will succeed
    valid_folder = FolderCreateModel(
        name="Valid Folder",
        parent="Projects",
        description="A valid folder model"
    )
    print(f"Valid folder created: {valid_folder.name}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Model Serialization

```python
from uuid import UUID
from scm.models.setup.folder_models import FolderResponseModel

# Create a response model
folder = FolderResponseModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Development",
    parent="Projects",
    description="Development projects folder",
    labels=["development", "serialization"]
)

# Convert to dictionary
folder_dict = folder.model_dump()
print(f"Dictionary representation: {folder_dict}")

# Convert to JSON string
folder_json = folder.model_dump_json()
print(f"JSON representation: {folder_json}")

# Exclude unset fields
folder_dict_minimal = folder.model_dump(exclude_unset=True)
print(f"Minimal dictionary representation: {folder_dict_minimal}")
```

### API Integration Examples

```python
from scm.client import ScmClient
from scm.models.setup.folder_models import FolderCreateModel

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Create a folder model
folder_model = FolderCreateModel(
    name="API Integration Folder",
    parent="Projects",
    description="A folder for API integration examples",
    labels=["api", "integration"]
)

# Use the model with the API client
response = client.folder.create(
    name=folder_model.name,
    parent=folder_model.parent,
    description=folder_model.description,
    labels=folder_model.labels
)

print(f"Created folder with ID: {response.id}")

# Update the folder
if response:
    updated = client.folder.update(
        folder_id=str(response.id),
        name="Updated API Folder",
        parent=response.parent,
        description="This folder was updated via the API",
        labels=[*response.labels, "updated"] if response.labels else ["updated"]
    )
    print(f"Updated folder name: {updated.name}")
