# Route Access List

The `RouteAccessList` class manages route access list objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete route access lists. These lists define permit or deny rules based on source and destination addresses with optional wildcard masks, used to filter routes in routing protocol configurations.

## Class Overview

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the Route Access List service directly through the client
route_access_lists = client.route_access_list
```

| Method     | Description                                                    | Parameters                                                                                                                       | Return Type                          |
|------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| `create()` | Creates a new route access list                                | `data: Dict[str, Any]`                                                                                                           | `RouteAccessListResponseModel`       |
| `get()`    | Retrieves a route access list by its unique ID                 | `object_id: str`                                                                                                                 | `RouteAccessListResponseModel`       |
| `update()` | Updates an existing route access list                          | `resource: RouteAccessListUpdateModel`                                                                                           | `RouteAccessListResponseModel`       |
| `list()`   | Lists route access lists with optional filtering               | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[RouteAccessListResponseModel]` |
| `fetch()`  | Fetches a single route access list by name within a container  | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `RouteAccessListResponseModel`       |
| `delete()` | Deletes a route access list by its ID                          | `object_id: str`                                                                                                                 | `None`                               |

### Route Access List Model Attributes

| Attribute     | Type                  | Required | Default | Description                                         |
|---------------|-----------------------|----------|---------|-----------------------------------------------------|
| `name`        | str                   | Yes      | None    | Route access list name                              |
| `id`          | UUID                  | Yes*     | None    | Unique identifier (*response/update only)           |
| `description` | str                   | No       | None    | Description                                         |
| `type`        | RouteAccessListType   | No       | None    | Access list type configuration                      |
| `folder`      | str                   | No**     | None    | Folder location. Max 64 chars                       |
| `snippet`     | str                   | No**     | None    | Snippet location. Max 64 chars                      |
| `device`      | str                   | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

### IPv4 Access List Configuration

The `type` attribute wraps IPv4 access list entries that define permit/deny rules.

#### RouteAccessListType

| Attribute | Type                | Required | Description             |
|-----------|---------------------|----------|-------------------------|
| `ipv4`    | RouteAccessListIpv4 | No       | IPv4 access list        |

#### RouteAccessListIpv4

| Attribute    | Type                           | Required | Description              |
|--------------|--------------------------------|----------|--------------------------|
| `ipv4_entry` | List[RouteAccessListIpv4Entry] | No       | IPv4 access list entries |

#### RouteAccessListIpv4Entry

| Attribute             | Type                             | Required | Description                        |
|-----------------------|----------------------------------|----------|------------------------------------|
| `name`                | int                              | No       | Sequence number (1-65535)          |
| `action`              | str                              | No       | Action: "deny" or "permit"         |
| `source_address`      | RouteAccessListSourceAddress     | No       | Source address configuration       |
| `destination_address` | RouteAccessListDestinationAddress| No       | Destination address configuration  |

#### RouteAccessListSourceAddress

| Attribute  | Type | Required | Description                |
|------------|------|----------|----------------------------|
| `address`  | str  | No       | Source IP address          |
| `wildcard` | str  | No       | Source IP wildcard mask    |

#### RouteAccessListDestinationAddress

| Attribute  | Type | Required | Description                     |
|------------|------|----------|---------------------------------|
| `address`  | str  | No       | Destination IP address          |
| `wildcard` | str  | No       | Destination IP wildcard mask    |

### Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Access list name already exists                                               |
| `ObjectNotPresentError`      | 404       | Access list not found                                                         |
| `ReferenceNotZeroError`      | 409       | Access list still referenced                                                  |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Methods

### List Route Access Lists

```python
# List all route access lists in a folder
access_lists = client.route_access_list.list(
   folder="Texas"
)

# Process results
for acl in access_lists:
   print(f"Name: {acl.name}")
   if acl.description:
      print(f"  Description: {acl.description}")
```

#### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters,
you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control
which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return access lists defined exactly in 'Texas'
exact_acls = client.route_access_list.list(
   folder='Texas',
   exact_match=True
)

for acl in exact_acls:
   print(f"Exact match: {acl.name} in {acl.folder}")

# Exclude all access lists from the 'All' folder
no_all_acls = client.route_access_list.list(
   folder='Texas',
   exclude_folders=['All']
)

for acl in no_all_acls:
   assert acl.folder != 'All'
   print(f"Filtered out 'All': {acl.name}")
```

#### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.route_access_list.max_limit = 4000

# List all access lists - auto-paginates through results
all_acls = client.route_access_list.list(folder='Texas')
```

### Fetch a Route Access List

```python
# Fetch by name and folder
acl = client.route_access_list.fetch(
   name="internal-networks",
   folder="Texas"
)
print(f"Found access list: {acl.name}")
if acl.type and acl.type.ipv4 and acl.type.ipv4.ipv4_entry:
   for entry in acl.type.ipv4.ipv4_entry:
      print(f"  Seq {entry.name}: {entry.action}")

# Get by ID
acl_by_id = client.route_access_list.get(acl.id)
print(f"Retrieved access list: {acl_by_id.name}")
```

### Create a Route Access List

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a route access list with permit and deny entries
acl_data = {
   "name": "internal-networks",
   "description": "Allow internal network routes",
   "type": {
      "ipv4": {
         "ipv4_entry": [
            {
               "name": 10,
               "action": "permit",
               "source_address": {
                  "address": "10.0.0.0",
                  "wildcard": "0.255.255.255"
               }
            },
            {
               "name": 20,
               "action": "permit",
               "source_address": {
                  "address": "172.16.0.0",
                  "wildcard": "0.15.255.255"
               }
            },
            {
               "name": 100,
               "action": "deny",
               "source_address": {
                  "address": "0.0.0.0",
                  "wildcard": "255.255.255.255"
               }
            }
         ]
      }
   },
   "folder": "Texas"
}

new_acl = client.route_access_list.create(acl_data)
print(f"Created route access list with ID: {new_acl.id}")

# Create a simple permit-all access list
permit_all_data = {
   "name": "permit-all-routes",
   "description": "Permit all routes",
   "type": {
      "ipv4": {
         "ipv4_entry": [
            {
               "name": 10,
               "action": "permit",
               "source_address": {
                  "address": "0.0.0.0",
                  "wildcard": "255.255.255.255"
               }
            }
         ]
      }
   },
   "folder": "Texas"
}

permit_all = client.route_access_list.create(permit_all_data)
print(f"Created permit-all access list with ID: {permit_all.id}")
```

### Update a Route Access List

```python
# Fetch existing access list
existing_acl = client.route_access_list.fetch(
   name="internal-networks",
   folder="Texas"
)

# Add a new entry for 192.168.0.0/16
existing_acl.type.ipv4.ipv4_entry.append({
   "name": 30,
   "action": "permit",
   "source_address": {
      "address": "192.168.0.0",
      "wildcard": "0.0.255.255"
   }
})

# Perform update
updated_acl = client.route_access_list.update(existing_acl)
```

### Delete a Route Access List

```python
# Delete by ID
acl_id = "123e4567-e89b-12d3-a456-426655440000"
client.route_access_list.delete(acl_id)
```

## Use Cases

#### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated route access list configurations",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

#### Monitoring Jobs

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
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
   # Create route access list
   acl_config = {
      "name": "test-acl",
      "type": {
         "ipv4": {
            "ipv4_entry": [
               {
                  "name": 10,
                  "action": "permit",
                  "source_address": {
                     "address": "10.0.0.0",
                     "wildcard": "0.255.255.255"
                  }
               }
            ]
         }
      },
      "folder": "Texas"
   }

   new_acl = client.route_access_list.create(acl_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added route access list",
      sync=True
   )

   # Check job status
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid access list data: {e.message}")
except NameNotUniqueError as e:
   print(f"Access list name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Access list not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Access list still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Related Topics

- [RouteAccessListBaseModel](../../models/network/route_access_list_models.md#Overview)
- [RouteAccessListCreateModel](../../models/network/route_access_list_models.md#Overview)
- [RouteAccessListUpdateModel](../../models/network/route_access_list_models.md#Overview)
- [RouteAccessListResponseModel](../../models/network/route_access_list_models.md#Overview)
- [RouteAccessListIpv4Entry](../../models/network/route_access_list_models.md#Overview)
