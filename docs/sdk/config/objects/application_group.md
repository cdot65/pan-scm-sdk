# Application Group Configuration Object

The `ApplicationGroup` class provides functionality to manage application groups in Palo Alto Networks' Strata Cloud
Manager. Application groups allow you to organize and manage collections of applications for use in security policies
and other
configurations.

## Overview

Application groups in Strata Cloud Manager allow you to:

- Group multiple applications together for easier management
- Create static groups with explicit lists of applications
- Organize application groups within folders, snippets, or devices
- Reference groups in security policies and other configurations
- Fetch and manage groups by name or ID

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during application
group
management.

## Methods

| Method     | Description                                      |
|------------|--------------------------------------------------|
| `create()` | Creates a new application group                  |
| `get()`    | Retrieves an application group by ID             |
| `update()` | Updates an existing application group            |
| `delete()` | Deletes an application group                     |
| `list()`   | Lists application groups with optional filtering |
| `fetch()`  | Retrieves a single application group by name     |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when application group data is invalid or for invalid response formats
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when an application group doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when application group names conflict
- `NameNotUniqueError`: Raised when creating duplicate group names
- `ReferenceNotZeroError`: Raised when deleting groups still referenced by policies

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out

## Creating Application Groups

The `create()` method allows you to create new application groups with proper error handling.

**Example: Creating an Application Group**

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import ApplicationGroup
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

application_groups = ApplicationGroup(client)

try:
    group_data = {
        "name": "web-apps",
        "members": ["ssl", "web-browsing"],
        "folder": "Texas",
    }

    new_group = application_groups.create(group_data)
    print(f"Created group: {new_group.name}")

except NameNotUniqueError as e:
    print(f"Group name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid group data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Application Groups

Use the `get()` method to retrieve an application group by its ID.

<div class="termy">

<!-- termynal -->

```python
try:
    group_id = "123e4567-e89b-12d3-a456-426655440000"
    group = application_groups.get(group_id)
    print(f"Group Name: {group.name}")
    print(f"Members: {group.members}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
```

</div>

## Updating Application Groups

The `update()` method allows you to modify existing application groups using Pydantic models.

<div class="termy">

<!-- termynal -->

```python
try:
    web_apps = application_groups.fetch(folder='Texas', name='web-apps')
    web_apps.members = ['ssl', 'web-browsing', 'dns-base']

    updated_group = application_groups.update(web_apps)
    print(f"Updated group: {updated_group.name}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting Application Groups

Use the `delete()` method to remove an application group.

<div class="termy">

<!-- termynal -->

```python
try:
    group_id = "123e4567-e89b-12d3-a456-426655440000"
    application_groups.delete(group_id)
    print("Group deleted successfully")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Group still in use: {e.message}")
```

</div>

## Listing Application Groups

The `list()` method retrieves multiple application groups with optional filtering. You can filter the results using the
following kwargs:

- `members`: List[str] - Filter by member applications (e.g., ['ssl', 'web-browsing'])

<div class="termy">

<!-- termynal -->

```python
try:
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

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching Application Groups

The `fetch()` method retrieves a single application group by name from a specific container, returning a Pydantic model.

<div class="termy">

<!-- termynal -->

```python
try:
    group = application_groups.fetch(
        name="web-apps",
        folder="Texas"
    )
    print(f"Found group: {group.name}")
    print(f"Current members: {group.members}")

except NotFoundError as e:
    print(f"Group not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an application group with proper error handling:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import ApplicationGroup
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

    # Initialize application group object
    application_groups = ApplicationGroup(client)

    try:
        # Create new group
        group_data = {
            "name": "web-apps",
            "members": ["ssl", "web-browsing"],
            "folder": "Texas",
        }

        new_group = application_groups.create(group_data)
        print(f"Created group: {new_group.name}")

        # Fetch the group by name
        try:
            fetched_group = application_groups.fetch(
                name="web-apps",
                folder="Texas"
            )
            print(f"Found group: {fetched_group.name}")

            # Update the group using Pydantic model
            fetched_group.members = ['ssl', 'web-browsing', 'dns-base']
            updated_group = application_groups.update(fetched_group)
            print(f"Updated members: {updated_group.members}")

        except NotFoundError as e:
            print(f"Group not found: {e.message}")

        # Clean up
        try:
            application_groups.delete(new_group.id)
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

- [ApplicationGroupCreateModel](../../models/objects/application_group_models.md#Overview)
- [ApplicationGroupUpdateModel](../../models/objects/application_group_models.md#Overview)
- [ApplicationGroupResponseModel](../../models/objects/application_group_models.md#Overview)