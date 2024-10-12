# Application Configuration Object

The `Application` class is used to manage application definitions in the Strata Cloud Manager. It allows you to create,
retrieve, update, delete, and list applications.

---

## Importing the Application Class

```python
from scm.config.objects import Application
```

## Methods

### `create(data: Dict[str, Any]) -> ApplicationResponseModel`

Creates a new application.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the application data.

**Example:**

```python
application_data = {
    "name": "test-app",
    "category": "collaboration",
    "subcategory": "internet-conferencing",
    "technology": "client-server",
    "risk": 1,
    "description": "Created via pan-scm-sdk",
    "ports": ["tcp/80,443", "udp/3478"],
    "folder": "Prisma Access",
    "evasive": False,
    "pervasive": False,
    "excessive_bandwidth_use": False,
    "used_by_malware": False,
    "transfers_files": False,
    "has_known_vulnerabilities": True,
    "tunnels_other_apps": False,
    "prone_to_misuse": False,
    "no_certifications": False,
}

new_application = application.create(application_data)
print(f"Created application with ID: {new_application.id}")
```

### `get(object_id: str) -> ApplicationResponseModel`

Retrieves an application by its ID.

**Parameters:**

- `object_id` (str): The UUID of the application.

**Example:**

```python
app_id = "123e4567-e89b-12d3-a456-426655440000"
app_object = application.get(app_id)
print(f"Application Name: {app_object.name}")
```

### `update(object_id: str, data: Dict[str, Any]) -> ApplicationResponseModel`

Updates an existing application.

**Parameters:**

- `object_id` (str): The UUID of the application.
- `data` (Dict[str, Any]): A dictionary containing the updated application data.

**Example:**

```python
update_data = {
    "description": "Updated application description",
}

updated_app = application.update(app_id, update_data)
print(f"Updated application with ID: {updated_app.id}")
```

### `delete(object_id: str) -> None`

Deletes an application by its ID.

**Parameters:**

- `object_id` (str): The UUID of the application.

**Example:**

```python
application.delete(app_id)
print(f"Deleted application with ID: {app_id}")
```

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[ApplicationResponseModel]`

Lists applications, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list applications from.
- `snippet` (Optional[str]): The snippet to list applications from.
- `device` (Optional[str]): The device to list applications from.
- `**filters`: Additional filters.

**Example:**

```python
applications = application.list(folder='Prisma Access')

for app in applications:
    print(f"Application Name: {app.name}, Category: {app.category}")
```

---

## Usage Example

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
application_data = {
    "name": "test-app",
    "category": "collaboration",
    "subcategory": "internet-conferencing",
    "technology": "client-server",
    "risk": 1,
    "description": "Created via pan-scm-sdk",
    "ports": ["tcp/80,443", "udp/3478"],
    "folder": "Prisma Access",
    "evasive": False,
    "pervasive": False,
    "excessive_bandwidth_use": False,
    "used_by_malware": False,
    "transfers_files": False,
    "has_known_vulnerabilities": True,
    "tunnels_other_apps": False,
    "prone_to_misuse": False,
    "no_certifications": False,
}

new_application = application.create(application_data)
print(f"Created application with ID: {new_application.id}")

# List applications
applications = application.list(folder='Prisma Access')
for app in applications:
    print(f"Application Name: {app.name}, Category: {app.category}")
```

---

## Related Models

- [ApplicationRequestModel](models/application_models.md#applicationrequestmodel)
- [ApplicationResponseModel](models/application_models.md#applicationresponsemodel)
