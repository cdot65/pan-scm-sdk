# Snippet Models

## Table of Contents

1. [Overview](#overview)
2. [Models](#models)
    - [FolderReference](#folderreference)
    - [SnippetBaseModel](#snippetbasemodel)
    - [SnippetCreateModel](#snippetcreatemodel)
    - [SnippetUpdateModel](#snippetupdatemodel)
    - [SnippetResponseModel](#snippetresponsemodel)
3. [Model Validation Rules](#model-validation-rules)
4. [Usage Examples](#usage-examples)
    - [Creating Model Instances](#creating-model-instances)
    - [Model Validation](#model-validation)
    - [Model Serialization](#model-serialization)
    - [API Integration Examples](#api-integration-examples)

## Overview

This page documents the Pydantic models used for snippet operations in the Strata Cloud Manager SDK. These models provide structured data validation and serialization for snippet creation, updates, and API responses.

## Models

### FolderReference

Reference to a folder that a snippet is applied to.

```python
class FolderReference(BaseModel):
    id: UUID
    name: str
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value or value.strip() == "":
            raise ValueError("Folder name cannot be empty")
        return value
```

### SnippetBaseModel

The base model for snippet resources containing common fields.

```python
class SnippetBaseModel(BaseModel):
    name: str
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    enable_prefix: Optional[bool] = None
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value or value.strip() == "":
            raise ValueError("Snippet name cannot be empty")
        return value
```

### SnippetCreateModel

Model for creating new snippet resources.

```python
class SnippetCreateModel(SnippetBaseModel):
    pass  # Inherits all fields from SnippetBaseModel
```

### SnippetUpdateModel

Model for updating existing snippet resources.

```python
class SnippetUpdateModel(SnippetBaseModel):
    id: UUID
```

### SnippetResponseModel

Model for snippet responses from the API.

```python
class SnippetResponseModel(SnippetBaseModel):
    id: UUID
    type: Optional[Literal["predefined", "custom", "readonly"]] = None
    display_name: Optional[str] = None
    last_update: Optional[str] = None
    created_in: Optional[str] = None
    folders: Optional[List[FolderReference]] = None
    shared_in: Optional[str] = None
```

## Model Validation Rules

| Field           | Validation Rules                                                |
|-----------------|-----------------------------------------------------------------|
| `name`          | Non-empty string, max 255 characters                            |
| `description`   | Optional text description                                       |
| `labels`        | Optional list of string labels                                  |
| `enable_prefix` | Optional boolean                                                |
| `id`            | Valid UUID format (required in response and update models)      |
| `type`          | One of: 'predefined', 'custom', 'readonly' (response only)      |
| `display_name`  | Optional string (response only)                                 |
| `last_update`   | Optional ISO8601 timestamp (response only)                      |
| `created_in`    | Optional ISO8601 timestamp (response only)                      |
| `folders`       | Optional list of FolderReference, each with valid UUID and name |
| `shared_in`     | Optional string (response only)                                 |

## Usage Examples

### Creating Model Instances

```python
from uuid import UUID
from scm.models.setup.snippet import (
    FolderReference,
    SnippetBaseModel,
    SnippetCreateModel,
    SnippetUpdateModel,
    SnippetResponseModel,
)

# Create a base snippet model
base_snippet = SnippetBaseModel(
    name="Base Snippet",
    description="A base snippet model",
    labels=["base", "example"],
    enable_prefix=True,
)

# Create a snippet creation model
create_snippet = SnippetCreateModel(
    name="New Snippet",
    description="A snippet for creation",
    labels=["new", "creation"],
    enable_prefix=False,
)

# Create a snippet update model
update_snippet = SnippetUpdateModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Updated Snippet",
    description="An updated snippet",
    labels=["updated", "modified"],
)

# Create a folder reference
folder_ref = FolderReference(
    id=UUID("87654321-4321-4321-4321-210987654321"),
    name="Example Folder",
)

# Create a snippet response model
response_snippet = SnippetResponseModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Response Snippet",
    description="A response snippet",
    labels=["response", "example"],
    enable_prefix=True,
    type="custom",
    display_name="Custom Snippet",
    last_update="2024-04-01T12:00:00Z",
    created_in="2024-03-01T08:00:00Z",
    folders=[folder_ref],
    shared_in="local",
)
```

### Model Validation

```python
from pydantic_core import ValidationError
from scm.models.setup.snippet import SnippetCreateModel

try:
    SnippetCreateModel(name="", description="Invalid snippet")
except ValidationError as e:
    print("Validation error:", e)
```

### Model Serialization

```python
snippet = response_snippet
# Convert to dict
snippet_dict = snippet.model_dump()
# Convert to JSON
snippet_json = snippet.model_dump_json()
```

### API Integration Examples

```python
from scm.config.setup.snippet import Snippet
snippets = Snippet(client)

# Create and send a snippet
new_snippet = SnippetCreateModel(
    name="QA Snippet",
    description="Quality Assurance snippet",
    labels=["qa"],
    enable_prefix=True,
)
created = snippets.create(new_snippet.model_dump(exclude_unset=True))

# Update a snippet
update = SnippetUpdateModel(
    id=created.id,
    name="QA Snippet",
    description="QA and Testing",
)
snippets.update(update)
```
