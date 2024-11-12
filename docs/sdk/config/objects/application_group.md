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
    "members": ["ssl", "web-browsing"],
    "folder": "Texas",
}

new_group = application_groups.create(group_data)
print(f"Created group: {new_group.name}")
```

</div>

## Getting Application Groups

Use the `get()` method to retrieve an application group by its ID.

<div class="termy">

<!-- termynal -->

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
group = application_groups.get(group_id)
print(f"Group Name: {group.name}")
print(f"Members: {group.members}")
```

</div>

## Updating Application Groups

The `update()` method allows you to modify existing application groups.

<div class="termy">

<!-- termynal -->

```python
web_apps = application_groups.fetch(folder='Texas', name='web-apps')
web_apps['members'] = ['ssl', 'web-browsing', 'dns-base']

updated_group = application_groups.update(web_apps)
print(f"Updated group: {updated_group.name}")
```

</div>

## Deleting Application Groups

Use the `delete()` method to remove an application group.

<div class="termy">

<!-- termynal -->

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
application_groups.delete(group_id)
print("Group deleted successfully")
```

</div>

## Listing Application Groups

The `list()` method retrieves multiple application groups with optional filtering. You can filter the results using the
following kwargs:

- `members`: List[str] - Filter by member applications (e.g., ['ssl', 'web-browsing'])

<div class="termy">

<!-- termynal -->

```python
# List all groups in a folder
groups = application_groups.list(folder="Texas")

# List groups containing specific members
ssl_groups = application_groups.list(
    folder="Texas",
    members=['ssl']
)

# List groups with multiple member matches
web_groups = application_groups.list(
    folder="Texas",
    members=['ssl', 'web-browsing']
)

# Print the results
for group in groups:
    print(f"Name: {group.name}, Members: {group.members}")
```

</div>

## Fetching Application Groups

The `fetch()` method retrieves a single application group by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
group = application_groups.fetch(
    name="web-apps",
    folder="Texas"
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
application_groups = ApplicationGroup(client)

# Create new group
group_data = {
    "name": "web-apps",
    "members": ["ssl", "web-browsing"],
    "folder": "Texas",
}

new_group = application_groups.create(group_data)
print(f"Created group: {new_group.name}")

# Fetch the group by name
fetched_group = application_groups.fetch(
    name="web-apps",
    folder="Texas"
)

# Modify the fetched group
fetched_group["members"] = ['ssl', 'web-browsing', 'dns-base']

# Update using the modified object
updated_group = application_groups.update(fetched_group)
print(f"Updated group: {updated_group.name}")
print(f"New members: {updated_group.members}")

# List all groups
groups = application_groups.list(folder="Texas")
for group in groups:
    print(f"Listed group: {group.name}")

# Clean up
application_groups.delete(new_group.id)
print("Group deleted successfully")
```

</div>

## Related Models

- [ApplicationGroupCreateModel](../../models/objects/application_group_models.md#applicationgroupcreatemodel)
- [ApplicationGroupUpdateModel](../../models/objects/application_group_models.md#applicationgroupupdatemodel)
- [ApplicationGroupResponseModel](../../models/objects/application_group_models.md#applicationgroupresponsemodel)