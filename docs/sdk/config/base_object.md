# Base Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Base Object Attributes](#base-object-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Objects](#creating-objects)
    - [Retrieving Objects](#retrieving-objects)
    - [Updating Objects](#updating-objects)
    - [Listing Objects](#listing-objects)
    - [Deleting Objects](#deleting-objects)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `BaseObject` class serves as the foundation for all configuration objects in Palo Alto Networks' Strata Cloud Manager. This class provides standardized CRUD operations (Create, Read, Update, Delete) and job management functionality that is inherited by all configuration object types.

## Core Methods

| Method             | Description                   | Parameters                                           | Return Type             |
|--------------------|-------------------------------|------------------------------------------------------|-------------------------|
| `create()`         | Creates new object            | `data: Dict[str, Any]`                               | `Dict[str, Any]`        |
| `get()`            | Retrieves object by ID        | `object_id: str`                                     | `Dict[str, Any]`        |
| `update()`         | Updates existing object       | `data: Dict[str, Any]`                               | `Dict[str, Any]`        |
| `delete()`         | Deletes object                | `object_id: str`                                     | `None`                  |
| `list()`           | Lists objects with filtering  | `**filters`                                          | `List[Dict[str, Any]]`  |
| `list_jobs()`      | Lists jobs with pagination    | `limit: int`, `offset: int`, `parent_id: str`        | `JobListResponse`       |
| `get_job_status()` | Gets job status               | `job_id: str`                                        | `JobStatusResponse`     |
| `commit()`         | Commits configuration changes | `folders: List[str]`, `description: str`, `**kwargs` | `CandidatePushResponse` |

## Base Object Attributes

| Attribute    | Type | Required | Description                             |
|--------------|------|----------|-----------------------------------------|
| `ENDPOINT`   | str  | Yes      | API endpoint path for object operations |
| `api_client` | Scm  | Yes      | Instance of SCM API client              |

## Exceptions

| Exception                    | HTTP Code | Description                   |
|------------------------------|-----------|-------------------------------|
| `InvalidObjectError`         | 400       | Invalid object data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters   |
| `NotFoundError`              | 404       | Object not found              |
| `AuthenticationError`        | 401       | Authentication failed         |
| `AuthorizationError`         | 403       | Permission denied             |
| `ConflictError`              | 409       | Object conflict               |
| `ServerError`                | 500       | Internal server error         |

## Basic Configuration

The BaseObject service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Most objects can be accessed directly through the client
# Example: client.address, client.service_group, client.security_rule, etc.
```

</div>

### Traditional Service Instantiation (Legacy)

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.objects import BaseObject

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# For custom or extended objects, you can use the BaseObject approach
class CustomObject(BaseObject):
   ENDPOINT = "/config/objects/v1/custom"

# Initialize custom object
custom_obj = CustomObject(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Objects

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient
from scm.config.objects import BaseObject
from scm.exceptions import InvalidObjectError

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create custom object class
class CustomObject(BaseObject):
   ENDPOINT = "/config/objects/v1/custom"

# Initialize custom object
custom_obj = CustomObject(client)

# Prepare object data
object_data = {
   "name": "test-object",
   "description": "Test object creation",
   "folder": "Texas"
}

# Create new object
try:
   new_object = custom_obj.create(object_data)
   print(f"Created object with ID: {new_object['id']}")
except InvalidObjectError as e:
   print(f"Invalid object data: {e.message}")
```

</div>

### Retrieving Objects

<div class="termy">

<!-- termynal -->
```python
# Get object by ID
try:
   object_id = "123e4567-e89b-12d3-a456-426655440000"
   retrieved_object = custom_obj.get(object_id)
   print(f"Retrieved object: {retrieved_object['name']}")
except NotFoundError as e:
   print(f"Object not found: {e.message}")
```

</div>

### Updating Objects

<div class="termy">

<!-- termynal -->
```python
# Update object data
update_data = {
   "id": "123e4567-e89b-12d3-a456-426655440000",
   "name": "updated-object",
   "description": "Updated description",
   "folder": "Texas"
}

# Perform update
try:
   updated_object = custom_obj.update(update_data)
   print(f"Updated object: {updated_object['name']}")
except InvalidObjectError as e:
   print(f"Invalid update data: {e.message}")
```

</div>

### Listing Objects

<div class="termy">

<!-- termynal -->
```python
# Define filter parameters
list_params = {
   "folder": "Texas",
   "limit": 100,
   "offset": 0
}

# List objects with filters
try:
   objects = custom_obj.list(**list_params)
   for obj in objects:
      print(f"Name: {obj['name']}")
except InvalidObjectError as e:
   print(f"Invalid filter parameters: {e.message}")
```

</div>

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters,
you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control 
which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

<div class="termy">

<!-- termynal -->
```python
# Only return objects defined exactly in 'Texas'
exact_objects = custom_obj.list(
   folder='Texas',
   exact_match=True
)

for obj in exact_objects:
   print(f"Exact match: {obj['name']} in {obj['folder']}")

# Exclude all objects from the 'All' folder
no_all_objects = custom_obj.list(
   folder='Texas',
   exclude_folders=['All']
)

for obj in no_all_objects:
   assert obj['folder'] != 'All'
   print(f"Filtered out 'All': {obj['name']}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

<div class="termy">

<!-- termynal -->
```python
# Initialize a custom object with a specified max_limit
custom_obj = CustomObject(client, max_limit=4321)

# List all objects, which will paginate in chunks of 4321
all_objects = custom_obj.list(folder='Texas')
```

</div>

### Deleting Objects

<div class="termy">

<!-- termynal -->
```python
# Delete object by ID
try:
   object_id = "123e4567-e89b-12d3-a456-426655440000"
   custom_obj.delete(object_id)
   print("Object deleted successfully")
except NotFoundError as e:
   print(f"Object not found: {e.message}")
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
   "description": "Configuration update",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit changes directly on the client
try:
   result = client.commit(**commit_params)
   print(f"Commit job ID: {result.job_id}")
except InvalidObjectError as e:
   print(f"Invalid commit parameters: {e.message}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->
```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
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
from scm.config.objects import BaseObject
from scm.exceptions import (
   InvalidObjectError,
   NotFoundError,
   AuthenticationError,
   ServerError
)

# Initialize client and custom object
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)
custom_obj = CustomObject(client)

try:
   # Attempt operation
   result = custom_obj.create({
      "name": "test-object",
      "folder": "Texas"
   })

   # Commit changes
   commit_result = client.commit(
      folders=["Texas"],
      description="Added test object",
      sync=True
   )

   # Check job status
   status = client.get_job_status(commit_result.job_id)

except InvalidObjectError as e:
   print(f"Invalid object data: {e.message}")
except NotFoundError as e:
   print(f"Object not found: {e.message}")
except AuthenticationError as e:
   print(f"Authentication failed: {e.message}")
except ServerError as e:
   print(f"Server error: {e.message}")
```

</div>

## Best Practices

1. **Client Usage**
   - Prefer the unified client interface (`client.object_name`) for standard objects
   - Only use the BaseObject approach for custom extensions or advanced use cases
   - Perform commits directly on the client (`client.commit()`)
   - Monitor jobs using client methods (`client.get_job_status()`, `client.list_jobs()`)
   - Initialize the client once and reuse across different object types

2. **Object Initialization** (when using BaseObject directly)
   - Define ENDPOINT in all subclasses
   - Validate api_client type
   - Use proper error handling
   - Initialize logging appropriately

3. **CRUD Operations**
   - Validate input data before operations
   - Handle response data consistently
   - Implement proper error handling
   - Use appropriate timeouts

4. **Job Management**
   - Monitor commit job status
   - Handle job failures appropriately
   - Use sync mode judiciously
   - Implement proper timeout handling

5. **Error Handling**
   - Catch specific exceptions first
   - Log error details
   - Provide meaningful error messages
   - Implement proper retry logic

6. **Performance**
   - Reuse object instances
   - Configure appropriate pagination limits during client initialization
   - Batch operations when possible
   - Cache frequently accessed data

## Full Script Examples

Refer to the [examples](https://github.com/cdot65/pan-scm-sdk/tree/main/examples) directory.

## Related Models

- [JobStatusResponse](../../models/operations/jobs.md)
- [JobListResponse](../../models/operations/jobs.md)
- [CandidatePushResponseModel](../../models/operations/candidate_push.md)
