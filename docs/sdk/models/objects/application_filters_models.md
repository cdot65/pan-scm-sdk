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
and behavioral
characteristics.

## Core Methods

| Method     | Description                  | Parameters                              | Return Type                             |
|------------|------------------------------|-----------------------------------------|-----------------------------------------|
| `create()` | Creates a new filter         | `data: Dict[str, Any]`                  | `ApplicationFiltersResponseModel`       |
| `get()`    | Retrieves a filter by ID     | `object_id: str`                        | `ApplicationFiltersResponseModel`       |
| `update()` | Updates an existing filter   | `filter: ApplicationFiltersUpdateModel` | `ApplicationFiltersResponseModel`       |
| `delete()` | Deletes a filter             | `object_id: str`                        | `None`                                  |
| `list()`   | Lists filters with filtering | `folder: str`, `**filters`              | `List[ApplicationFiltersResponseModel]` |

## Application Filters Model Attributes

| Attribute                   | Type      | Required | Description                                  |
|-----------------------------|-----------|----------|----------------------------------------------|
| `name`                      | str       | Yes      | Name of filter (max 31 chars)                |
| `id`                        | UUID      | No*      | Unique identifier (*response only)           |
| `category`                  | List[str] | No       | List of application categories               |
| `sub_category`              | List[str] | No       | List of application subcategories            |
| `technology`                | List[str] | No       | List of technologies                         |
| `risk`                      | List[int] | No       | List of risk levels                          |
| `evasive`                   | bool      | No       | Filter for evasive applications              |
| `used_by_malware`           | bool      | No       | Filter for applications used by malware      |
| `transfers_files`           | bool      | No       | Filter for file transfer applications        |
| `has_known_vulnerabilities` | bool      | No       | Filter for applications with vulnerabilities |
| `tunnels_other_apps`        | bool      | No       | Filter for tunneling applications            |
| `prone_to_misuse`           | bool      | No       | Filter for applications prone to misuse      |
| `pervasive`                 | bool      | No       | Filter for pervasive applications            |
| `is_saas`                   | bool      | No       | Filter for SaaS applications                 |
| `new_appid`                 | bool      | No       | Filter for applications with new AppID       |
| `saas_certifications`       | List[str] | No       | Filter by SaaS certifications                |
| `saas_risk`                 | List[str] | No       | Filter by SaaS risk levels                   |
| `folder`                    | str       | Yes**    | Folder location (**one container required)   |
| `snippet`                   | str       | Yes**    | Snippet location (**one container required)  |

\* Optional in create/update operations, required in response
\** Exactly one container type (folder/snippet) must be provided

## Exceptions

The Application Filters models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet) are specified
    - When no container type is specified for create operations
    - When invalid values are provided for boolean fields
    - When list fields contain invalid or duplicate values

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import ApplicationFilters

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize ApplicationFilters object
app_filters = ApplicationFilters(client)
```

</div>

## Usage Examples

### Creating Application Filters

<div class="termy">

<!-- termynal -->

```python
# Basic filter configuration
basic_filter = {
    "name": "high-risk-apps",
    "risk": [4, 5],
    "has_known_vulnerabilities": True,
    "folder": "Security"
}

# Create basic filter
basic_filter_obj = app_filters.create(basic_filter)

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
saas_filter_obj = app_filters.create(saas_filter)
```

</div>

### Retrieving Application Filters

<div class="termy">

<!-- termynal -->

```python
# Fetch by ID
filter_id = "123e4567-e89b-12d3-a456-426655440000"
filter_obj = app_filters.get(filter_id)
print(f"Retrieved filter: {filter_obj.name}")

# Fetch by name and folder
filter_obj = app_filters.fetch(name="high-risk-apps", folder="Security")
print(f"Found filter: {filter_obj.name}")
print(f"Risk levels: {filter_obj.risk}")
print(f"Has vulnerabilities: {filter_obj.has_known_vulnerabilities}")
```

</div>

### Updating Application Filters

<div class="termy">

<!-- termynal -->

```python
# Update filter configuration
update_filter = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "high-risk-apps-updated",
    "risk": [3, 4, 5],
    "has_known_vulnerabilities": True,
    "used_by_malware": True
}

# Perform update
updated_filter = app_filters.update(update_filter)
```

</div>

### Listing Application Filters

<div class="termy">

<!-- termynal -->

```python
# List all filters in a folder
all_filters = app_filters.list(folder="Security")

# Process results
for filter_obj in all_filters:
    print(f"Name: {filter_obj.name}")
    if filter_obj.risk:
        print(f"Risk levels: {filter_obj.risk}")
    if filter_obj.category:
        print(f"Categories: {', '.join(filter_obj.category)}")

# List with specific criteria
saas_filters = app_filters.list(
    folder="Cloud",
    is_saas=True,
    transfers_files=True
)

# List with multiple filter parameters
high_risk_filters = app_filters.list(
    folder="Security",
    risk=[4, 5],
    has_known_vulnerabilities=True
)
```

</div>

### Deleting Application Filters

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
filter_id = "123e4567-e89b-12d3-a456-426655440000"

try:
    app_filters.delete(filter_id)
    print(f"Successfully deleted filter {filter_id}")
except ObjectNotPresentError:
    print("Filter not found")
except ReferenceNotZeroError:
    print("Filter is still referenced by security policies")
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Security", "Cloud"],
    "description": "Updated application filters",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
try:
    result = app_filters.commit(**commit_params)
    print(f"Commit job ID: {result.job_id}")
except CommitInProgressError:
    print("Another commit is already in progress")
except CommitFailedError as e:
    print(f"Commit failed: {str(e)}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = app_filters.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = app_filters.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")

# Wait for job completion
try:
    app_filters.wait_for_job(result.job_id, timeout=300)
    print("Configuration changes applied successfully")
except JobTimeoutError:
    print("Job timed out waiting for completion")
except JobFailedError as e:
    print(f"Job failed: {str(e)}")
```

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ApplicationFiltersCreateModel

try:
    # This will raise a validation error
    invalid_filter = ApplicationFiltersCreateModel(
        name="invalid-filter",
        risk=[6],  # Invalid risk level
        folder="Security",
        snippet="MySnippet"  # Can't specify both folder and snippet
    )
except ValueError as e:
    print(f"Validation error: {str(e)}")

try:
    # This will raise a validation error for missing container
    invalid_filter = ApplicationFiltersCreateModel(
        name="invalid-filter",
        risk=[3, 4]
        # No folder or snippet specified
    )
except ValueError as e:
    print(f"Validation error: {str(e)}")
```

</div>

## Error Handling {#error-handling}

Application Filters models implement validation to ensure correct data:

- Container validation ensures exactly one container type (folder/snippet) is specified
- Name validation enforces length and character constraints
- Field validation ensures risk levels are within range (1-5)
- Boolean fields are properly formatted

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
