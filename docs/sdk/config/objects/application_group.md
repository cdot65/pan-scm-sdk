# Application Group Configuration Object

The `ApplicationGroup` class provides functionality to manage application groups in Palo Alto Networks' Strata Cloud
Manager.
Application groups allow you to organize and manage collections of applications for use in security policies and other
configurations.

## Overview

Application groups in Strata Cloud Manager allow you to:

- Group multiple applications together for easier management
- Create static groups with explicit lists of applications
- Organize application groups within folders, snippets, or devices
- Reference groups in security policies and other configurations
- Fetch and manage groups by name or ID

## Methods

| Method     | Description                                      |
|------------|--------------------------------------------------|
| `create()` | Creates a new application group                  |
| `get()`    | Retrieves an application group by ID             |
| `update()` | Updates an existing application group            |
| `delete()` | Deletes an application group                     |
| `list()`   | Lists application groups with optional filtering |
| `fetch()`  | Retrieves a single application group by name     |

## Creating Application Groups

The `create()` method allows you to create new application groups. You must specify a name, members list, and exactly
one
container type (folder, snippet, or device).

**Example: Creating an Application Group**

<div class="termy">

<!-- termynal -->

```python
group_data = {
    "name": "web-apps",
    "members": ["http", "https", "web-browsing"],
    "folder": "Shared",
}

new_group = application_group.create(group_data)
print(f"Created group: {new_group['name']}")
```

</div>

## Getting Application Groups

Use the `get()` method to retrieve an application group by its ID.

<div class="termy">

<!-- termynal -->

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
group = application_group.get(group_id)
print(f"Group Name: {group['name']}")
print(f"Members: {group['members']}")
```

</div>

## Updating Application Groups

The `update()` method allows you to modify existing application groups.

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "updated-web-apps",
    "members": ["http", "https", "web-browsing", "ssl"],
    "folder": "Shared"
}

updated_group = application_group.update(update_data)
print(f"Updated group: {updated_group['name']}")
```

</div>

## Deleting Application Groups

Use the `delete()` method to remove an application group.

<div class="termy">

<!-- termynal -->

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
application_group.delete(group_id)
print("Group deleted successfully")
```

</div>

## Listing Application Groups

The `list()` method retrieves multiple application groups with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all groups in a folder
groups = application_group.list(folder="Shared")
for group in groups:
    print(f"Name: {group['name']}, Members: {group['members']}")

# List groups with specific names
filtered_groups = application_group.list(
    folder="Shared",
    names=["web-apps", "db-apps"]
)
for group in filtered_groups:
    print(f"Filtered group: {group['name']}")
```

</div>

## Fetching Application Groups

The `fetch()` method retrieves a single application group by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
group = application_group.fetch(
    name="web-apps",
    folder="Shared"
)
print(f"Found group: {group['name']}")
print(f"Current members: {group['members']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an application group:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import ApplicationGroup

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize application group object
application_group = ApplicationGroup(client)

# Create new group
create_data = {
    "name": "test-apps",
    "members": ["http", "https"],
    "folder": "Shared"
}

new_group = application_group.create(create_data)
print(f"Created group: {new_group['name']}")

# Fetch the group by name
fetched_group = application_group.fetch(
    name="test-apps",
    folder="Shared"
)

# Modify the fetched group
fetched_group["members"] = ["http", "https", "ssl"]

# Update using the modified object
updated_group = application_group.update(fetched_group)
print(f"Updated group: {updated_group['name']}")
print(f"New members: {updated_group['members']}")

# List all groups
groups = application_group.list(folder="Shared")
for group in groups:
    print(f"Listed group: {group['name']}")

# Clean up
application_group.delete(new_group['id'])
print("Group deleted successfully")
```

</div>

## Related Models

- [ApplicationGroupCreateModel](../../models/objects/application_group_models.md#applicationgroupcreatemodel)
- [ApplicationGroupUpdateModel](../../models/objects/application_group_models.md#applicationgroupupdatemodel)
- [ApplicationGroupResponseModel](../../models/objects/application_group_models.md#applicationgroupresponsemodel)