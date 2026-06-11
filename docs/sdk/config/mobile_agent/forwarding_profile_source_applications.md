# GlobalProtect Forwarding Profile Source Applications Configuration Object

Manages GlobalProtect forwarding profile source applications in Palo Alto Networks Strata Cloud Manager. Source applications define lists of applications that can be referenced by forwarding profiles.

## Class Overview

The `ForwardingProfileSourceApplications` class inherits from `BaseObject` and provides CRUD operations for GlobalProtect forwarding profile source application objects.

### Methods

| Method     | Description                          | Parameters                                                          | Return Type                                              |
|------------|--------------------------------------|---------------------------------------------------------------------|----------------------------------------------------------|
| `create()` | Creates a new source application     | `data: Dict[str, Any]`, `folder: str`                               | `ForwardingProfileSourceApplicationResponseModel`        |
| `get()`    | Retrieves a source application by ID | `object_id: Union[str, UUID]`                                       | `ForwardingProfileSourceApplicationResponseModel`        |
| `update()` | Updates an existing source application | `source_application: ForwardingProfileSourceApplicationUpdateModel` | `ForwardingProfileSourceApplicationResponseModel`        |
| `delete()` | Deletes a source application         | `object_id: Union[str, UUID]`                                       | `None`                                                   |
| `list()`   | Lists source applications            | `folder: str`, `name: Optional[str]`                                | `List[ForwardingProfileSourceApplicationResponseModel]`  |
| `fetch()`  | Gets a source application by name    | `name: str`, `folder: str`                                          | `ForwardingProfileSourceApplicationResponseModel`        |

### Model Attributes

| Attribute      | Type      | Required | Default | Description                                       |
|----------------|-----------|----------|---------|---------------------------------------------------|
| `name`         | str       | Yes      | None    | Name of the source application (max 64 chars)     |
| `applications` | List[str] | Yes      | None    | List of applications                              |
| `description`  | str       | No       | None    | Description of the source application (max 1023)  |
| `id`           | UUID      | Yes*     | None    | UUID of the source application                    |

\* Present in update and response models only. The `folder` ("Mobile Users") is passed as a query parameter on `create()` and `list()`, not as a model field.

### Exceptions

| Exception                    | HTTP Code | Description                            |
|------------------------------|-----------|----------------------------------------|
| `InvalidObjectError`         | 400       | Invalid data, folder, or response      |
| `MissingQueryParameterError` | 400       | Missing required parameters            |
| `ObjectNotPresentError`      | 404       | Source application not found           |
| `AuthenticationError`        | 401       | Authentication failed                  |
| `ServerError`                | 500       | Internal server error                  |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

source_applications = client.forwarding_profile_source_application
```

## Methods

### List Source Applications

```python
all_apps = client.forwarding_profile_source_application.list()

for app in all_apps:
    print(f"Name: {app.name}, Applications: {app.applications}")
```

**Controlling pagination with max_limit:**

```python
client.forwarding_profile_source_application.max_limit = 1000

all_apps = client.forwarding_profile_source_application.list()
```

### Fetch a Source Application

```python
app = client.forwarding_profile_source_application.fetch(
    name="saas-apps",
    folder="Mobile Users",
)
print(f"Found source application: {app.name}")
```

### Create a Source Application

```python
app_config = {
    "name": "saas-apps",
    "description": "SaaS applications forwarded via proxy",
    "applications": ["office365-enterprise-access", "slack", "zoom"],
}
new_app = client.forwarding_profile_source_application.create(app_config)
print(f"Created source application with ID: {new_app.id}")
```

### Update a Source Application

```python
from scm.models.mobile_agent import ForwardingProfileSourceApplicationUpdateModel

existing = client.forwarding_profile_source_application.fetch(name="saas-apps")

update_model = ForwardingProfileSourceApplicationUpdateModel(
    id=existing.id,
    name=existing.name,
    applications=existing.applications + ["github"],
)
updated = client.forwarding_profile_source_application.update(update_model)
```

### Delete a Source Application

```python
client.forwarding_profile_source_application.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Related Documentation

- [Forwarding Profile Source Application Models](../../models/mobile_agent/forwarding_profile_source_applications_models.md)
- [Mobile Agent Configuration](index.md)
