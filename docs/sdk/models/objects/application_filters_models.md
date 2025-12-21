# Application Filters Models

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Application Filters Model Attributes](#application-filters-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Application Filters](#creating-application-filters)
    - [Retrieving Application Filters](#retrieving-application-filters)
    - [Updating Application Filters](#updating-application-filters)
    - [Listing Application Filters](#listing-application-filters)
    - [Deleting Application Filters](#deleting-application-filters)
7. [Managing Configuration Changes](#managing-configuration-changes)
8. [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview {#Overview}
<span id="overview"></span>
<span id="error-handling"></span>
<span id="best-practices"></span>
<span id="related-models"></span>

The Application Filters models provide a structured way to manage application filters in Palo Alto Networks' Strata
Cloud Manager.
These models support filtering applications based on various criteria including categories, technologies, risk levels,
and behavioral characteristics.

### Models

| Model                             | Purpose                                          |
|-----------------------------------|--------------------------------------------------|
| `ApplicationFiltersBaseModel`     | Base model with common fields for all operations |
| `ApplicationFiltersCreateModel`   | Model for creating new application filters       |
| `ApplicationFiltersUpdateModel`   | Model for updating existing application filters  |
| `ApplicationFiltersResponseModel` | Model for API responses                          |

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Core Methods

| Method     | Description                       | Parameters                                      | Return Type                             |
|------------|-----------------------------------|-------------------------------------------------|-----------------------------------------|
| `create()` | Creates a new filter              | `data: Dict[str, Any]`                          | `ApplicationFiltersResponseModel`       |
| `get()`    | Retrieves a filter by ID          | `object_id: str`                                | `ApplicationFiltersResponseModel`       |
| `update()` | Updates an existing filter        | `application: ApplicationFiltersUpdateModel`    | `ApplicationFiltersResponseModel`       |
| `delete()` | Deletes a filter                  | `object_id: str`                                | `None`                                  |
| `list()`   | Lists filters with filtering      | `folder: str`, `snippet: str`, `**filters`      | `List[ApplicationFiltersResponseModel]` |
| `fetch()`  | Gets filter by name and container | `name: str`, `folder: str`, `snippet: str`      | `ApplicationFiltersResponseModel`       |

## Application Filters Model Attributes

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

## Basic Configuration

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the application_filter service directly through the client
# No need to create a separate ApplicationFilters instance
```

## Usage Examples

### Creating Application Filters

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
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

### Retrieving Application Filters

```python
# Fetch by ID
filter_id = "123e4567-e89b-12d3-a456-426655440000"
filter_obj = client.application_filter.get(filter_id)
print(f"Retrieved filter: {filter_obj.name}")

# Fetch by name and folder
filter_obj = client.application_filter.fetch(name="high-risk-apps", folder="Security")
print(f"Found filter: {filter_obj.name}")
print(f"Risk levels: {filter_obj.risk}")
print(f"Has vulnerabilities: {filter_obj.has_known_vulnerabilities}")
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

### Listing Application Filters

```python
# List all filters in a folder
all_filters = client.application_filter.list(folder="Security")

# Process results
for filter_obj in all_filters:
    print(f"Name: {filter_obj.name}")
    if filter_obj.risk:
        print(f"Risk levels: {filter_obj.risk}")
    if filter_obj.category:
        print(f"Categories: {', '.join(filter_obj.category)}")

# List with specific criteria
saas_filters = client.application_filter.list(
    folder="Cloud",
    is_saas=True,
    transfers_files=True
)

# List with multiple filter parameters
high_risk_filters = client.application_filter.list(
    folder="Security",
    risk=[4, 5],
    has_known_vulnerabilities=True
)
```

### Deleting Application Filters

```python
from scm.exceptions import ObjectNotPresentError, ReferenceNotZeroError

# Delete by ID
filter_id = "123e4567-e89b-12d3-a456-426655440000"

try:
    client.application_filter.delete(filter_id)
    print(f"Successfully deleted filter {filter_id}")
except ObjectNotPresentError:
    print("Filter not found")
except ReferenceNotZeroError:
    print("Filter is still referenced by security policies")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Security", "Cloud"],
    "description": "Updated application filters",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job directly on the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly on the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import InvalidObjectError, ValidationError

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # This will raise a validation error - can't specify both folder and snippet
    invalid_filter = {
        "name": "invalid-filter",
        "risk": [4, 5],
        "folder": "Security",
        "snippet": "MySnippet"
    }
    client.application_filter.create(invalid_filter)
except ValueError as e:
    print(f"Validation error: {str(e)}")

try:
    # This will raise a validation error for missing container
    invalid_filter = {
        "name": "invalid-filter",
        "risk": [3, 4]
        # No folder or snippet specified
    }
    client.application_filter.create(invalid_filter)
except ValueError as e:
    print(f"Validation error: {str(e)}")
```

## Model Validation {#error-handling}

Application Filters models implement validation to ensure correct data:

- Container validation ensures exactly one container type (folder/snippet) is specified
- Name validation enforces length (max 31 chars) and pattern constraints
- Boolean fields default to `False` if not specified

## Best Practices {#best-practices}

1. **Filter Design**
    - Use descriptive filter names
    - Combine multiple criteria effectively
    - Keep filters focused and specific
    - Document filter purposes
    - Review and update regularly

2. **Container Management**
    - Always specify exactly one container (folder or snippet)
    - Use consistent container names
    - Validate container existence
    - Group related filters

3. **Performance**
    - Avoid overly broad filters
    - Use specific criteria when possible
    - Consider impact on policy processing
    - Monitor filter match rates

4. **Security**
    - Regularly review high-risk filters
    - Monitor new application matches
    - Update risk criteria periodically
    - Document security implications

## Related Models {#related-models}

These models are defined within this module:

- ApplicationFiltersCreateModel - For creating new application filters
- ApplicationFiltersUpdateModel - For updating existing application filters
- ApplicationFiltersResponseModel - Response model containing application filter data
