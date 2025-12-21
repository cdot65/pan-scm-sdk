# Label Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Exceptions](#exceptions)
4. [Model Validators](#model-validators)
5. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Label models provide a structured way to manage label resources in Palo Alto Networks' Strata Cloud Manager.
These models represent simple key-value labels used for resource classification and organization. The models handle
validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `LabelBaseModel`: Base model with fields common to all label operations
- `LabelCreateModel`: Model for creating new labels
- `LabelUpdateModel`: Model for updating existing labels
- `LabelResponseModel`: Response model for label operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### LabelBaseModel

| Attribute   | Type | Required | Default | Description                             |
|-------------|------|----------|---------|-----------------------------------------|
| name        | str  | Yes      | None    | Name of label. Max length: 63 chars     |
| description | str  | No       | None    | Description of the label                |

### LabelCreateModel

Inherits all fields from `LabelBaseModel` without additional fields.

### LabelUpdateModel

Extends `LabelBaseModel` by adding:

| Attribute | Type | Required | Default | Description                         |
|-----------|------|----------|---------|-------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the label  |

### LabelResponseModel

Extends `LabelBaseModel` by adding:

| Attribute | Type | Required | Default | Description                         |
|-----------|------|----------|---------|-------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the label  |

## Exceptions

The Label models can raise the following exceptions during validation:

- **ValueError**: Raised when field validation fails
- **ValidationError**: Raised by Pydantic when model validation fails

## Model Validators

The Label models include validators to ensure data integrity:

- **Name validation**: Ensures the name meets the maximum length requirement of 63 characters
- **ID validation**: Ensures valid UUID format for update and response models

## Usage Examples

### Creating a Label

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
label_data = {
    "name": "environment",
    "description": "Environment classification label"
}

response = client.label.create(label_data)
print(f"Created label: {response.name} with ID: {response.id}")
```

### Updating a Label

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing label
existing = client.label.fetch(name="environment")

# Modify attributes using dot notation
existing.description = "Updated environment classification label"

# Pass modified object to update()
updated = client.label.update(existing)
print(f"Updated label: {updated.name}")
```

### Listing Labels

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List all labels
all_labels = client.label.list()

for label in all_labels:
    print(f"Label: {label.name}")
    print(f"ID: {label.id}")
    print(f"Description: {label.description}")
```

### Fetching a Label by Name

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch label by name
label = client.label.fetch(name="environment")
if label:
    print(f"Found label: {label.name}")
    print(f"ID: {label.id}")
    print(f"Description: {label.description}")
else:
    print("Label not found")
```

