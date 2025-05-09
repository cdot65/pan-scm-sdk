# Label Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Label Model Attributes](#label-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Label Objects](#creating-label-objects)
    - [Retrieving Labels](#retrieving-labels)
    - [Updating Labels](#updating-labels)
    - [Listing Labels](#listing-labels)
    - [Deleting Labels](#deleting-labels)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `Label` class provides functionality to manage label objects in Palo Alto Networks' Strata Cloud Manager. This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting label objects.
Labels are simple key-value objects that can be used for resource classification and organization.

## Core Methods

| Method     | Description                     | Parameters                  | Return Type                |
|------------|---------------------------------|-----------------------------|----------------------------|
| `create()` | Creates a new label object      | `data: Dict[str, Any]`      | `LabelResponseModel`       |
| `get()`    | Retrieves a label by ID         | `label_id: str`             | `LabelResponseModel`       |
| `update()` | Updates an existing label       | `label: LabelUpdateModel`   | `LabelResponseModel`       |
| `delete()` | Deletes a label                 | `label_id: str`             | `None`                     |
| `list()`   | Lists labels with filtering     | `**filters`                 | `List[LabelResponseModel]` |
| `fetch()`  | Gets label by name              | `name: str`                 | `Optional[LabelResponseModel]` |

## Label Model Attributes

| Attribute     | Type      | Required | Description                              |
|---------------|-----------|----------|------------------------------------------|
| `name`        | str       | Yes      | Name of label object (max 63 chars)      |
| `id`          | UUID      | Yes*     | Unique identifier (*response only)       |
| `description` | str       | No       | Object description                       |

## Exceptions

| Exception                | HTTP Code | Description                |
|--------------------------|-----------|----------------------------|
| `InvalidObjectError`     | 400       | Invalid label data or format |
| `ObjectNotPresentError`  | 404       | Label not found            |
| `APIError`               | Various   | General API errors         |

## Basic Configuration

The Label service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Label service directly through the client
# No need to create a separate Label instance
labels = client.label
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.setup import Label

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Label object explicitly
labels = Label(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Label Objects

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Prepare label configuration
label_config = {
   "name": "environment",
   "description": "Environment classification label"
}

# Create the label object using the unified client interface
new_label = client.label.create(label_config)
print(f"Created label with ID: {new_label.id}")
```

### Retrieving Labels

```python
# Fetch by name
label = client.label.fetch(name="environment")
print(f"Found label: {label.name}")

# Get by ID
label_by_id = client.label.get(label.id)
print(f"Retrieved label: {label_by_id.name}")
```

### Updating Labels

```python
# Fetch existing label
existing_label = client.label.fetch(name="environment")

# Update specific attributes
existing_label.description = "Updated environment classification label"

# Perform update
updated_label = client.label.update(existing_label)
print(f"Updated label description: {updated_label.description}")
```

### Listing Labels

```python
# List all labels
all_labels = client.label.list()
print(f"Found {len(all_labels)} labels")

# Process results
for label in all_labels:
   print(f"Label: {label.name}, Description: {label.description}")
```

### Deleting Labels

```python
# Delete by ID
label_id = "123e4567-e89b-12d3-a456-426655440000"
client.label.delete(label_id)
print(f"Deleted label with ID: {label_id}")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Added new labels",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
   InvalidObjectError,
   ObjectNotPresentError,
   APIError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create label configuration
   label_config = {
      "name": "test_label",
      "description": "Test label"
   }

   # Create the label using the unified client interface
   new_label = client.label.create(label_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Texas"],
      description="Added test label",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid label data: {e.message}")
except ObjectNotPresentError as e:
   print(f"Label not found: {e.message}")
except APIError as e:
   print(f"API error: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.label`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)

2. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

3. **Performance**
    - Reuse client instances
    - Use appropriate pagination for list operations
    - Implement proper retry mechanisms
    - Cache frequently accessed objects

4. **Security**
    - Follow the least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication handling

## Related Models

- [LabelCreateModel](../../models/setup/label_models.md)
- [LabelUpdateModel](../../models/setup/label_models.md)
- [LabelResponseModel](../../models/setup/label_models.md)