# Application Configuration Object

The `Application` class is used to manage application definitions in the Strata Cloud Manager. It allows you to create,
retrieve, update, delete, and list applications.

---

## Importing the Application Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.objects import Application
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> ApplicationResponseModel`

Creates a new application.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the application data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
application_data = {
    "name": "custom-app",
    "category": "business-systems",
    "subcategory": "database",
    "technology": "client-server",
    "risk": 3,
    "description": "Custom application for internal use",
    "ports": ["tcp/1234", "udp/5678"],
    "folder": "Custom Apps",
    "has_known_vulnerabilities": True,
    "transfers_files": True
}

new_application = application.create(application_data)
print(f"Created application with ID: {new_application.id}")
```

</div>

### `get(object_id: str) -> ApplicationResponseModel`

Retrieves an application by its ID.

**Parameters:**

- `object_id` (str): The UUID of the application.

**Example:**

<div class="termy">

<!-- termynal -->

```python
app_id = "123e4567-e89b-12d3-a456-426655440000"
app_object = application.get(app_id)
print(f"Application Name: {app_object.name}, Category: {app_object.category}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> ApplicationResponseModel`

Updates an existing application.

**Parameters:**

- `object_id` (str): The UUID of the application.
- `data` (Dict[str, Any]): A dictionary containing the updated application data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated custom application description",
    "risk": 4,
    "prone_to_misuse": True
}

updated_app = application.update(app_id, update_data)
print(f"Updated application: {updated_app.name}, New risk level: {updated_app.risk}")
```

</div>

### `delete(object_id: str) -> None`

Deletes an application by its ID.

**Parameters:**

- `object_id` (str): The UUID of the application.

**Example:**

<div class="termy">

<!-- termynal -->

```python
application.delete(app_id)
print(f"Deleted application with ID: {app_id}")
```

</div>

###
`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[ApplicationResponseModel]`

Lists applications, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list applications from.
- `snippet` (Optional[str]): The snippet to list applications from.
- `device` (Optional[str]): The device to list applications from.
- `**filters`: Additional filters.

**Example:**

<div class="termy">

<!-- termynal -->

```python
# List applications in a specific folder
folder_apps = application.list(folder='Custom Apps')
for app in folder_apps:
    print(f"Application: {app.name}, Technology: {app.technology}")

# List applications with specific filters
filtered_apps = application.list(folder='Prisma Access', category='collaboration', risk=4)
for app in filtered_apps:
    print(f"High-risk app: {app.name}, Subcategory: {app.subcategory}")
```

</div>

---

## Usage Example

Here's a comprehensive example demonstrating the usage of the `Application` class:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Application

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an Application instance
application = Application(scm)

# Create a new application
new_app_data = {
    "name": "custom-collab-app",
    "category": "collaboration",
    "subcategory": "video-conferencing",
    "technology": "browser-based",
    "risk": 2,
    "description": "Custom video conferencing application",
    "ports": ["tcp/8080", "udp/9000-9010"],
    "folder": "Custom Collaboration Apps",
    "evasive": False,
    "pervasive": True,
    "excessive_bandwidth_use": True,
    "transfers_files": True,
    "has_known_vulnerabilities": False
}

new_app = application.create(new_app_data)
print(f"Created new application: {new_app.name} (ID: {new_app.id})")

# Retrieve the created application
retrieved_app = application.get(new_app.id)
print(f"Retrieved application: {retrieved_app.name}, Risk: {retrieved_app.risk}")

# Update the application
update_data = {
    "description": "Updated custom video conferencing application",
    "risk": 3,
    "has_known_vulnerabilities": True
}
updated_app = application.update(new_app.id, update_data)
print(f"Updated application: {updated_app.name}, New risk: {updated_app.risk}")

# List applications in the folder
folder_apps = application.list(folder='Custom Collaboration Apps')
print("Applications in 'Custom Collaboration Apps' folder:")
for app in folder_apps:
    print(f"- {app.name} ({app.technology})")

# Delete the application
application.delete(new_app.id)
print(f"Deleted application: {new_app.name}")
```

</div>

---

## Related Models

- [ApplicationRequestModel](../../models/objects/application_models.md#applicationrequestmodel)
- [ApplicationResponseModel](../../models/objects/application_models.md#applicationresponsemodel)
