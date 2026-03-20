# Application Filters Models

Pydantic models for managing application filter objects in Strata Cloud Manager.

## Overview

The Application Filters models provide a structured way to manage application filters in Palo Alto Networks' Strata
Cloud Manager.
These models support filtering applications based on various criteria including categories, technologies, risk levels,
and behavioral characteristics.

## Models

| Model                             | Purpose                                          |
|-----------------------------------|--------------------------------------------------|
| `ApplicationFiltersBaseModel`     | Base model with common fields for all operations |
| `ApplicationFiltersCreateModel`   | Model for creating new application filters       |
| `ApplicationFiltersUpdateModel`   | Model for updating existing application filters  |
| `ApplicationFiltersResponseModel` | Model for API responses                          |

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute                   | Type      | Required | Default | Description                                  |
|-----------------------------|-----------|----------|---------|----------------------------------------------|
| `name`                      | str       | Yes      | None    | Name of filter (max 31 chars)                |
| `id`                        | UUID      | No*      | None    | Unique identifier (*response only)           |
| `category`                  | List[str] | No       | None    | List of application categories               |
| `sub_category`              | List[str] | No       | None    | List of application subcategories            |
| `technology`                | List[str] | No       | None    | List of technologies                         |
| `risk`                      | List[int] | No       | None    | List of risk levels                          |
| `evasive`                   | bool      | No       | False   | Filter for evasive applications              |
| `used_by_malware`           | bool      | No       | False   | Filter for applications used by malware      |
| `transfers_files`           | bool      | No       | False   | Filter for file transfer applications        |
| `has_known_vulnerabilities` | bool      | No       | False   | Filter for applications with vulnerabilities |
| `tunnels_other_apps`        | bool      | No       | False   | Filter for tunneling applications            |
| `prone_to_misuse`           | bool      | No       | False   | Filter for applications prone to misuse      |
| `pervasive`                 | bool      | No       | False   | Filter for pervasive applications            |
| `is_saas`                   | bool      | No       | False   | Filter for SaaS applications                 |
| `new_appid`                 | bool      | No       | False   | Filter for applications with new AppID       |
| `excessive_bandwidth_use`   | bool      | No       | False   | Filter for apps using excessive bandwidth    |
| `saas_certifications`       | List[str] | No       | None    | Filter by SaaS certifications                |
| `saas_risk`                 | List[str] | No       | None    | Filter by SaaS risk levels                   |
| `exclude`                   | List[str] | No       | None    | List of applications to exclude              |
| `tag`                       | List[str] | No       | None    | Tags associated with the filter              |
| `folder`                    | str       | Yes**    | None    | Folder location (**one container required)   |
| `snippet`                   | str       | Yes**    | None    | Snippet location (**one container required)  |

\* Optional in create/update operations, present in response
\** Exactly one container type (folder/snippet) must be provided

## Exceptions

The Application Filters models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet) are specified
    - When no container type is specified for create operations
    - When invalid values are provided for boolean fields
    - When list fields contain invalid or duplicate values

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.objects import ApplicationFiltersCreateModel

# Error: multiple containers specified
try:
    invalid_filter = ApplicationFiltersCreateModel(
        name="invalid-filter",
        risk=[4, 5],
        folder="Security",
        snippet="MySnippet"  # Can't specify both folder and snippet
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder' or 'snippet' must be provided."

# Error: no container specified
try:
    invalid_filter = ApplicationFiltersCreateModel(
        name="invalid-filter",
        risk=[3, 4]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder' or 'snippet' must be provided."
```

## Usage Examples

### Creating Application Filters

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Basic filter configuration
basic_filter = {
    "name": "high-risk-apps",
    "risk": [4, 5],
    "has_known_vulnerabilities": True,
    "folder": "Security"
}

# Create basic filter
basic_filter_obj = client.application_filter.create(basic_filter)

# Advanced filter configuration
saas_filter = {
    "name": "risky-saas",
    "is_saas": True,
    "category": ["collaboration", "file-sharing"],
    "risk": [3, 4, 5],
    "transfers_files": True,
    "folder": "Cloud"
}

# Create SaaS filter
saas_filter_obj = client.application_filter.create(saas_filter)
```

### Updating Application Filters

```python
# Fetch existing filter
existing = client.application_filter.fetch(name="high-risk-apps", folder="Security")

# Modify attributes using dot notation
existing.risk = [3, 4, 5]
existing.has_known_vulnerabilities = True
existing.used_by_malware = True

# Pass modified object to update()
updated = client.application_filter.update(existing)
```

### Parsing Application Filters Response

```python
from scm.models.objects import ApplicationFiltersResponseModel

# Parse API response
response = ApplicationFiltersResponseModel(**api_response)
print(f"Name: {response.name}")
if response.risk:
    print(f"Risk levels: {response.risk}")
if response.category:
    print(f"Categories: {', '.join(response.category)}")
```
