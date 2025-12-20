# Application Models

## Overview {#Overview}

The Application models provide a structured way to manage custom applications in Palo Alto Networks' Strata Cloud
Manager. These models support defining application characteristics like category, risk level, and behavioral attributes.
Applications can be defined in folders or snippets. The models handle validation of inputs and outputs when interacting
with the SCM API.

### Models

| Model                      | Purpose                                          |
|----------------------------|--------------------------------------------------|
| `ApplicationBaseModel`     | Base model with common fields for all operations |
| `ApplicationCreateModel`   | Model for creating new applications              |
| `ApplicationUpdateModel`   | Model for updating existing applications         |
| `ApplicationResponseModel` | Model for API responses                          |

The Base, Create, and Update models use `extra="forbid"` configuration, which rejects any fields not explicitly defined.
The Response model uses `extra="allow"` to handle undocumented API fields (SaaS attributes, compliance flags, etc.).

## Attributes

| Attribute                 | Type      | Required | Default | Description                                                                            |
|---------------------------|-----------|----------|---------|----------------------------------------------------------------------------------------|
| name                      | str       | Yes      | None    | Name of the application. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
| category                  | str       | Yes      | None    | High-level category. Max length: 50 chars                                              |
| subcategory               | str       | Yes      | None    | Specific sub-category. Max length: 50 chars                                            |
| technology                | str       | Yes      | None    | Underlying technology. Max length: 50 chars                                            |
| risk                      | int       | Yes      | None    | Risk level associated with the application                                             |
| description               | str       | No       | None    | Description of the application. Max length: 1023 chars                                 |
| ports                     | List[str] | No       | None    | List of TCP/UDP ports                                                                  |
| tag                       | List[str] | No       | None    | Tags associated with the application                                                   |
| folder                    | str       | No*      | None    | Folder where application is defined. Max length: 64 chars                              |
| snippet                   | str       | No*      | None    | Snippet where application is defined. Max length: 64 chars                             |
| evasive                   | bool      | No       | False   | Uses evasive techniques                                                                |
| pervasive                 | bool      | No       | False   | Widely used                                                                            |
| excessive_bandwidth_use   | bool      | No       | False   | Uses excessive bandwidth                                                               |
| used_by_malware           | bool      | No       | False   | Commonly used by malware                                                               |
| transfers_files           | bool      | No       | False   | Transfers files                                                                        |
| has_known_vulnerabilities | bool      | No       | False   | Has known vulnerabilities                                                              |
| tunnels_other_apps        | bool      | No       | False   | Tunnels other applications                                                             |
| prone_to_misuse           | bool      | No       | False   | Prone to misuse                                                                        |
| no_certifications         | bool      | No       | False   | Lacks certifications                                                                   |
| id                        | UUID      | Yes**    | None    | UUID of the application (response only)                                                |

\* Exactly one container type (folder/snippet) must be provided
\** Only required for response model

## Exceptions

The Application models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet) are specified for create operations
    - When no container type is specified for create operations
    - When name pattern validation fails
    - When field length validations fail
    - When required fields are missing

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# Using dictionary
from scm.config.objects import Application

# Error: multiple containers specified
try:
    app_dict = {
        "name": "invalid-app",
        "category": "business-systems",
        "subcategory": "database",
        "technology": "client-server",
        "risk": 3,
        "folder": "Texas",
        "snippet": "Config"  # Can't specify both folder and snippet
    }
    app = Application(api_client)
    response = app.create(app_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder' or 'snippet' must be provided."

# Using model directly
from scm.models.objects import ApplicationCreateModel

# Error: no container specified
try:
    app = ApplicationCreateModel(
        name="invalid-app",
        category="business-systems",
        subcategory="database",
        technology="client-server",
        risk=3
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder' or 'snippet' must be provided."
```

## Usage Examples

### Creating a Basic Application

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
app_dict = {
    "name": "custom-db",
    "category": "business-systems",
    "subcategory": "database",
    "technology": "client-server",
    "risk": 3,
    "folder": "Texas",
    "ports": ["tcp/1433"]
}

response = client.application.create(app_dict)
```

### Creating an Application with Behavioral Attributes

```python
# Using dictionary
app_dict = {
    "name": "file-share",
    "category": "collaboration",
    "subcategory": "file-sharing",
    "technology": "peer-to-peer",
    "risk": 4,
    "folder": "Texas",
    "description": "Custom file sharing application",
    "ports": ["tcp/6346", "tcp/6347"],
    "evasive": True,
    "transfers_files": True,
    "excessive_bandwidth_use": True,
    "prone_to_misuse": True
}

response = client.application.create(app_dict)
```

### Updating an Application

```python
# Fetch existing application
existing = client.application.fetch(name="custom-db", folder="Texas")

# Modify attributes using dot notation
existing.risk = 4
existing.description = "Updated database application"
existing.has_known_vulnerabilities = True

# Pass modified object to update()
updated = client.application.update(existing)
```
