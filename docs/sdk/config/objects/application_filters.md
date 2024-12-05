# Application Filters Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Application Filter Model Attributes](#application-filter-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Application Filters](#creating-application-filters)
    - [Retrieving Application Filters](#retrieving-application-filters)
    - [Updating Application Filters](#updating-application-filters)
    - [Listing Application Filters](#listing-application-filters)
    - [Deleting Application Filters](#deleting-application-filters)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `ApplicationFilters` class provides functionality to manage application filter definitions in Palo Alto Networks'
Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and
deleting
application filters that help organize and filter applications based on various criteria like categories, risk levels,
and behaviors.

## Core Methods

| Method     | Description                       | Parameters                                   | Return Type                             |
|------------|-----------------------------------|----------------------------------------------|-----------------------------------------|
| `create()` | Creates a new filter              | `data: Dict[str, Any]`                       | `ApplicationFiltersResponseModel`       |
| `get()`    | Retrieves a filter by ID          | `object_id: str`                             | `ApplicationFiltersResponseModel`       |
| `update()` | Updates an existing filter        | `application: ApplicationFiltersUpdateModel` | `ApplicationFiltersResponseModel`       |
| `delete()` | Deletes a filter                  | `object_id: str`                             | `None`                                  |
| `list()`   | Lists filters with filtering      | `folder: str`, `**filters`                   | `List[ApplicationFiltersResponseModel]` |
| `fetch()`  | Gets filter by name and container | `name: str`, `folder: str`                   | `ApplicationFiltersResponseModel`       |

## Application Filter Model Attributes

| Attribute                   | Type      | Required | Description                                 |
|-----------------------------|-----------|----------|---------------------------------------------|
| `name`                      | str       | Yes      | Name of filter (max 31 chars)               |
| `id`                        | UUID      | Yes*     | Unique identifier (*response only)          |
| `category`                  | List[str] | No       | List of application categories              |
| `sub_category`              | List[str] | No       | List of application subcategories           |
| `technology`                | List[str] | No       | List of application technologies            |
| `risk`                      | List[int] | No       | List of risk levels (1-5)                   |
| `folder`                    | str       | Yes**    | Folder location (**one container required)  |
| `snippet`                   | str       | Yes**    | Snippet location (**one container required) |
| `evasive`                   | bool      | No       | Filter evasive applications                 |
| `used_by_malware`           | bool      | No       | Filter malware-associated apps              |
| `transfers_files`           | bool      | No       | Filter file-transferring apps               |
| `has_known_vulnerabilities` | bool      | No       | Filter apps with vulnerabilities            |
| `tunnels_other_apps`        | bool      | No       | Filter tunneling applications               |
| `prone_to_misuse`           | bool      | No       | Filter misuse-prone applications            |
| `pervasive`                 | bool      | No       | Filter pervasive applications               |
| `is_saas`                   | bool      | No       | Filter SaaS applications                    |
| `new_appid`                 | bool      | No       | Filter new applications                     |
| `saas_risk`                 | List[str] | No       | Filter by SaaS risk levels                  |
| `saas_certifications`       | List[str] | No       | Filter by SaaS certifications               |

## Exceptions

| Exception                    | HTTP Code | Description                   |
|------------------------------|-----------|-------------------------------|
| `InvalidObjectError`         | 400       | Invalid filter data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters   |
| `NameNotUniqueError`         | 409       | Filter name already exists    |
| `ObjectNotPresentError`      | 404       | Filter not found              |
| `ReferenceNotZeroError`      | 409       | Filter still referenced       |
| `AuthenticationError`        | 401       | Authentication failed         |
| `ServerError`                | 500       | Internal server error         |

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
# High-risk applications filter
high_risk_filter = {
    "name": "high-risk-apps",
    "category": ["business-systems", "collaboration"],
    "risk": [4, 5],
    "folder": "Texas",
    "has_known_vulnerabilities": True,
    "used_by_malware": True
}

# Create high-risk filter
high_risk = app_filters.create(high_risk_filter)

# SaaS applications filter
saas_filter = {
    "name": "saas-apps",
    "folder": "Texas",
    "is_saas": True,
    "saas_risk": ["high", "medium"],
    "saas_certifications": ["soc2", "iso27001"]
}

# Create SaaS filter
saas = app_filters.create(saas_filter)
```

</div>

### Retrieving Application Filters

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
filter_obj = app_filters.fetch(name="high-risk-apps", folder="Texas")
print(f"Found filter: {filter_obj.name}")

# Get by ID
filter_by_id = app_filters.get(filter_obj.id)
print(f"Retrieved filter: {filter_by_id.name}")
print(f"Risk levels: {filter_by_id.risk}")
```

</div>

### Updating Application Filters

<div class="termy">

<!-- termynal -->

```python
# Fetch existing filter
existing_filter = app_filters.fetch(name="high-risk-apps", folder="Texas")

# Update filter criteria
existing_filter.risk = [3, 4, 5]
existing_filter.category.append("networking")
existing_filter.prone_to_misuse = True
existing_filter.tunnels_other_apps = True

# Perform update
updated_filter = app_filters.update(existing_filter)
```

</div>

### Listing Application Filters

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_results = app_filters.list(
    folder='Texas',
    category=['business-systems'],
    risk=[4, 5]
)

# Process results
for filter_obj in filtered_results:
    print(f"Name: {filter_obj.name}")
    print(f"Categories: {filter_obj.category}")
    print(f"Risk levels: {filter_obj.risk}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "technology": ["client-server"],
    "subcategory": ["database"]
}

# List with filters as kwargs
filtered_results = app_filters.list(**list_params)
```

</div>

### Deleting Application Filters

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
filter_id = "123e4567-e89b-12d3-a456-426655440000"
app_filters.delete(filter_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated application filters",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = app_filters.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
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
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

try:
    # Create filter configuration
    filter_config = {
        "name": "test-filter",
        "category": ["business-systems"],
        "risk": [4, 5],
        "folder": "Texas",
        "has_known_vulnerabilities": True
    }

    # Create the filter
    new_filter = app_filters.create(filter_config)

    # Commit changes
    result = app_filters.commit(
        folders=["Texas"],
        description="Added test filter",
        sync=True
    )

    # Check job status
    status = app_filters.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid filter data: {e.message}")
except NameNotUniqueError as e:
    print(f"Filter name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Filter not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Filter still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Filter Definition**
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
    - Use specific criteria combinations
    - Consider filter evaluation impact
    - Cache frequently used filters
    - Monitor filter match counts

4. **Security**
    - Regularly review risk criteria
    - Update vulnerability flags
    - Monitor malware associations
    - Track certification status
    - Validate SaaS risks

5. **Maintenance**
    - Review filter effectiveness
    - Update criteria as needed
    - Remove unused filters
    - Document filter changes
    - Monitor filter usage

## Full Script Examples

Refer to
the [application_filters.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/application_filters.py).

## Related Models

- [ApplicationFiltersCreateModel](../../models/objects/application_filters_models.md#Overview)
- [ApplicationFiltersUpdateModel](../../models/objects/application_filters_models.md#Overview)
- [ApplicationFiltersResponseModel](../../models/objects/application_filters_models.md#Overview)
