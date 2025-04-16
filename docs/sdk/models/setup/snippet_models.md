# Snippet Models

## Table of Contents

1. [Overview](#overview)
2. [Models](#models)
    - [SnippetBaseModel](#snippetbasemodel)
    - [SnippetCreateModel](#snippetcreatemodel)
    - [SnippetUpdateModel](#snippetupdatemodel)
    - [SnippetResponseModel](#snippetresponsemodel)
    - [FolderReference](#folderreference)
3. [Model Validation Rules](#model-validation-rules)
4. [Usage Examples](#usage-examples)
    - [Creating Model Instances](#creating-model-instances)
    - [Model Validation](#model-validation)
    - [Model Serialization](#model-serialization)
    - [API Integration Examples](#api-integration-examples)

## Overview

This page documents the Pydantic models used for snippet operations in the Strata Cloud Manager SDK. These models provide
structured data validation and serialization for snippet creation, updates, and API responses.

## Models

### SnippetBaseModel

Base model for snippet objects with common fields.

```python
class SnippetBaseModel(BaseModel):
    name: str
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    enable_prefix: bool = False
```

### SnippetCreateModel

Model for creating new snippets.

```python
class SnippetCreateModel(SnippetBaseModel):
    pass  # Inherits all fields from SnippetBaseModel
```

### SnippetUpdateModel

Model for updating existing snippets.

```python
class SnippetUpdateModel(SnippetBaseModel):
    id: UUID  # Required for update operations
```

### SnippetResponseModel

Model for snippet responses from the API.

```python
class SnippetResponseModel(SnippetBaseModel):
    id: UUID
    folders: Optional[List[FolderReference]] = None
```

### FolderReference

Model for folder references within snippets.

```python
class FolderReference(BaseModel):
    id: UUID
    name: str
```

## Model Validation Rules

| Field           | Validation Rules                                          |
|-----------------|------------------------------------------------------------|
| `name`          | Non-empty string, max 255 characters                       |
| `description`   | Optional text description                                  |
| `labels`        | Optional list of string labels                             |
| `enable_prefix` | Boolean flag, defaults to False                            |
| `id`            | Valid UUID format                                          |
| `folders`       | Optional list of folder references with valid UUIDs        |

## Usage Examples

### Creating Model Instances

```python
from uuid import UUID
from typing import List, Optional
from scm.models.setup.snippet_models import (
    SnippetBaseModel,
    SnippetCreateModel,
    SnippetUpdateModel,
    SnippetResponseModel,
    FolderReference
)

# Create a base snippet model
base_snippet = SnippetBaseModel(
    name="Base Snippet",
    description="A base snippet model",
    labels=["base", "example"],
    enable_prefix=True
)

# Create a snippet creation model
create_snippet = SnippetCreateModel(
    name="New Snippet",
    description="A snippet for creation",
    labels=["new", "creation"],
    enable_prefix=False
)

# Create a snippet update model
update_snippet = SnippetUpdateModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Updated Snippet",
    description="An updated snippet",
    labels=["updated", "modified"]
)

# Create a folder reference
folder_ref = FolderReference(
    id=UUID("87654321-4321-4321-4321-210987654321"),
    name="Example Folder"
)

# Create a snippet response model
response_snippet = SnippetResponseModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Response Snippet",
    description="A response snippet",
    labels=["response", "example"],
    enable_prefix=True,
    folders=[folder_ref]
)
```

### Model Validation

```python
from pydantic import ValidationError
from scm.models.setup.snippet_models import SnippetCreateModel

try:
    # This will fail validation (empty name)
    invalid_snippet = SnippetCreateModel(
        name="",
        description="Invalid snippet"
    )
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    # This will succeed
    valid_snippet = SnippetCreateModel(
        name="Valid Snippet",
        description="A valid snippet"
    )
    print(f"Valid snippet created: {valid_snippet.name}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Model Serialization

```python
from uuid import UUID
from scm.models.setup.snippet_models import SnippetResponseModel, FolderReference

# Create a response model
snippet = SnippetResponseModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Example Snippet",
    description="An example snippet",
    labels=["example", "serialization"],
    folders=[
        FolderReference(
            id=UUID("87654321-4321-4321-4321-210987654321"),
            name="Example Folder"
        )
    ]
)

# Convert to dictionary
snippet_dict = snippet.model_dump()
print(f"Dictionary representation: {snippet_dict}")

# Convert to JSON string
snippet_json = snippet.model_dump_json()
print(f"JSON representation: {snippet_json}")
```

### API Integration Examples

```python
from scm.client import ScmClient
from scm.models.setup.snippet_models import SnippetCreateModel

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Create a snippet model
snippet_model = SnippetCreateModel(
    name="API Integration Snippet",
    description="A snippet for API integration",
    labels=["api", "integration"]
)

# Use the model with the API client
response = client.snippet.create(
    name=snippet_model.name,
    description=snippet_model.description,
    labels=snippet_model.labels,
    enable_prefix=snippet_model.enable_prefix
)

print(f"Created snippet with ID: {response.id}")
