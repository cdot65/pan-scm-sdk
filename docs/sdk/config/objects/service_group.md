# Service Group

The `ServiceGroup` service manages service group objects in Strata Cloud Manager, organizing collections of services for use in security policies and NAT rules.

## Class Overview

The `ServiceGroup` class provides CRUD operations for service group objects. It is accessed through the `client.service_group` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the ServiceGroup service
service_groups = client.service_group
```

### Key Attributes

| Attribute | Type        | Required | Description                                |
|-----------|-------------|----------|--------------------------------------------|
| `name`    | `str`       | Yes      | Name of group (max 63 chars)               |
| `id`      | `UUID`      | Yes*     | Unique identifier (*response only)         |
| `members` | `List[str]` | Yes      | List of service members (1-1024 items)     |
| `tag`     | `List[str]` | No       | List of tags                               |
| `folder`  | `str`       | Yes**    | Folder location (**one container required) |
| `snippet` | `str`       | Yes**    | Snippet location (**one container required)|
| `device`  | `str`       | Yes**    | Device location (**one container required) |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Service Groups

Retrieves a list of service group objects with optional filtering.

```python
groups = client.service_group.list(
    folder="Texas",
    values=["HTTP", "HTTPS"],
    tags=["Production"]
)

for group in groups:
    print(f"Name: {group.name}, Members: {', '.join(group.members)}")
```

### Fetch a Service Group

Retrieves a single service group by name and container.

```python
group = client.service_group.fetch(name="web-services", folder="Texas")
print(f"Found group: {group.name}")
```

### Create a Service Group

Creates a new service group object.

```python
new_group = client.service_group.create({
    "name": "web-services",
    "members": ["HTTP", "HTTPS"],
    "folder": "Texas",
    "tag": ["Web"]
})
```

### Update a Service Group

Updates an existing service group.

```python
existing = client.service_group.fetch(name="web-services", folder="Texas")
existing.members = ["HTTP", "HTTPS", "HTTP-8080"]
existing.tag = ["Web", "Updated"]

updated = client.service_group.update(existing)
```

### Delete a Service Group

Deletes a service group by ID.

```python
client.service_group.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Organizing Services by Function

Group related services for simplified policy management.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Web services group
client.service_group.create({
    "name": "web-services",
    "members": ["HTTP", "HTTPS"],
    "folder": "Texas",
    "tag": ["Web"]
})

# Application services group
client.service_group.create({
    "name": "app-services",
    "members": ["HTTP", "HTTPS", "SSH", "FTP"],
    "folder": "Texas",
    "tag": ["Application", "Production"]
})
```

### Filtering Service Groups

Use advanced filtering to find specific groups.

```python
# Exact match with exclusions
filtered = client.service_group.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"],
    exclude_devices=["DeviceA"]
)

for group in filtered:
    print(f"Group: {group.name} in {group.folder}")
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_group = client.service_group.create({
        "name": "test-group",
        "members": ["HTTP", "HTTPS"],
        "folder": "Texas",
        "tag": ["Test"]
    })
except InvalidObjectError as e:
    print(f"Invalid group data: {e.message}")
except NameNotUniqueError as e:
    print(f"Group name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Group not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Group still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Service Group Models](../../models/objects/service_group_models.md#Overview)
- [Service](service.md)
