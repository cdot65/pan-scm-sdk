# Application Group Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Application Group Model Attributes](#application-group-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Application Groups](#creating-application-groups)
    - [Retrieving Application Groups](#retrieving-application-groups)
    - [Updating Application Groups](#updating-application-groups)
    - [Listing Application Groups](#listing-application-groups)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Application Groups](#deleting-application-groups)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `ApplicationGroup` class provides functionality to manage application groups in Palo Alto Networks' Strata Cloud
Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting
application groups that organize collections of applications for use in security policies.

## Core Methods

| Method     | Description                   | Parameters                               | Return Type                           |
|------------|-------------------------------|------------------------------------------|---------------------------------------|
| `create()` | Creates a new app group       | `data: Dict[str, Any]`                   | `ApplicationGroupResponseModel`       |
| `get()`    | Retrieves a group by ID       | `object_id: str`                         | `ApplicationGroupResponseModel`       |
| `update()` | Updates an existing group     | `app_group: ApplicationGroupUpdateModel` | `ApplicationGroupResponseModel`       |
| `delete()` | Deletes a group               | `object_id: str`                         | `None`                                |
| `list()`   | Lists groups with filtering   | `folder: str`, `**filters`               | `List[ApplicationGroupResponseModel]` |
| `fetch()`  | Gets group by name and folder | `name: str`, `folder: str`               | `ApplicationGroupResponseModel`       |

## Application Group Model Attributes

| Attribute | Type      | Required | Description                                 |
|-----------|-----------|----------|---------------------------------------------|
| `name`    | str       | Yes      | Name of group (max 63 chars)                |
| `id`      | UUID      | Yes*     | Unique identifier (*response only)          |
| `members` | List[str] | Yes      | List of application names                   |
| `folder`  | str       | Yes**    | Folder location (**one container required)  |
| `snippet` | str       | Yes**    | Snippet location (**one container required) |
| `device`  | str       | Yes**    | Device location (**one container required)  |

## Exceptions

| Exception                    | HTTP Code | Description                        |
|------------------------------|-----------|------------------------------------|
| `InvalidObjectError`         | 400       | Invalid group data or format       |
| `MissingQueryParameterError` | 400       | Missing required parameters        |
| `NameNotUniqueError`         | 409       | Group name already exists          |
| `ObjectNotPresentError`      | 404       | Group not found                    |
| `ReferenceNotZeroError`      | 409       | Group still referenced by policies |
| `AuthenticationError`        | 401       | Authentication failed              |
| `ServerError`                | 500       | Internal server error              |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
    from scm.client import ScmClient

    # Initialize client using the unified client approach
    client = ScmClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id"
    )

    # Access the application_group module directly through the client
    # client.application_group is automatically initialized for you
```

</div>

You can also use the traditional approach if preferred:

```python
    from scm.client import Scm
    from scm.config.objects import ApplicationGroup

    # Initialize client
    client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id"
    )

    # Initialize ApplicationGroup object
    application_groups = ApplicationGroup(client)
```

## Usage Examples

### Creating Application Groups

<div class="termy">

<!-- termynal -->

```python
    # Basic application group configuration
    basic_group = {
        "name": "web-apps",
        "members": ["ssl", "web-browsing"],
        "folder": "Texas"
    }

    # Create basic group
    basic_group_obj = client.application_group.create(basic_group)

    # Microsoft 365 application group
    ms365_group = {
        "name": "microsoft-365",
        "members": [
            "ms-office365",
            "ms-exchange-online",
            "ms-sharepoint-online"
        ],
        "folder": "Texas"
    }

    # Create Microsoft 365 group
    ms365_group_obj = client.application_group.create(ms365_group)
```

</div>

### Retrieving Application Groups

<div class="termy">

<!-- termynal -->

```python
    # Fetch by name and folder
    group = client.application_group.fetch(name="web-apps", folder="Texas")
    print(f"Found group: {group.name}")

    # Get by ID
    group_by_id = client.application_group.get(group.id)
    print(f"Retrieved group: {group_by_id.name}")
    print(f"Members: {', '.join(group_by_id.members)}")
```

</div>

### Updating Application Groups

<div class="termy">

<!-- termynal -->

```python
    # Fetch existing group
    existing_group = client.application_group.fetch(name="web-apps", folder="Texas")

    # Update members
    existing_group.members = ["ssl", "web-browsing", "dns"]

    # Perform update
    updated_group = client.application_group.update(existing_group)
```

</div>

### Listing Application Groups

<div class="termy">

<!-- termynal -->

```python
    # List with direct filter parameters
    filtered_groups = client.application_group.list(
        folder='Texas',
        members=['ssl']
    )

    # Process results
    for group in filtered_groups:
        print(f"Name: {group.name}")
        print(f"Members: {', '.join(group.members)}")

    # Define filter parameters as dictionary
    list_params = {
        "folder": "Texas",
        "members": ["ms-office365"]
    }

    # List with filters as kwargs
    filtered_groups = client.application_group.list(**list_params)
```

</div>

### Filtering Responses

<div class="termy">

<!-- termynal -->

```python
    # Only return application groups defined exactly in 'Texas'
    exact_application_groups = client.application_group.list(
      folder='Texas',
      exact_match=True
    )

    for app in exact_application_groups:
        print(f"Exact match: {app.name} in {app.folder}")

    # Exclude all application groups from the 'All' folder
    no_all_application_groups = client.application_group.list(
      folder='Texas',
      exclude_folders=['All']
    )

    for app in no_all_application_groups:
        assert app.folder != 'All'
        print(f"Filtered out 'All': {app.name}")

    # Exclude application groups that come from 'default' snippet
    no_default_snippet = client.application_group.list(
      folder='Texas',
      exclude_snippets=['default']
    )

    for app in no_default_snippet:
        assert app.snippet != 'default'
        print(f"Filtered out 'default' snippet: {app.name}")

    # Exclude application groups associated with 'DeviceA'
    no_deviceA = client.application_group.list(
      folder='Texas',
      exclude_devices=['DeviceA']
    )

    for app in no_deviceA:
        assert app.device != 'DeviceA'
        print(f"Filtered out 'DeviceA': {app.name}")

    # Combine exact_match with multiple exclusions
    combined_filters = client.application_group.list(
      folder='Texas',
      exact_match=True,
      exclude_folders=['All'],
      exclude_snippets=['default'],
      exclude_devices=['DeviceA']
    )

    for app in combined_filters:
        print(f"Combined filters result: {app.name} in {app.folder}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

<div class="termy">

<!-- termynal -->

```python
    # Initialize the ScmClient with a custom max_limit for application groups
    # This will retrieve up to 4321 objects per API call, up to the API limit of 5000.
    client = ScmClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        application_group_max_limit=4321
    )

    # Now when we call list(), it will use the specified max_limit for each request
    # while auto-paginating through all available objects.
    all_groups = client.application_group.list(folder='Texas')

    # 'all_groups' contains all objects from 'Texas', fetched in chunks of up to 4321 at a time.
```

</div>

### Deleting Application Groups

<div class="termy">

<!-- termynal -->

```python
    # Delete by ID
    group_id = "123e4567-e89b-12d3-a456-426655440000"
    client.application_group.delete(group_id)
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
        "description": "Updated application groups",
        "sync": True,
        "timeout": 300  # 5 minute timeout
    }

    # Commit the changes directly on the client
    # Note: All commit operations should be performed on the client directly
    result = client.commit(**commit_params)

    print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
    # Get status of specific job directly on the client
    job_status = client.get_job_status(result.job_id)
    print(f"Job status: {job_status.data[0].status_str}")

    # List recent jobs directly on the client
    recent_jobs = client.list_jobs(limit=10)
    for job in recent_jobs.data:
        print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

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
        # Create group configuration
        group_config = {
            "name": "test_group",
            "members": ["ssl", "web-browsing"],
            "folder": "Texas"
        }

        # Create the group using the unified client
        new_group = client.application_group.create(group_config)

        # Commit changes directly on the client
        result = client.commit(
            folders=["Texas"],
            description="Added test group",
            sync=True
        )

        # Check job status on the client
        status = client.get_job_status(result.job_id)

    except InvalidObjectError as e:
        print(f"Invalid group data: {e.message}")
    except NameNotUniqueError as e:
        print(f"Group name already exists: {e.message}")
    except ObjectNotPresentError as e:
        print(f"Group not found: {e.message}")
    except ReferenceNotZeroError as e:
        print(f"Group still in use: {e.message}")
    except MissingQueryParameterError as e:
        print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified `ScmClient` approach for simpler code
    - Access application group operations via `client.application_group` property
    - Perform commit operations directly on the client
    - Monitor jobs directly on the client
    - Set appropriate max_limit parameters for large datasets using `application_group_max_limit`

2. **Group Management**
    - Use descriptive group names
    - Organize related applications together
    - Keep member lists current
    - Document group purposes
    - Review group memberships regularly

3. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names
    - Validate container existence
    - Group related configurations

4. **Error Handling**
    - Implement comprehensive error handling
    - Check job status after commits
    - Handle specific exceptions
    - Log error details
    - Monitor commit status

5. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed groups
    - Implement proper retry logic
    - Batch related changes

5. **Security**
    - Follow the least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication
    - Monitor policy references

## Full Script Examples

Refer to
the [application_group.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/application_group.py).

## Related Models

- [ApplicationGroupCreateModel](../../models/objects/application_group_models.md#Overview)
- [ApplicationGroupUpdateModel](../../models/objects/application_group_models.md#Overview)
- [ApplicationGroupResponseModel](../../models/objects/application_group_models.md#Overview)
