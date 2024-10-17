# Application Group Configuration Object

The `ApplicationGroup` class is used to manage application groups in the Strata Cloud Manager.

---

## Importing the ApplicationGroup Class

```python
from scm.client import Scm
from scm.config.objects import ApplicationGroup

# create a SCM session
scm = Scm(
    client_id="example",
    client_secret="example",
    tsg_id="example"
)

# pass SCM session into the ApplicationGroup object
application_group = ApplicationGroup(scm)
```

## Methods

### `create(data: Dict[str, Any]) -> ApplicationGroupResponseModel`

Creates a new application group.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the application group data.

**Example:**

```python
application_group_data = {
    "name": "example-group",
    "folder": "Prisma Access",
    "members": ["office365-consumer-access", "office365-enterprise-access"],
}

new_application_group = application_group.create(application_group_data)
print(f"Created application group with ID: {new_application_group.id}")
```

### `get(object_id: str) -> ApplicationGroupResponseModel`

Retrieves an application group by its ID.

**Parameters:**

- `object_id` (str): The UUID of the application group.

**Example:**

```python
group_id = "123e4567-e89b-12d3-a456-426655440000"
group_object = application_group.get(group_id)
print(f"application Group Name: {group_object.name}")
```

### `update(object_id: str, data: Dict[str, Any]) -> ApplicationGroupResponseModel`

Updates an existing application group.

**Parameters:**

- `object_id` (str): The UUID of the application group.
- `data` (Dict[str, Any]): A dictionary containing the updated application group data.

**Example:**

```python
update_data = {
    "name": "Test123",
    "folder": "Prisma Access",
    "members": ["Updated list of members"],
}

updated_group = application_group.update(group_id, update_data)
print(f"Updated application group with ID: {updated_group.id}")
```

### `delete(object_id: str) -> None`

Deletes an application group by its ID.

**Parameters:**

- `object_id` (str): The UUID of the application group.

**Example:**

```python
application_group.delete(group_id)
print(f"Deleted application group with ID: {group_id}")
```

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[ApplicationGroupResponseModel]`

Lists application groups, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list application groups from.
- `snippet` (Optional[str]): The snippet to list application groups from.
- `device` (Optional[str]): The device to list application groups from.
- `**filters`: Additional filters.

**Example:**

```python
groups = application_group.list(folder='Prisma Access')

for group in groups:
    print(f"application Group Name: {group.name}, Members: {group.members}")
```

---

## Usage Example

```python
from scm.client import Scm
from scm.config.objects import ApplicationGroup

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an ApplicationGroup instance
application_group = ApplicationGroup(scm)

# Create a new static application group
application_group_data = {
    "name": "example-group",
    "folder": "Prisma Access",
    "members": [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
}

new_group = application_group.create(application_group_data)
print(f"Created application group with ID: {new_group.id}")
```

---

## Related Models

- [ApplicationGroupRequestModel](../../models/objects/application_group_models.md#ApplicationGrouprequestmodel)
- [ApplicationGroupResponseModel](../../models/objects/application_group_models.md#ApplicationGroupresponsemodel)
