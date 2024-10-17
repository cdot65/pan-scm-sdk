# Address Group Configuration Object

The `AddressGroup` class is used to manage address groups in the Strata Cloud Manager. Address groups can be either
static (containing a list of addresses) or dynamic (using a tag-based filter).

---

## Importing the AddressGroup Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.objects import AddressGroup
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> AddressGroupResponseModel`

Creates a new address group.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the address group data.

**Example 1 (Static Group):**

<div class="termy">

<!-- termynal -->

```python
address_group_data = {
    "name": "example-static-group",
    "description": "This is a static address group",
    "static": ["server1", "server2", "server3"],
    "folder": "Prisma Access",
}

new_address_group = address_group.create(address_group_data)
print(f"Created static address group with ID: {new_address_group.id}")
```

</div>

**Example 2 (Dynamic Group):**

<div class="termy">

<!-- termynal -->

```python
address_group_data = {
    "name": "example-dynamic-group",
    "description": "This is a dynamic address group",
    "dynamic": {
        "filter": "'aws-tag' and 'production'"
    },
    "folder": "Prisma Access",
}

new_address_group = address_group.create(address_group_data)
print(f"Created dynamic address group with ID: {new_address_group.id}")
```

</div>

### `get(object_id: str) -> AddressGroupResponseModel`

Retrieves an address group by its ID.

**Parameters:**

- `object_id` (str): The UUID of the address group.

**Example:**

<div class="termy">

<!-- termynal -->

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
group_object = address_group.get(group_id)
print(f"Address Group Name: {group_object.name}")
print(f"Address Group Type: {'Dynamic' if group_object.dynamic else 'Static'}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> AddressGroupResponseModel`

Updates an existing address group.

**Parameters:**

- `object_id` (str): The UUID of the address group.
- `data` (Dict[str, Any]): A dictionary containing the updated address group data.

**Example 3 (Updating a Static Group):**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated static group description",
    "static": ["server1", "server2", "server3", "server4"],
}

updated_group = address_group.update(group_id, update_data)
print(f"Updated static address group with ID: {updated_group.id}")
print(f"New static addresses: {updated_group.static}")
```

</div>

**Example 4 (Updating a Dynamic Group):**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated dynamic group description",
    "dynamic": {
        "filter": "'aws-tag' and 'production' or 'staging'"
    },
}

updated_group = address_group.update(group_id, update_data)
print(f"Updated dynamic address group with ID: {updated_group.id}")
print(f"New dynamic filter: {updated_group.dynamic.filter}")
```

</div>

### `delete(object_id: str) -> None`

Deletes an address group by its ID.

**Parameters:**

- `object_id` (str): The UUID of the address group.

**Example:**

<div class="termy">

<!-- termynal -->

```python
address_group.delete(group_id)
print(f"Deleted address group with ID: {group_id}")
```

</div>

###
`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[AddressGroupResponseModel]`

Lists address groups, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list address groups from.
- `snippet` (Optional[str]): The snippet to list address groups from.
- `device` (Optional[str]): The device to list address groups from.
- `**filters`: Additional filters.

**Example 5 (Listing Address Groups in a Folder):**

<div class="termy">

<!-- termynal -->

```python
groups = address_group.list(folder='Prisma Access')

for group in groups:
    print(f"Address Group Name: {group.name}")
    print(f"Type: {'Dynamic' if group.dynamic else 'Static'}")
    print(f"Description: {group.description}")
    print("---")
```

</div>

**Example 6 (Listing Address Groups with Filters):**

<div class="termy">

<!-- termynal -->

```python
groups = address_group.list(folder='Prisma Access', names=['web-servers', 'db-servers'], tags=['production'])

for group in groups:
    print(f"Address Group Name: {group.name}")
    print(f"Type: {'Dynamic' if group.dynamic else 'Static'}")
    print(f"Tags: {group.tag}")
    print("---")
```

</div>

---

## Full Usage Example

Here's a complete example demonstrating how to use the `AddressGroup` class:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import AddressGroup

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an AddressGroup instance
address_group = AddressGroup(scm)

# Create a new static address group
static_group_data = {
    "name": "web-servers",
    "description": "Web server address group",
    "static": ["web1.example.com", "web2.example.com"],
    "folder": "Prisma Access",
    "tag": ["production", "web"]
}

new_static_group = address_group.create(static_group_data)
print(f"Created static address group with ID: {new_static_group.id}")

# Create a new dynamic address group
dynamic_group_data = {
    "name": "dynamic-db-servers",
    "description": "Dynamic database server address group",
    "dynamic": {
        "filter": "'database-server' and 'production'"
    },
    "folder": "Prisma Access",
    "tag": ["production", "database"]
}

new_dynamic_group = address_group.create(dynamic_group_data)
print(f"Created dynamic address group with ID: {new_dynamic_group.id}")

# List all address groups in the folder
groups = address_group.list(folder='Prisma Access')
for group in groups:
    print(f"Address Group: {group.name}")
    print(f"Type: {'Dynamic' if group.dynamic else 'Static'}")
    print(f"Description: {group.description}")
    print(f"Tags: {group.tag}")
    print("---")

# Update the static group
update_static_data = {
    "description": "Updated web server address group",
    "static": ["web1.example.com", "web2.example.com", "web3.example.com"],
}
updated_static_group = address_group.update(new_static_group.id, update_static_data)
print(f"Updated static group: {updated_static_group.name}")
print(f"New static addresses: {updated_static_group.static}")

# Delete the dynamic group
address_group.delete(new_dynamic_group.id)
print(f"Deleted dynamic group with ID: {new_dynamic_group.id}")
```

</div>

---

## Related Models

- [AddressGroupRequestModel](../../models/objects/address_group_models.md#addressgrouprequestmodel)
- [AddressGroupResponseModel](../../models/objects/address_group_models.md#addressgroupresponsemodel)
