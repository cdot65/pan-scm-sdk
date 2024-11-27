# Service Group Configuration Object

The `ServiceGroup` class provides functionality to manage service groups in Palo Alto Networks' Strata Cloud Manager.
Service groups allow you to organize and manage collections of services for use in security policies and NAT rules.

## Overview

Service Groups in Strata Cloud Manager allow you to:

- Create groups of services for simplified policy management
- Organize services within folders, snippets, or devices
- Apply tags for better organization and management
- Reference multiple services in a single policy rule

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during service group
management.

## Methods

| Method     | Description                                   |
|------------|-----------------------------------------------|
| `create()` | Creates a new service group                   |
| `get()`    | Retrieves a service group by ID               |
| `update()` | Updates an existing service group             |
| `delete()` | Deletes a service group                       |
| `list()`   | Lists service groups with optional filtering  |
| `fetch()`  | Retrieves a single service group by name      |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when service group data is invalid or for invalid response formats
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when a service group doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when service group names conflict
- `NameNotUniqueError`: Raised when creating duplicate group names
- `ReferenceNotZeroError`: Raised when deleting groups still referenced by policies

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out

## Creating Service Groups

The `create()` method allows you to create new service groups with proper error handling.

**Example: Creating a Service Group**

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.objects import ServiceGroup
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

service_groups = ServiceGroup(client)

try:
    group_data = {
        "name": "web-services",
        "members": ["HTTP", "HTTPS"],
        "folder": "Texas",
        "tag": ["Python", "Automation"]
    }

    new_group = service_groups.create(group_data)
    print(f"Created group: {new_group.name}")

except NameNotUniqueError as e:
    print(f"Group name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid group data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Service Groups

Use the `get()` method to retrieve a service group by its ID.

<div class="termy">

<!-- termynal -->
```python
try:
    group_id = "123e4567-e89b-12d3-a456-426655440000"
    group = service_groups.get(group_id)
    print(f"Group Name: {group.name}")
    print(f"Members: {', '.join(group.members)}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
```

</div>

## Updating Service Groups

The `update()` method allows you to modify existing service groups using Pydantic models.

<div class="termy">

<!-- termynal -->
```python
try:
    # Fetch returns a Pydantic model
    web_group = service_groups.fetch(folder='Texas', name='web-services')
    
    # Update the model's members
    web_group.members.append('HTTP-8080')
    
    # Update using the Pydantic model
    updated_group = service_groups.update(web_group)
    print(f"Updated group: {updated_group.name}")
    print(f"New members: {', '.join(updated_group.members)}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting Service Groups

Use the `delete()` method to remove a service group.

<div class="termy">

<!-- termynal -->
```python
try:
    group_id = "123e4567-e89b-12d3-a456-426655440000"
    service_groups.delete(group_id)
    print("Group deleted successfully")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Group still in use: {e.message}")
```

</div>

## Listing Service Groups

The `list()` method retrieves multiple service groups with optional filtering. You can filter the results using the
following kwargs:

- `values`: List[str] - Filter by member values (e.g., ['HTTP', 'HTTPS'])
- `tags`: List[str] - Filter by tags (e.g., ['Automation', 'Production'])

<div class="termy">

<!-- termynal -->
```python
try:
    # List all groups in a folder
    groups = service_groups.list(folder="Texas")

    # List groups with specific members
    web_groups = service_groups.list(
        folder="Texas",
        values=['HTTP', 'HTTPS']
    )

    # List groups with specific tags
    tagged_groups = service_groups.list(
        folder="Texas",
        tags=['Automation', 'Production']
    )

    # Print the results
    for group in groups:
        print(f"Name: {group.name}")
        print(f"Members: {', '.join(group.members)}")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching Service Groups

The `fetch()` method retrieves a single service group by name from a specific container, returning a Pydantic model.

<div class="termy">

<!-- termynal -->
```python
try:
    group = service_groups.fetch(
        name="web-services",
        folder="Texas"
    )
    print(f"Found group: {group.name}")
    print(f"Current members: {', '.join(group.members)}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a service group with proper error handling:

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.objects import ServiceGroup
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
    ReferenceNotZeroError
)

try:
    # Initialize client with debug logging
    client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        log_level="DEBUG"  # Enable detailed logging
    )

    # Initialize service group object
    service_groups = ServiceGroup(client)

    try:
        # Create new service group
        group_data = {
            "name": "test-services",
            "members": ["HTTP", "HTTPS", "SSH"],
            "folder": "Texas",
            "tag": ["Automation"]
        }

        new_group = service_groups.create(group_data)
        print(f"Created group: {new_group.name}")

        # Fetch and update the group
        try:
            fetched_group = service_groups.fetch(
                name="test-services",
                folder="Texas"
            )
            print(f"Found group: {fetched_group.name}")

            # Update the group using Pydantic model
            fetched_group.members.append("FTP")

            updated_group = service_groups.update(fetched_group)
            print(f"Updated group: {updated_group.name}")
            print(f"New members: {', '.join(updated_group.members)}")

        except NotFoundError as e:
            print(f"Group not found: {e.message}")

        # Clean up
        try:
            service_groups.delete(new_group.id)
            print("Group deleted successfully")
        except ReferenceNotZeroError as e:
            print(f"Cannot delete group - still in use: {e.message}")

    except NameNotUniqueError as e:
        print(f"Group name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid group data: {e.message}")
        if e.details:
            print(f"Details: {e.details}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.http_status_code}")
```

</div>

## Full script examples

Refer to the [examples](../../../../examples/scm/config/objects) directory.

## Related Models

- [ServiceGroupCreateModel](../../models/objects/service_group_models.md#Overview)
- [ServiceGroupUpdateModel](../../models/objects/service_group_models.md#Overview)
- [ServiceGroupResponseModel](../../models/objects/service_group_models.md#Overview)