# Dynamic User Group

The `DynamicUserGroup` service manages dynamic user group objects in Strata Cloud Manager, enabling user-based policies and filtering through tag-based membership expressions.

## Class Overview

The `DynamicUserGroup` class provides CRUD operations for dynamic user group objects. It is accessed through the `client.dynamic_user_group` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the DynamicUserGroup service
dugs = client.dynamic_user_group
```

### Key Attributes

| Attribute     | Type        | Required | Description                                          |
|---------------|-------------|----------|------------------------------------------------------|
| `name`        | `str`       | Yes      | Name of dynamic user group (max 63 chars)            |
| `id`          | `UUID`      | Yes*     | Unique identifier (*response only)                   |
| `filter`      | `str`       | Yes      | Filter expression for matching users (max 2047 chars)|
| `description` | `str`       | No       | Object description (max 1023 chars)                  |
| `tag`         | `List[str]` | No       | List of tags (each max 127 chars)                    |
| `folder`      | `str`       | Yes**    | Folder location (**one container required)           |
| `snippet`     | `str`       | Yes**    | Snippet location (**one container required)          |
| `device`      | `str`       | Yes**    | Device location (**one container required)           |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Dynamic User Groups

Retrieves a list of dynamic user group objects with optional filtering.

```python
dugs = client.dynamic_user_group.list(
    folder="Texas",
    tags=["Automation"]
)

for dug in dugs:
    print(f"Name: {dug.name}, Filter: {dug.filter}")
```

### Fetch a Dynamic User Group

Retrieves a single dynamic user group by name and container.

```python
dug = client.dynamic_user_group.fetch(
    name="high_risk_users",
    folder="Texas"
)
print(f"Found group: {dug.name}")
```

### Create a Dynamic User Group

Creates a new dynamic user group object.

```python
new_dug = client.dynamic_user_group.create({
    "name": "high_risk_users",
    "filter": "tag.criticality.high",
    "description": "Users with high risk classification",
    "folder": "Texas",
    "tag": ["RiskManagement", "Automation"]
})
```

### Update a Dynamic User Group

Updates an existing dynamic user group.

```python
existing = client.dynamic_user_group.fetch(
    name="high_risk_users",
    folder="Texas"
)
existing.filter = "tag.criticality.high or tag.risk_score.gt.80"
existing.description = "Users with high risk assessment score"

updated = client.dynamic_user_group.update(existing)
```

### Delete a Dynamic User Group

Deletes a dynamic user group by ID.

```python
client.dynamic_user_group.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Role-Based User Groups

Create dynamic groups for different organizational roles.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# High-risk users
client.dynamic_user_group.create({
    "name": "high_risk_users",
    "filter": "tag.criticality.high",
    "folder": "Texas",
    "description": "Users with high risk classification",
    "tag": ["RiskManagement"]
})

# External contractors
client.dynamic_user_group.create({
    "name": "external_contractors",
    "filter": "tag.user_type.contractor",
    "folder": "Texas",
    "description": "All external contractor accounts"
})
```

### Filtering Dynamic User Groups

Use advanced filtering to narrow results.

```python
# Exact match with exclusions
filtered = client.dynamic_user_group.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"],
    exclude_devices=["DeviceA"]
)

for dug in filtered:
    print(f"Group: {dug.name} in {dug.folder}")
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError
)

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_dug = client.dynamic_user_group.create({
        "name": "test_group",
        "filter": "tag.department.it",
        "folder": "Texas",
        "description": "IT department users"
    })
except InvalidObjectError as e:
    print(f"Invalid data: {e.message}")
except NameNotUniqueError as e:
    print(f"Name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Dynamic User Group Models](../../models/objects/dynamic_user_group_models.md#Overview)
- [Tag](tag.md)
