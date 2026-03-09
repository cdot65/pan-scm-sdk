# Application

The `Application` service manages custom application definitions in Strata Cloud Manager, allowing fine-grained control over application characteristics, risk levels, and security behaviors.

## Class Overview

The `Application` class provides CRUD operations for custom application objects. It is accessed through the `client.application` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Application service
applications = client.application
```

### Key Attributes

| Attribute                   | Type        | Required | Description                                |
|-----------------------------|-------------|----------|--------------------------------------------|
| `name`                      | `str`       | Yes      | Name of application (max 63 chars)         |
| `id`                        | `UUID`      | Yes*     | Unique identifier (*response only)         |
| `category`                  | `str`       | Yes      | High-level category (max 50 chars)         |
| `subcategory`               | `str`       | Yes      | Specific sub-category (max 50 chars)       |
| `technology`                | `str`       | Yes      | Underlying technology (max 50 chars)       |
| `risk`                      | `int`       | Yes      | Risk level (1-5)                           |
| `description`               | `str`       | No       | Description (max 1023 chars)               |
| `ports`                     | `List[str]` | No       | Associated TCP/UDP ports                   |
| `tag`                       | `List[str]` | No       | Tags associated with the application       |
| `folder`                    | `str`       | Yes**    | Folder location (**one container required) |
| `snippet`                   | `str`       | Yes**    | Snippet location (**one container required)|
| `evasive`                   | `bool`      | No       | Uses evasive techniques                    |
| `pervasive`                 | `bool`      | No       | Widely used                                |
| `excessive_bandwidth_use`   | `bool`      | No       | Uses excessive bandwidth                   |
| `used_by_malware`           | `bool`      | No       | Used by malware                            |
| `transfers_files`           | `bool`      | No       | Transfers files                            |
| `has_known_vulnerabilities` | `bool`      | No       | Has known vulnerabilities                  |
| `tunnels_other_apps`        | `bool`      | No       | Tunnels other applications                 |
| `prone_to_misuse`           | `bool`      | No       | Prone to misuse                            |
| `no_certifications`         | `bool`      | No       | Lacks certifications                       |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Applications

Retrieves a list of application objects with optional filtering.

```python
apps = client.application.list(
    folder="Texas",
    category=["business-systems"],
    risk=[3, 4, 5]
)

for app in apps:
    print(f"Name: {app.name}, Category: {app.category}, Risk: {app.risk}")
```

### Fetch an Application

Retrieves a single application by name and container.

```python
app = client.application.fetch(name="custom-database", folder="Texas")
print(f"Found application: {app.name}")
```

### Create an Application

Creates a new custom application definition.

```python
new_app = client.application.create({
    "name": "custom-database",
    "category": "business-systems",
    "subcategory": "database",
    "technology": "client-server",
    "risk": 3,
    "description": "Custom database application",
    "ports": ["tcp/1521"],
    "folder": "Texas"
})
```

### Update an Application

Updates an existing application object.

```python
existing = client.application.fetch(name="custom-database", folder="Texas")
existing.risk = 4
existing.has_known_vulnerabilities = True
existing.ports = ["tcp/1521", "tcp/1522"]

updated = client.application.update(existing)
```

### Delete an Application

Deletes an application object by ID.

```python
client.application.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Defining a Custom Application with Security Attributes

Create an application with full security characteristics.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

client.application.create({
    "name": "secure-chat",
    "category": "collaboration",
    "subcategory": "instant-messaging",
    "technology": "client-server",
    "risk": 2,
    "description": "Secure internal chat application",
    "ports": ["tcp/8443"],
    "folder": "Texas",
    "transfers_files": True,
    "has_known_vulnerabilities": False,
    "evasive": False,
    "pervasive": True
})
```

### Filtering Applications by Risk and Category

Find applications matching specific risk and category criteria.

```python
# Find high-risk business applications
high_risk = client.application.list(
    folder="Texas",
    category=["business-systems"],
    risk=[4, 5]
)

for app in high_risk:
    print(f"{app.name}: risk={app.risk}, category={app.category}")

# Exact match with exclusions
filtered = client.application.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"]
)
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_app = client.application.create({
        "name": "test-app",
        "category": "business-systems",
        "subcategory": "database",
        "technology": "client-server",
        "risk": 3,
        "folder": "Texas",
        "ports": ["tcp/1521"]
    })
except InvalidObjectError as e:
    print(f"Invalid application data: {e.message}")
except NameNotUniqueError as e:
    print(f"Application name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Application not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Application still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Application Models](../../models/objects/application_models.md#Overview)
- [Application Filters](application_filters.md)
- [Application Group](application_group.md)
