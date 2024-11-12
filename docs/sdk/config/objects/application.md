# Application Configuration Object

The `Application` class provides functionality to manage custom application definitions in Palo Alto Networks' Strata
Cloud Manager.
Applications represent network applications and their characteristics, allowing you to define custom applications beyond
the predefined ones available in the system.

## Overview

Applications in Strata Cloud Manager allow you to:

- Define custom applications with specific characteristics
- Categorize applications by type, risk level, and behavior
- Specify application properties like ports and protocols
- Track security-relevant attributes like known vulnerabilities
- Organize applications within folders or snippets

## Methods

| Method     | Description                                |
|------------|--------------------------------------------|
| `create()` | Creates a new application definition       |
| `get()`    | Retrieves an application by ID             |
| `update()` | Updates an existing application            |
| `delete()` | Deletes an application                     |
| `list()`   | Lists applications with optional filtering |
| `fetch()`  | Retrieves a single application by name     |

## Creating Applications

The `create()` method allows you to define new custom applications. You must specify required fields like name,
category,
subcategory, technology, and risk level.

**Example: Creating a Custom Application**

<div class="termy">

<!-- termynal -->

```python
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
```

</div>

## Getting Applications

Use the `get()` method to retrieve an application by its ID.

<div class="termy">

<!-- termynal -->

```python
app_id = "123e4567-e89b-12d3-a456-426655440000"
app = applications.get(app_id)
print(f"Application: {app.name}")
print(f"Risk Level: {app.risk}")
```

</div>

## Updating Applications

The `update()` method allows you to modify existing applications.

<div class="termy">

<!-- termynal -->

```python
fetched_app = applications.fetch(folder='Texas', name='internal-chat')

fetched_app['description'] = 'Updated description for internal chat application'

updated_app = applications.update(fetched_app)
print(f"Updated application: {updated_app.name}")
```

</div>

## Deleting Applications

Use the `delete()` method to remove an application.

<div class="termy">

<!-- termynal -->

```python
app_id = "123e4567-e89b-12d3-a456-426655440000"
applications.delete(app_id)
print("Application deleted successfully")
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

<!-- termynal -->

```python
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
```

</div>

## Fetching Applications

The `fetch()` method retrieves a single application by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
app = application.fetch(
    name="internal-chat",
    folder="Texas"
)
print(f"Found application: {app['name']}")
print(f"Current risk level: {app['risk']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an application:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Application

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize application object
applications = Application(client)

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
fetched_app = applications.fetch(
    name="custom-app",
    folder="Texas"
)

# Modify the fetched application
fetched_app["description"] = "Updated database application"
fetched_app["risk"] = 4
fetched_app["has_known_vulnerabilities"] = True

# Update using the modified object
updated_app = applications.update(fetched_app)
print(f"Updated application: {updated_app.name}")
print(f"New risk level: {updated_app.risk}")

# List all applications
apps = applications.list(folder="Texas")
for app in apps:
    print(f"Listed application: {app.name}")

# Clean up
applications.delete(new_app.id)
print("Application deleted successfully")
```

</div>

## Related Models

- [ApplicationCreateModel](../../models/objects/application_models.md#applicationcreatemodel)
- [ApplicationUpdateModel](../../models/objects/application_models.md#applicationupdatemodel)
- [ApplicationResponseModel](../../models/objects/application_models.md#applicationresponsemodel)