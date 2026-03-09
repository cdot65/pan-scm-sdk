# Tag

The `Tag` service manages tag objects in Strata Cloud Manager, providing color-coded labels for organizing and categorizing resources across security policies.

## Class Overview

The `Tag` class provides CRUD operations for tag objects. It is accessed through the `client.tag` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Tag service
tags = client.tag
```

### Key Attributes

| Attribute  | Type   | Required | Description                            |
|------------|--------|----------|----------------------------------------|
| `name`     | `str`  | Yes      | Name of the tag object (max 127 chars) |
| `id`       | `UUID` | Yes*     | Unique identifier (*response only)     |
| `color`    | `str`  | No       | Color from a predefined list           |
| `comments` | `str`  | No       | Comments (max 1023 chars)              |
| `folder`   | `str`  | Yes**    | Folder location (max 64 chars)         |
| `snippet`  | `str`  | Yes**    | Snippet location (max 64 chars)        |
| `device`   | `str`  | Yes**    | Device location (max 64 chars)         |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Tags

Retrieves a list of tag objects with optional filtering.

```python
tags = client.tag.list(
    folder="Texas",
    colors=["Red", "Blue"]
)

for tag in tags:
    print(f"Name: {tag.name}, Color: {tag.color}")
```

### Fetch a Tag

Retrieves a single tag by name and container.

```python
tag = client.tag.fetch(name="Production", folder="Texas")
print(f"Found tag: {tag.name}, Color: {tag.color}")
```

### Create a Tag

Creates a new tag object.

```python
new_tag = client.tag.create({
    "name": "Production",
    "color": "Red",
    "comments": "Production environment resources",
    "folder": "Texas"
})
```

### Update a Tag

Updates an existing tag object.

```python
existing = client.tag.fetch(name="Production", folder="Texas")
existing.color = "Azure Blue"
existing.comments = "Updated production environment tag"

updated = client.tag.update(existing)
```

### Delete a Tag

Deletes a tag object by ID.

```python
client.tag.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Creating an Environment Tag Set

Define tags for different environments with consistent color coding.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

environments = [
    {"name": "Production", "color": "Red", "comments": "Production resources"},
    {"name": "Development", "color": "Blue", "comments": "Development resources"},
    {"name": "Web-Servers", "color": "Green", "comments": "Web server resources"},
]

for env in environments:
    env["folder"] = "Texas"
    client.tag.create(env)
    print(f"Created tag: {env['name']}")
```

### Filtering Tags

Use advanced filtering to find specific tags.

```python
# Filter by color
red_tags = client.tag.list(
    folder="Texas",
    colors=["Red", "Blue"]
)

# Exact match with exclusions
filtered = client.tag.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"],
    exclude_devices=["DeviceA"],
    colors=["Red"]
)

for tag in filtered:
    print(f"Tag: {tag.name} in {tag.folder}, Color: {tag.color}")
```

### Batch Tag Operations with Commit

Create multiple tags and commit the changes.

```python
tag_names = ["Reviewed", "Approved", "Pending"]

for name in tag_names:
    client.tag.create({
        "name": name,
        "color": "Green",
        "folder": "Texas"
    })

result = client.commit(
    folders=["Texas"],
    description="Added workflow tags",
    sync=True
)
print(f"Commit job ID: {result.job_id}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_tag = client.tag.create({
        "name": "test_tag",
        "color": "Red",
        "folder": "Texas",
        "comments": "Test tag"
    })
except InvalidObjectError as e:
    print(f"Invalid tag data: {e.message}")
except NameNotUniqueError as e:
    print(f"Tag name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Tag not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Tag still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Tag Models](../../models/objects/tag_models.md#Overview)
- [Address](address.md)
- [Address Group](address_group.md)
