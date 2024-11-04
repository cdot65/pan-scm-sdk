# Address Group Configuration Object

The `AddressGroup` class provides functionality to manage address groups in Palo Alto Networks' Strata Cloud Manager.
Address
groups can be used to organize and manage collections of addresses either statically (by explicitly listing addresses)
or
dynamically (using tag-based filters).

## Overview

Address groups are essential components in network security policy management, allowing you to:

- Create static groups with explicit lists of addresses
- Define dynamic groups that automatically update based on tag filters
- Organize addresses within folders, snippets, or devices
- Apply tags for better organization and management

## Methods

| Method     | Description                                  |
|------------|----------------------------------------------|
| `create()` | Creates a new address group                  |
| `get()`    | Retrieves an address group by ID             |
| `update()` | Updates an existing address group            |
| `delete()` | Deletes an address group                     |
| `list()`   | Lists address groups with optional filtering |
| `fetch()`  | Retrieves a single address group by name     |

## Creating Address Groups

The `create()` method allows you to create new address groups. You must specify either a static list of addresses or a
dynamic filter, along with exactly one container type (folder, snippet, or device).

**Example: Creating a Static Address Group**

<div class="termy">

<!-- termynal -->

```python
static_group = {
    "name": "web_servers",
    "description": "Web server group",
    "static": ["web1", "web2", "web3"],
    "folder": "Shared",
    "tag": ["production", "web"]
}

new_group = address_group.create(static_group)
print(f"Created group: {new_group['name']}")
```

</div>

**Example: Creating a Dynamic Address Group**

<div class="termy">

<!-- termynal -->

```python
dynamic_group = {
    "name": "prod_servers",
    "description": "Production servers",
    "dynamic": {
        "filter": "'production' and 'server'"
    },
    "folder": "Shared",
    "tag": ["production"]
}

new_group = address_group.create(dynamic_group)
print(f"Created group: {new_group['name']}")
```

</div>

## Getting Address Groups

Use the `get()` method to retrieve an address group by its ID.

<div class="termy">

<!-- termynal -->

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
group = address_group.get(group_id)
print(f"Group Name: {group['name']}")
print(f"Type: {'Dynamic' if 'dynamic' in group else 'Static'}")
```

</div>

## Updating Address Groups

The `update()` method allows you to modify existing address groups.

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "description": "Updated server group",
    "tag": ["production", "updated"]
}

updated_group = address_group.update(update_data)
print(f"Updated group: {updated_group['name']}")
```

</div>

## Deleting Address Groups

Use the `delete()` method to remove an address group.

<div class="termy">

<!-- termynal -->

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
address_group.delete(group_id)
print("Group deleted successfully")
```

</div>

## Listing Address Groups

The `list()` method retrieves multiple address groups with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all groups in a folder with specific tags
groups = address_group.list(
    folder="Shared",
    tags=["production"]
)

for group in groups:
    print(f"Name: {group['name']}")
    print(f"Type: {'Dynamic' if 'dynamic' in group else 'Static'}")
```

</div>

## Fetching Address Groups

The `fetch()` method retrieves a single address group by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
group = address_group.fetch(
    name="web_servers",
    folder="Shared"
)
print(f"Found group: {group['name']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an address group:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import AddressGroup

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize address group object
address_group = AddressGroup(client)

# Create a new static group
static_group = {
    "name": "app_servers",
    "description": "Application servers",
    "static": ["app1", "app2"],
    "folder": "Shared",
    "tag": ["production"]
}

new_group = address_group.create(static_group)
print(f"Created group: {new_group['name']}")

# Fetch the group by name
fetched_group = address_group.fetch(
    name="app_servers",
    folder="Shared"
)

# Modify the fetched group
fetched_group["description"] = "Updated application servers"
fetched_group["tag"] = ["production", "updated"]

# Update the group
updated_group = address_group.update(fetched_group)
print(f"Updated group description: {updated_group['description']}")

# List all groups
groups = address_group.list(folder="Shared")
for group in groups:
    print(f"Listed group: {group['name']}")

# Clean up
address_group.delete(new_group['id'])
print("Group deleted successfully")
```

</div>

## Related Models

- [AddressGroupCreateModel](../../models/objects/address_group_models.md#addressgroupcreatemodel)
- [AddressGroupUpdateModel](../../models/objects/address_group_models.md#addressgroupupdatemodel)
- [AddressGroupResponseModel](../../models/objects/address_group_models.md#addressgroupresponsemodel)