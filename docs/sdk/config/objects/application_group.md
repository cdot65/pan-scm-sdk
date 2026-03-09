# Application Group

The `ApplicationGroup` service manages application group objects in Strata Cloud Manager, organizing collections of applications for use in security policies.

## Class Overview

The `ApplicationGroup` class provides CRUD operations for application group objects. It is accessed through the `client.application_group` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the ApplicationGroup service
app_groups = client.application_group
```

### Key Attributes

| Attribute | Type        | Required | Description                                         |
|-----------|-------------|----------|-----------------------------------------------------|
| `name`    | `str`       | Yes      | Name of group (max 31 chars)                        |
| `id`      | `UUID`      | Yes*     | Unique identifier (*response only)                  |
| `members` | `List[str]` | Yes      | List of application names (min 1, max 1024 entries) |
| `folder`  | `str`       | Yes**    | Folder location (**one container required)          |
| `snippet` | `str`       | Yes**    | Snippet location (**one container required)         |
| `device`  | `str`       | Yes**    | Device location (**one container required)          |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Application Groups

Retrieves a list of application group objects with optional filtering.

```python
groups = client.application_group.list(
    folder="Texas",
    members=["ssl"]
)

for group in groups:
    print(f"Name: {group.name}, Members: {', '.join(group.members)}")
```

### Fetch an Application Group

Retrieves a single application group by name and container.

```python
group = client.application_group.fetch(name="web-apps", folder="Texas")
print(f"Found group: {group.name}")
```

### Create an Application Group

Creates a new application group.

```python
new_group = client.application_group.create({
    "name": "web-apps",
    "members": ["ssl", "web-browsing"],
    "folder": "Texas"
})
```

### Update an Application Group

Updates an existing application group.

```python
existing = client.application_group.fetch(name="web-apps", folder="Texas")
existing.members = ["ssl", "web-browsing", "dns"]

updated = client.application_group.update(existing)
```

### Delete an Application Group

Deletes an application group by ID.

```python
client.application_group.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Organizing Applications by Function

Group related applications for simplified policy management.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Microsoft 365 application group
client.application_group.create({
    "name": "microsoft-365",
    "members": [
        "ms-office365",
        "ms-exchange-online",
        "ms-sharepoint-online"
    ],
    "folder": "Texas"
})

# Basic web applications group
client.application_group.create({
    "name": "web-basics",
    "members": ["ssl", "web-browsing", "dns"],
    "folder": "Texas"
})
```

### Filtering Application Groups

Use advanced filtering to find specific groups.

```python
# Exact match with exclusions
filtered = client.application_group.list(
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
    new_group = client.application_group.create({
        "name": "test_group",
        "members": ["ssl", "web-browsing"],
        "folder": "Texas"
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

- [Application Group Models](../../models/objects/application_group_models.md#Overview)
- [Application](application.md)
- [Application Filters](application_filters.md)
