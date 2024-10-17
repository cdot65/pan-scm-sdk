# Address Group Configuration Object

The `AddressGroup` class is used to manage address groups in the Strata Cloud Manager. Address groups can be either
static (containing a list of addresses) or dynamic (using a tag-based filter).

---

## Importing the AddressGroup Class

```python
from scm.config.objects import AddressGroup
```

## Methods

### `create(data: Dict[str, Any]) -> AddressGroupResponseModel`

Creates a new address group.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the address group data.

**Example (Static Group):**

```python
address_group_data = {
    "name": "example-group",
    "description": "This is a test address group",
    "static": ["test123", "test456"],
    "folder": "Prisma Access",
}

new_address_group = address_group.create(address_group_data)
print(f"Created address group with ID: {new_address_group.id}")
```

**Example (Dynamic Group):**

```python
address_group_data = {
    "name": "dynamic-group",
    "description": "Dynamic address group",
    "dynamic": {
        "filter": "'tag1' or 'tag2'"
    },
    "folder": "Prisma Access",
}

new_address_group = address_group.create(address_group_data)
print(f"Created address group with ID: {new_address_group.id}")
```

### `get(object_id: str) -> AddressGroupResponseModel`

Retrieves an address group by its ID.

**Parameters:**

- `object_id` (str): The UUID of the address group.

**Example:**

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
group_object = address_group.get(group_id)
print(f"Address Group Name: {group_object.name}")
```

### `update(object_id: str, data: Dict[str, Any]) -> AddressGroupResponseModel`

Updates an existing address group.

**Parameters:**

- `object_id` (str): The UUID of the address group.
- `data` (Dict[str, Any]): A dictionary containing the updated address group data.

**Example:**

```python
update_data = {
    "description": "Updated group description",
}

updated_group = address_group.update(group_id, update_data)
print(f"Updated address group with ID: {updated_group.id}")
```

### `delete(object_id: str) -> None`

Deletes an address group by its ID.

**Parameters:**

- `object_id` (str): The UUID of the address group.

**Example:**

```python
address_group.delete(group_id)
print(f"Deleted address group with ID: {group_id}")
```

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[AddressGroupResponseModel]`

Lists address groups, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list address groups from.
- `snippet` (Optional[str]): The snippet to list address groups from.
- `device` (Optional[str]): The device to list address groups from.
- `**filters`: Additional filters.

**Example:**

```python
groups = address_group.list(folder='Prisma Access')

for group in groups:
    print(f"Address Group Name: {group.name}, Type: {'Dynamic' if group.dynamic else 'Static'}")
```

---

## Usage Example

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
address_group_data = {
    "name": "example-group",
    "description": "This is a test address group",
    "static": ["test123", "test456"],
    "folder": "Prisma Access",
}

new_group = address_group.create(address_group_data)
print(f"Created address group with ID: {new_group.id}")

# List address groups
groups = address_group.list(folder='Prisma Access')
for group in groups:
    print(f"Address Group Name: {group.name}, Type: {'Dynamic' if group.dynamic else 'Static'}")
```

---

## Related Models

- [AddressGroupRequestModel](../../models/objects/address_group_models.md#addressgrouprequestmodel)
- [AddressGroupResponseModel](../../models/objects/address_group_models.md#addressgroupresponsemodel)
