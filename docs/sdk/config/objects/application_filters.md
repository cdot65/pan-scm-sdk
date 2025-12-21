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
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
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

| Method     | Description                       | Parameters                                                              | Return Type                             |
|------------|-----------------------------------|-------------------------------------------------------------------------|-----------------------------------------|
| `create()` | Creates a new filter              | `data: Dict[str, Any]`                                                  | `ApplicationFiltersResponseModel`       |
| `get()`    | Retrieves a filter by ID          | `object_id: str`                                                        | `ApplicationFiltersResponseModel`       |
| `update()` | Updates an existing filter        | `application: ApplicationFiltersUpdateModel`                            | `ApplicationFiltersResponseModel`       |
| `delete()` | Deletes a filter                  | `object_id: str`                                                        | `None`                                  |
| `list()`   | Lists filters with filtering      | `folder: str`, `snippet: str`, `exact_match: bool`, `**filters`         | `List[ApplicationFiltersResponseModel]` |
| `fetch()`  | Gets filter by name and container | `name: str`, `folder: str`, `snippet: str`                              | `ApplicationFiltersResponseModel`       |

## Application Filter Model Attributes

| Attribute                   | Type      | Required | Default | Description                                 |
|-----------------------------|-----------|----------|---------|---------------------------------------------|
| `name`                      | str       | Yes      | None    | Name of filter (max 31 chars)               |
| `id`                        | UUID      | Yes*     | None    | Unique identifier (*response only)          |
| `category`                  | List[str] | No       | None    | List of application categories              |
| `sub_category`              | List[str] | No       | None    | List of application subcategories           |
| `technology`                | List[str] | No       | None    | List of application technologies            |
| `risk`                      | List[int] | No       | None    | List of risk levels (1-5)                   |
| `folder`                    | str       | Yes**    | None    | Folder location (**one container required)  |
| `snippet`                   | str       | Yes**    | None    | Snippet location (**one container required) |
| `evasive`                   | bool      | No       | False   | Filter evasive applications                 |
| `used_by_malware`           | bool      | No       | False   | Filter malware-associated apps              |
| `transfers_files`           | bool      | No       | False   | Filter file-transferring apps               |
| `has_known_vulnerabilities` | bool      | No       | False   | Filter apps with vulnerabilities            |
| `tunnels_other_apps`        | bool      | No       | False   | Filter tunneling applications               |
| `prone_to_misuse`           | bool      | No       | False   | Filter misuse-prone applications            |
| `pervasive`                 | bool      | No       | False   | Filter pervasive applications               |
| `is_saas`                   | bool      | No       | False   | Filter SaaS applications                    |
| `new_appid`                 | bool      | No       | False   | Filter new applications                     |
| `excessive_bandwidth_use`   | bool      | No       | False   | Filter apps using excessive bandwidth       |
| `saas_risk`                 | List[str] | No       | None    | Filter by SaaS risk levels                  |
| `saas_certifications`       | List[str] | No       | None    | Filter by SaaS certifications               |
| `exclude`                   | List[str] | No       | None    | List of applications to exclude             |
| `tag`                       | List[str] | No       | None    | Tags associated with the filter             |

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

```python
    from scm.client import ScmClient

    # Initialize client using the unified client approach
    client = ScmClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id"
    )

    # Access the application_filters module directly through the client
    # client.application_filter is automatically initialized for you
```

You can also use the traditional approach if preferred:

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

## Usage Examples

### Creating Application Filters

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
    high_risk = client.application_filter.create(high_risk_filter)

    # SaaS applications filter
    saas_filter = {
        "name": "saas-apps",
        "folder": "Texas",
        "is_saas": True,
        "saas_risk": ["high", "medium"],
        "saas_certifications": ["soc2", "iso27001"]
    }

    # Create SaaS filter
    saas = client.application_filter.create(saas_filter)
```

### Retrieving Application Filters

```python
    # Fetch by name and folder
    filter_obj = client.application_filter.fetch(name="high-risk-apps", folder="Texas")
    print(f"Found filter: {filter_obj.name}")

    # Get by ID
    filter_by_id = client.application_filter.get(filter_obj.id)
    print(f"Retrieved filter: {filter_by_id.name}")
    print(f"Risk levels: {filter_by_id.risk}")
```

### Updating Application Filters

```python
    # Fetch existing filter
    existing_filter = client.application_filter.fetch(name="high-risk-apps", folder="Texas")

    # Update filter criteria
    existing_filter.risk = [3, 4, 5]
    existing_filter.category.append("networking")
    existing_filter.prone_to_misuse = True
    existing_filter.tunnels_other_apps = True

    # Perform update
    updated_filter = client.application_filter.update(existing_filter)
```

### Listing Application Filters

```python
    # List with direct filter parameters
    filtered_results = client.application_filter.list(
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
    filtered_results = client.application_filter.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results. Alongside basic filters
(like `category`, `subcategory`, `technology`, and `risk`), you can leverage `exact_match`, `exclude_folders`, and
`exclude_snippets` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder` or `snippet`) are returned.
- `exclude_folders (List[str])`: List of folder names to exclude from results.
- `exclude_snippets (List[str])`: List of snippet values to exclude from results.

```python
    # Only return filters defined exactly in 'Texas'
    exact_filters = client.application_filter.list(
        folder='Texas',
        exact_match=True
    )

    for f in exact_filters:
        print(f"Exact match: {f.name} in {f.folder}")

    # Exclude all filters from the 'All' folder
    no_all_filters = client.application_filter.list(
        folder='Texas',
        exclude_folders=['All']
    )

    for f in no_all_filters:
        assert f.folder != 'All'
        print(f"Filtered out 'All': {f.name}")

    # Exclude filters that come from 'default' snippet
    no_default_snippet = client.application_filter.list(
        folder='Texas',
        exclude_snippets=['default']
    )

    for f in no_default_snippet:
        assert f.snippet != 'default'
        print(f"Filtered out 'default' snippet: {f.name}")

    # Combine exact_match with exclusions
    combined_filters = client.application_filter.list(
        folder='Texas',
        exact_match=True,
        exclude_folders=['All'],
        exclude_snippets=['default']
    )

    for f in combined_filters:
        print(f"Combined filters result: {f.name} in {f.folder}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Configure max_limit on the application_filter service
client.application_filter.max_limit = 4321

# List all filters - auto-paginates through results
all_filters = client.application_filter.list(folder='Texas')

# The list() method will retrieve up to 4321 objects per API call (max 5000)
# and auto-paginate through all available objects.
```

### Deleting Application Filters

```python
    # Delete by ID
    filter_id = "123e4567-e89b-12d3-a456-426655440000"
    client.application_filter.delete(filter_id)
```

## Managing Configuration Changes

### Performing Commits

```python
    # Prepare commit parameters
    commit_params = {
        "folders": ["Texas"],
        "description": "Updated application filters",
        "sync": True,
        "timeout": 300  # 5 minute timeout
    }

    # Commit the changes directly on the client
    # Note: All commit operations should be performed on the client directly
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
    from scm.exceptions import (
        InvalidObjectError,
        MissingQueryParameterError,
        NameNotUniqueError,
        ObjectNotPresentError,
        ReferenceNotZeroError
    )

    # Initialize client
    client = ScmClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id"
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

        # Create the filter using the unified client
        new_filter = client.application_filter.create(filter_config)

        # Commit changes directly on the client
        result = client.commit(
            folders=["Texas"],
            description="Added test filter",
            sync=True
        )

        # Check job status on the client
        status = client.get_job_status(result.job_id)

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

## Best Practices

1. **Client Usage**
    - Use the unified `ScmClient` approach for simpler code
    - Access application filters operations via `client.application_filter` property
    - Perform commit operations directly on the client
    - Monitor jobs directly on the client
    - Set appropriate max_limit parameters for large datasets using `application_filters_max_limit`

2. **Filter Definition**
    - Use descriptive filter names
    - Combine multiple criteria effectively
    - Keep filters focused and specific
    - Document filter purposes
    - Review and update regularly

3. **Container Management**
    - Always specify exactly one container (folder or snippet)
    - Use consistent container names
    - Validate container existence
    - Group related filters

4. **Performance**
    - Avoid overly broad filters
    - Use specific criteria combinations
    - Consider filter evaluation impact
    - Cache frequently used filters
    - Monitor filter match counts

5. **Security**
    - Regularly review risk criteria
    - Update vulnerability flags
    - Monitor malware associations
    - Track certification status
    - Validate SaaS risks

6. **Maintenance**
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
