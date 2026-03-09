# Address Group

The `AddressGroup` service manages address group objects in Strata Cloud Manager, supporting static groups with explicit member lists and dynamic groups with tag-based filters.

## Class Overview

The `AddressGroup` class provides CRUD operations for address group objects. It is accessed through the `client.address_group` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the AddressGroup service
address_groups = client.address_group
```

### Key Attributes

| Attribute     | Type            | Required     | Description                                |
|---------------|-----------------|--------------|--------------------------------------------|
| `name`        | `str`           | Yes          | Name of group (max 63 chars)               |
| `id`          | `UUID`          | Yes*         | Unique identifier (*response only)         |
| `static`      | `List[str]`     | One Required | List of static addresses                   |
| `dynamic`     | `DynamicFilter` | One Required | Tag-based filter for dynamic membership    |
| `description` | `str`           | No           | Object description (max 1023 chars)        |
| `tag`         | `List[str]`     | No           | List of tags (max 127 chars each)          |
| `folder`      | `str`           | Yes**        | Folder location (**one container required) |
| `snippet`     | `str`           | Yes**        | Snippet location (**one container required)|
| `device`      | `str`           | Yes**        | Device location (**one container required) |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Address Groups

Retrieves a list of address group objects with optional filtering.

```python
groups = client.address_group.list(
    folder="Texas",
    types=["static"],
    tags=["Production"]
)

for group in groups:
    print(f"Name: {group.name}")
    if group.static:
        print(f"Members: {', '.join(group.static)}")
```

### Fetch an Address Group

Retrieves a single address group by name and container.

```python
group = client.address_group.fetch(name="web_servers", folder="Texas")
print(f"Found group: {group.name}")
```

### Create an Address Group

Creates a new address group object.

```python
# Static group
static_group = client.address_group.create({
    "name": "web_servers",
    "static": ["webserver", "prod-server"],
    "description": "Web server group",
    "folder": "Texas",
    "tag": ["Production", "Web"]
})

# Dynamic group
dynamic_group = client.address_group.create({
    "name": "python_servers",
    "dynamic": {"filter": "'Python' and 'Production'"},
    "description": "Python production servers",
    "folder": "Texas"
})
```

### Update an Address Group

Updates an existing address group object.

```python
existing = client.address_group.fetch(name="web_servers", folder="Texas")
existing.static = ["webserver", "prod-server", "staging-server"]
existing.description = "Updated web server group"

updated = client.address_group.update(existing)
```

### Delete an Address Group

Deletes an address group object by ID.

```python
client.address_group.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Managing Static and Dynamic Groups

Create both types of groups for different use cases.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Static group for known servers
client.address_group.create({
    "name": "database_servers",
    "static": ["db-primary", "db-replica-1", "db-replica-2"],
    "folder": "Texas",
    "tag": ["Database", "Production"]
})

# Dynamic group that auto-updates based on tags
client.address_group.create({
    "name": "all_production",
    "dynamic": {"filter": "'Production'"},
    "folder": "Texas",
    "description": "All production-tagged addresses"
})
```

### Filtering Address Groups

Use advanced filtering to find specific groups.

```python
# Only return groups defined exactly in 'Texas'
exact = client.address_group.list(
    folder="Texas",
    exact_match=True
)

# Combine filters
combined = client.address_group.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"]
)

for group in combined:
    print(f"Group: {group.name} in {group.folder}")
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
    new_group = client.address_group.create({
        "name": "test_group",
        "static": ["server1", "server2"],
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

- [Address Group Models](../../models/objects/address_group_models.md#Overview)
- [Address](address.md)
- [Tag](tag.md)
