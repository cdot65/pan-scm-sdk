# Application Group Configuration Object

The `ApplicationGroup` class is used to manage application groups in the Strata Cloud Manager.

---

## Importing the ApplicationGroup Class

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import ApplicationGroup

# create a SCM session
api_client = Scm(
    client_id="example",
    client_secret="example",
    tsg_id="example"
)

# pass SCM session into the ApplicationGroup object
application_group = ApplicationGroup(api_client)
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> ApplicationGroupResponseModel`

Creates a new application group.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the application group data.

**Example 1: Creating a static application group**

<div class="termy">

<!-- termynal -->

```python
static_group_data = {
    "name": "static-app-group",
    "folder": "Prisma Access",
    "members": ["office365-consumer-access", "office365-enterprise-access"],
}

new_static_group = application_group.create(static_group_data)
print(f"Created static application group with ID: {new_static_group.id}")
```

</div>

**Example 2: Creating a dynamic application group**

<div class="termy">

<!-- termynal -->

```python
dynamic_group_data = {
    "name": "dynamic-app-group",
    "folder": "Prisma Access",
    "dynamic": {"filter": "'aws.ec2.tag.AppType' eq 'web'"},
}

new_dynamic_group = application_group.create(dynamic_group_data)
print(f"Created dynamic application group with ID: {new_dynamic_group.id}")
```

</div>

### `get(object_id: str) -> ApplicationGroupResponseModel`

Retrieves an application group by its ID.

**Parameters:**

- `object_id` (str): The UUID of the application group.

**Example:**

<div class="termy">

<!-- termynal -->

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
group_object = application_group.get(group_id)
print(f"Application Group Name: {group_object.name}")
print(f"Members: {group_object.members}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> ApplicationGroupResponseModel`

Updates an existing application group.

**Parameters:**

- `object_id` (str): The UUID of the application group.
- `data` (Dict[str, Any]): A dictionary containing the updated application group data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "name": "updated-app-group",
    "folder": "Prisma Access",
    "members": ["updated-app-1", "updated-app-2"],
}

updated_group = application_group.update(group_id, update_data)
print(f"Updated application group with ID: {updated_group.id}")
print(f"New name: {updated_group.name}")
print(f"New members: {updated_group.members}")
```

</div>

### `delete(object_id: str) -> None`

Deletes an application group by its ID.

**Parameters:**

- `object_id` (str): The UUID of the application group.

**Example:**

<div class="termy">

<!-- termynal -->

```python
group_id_to_delete = "123e4567-e89b-12d3-a456-426655440000"
application_group.delete(group_id_to_delete)
print(f"Deleted application group with ID: {group_id_to_delete}")
```

</div>

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[ApplicationGroupResponseModel]`

Lists application groups, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list application groups from.
- `snippet` (Optional[str]): The snippet to list application groups from.
- `device` (Optional[str]): The device to list application groups from.
- `**filters`: Additional filters.

**Example 1: Listing all application groups in a folder**

<div class="termy">

<!-- termynal -->

```python
groups = application_group.list(folder='Prisma Access')

for group in groups:
    print(f"Application Group Name: {group.name}, Members: {group.members}")
```

</div>

**Example 2: Listing application groups with specific names**

<div class="termy">

<!-- termynal -->

```python
groups = application_group.list(folder='Prisma Access', names=['web-apps', 'db-apps'])

for group in groups:
    print(f"Application Group Name: {group.name}, Members: {group.members}")
```

</div>

---

## Full Usage Example

Here's a comprehensive example that demonstrates creating, retrieving, updating, and deleting an application group:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import ApplicationGroup

# Initialize the SCM client
api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an ApplicationGroup instance
application_group = ApplicationGroup(api_client)

# Create a new application group
new_group_data = {
    "name": "example-app-group",
    "folder": "Prisma Access",
    "members": ["app1", "app2", "app3"]
}

new_group = application_group.create(new_group_data)
print(f"Created application group with ID: {new_group.id}")

# Retrieve the created group
retrieved_group = application_group.get(new_group.id)
print(f"Retrieved group name: {retrieved_group.name}")
print(f"Retrieved group members: {retrieved_group.members}")

# Update the group
update_data = {
    "name": "updated-app-group",
    "folder": "Prisma Access",
    "members": ["app1", "app2", "app3", "app4"]
}

updated_group = application_group.update(new_group.id, update_data)
print(f"Updated group name: {updated_group.name}")
print(f"Updated group members: {updated_group.members}")

# List all groups in the folder
all_groups = application_group.list(folder="Prisma Access")
print("All groups in Prisma Access folder:")
for group in all_groups:
    print(f"- {group.name}")

# Delete the group
application_group.delete(new_group.id)
print(f"Deleted application group with ID: {new_group.id}")
```

</div>

---

## Related Models

- [ApplicationGroupRequestModel](../../models/objects/application_group_models.md#applicationgrouprequestmodel)
- [ApplicationGroupResponseModel](../../models/objects/application_group_models.md#applicationgroupresponsemodel)