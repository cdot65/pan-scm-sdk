# Snippet Models

## Table of Contents

1. [Overview](#overview)
2. [Models](#models)
    - [SnippetResponseModel](#snippetresponsemodel)
3. [Model Fields](#model-fields)
4. [Usage Examples](#usage-examples)

## Overview

This page documents the Pydantic models used for snippet operations in the Strata Cloud Manager SDK. These models provide
structured data validation and serialization for snippet creation, updates, and API responses.

## Models

### SnippetResponseModel

Model for snippet responses from the API.

```python
class SnippetResponseModel(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    enable_prefix: bool = False
```

## Model Fields

| Field           | Type                | Required | Description                                      |
|-----------------|---------------------|----------|--------------------------------------------------|
| `id`            | UUID                | Yes      | Unique identifier for the snippet                |
| `name`          | str                 | Yes      | Name of the snippet                              |
| `description`   | Optional[str]       | No       | Optional description of the snippet              |
| `labels`        | Optional[List[str]] | No       | Optional list of labels to apply to the snippet  |
| `enable_prefix` | bool                | No       | Whether to enable prefix for this snippet        |

## Usage Examples

### Working with Snippet Models

```python
from uuid import UUID
from scm.models.setup.snippet_models import SnippetResponseModel

# Create a snippet model instance from API response
snippet = SnippetResponseModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="Example Snippet",
    description="This is an example snippet",
    labels=["example", "documentation"],
    enable_prefix=True
)

print(f"Snippet ID: {snippet.id}")
print(f"Snippet Name: {snippet.name}")
print(f"Snippet Description: {snippet.description}")
print(f"Snippet Labels: {', '.join(snippet.labels)}")
print(f"Prefix Enabled: {snippet.enable_prefix}")
```

### Parsing API Response to Snippet Model

```python
import json
from uuid import UUID
from scm.models.setup.snippet_models import SnippetResponseModel

# Example API response
api_response = {
    "id": "12345678-1234-1234-1234-123456789012",
    "name": "API Response Snippet",
    "description": "Snippet from API response",
    "labels": ["api", "response"],
    "enable_prefix": False
}

# Parse response into model
snippet = SnippetResponseModel.model_validate(api_response)

# Access model fields
print(f"Snippet Name: {snippet.name}")
```

### Using Snippet Model with SDK Client

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Create a new snippet
new_snippet = client.snippet.create(
    name="Configuration Snippet",
    description="Common configuration snippet",
    labels=["config", "reusable"],
    enable_prefix=True
)

# The returned object is a SnippetResponseModel
print(f"Created snippet with ID: {new_snippet.id}")
```
