# Address Group Configuration Object

The `AddressGroup` class provides functionality to manage address groups in Palo Alto Networks' Strata Cloud Manager.
Address groups can be used to organize and manage collections of addresses either statically (by explicitly listing
addresses)
or dynamically (using tag-based filters).

## Overview

Address groups are essential components in network security policy management, allowing you to:

- Create static groups with explicit lists of addresses
- Define dynamic groups that automatically update based on tag filters
- Organize addresses within folders, snippets, or devices
- Apply tags for better organization and management

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during address group
management.

## Methods

| Method     | Description                                  |
|------------|----------------------------------------------|
| `create()` | Creates a new address group                  |
| `get()`    | Retrieves an address group by ID             |
| `update()` | Updates an existing address group            |
| `delete()` | Deletes an address group                     |
| `list()`   | Lists address groups with optional filtering |
| `fetch()`  | Retrieves a single address group by name     |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when address group data is invalid or for invalid response formats
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when an address group doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when address group names conflict
- `NameNotUniqueError`: Raised when creating duplicate group names
- `ReferenceNotZeroError`: Raised when deleting groups still referenced by policies

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out

## Creating Address Groups

The `create()` method allows you to create new address groups with proper error handling.

**Example: Creating a Static Address Group**

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import AddressGroup
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

address_groups = AddressGroup(client)

try:
    static_group = {
        "name": "web_servers",
        "description": "Web server group",
        "static": ["example_website", "webserver_network"],
        "folder": "Texas",
        "tag": ["Automation"]
    }

    new_group = address_groups.create(static_group)
    print(f"Created group: {new_group.name}")

except NameNotUniqueError as e:
    print(f"Group name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid group data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

**Example: Creating a Dynamic Address Group**

<div class="termy">

<!-- termynal -->

```python
try:
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

except InvalidObjectError as e:
    print(f"Invalid group data: {e.message}")
    print(f"Error code: {e.error_code}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Address Groups

Use the `get()` method to retrieve an address group by its ID.

<div class="termy">

<!-- termynal -->

```python
try:
    group_id = "d4d09614-55a3-4a94-911b-f1bbda353ca6"
    group = address_groups.get(group_id)
    print(f"Group Name: {group.name}")
    print(f"Type: {'Dynamic' if group.dynamic else 'Static'}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
```

</div>

## Updating Address Groups

The `update()` method allows you to modify existing address groups using Pydantic models.

<div class="termy">

<!-- termynal -->

```python
try:
    # return an existing group as a Pydantic model
    python_server_group = address_groups.fetch(folder='Texas', name='python servers')

    # update the model's description attribute
    python_server_group.description = 'updated description'

    # push changes to the SCM API
    updated_group = address_groups.update(python_server_group)
    print(f"Updated group: {updated_group.name}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting Address Groups

Use the `delete()` method to remove an address group.

<div class="termy">

<!-- termynal -->

```python
try:
    group_id = "d4d09614-55a3-4a94-911b-f1bbda353ca6"
    address_groups.delete(group_id)
    print("Group deleted successfully")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Group still in use: {e.message}")
```

</div>

## Listing Address Groups

The `list()` method retrieves multiple address groups with optional filtering. You can filter the results using the
following kwargs:

- `types`: List[str] - Filter by group types (e.g., ['static', 'dynamic'])
- `values`: List[str] - Filter by group values (static members or dynamic filter values)
- `tags`: List[str] - Filter by tags (e.g., ['Automation', 'Production'])

<div class="termy">

<!-- termynal -->

```python
try:
    # List all groups in a folder
    groups = address_groups.list(folder="Texas")

    # List only static groups
    static_groups = address_groups.list(
        folder="Texas",
        types=['static']
    )

    # List groups with specific values
    specific_groups = address_groups.list(
        folder="Texas",
        values=['web_server1', 'web_server2']
    )

    # List groups with specific tags
    tagged_groups = address_groups.list(
        folder="Texas",
        tags=['Automation', 'Production']
    )

    # Print the results
    for group in groups:
        print(f"Name: {group.name}")
        print(f"Type: {'Dynamic' if group.dynamic else 'Static'}")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching Address Groups

The `fetch()` method retrieves a single address group by name from a specific container, returning a Pydantic model.

<div class="termy">

<!-- termynal -->

```python
try:
    # pass in the folder and name required parameters
    dag_group = address_groups.fetch(folder='Texas', name='DAG_test')
    print(f"Found group: {dag_group.name}")
    print(f"Description: {dag_group.description}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full script examples

Refer to
the [address_group.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/address_group.py).

## Related Models

- [AddressGroupCreateModel](../../models/objects/address_group_models.md#Overview)
- [AddressGroupUpdateModel](../../models/objects/address_group_models.md#Overview)
- [AddressGroupResponseModel](../../models/objects/address_group_models.md#Overview)