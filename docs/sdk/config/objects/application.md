# Application Configuration Object

The `Application` class provides functionality to manage custom application definitions in Palo Alto Networks' Strata
Cloud Manager. Applications represent network applications and their characteristics, allowing you to define custom
applications beyond the predefined ones available in the system.

## Overview

Applications in Strata Cloud Manager allow you to:

- Define custom applications with specific characteristics
- Categorize applications by type, risk level, and behavior
- Specify application properties like ports and protocols
- Track security-relevant attributes like known vulnerabilities
- Organize applications within folders or snippets

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during application
management.

## Methods

| Method     | Description                                |
|------------|--------------------------------------------|
| `create()` | Creates a new application definition       |
| `get()`    | Retrieves an application by ID             |
| `update()` | Updates an existing application            |
| `delete()` | Deletes an application                     |
| `list()`   | Lists applications with optional filtering |
| `fetch()`  | Retrieves a single application by name     |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when application data is invalid or malformed
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when an application doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when application names conflict
- `NameNotUniqueError`: Raised when creating duplicate application names
- `ReferenceNotZeroError`: Raised when deleting applications still referenced by policies

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out
- `SessionTimeoutError`: When the API session times out

## Creating Applications

The `create()` method allows you to define new custom applications with proper error handling.

**Example: Creating a Custom Application**

<div class="termy">

```python
from scm.client import Scm
from scm.config.objects import Application
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

applications = Application(client)

try:
    app_data = {
        "name": "internal-chat",
        "category": "collaboration",
        "subcategory": "instant-messaging",
        "technology": "client-server",
        "risk": 2,
        "description": "Internal chat application",
        "ports": ["tcp/8443"],
        "folder": "Texas",
        "transfers_files": True,
        "has_known_vulnerabilities": False
    }

    new_app = applications.create(app_data)
    print(f"Created application: {new_app.name}")

except NameNotUniqueError as e:
    print(f"Application name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid application data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Applications

Use the `get()` method to retrieve an application by its ID.

<div class="termy">

```python
try:
    app_id = "123e4567-e89b-12d3-a456-426655440000"
    app = applications.get(app_id)
    print(f"Application: {app.name}")
    print(f"Risk Level: {app.risk}")

except NotFoundError as e:
    print(f"Application not found: {e.message}")
```

</div>

## Updating Applications

The `update()` method allows you to modify existing applications.

<div class="termy">

```python
try:
    fetched_app = applications.fetch(folder='Texas', name='internal-chat')

    fetched_app['description'] = 'Updated description for internal chat application'

    updated_app = applications.update(fetched_app)
    print(f"Updated application: {updated_app.name}")

except NotFoundError as e:
    print(f"Application not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting Applications

Use the `delete()` method to remove an application.

<div class="termy">

```python
try:
    app_id = "123e4567-e89b-12d3-a456-426655440000"
    applications.delete(app_id)
    print("Application deleted successfully")

except NotFoundError as e:
    print(f"Application not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Application still in use: {e.message}")
```

</div>

## Listing Applications

The `list()` method retrieves multiple applications with optional filtering. You can filter the results using the
following kwargs:

- `category`: List[str] - Filter by category (e.g., ['collaboration', 'business-systems'])
- `subcategory`: List[str] - Filter by subcategory (e.g., ['instant-messaging', 'database'])
- `technology`: List[str] - Filter by technology (e.g., ['client-server', 'peer-to-peer'])
- `risk`: List[int] - Filter by risk level (e.g., [1, 2, 3])

<div class="termy">

```python
try:
    # List all applications in a folder
    apps = applications.list(folder="Texas")

    # List applications by category
    collab_apps = applications.list(
        folder="Texas",
        category=['collaboration']
    )

    # List applications by risk level
    high_risk_apps = applications.list(
        folder="Texas",
        risk=[4, 5]
    )

    # List applications by technology
    client_server_apps = applications.list(
        folder="Texas",
        technology=['client-server']
    )

    # Combine multiple filters
    filtered_apps = applications.list(
        folder="Texas",
        category=['business-systems'],
        subcategory=['database'],
        risk=[3, 4, 5]
    )

    # Print the results
    for app in apps:
        print(f"Name: {app.name}, Category: {app.category}, Risk: {app.risk}")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching Applications

The `fetch()` method retrieves a single application by name from a specific container.

<div class="termy">

```python
try:
    app = applications.fetch(
        name="internal-chat",
        folder="Texas"
    )
    print(f"Found application: {app['name']}")
    print(f"Current risk level: {app['risk']}")

except NotFoundError as e:
    print(f"Application not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an application with proper error handling:

<div class="termy">

```python
from scm.client import Scm
from scm.config.objects import Application
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

    # Initialize application object
    applications = Application(client)

    try:
        # Create new application
        app_data = {
            "name": "custom-app",
            "category": "business-systems",
            "subcategory": "database",
            "technology": "client-server",
            "risk": 3,
            "description": "Custom database application",
            "ports": ["tcp/1521"],
            "folder": "Texas",
            "transfers_files": True
        }

        new_app = applications.create(app_data)
        print(f"Created application: {new_app.name}")

        # Fetch the application by name
        try:
            fetched_app = applications.fetch(
                name="custom-app",
                folder="Texas"
            )
            print(f"Found application: {fetched_app['name']}")

            # Update the application
            fetched_app["description"] = "Updated database application"
            fetched_app["risk"] = 4
            fetched_app["has_known_vulnerabilities"] = True

            updated_app = applications.update(fetched_app)
            print(f"Updated application: {updated_app.name}")
            print(f"New risk level: {updated_app.risk}")

        except NotFoundError as e:
            print(f"Application not found: {e.message}")

        # Clean up
        try:
            applications.delete(new_app.id)
            print("Application deleted successfully")
        except ReferenceNotZeroError as e:
            print(f"Cannot delete application - still in use: {e.message}")

    except NameNotUniqueError as e:
        print(f"Application name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid application data: {e.message}")
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

- [ApplicationCreateModel](../../models/objects/application_models.md#Overview)
- [ApplicationUpdateModel](../../models/objects/application_models.md#Overview)
- [ApplicationResponseModel](../../models/objects/application_models.md#Overview)