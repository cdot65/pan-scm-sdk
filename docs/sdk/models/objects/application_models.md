# Application Models

## Overview

The Application models provide a structured way to manage custom applications in Palo Alto Networks' Strata Cloud
Manager.
These models support defining application characteristics like category, risk level, and behavioral attributes.
Applications
can be defined in folders or snippets. The models handle validation of inputs and outputs when interacting with the SCM
API.

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

<div class="termy">

<!-- termynal -->

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

</div>

## Usage Examples

### Creating a Basic Application

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.objects import Application

app_dict = {
    "name": "custom-db",
    "category": "business-systems",
    "subcategory": "database",
    "technology": "client-server",
    "risk": 3,
    "folder": "Texas",
    "ports": ["tcp/1433"]
}

app = Application(api_client)
response = app.create(app_dict)

# Using model directly
from scm.models.objects import ApplicationCreateModel

app = ApplicationCreateModel(
    name="custom-db",
    category="business-systems",
    subcategory="database",
    technology="client-server",
    risk=3,
    folder="Custom Apps",
    ports=["tcp/1433"]
)

payload = app.model_dump(exclude_unset=True)
response = app.create(payload)
```

</div>

### Creating an Application with Behavioral Attributes

<div class="termy">

<!-- termynal -->

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

response = app.create(app_dict)

# Using model directly
app = ApplicationCreateModel(
    name="file-share",
    category="collaboration",
    subcategory="file-sharing",
    technology="peer-to-peer",
    risk=4,
    folder="Texas",
    description="Custom file sharing application",
    ports=["tcp/6346", "tcp/6347"],
    evasive=True,
    transfers_files=True,
    excessive_bandwidth_use=True,
    prone_to_misuse=True
)

payload = app.model_dump(exclude_unset=True)
response = app.create(payload)
```

</div>

### Updating an Application

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "custom-db-updated",
    "risk": 4,
    "description": "Updated database application",
    "has_known_vulnerabilities": True
}

response = app.update(update_dict)

# Using model directly
from scm.models.objects import ApplicationUpdateModel

update = ApplicationUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="custom-db-updated",
    risk=4,
    description="Updated database application",
    has_known_vulnerabilities=True
)

payload = update.model_dump(exclude_unset=True)
response = app.update(payload)
```

</div>
