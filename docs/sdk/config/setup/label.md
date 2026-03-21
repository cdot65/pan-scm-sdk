# Label Configuration Object

Manages label objects for resource classification and organization in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `Label` class inherits from `BaseObject` and provides CRUD operations for label objects used for resource classification.

### Methods

| Method     | Description                 | Parameters                                           | Return Type                |
|------------|-----------------------------|------------------------------------------------------|----------------------------|
| `create()` | Creates a new label object  | `data: Dict[str, Any]`                               | `LabelResponseModel`       |
| `get()`    | Retrieves a label by ID     | `label_id: Union[str, UUID]`                         | `LabelResponseModel`       |
| `update()` | Updates an existing label   | `label: Union[LabelUpdateModel, LabelResponseModel]` | `LabelResponseModel`       |
| `delete()` | Deletes a label             | `label_id: Union[str, UUID]`                         | `None`                     |
| `list()`   | Lists labels with filtering | `**filters`                                          | `List[LabelResponseModel]` |
| `fetch()`  | Gets label by name          | `name: str`                                          | `LabelResponseModel`       |

### Model Attributes

| Attribute     | Type | Required | Default | Description                                |
|---------------|------|----------|---------|--------------------------------------------|
| `name`        | str  | Yes      | None    | Name of label object. Max length: 63 chars |
| `id`          | UUID | Yes*     | None    | Unique identifier (*response/update only)  |
| `description` | str  | No       | None    | Object description                         |

\* Only required for response and update models

### Exceptions

| Exception              | HTTP Code | Description                  |
|------------------------|-----------|------------------------------|
| `InvalidObjectError`   | 400       | Invalid label data or format |
| `ObjectNotPresentError`| 404       | Label not found              |
| `APIError`             | Various   | General API errors           |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

labels = client.label
```

## Methods

### List Labels

```python
all_labels = client.label.list()

for label in all_labels:
    print(f"Label: {label.name}, Description: {label.description}")
```

**Controlling pagination with max_limit:**

```python
client.label.max_limit = 100

all_labels = client.label.list()
```

### Fetch a Label

```python
label = client.label.fetch(name="environment")
if label:
    print(f"Found label: {label.name}, ID: {label.id}")
```

### Create a Label

```python
label_config = {
    "name": "environment",
    "description": "Environment classification label"
}
new_label = client.label.create(label_config)
print(f"Created label with ID: {new_label.id}")
```

### Update a Label

```python
existing_label = client.label.fetch(name="environment")

existing_label.description = "Updated environment classification label"

updated_label = client.label.update(existing_label)
```

### Delete a Label

```python
client.label.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a Label by ID

```python
label = client.label.get("123e4567-e89b-12d3-a456-426655440000")
print(f"Retrieved label: {label.name}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Added new labels",
    sync=True,
    timeout=300
)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    ObjectNotPresentError,
    APIError
)

try:
    label_config = {
        "name": "test_label",
        "description": "Test label"
    }
    new_label = client.label.create(label_config)
    result = client.commit(
        folders=["Texas"],
        description="Added test label",
        sync=True
    )
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid label data: {e.message}")
except ObjectNotPresentError as e:
    print(f"Label not found: {e.message}")
except APIError as e:
    print(f"API error: {e.message}")
```

## Related Topics

- [Label Models](../../models/setup/label_models.md#Overview)
- [Setup Overview](index.md)
- [API Client](../../client.md)
