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
    "folder": "Custom Apps",
    "transfers_files": True,
    "has_known_vulnerabilities": False
}

new_app = application.create(app_data)
print(f"Created application: {new_app['name']}")
```

</div>

## Getting Applications

Use the `get()` method to retrieve an application by its ID.

<div class="termy">

<!-- termynal -->

```python
app_id = "123e4567-e89b-12d3-a456-426655440000"
app = application.get(app_id)
print(f"Application: {app['name']}")
print(f"Risk Level: {app['risk']}")
```

</div>

## Updating Applications

The `update()` method allows you to modify existing applications.

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "description": "Updated chat application",
    "risk": 3,
    "has_known_vulnerabilities": True
}

updated_app = application.update(update_data)
print(f"Updated application: {updated_app['name']}")
```

</div>

## Deleting Applications

Use the `delete()` method to remove an application.

<div class="termy">

<!-- termynal -->

```python
app_id = "123e4567-e89b-12d3-a456-426655440000"
application.delete(app_id)
print("Application deleted successfully")
```

</div>

## Listing Applications

The `list()` method retrieves multiple applications with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all applications in a folder
apps = application.list(folder="Custom Apps")
for app in apps:
    print(f"Name: {app['name']}, Risk: {app['risk']}")

# List with specific filters
high_risk_apps = application.list(
    folder="Custom Apps",
    risk=4,
    has_known_vulnerabilities=True
)
for app in high_risk_apps:
    print(f"High-risk app: {app['name']}")
```

</div>

## Fetching Applications

The `fetch()` method retrieves a single application by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
app = application.fetch(
    name="internal-chat",
    folder="Custom Apps"
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
application = Application(client)

# Create new application
app_data = {
    "name": "custom-app",
    "category": "business-systems",
    "subcategory": "database",
    "technology": "client-server",
    "risk": 3,
    "description": "Custom database application",
    "ports": ["tcp/1521"],
    "folder": "Custom Apps",
    "transfers_files": True
}

new_app = application.create(app_data)
print(f"Created application: {new_app['name']}")

# Fetch the application by name
fetched_app = application.fetch(
    name="custom-app",
    folder="Custom Apps"
)

# Modify the fetched application
fetched_app["description"] = "Updated database application"
fetched_app["risk"] = 4
fetched_app["has_known_vulnerabilities"] = True

# Update using the modified object
updated_app = application.update(fetched_app)
print(f"Updated application: {updated_app['name']}")
print(f"New risk level: {updated_app['risk']}")

# List all applications
apps = application.list(folder="Custom Apps")
for app in apps:
    print(f"Listed application: {app['name']}")

# Clean up
application.delete(new_app['id'])
print("Application deleted successfully")
```

</div>

## Related Models

- [ApplicationCreateModel](../../models/objects/application_models.md#applicationcreatemodel)
- [ApplicationUpdateModel](../../models/objects/application_models.md#applicationupdatemodel)
- [ApplicationResponseModel](../../models/objects/application_models.md#applicationresponsemodel)