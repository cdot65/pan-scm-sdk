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
    "static": ["example_website", "webserver_network"],
    "folder": "Texas",
    "tag": ["Python", "Automation"]
}

new_group = address_groups.create(static_group)
print(f"Created group: {new_group.name}")
```

</div>

**Example: Creating a Dynamic Address Group**

<div class="termy">

<!-- termynal -->

```python
dynamic_group = {
    "name": "python servers",
    "description": "Python-based automation servers",
    "dynamic": {
        "filter": "'Python'"
    },
    "folder": "Texas",
    "tag": ["Automation"]
}

new_group = address_groups.create(dynamic_group)
print(f"Created group: {new_group.name}")
```

</div>

## Getting Address Groups

Use the `get()` method to retrieve an address group by its ID.

<div class="termy">

<!-- termynal -->

```python
group_id = "d4d09614-55a3-4a94-911b-f1bbda353ca6"
group = address_groups.get(group_id)
print(f"Group Name: {group.name}")
print(f"Type: {'Dynamic' if 'dynamic' in group else 'Static'}")
```

</div>

## Updating Address Groups

The `update()` method allows you to modify existing address groups.

<div class="termy">

<!-- termynal -->

```python
# return an existing group
python_server_group = address_groups.fetch(folder='Texas', name='python servers')

# perform the update
python_server_group['description'] = 'updated description'

# push changes to the SCM API
updated_group = address_groups.update(python_server_group)

print(f"Updated group: {updated_group.name}")
```

</div>

## Deleting Address Groups

Use the `delete()` method to remove an address group.

<div class="termy">

<!-- termynal -->

```python
group_id = "d4d09614-55a3-4a94-911b-f1bbda353ca6"
address_groups.delete(group_id)
print("Group deleted successfully")
```

</div>

## Listing Address Groups

The `list()` method retrieves multiple address groups with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all groups in a folder
groups = address_groups.list(folder="Texas")

for group in groups:
    print(f"Name: {group.name}")
    print(f"Type: {'Dynamic' if 'dynamic' in group else 'Static'}")
```

</div>

## Fetching Address Groups

The `fetch()` method retrieves a single address group by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
# pass in the folder and name required parameters, will return a dictionary object
dag_group = address_groups.fetch(folder='Texas', name='DAG_test')

# print out the name of the group to the screen
print(f"Found group: {dag_group['name']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an address group:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address, AddressGroup

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize address and address group objects
addresses = Address(client)
address_groups = AddressGroup(client)

# Create address object `test_network1`
ao1 = {
    "name": "test_network1",
    "ip_netmask": "10.0.0.0/24",
    "description": "Test network",
    "folder": "Texas",
    "tag": ["Automation"]
}
test_network1 = addresses.create(ao1)

# Create address object `test_network2`
ao2 = {
    "name": "test_network2",
    "ip_netmask": "10.0.1.0/24",
    "description": "Test network",
    "folder": "Texas",
    "tag": ["Automation"]
}
test_network2 = addresses.create(ao2)

# Create a new static group
test_network_group = {
    "name": "test_network_group",
    "description": "Test networks",
    "static": [test_network1.name, test_network2.name],
    "folder": "Texas",
    "tag": ["Automation"]
}

new_group = address_groups.create(test_network_group)
print(f"Created group: {new_group.name}")

# Fetch the group by name
fetched_group = address_groups.fetch(
    name="test_network_group",
    folder="Texas"
)

# Modify the fetched group
fetched_group["description"] = "Updated test networks"
fetched_group["tag"] = ["Automation"]

# Update the group
address_groups.update(fetched_group)

# List all groups
groups = address_groups.list(folder="Texas")
for group in groups:
    print(f"Listed group: {group.name}")

# Clean up
address_groups.delete(new_group.id)
print("Group deleted successfully")
```

</div>

## Related Models

- [AddressGroupCreateModel](../../models/objects/address_group_models.md#addressgroupcreatemodel)
- [AddressGroupUpdateModel](../../models/objects/address_group_models.md#addressgroupupdatemodel)
- [AddressGroupResponseModel](../../models/objects/address_group_models.md#addressgroupresponsemodel)