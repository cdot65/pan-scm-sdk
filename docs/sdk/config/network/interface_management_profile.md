# Interface Management Profile

The `InterfaceManagementProfile` class manages interface management profile objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete interface management profiles. These profiles control which management services (HTTP, HTTPS, SSH, Telnet, ping, etc.) are accessible on a firewall interface.

## Class Overview

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the Interface Management Profile service directly through the client
profiles = client.interface_management_profile
```

| Method     | Description                                                                | Parameters                                                                                                                       | Return Type                                    |
|------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| `create()` | Creates a new interface management profile                                 | `data: Dict[str, Any]`                                                                                                           | `InterfaceManagementProfileResponseModel`      |
| `get()`    | Retrieves an interface management profile by its unique ID                 | `object_id: str`                                                                                                                 | `InterfaceManagementProfileResponseModel`      |
| `update()` | Updates an existing interface management profile                           | `profile: InterfaceManagementProfileUpdateModel`                                                                                 | `InterfaceManagementProfileResponseModel`      |
| `list()`   | Lists interface management profiles with optional filtering                | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[InterfaceManagementProfileResponseModel]` |
| `fetch()`  | Fetches a single interface management profile by name within a container   | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `InterfaceManagementProfileResponseModel`      |
| `delete()` | Deletes an interface management profile by its ID                          | `object_id: str`                                                                                                                 | `None`                                         |

### Interface Management Profile Model Attributes

| Attribute                       | Type           | Required      | Default | Description                                                 |
|---------------------------------|----------------|---------------|---------|-------------------------------------------------------------|
| `name`                          | str            | Yes           | None    | Profile name. Max 63 chars. Pattern: `^[0-9a-zA-Z._\- ]+$` |
| `id`                            | UUID           | Yes*          | None    | Unique identifier (*response/update only)                   |
| `http`                          | bool           | No            | None    | Enable HTTP management                                      |
| `https`                         | bool           | No            | None    | Enable HTTPS management                                     |
| `telnet`                        | bool           | No            | None    | Enable Telnet management                                    |
| `ssh`                           | bool           | No            | None    | Enable SSH management                                       |
| `ping`                          | bool           | No            | None    | Enable ping                                                 |
| `http_ocsp`                     | bool           | No            | None    | Enable HTTP OCSP (alias: `http-ocsp`)                       |
| `response_pages`                | bool           | No            | None    | Enable response pages (alias: `response-pages`)             |
| `userid_service`                | bool           | No            | None    | Enable User-ID service (alias: `userid-service`)            |
| `userid_syslog_listener_ssl`    | bool           | No            | None    | Enable User-ID syslog listener SSL (alias: `userid-syslog-listener-ssl`) |
| `userid_syslog_listener_udp`    | bool           | No            | None    | Enable User-ID syslog listener UDP (alias: `userid-syslog-listener-udp`) |
| `permitted_ip`                  | List[str]      | No            | None    | List of permitted IP addresses (alias: `permitted-ip`)      |
| `folder`                        | str            | No**          | None    | Folder location. Max 64 chars                               |
| `snippet`                       | str            | No**          | None    | Snippet location. Max 64 chars                              |
| `device`                        | str            | No**          | None    | Device location. Max 64 chars                               |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

!!! note
    Several fields use aliases with hyphens in the API (e.g., `http-ocsp`, `response-pages`, `userid-service`). The SDK models are configured with `populate_by_name=True`, so you can use either the Python attribute name (underscore) or the API alias (hyphen) when constructing dictionaries.

### Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Profile name already exists                                                   |
| `ObjectNotPresentError`      | 404       | Profile not found                                                             |
| `ReferenceNotZeroError`      | 409       | Profile still referenced by an interface                                      |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Methods

### List Interface Management Profiles

```python
# List all profiles in a folder
profiles = client.interface_management_profile.list(
   folder="Texas"
)

# Process results
for profile in profiles:
   print(f"Name: {profile.name}")
   print(f"  HTTPS: {profile.https}")
   print(f"  SSH: {profile.ssh}")
   print(f"  Ping: {profile.ping}")

# List with boolean filters
ssh_profiles = client.interface_management_profile.list(
   folder="Texas",
   ssh=True
)

for profile in ssh_profiles:
   print(f"SSH-enabled profile: {profile.name}")
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
# Only return profiles defined exactly in 'Texas'
exact_profiles = client.interface_management_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.interface_management_profile.list(
   folder='Texas',
   exclude_folders=['All']
)

for profile in no_all_profiles:
   assert profile.folder != 'All'
   print(f"Filtered out 'All': {profile.name}")
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
client.interface_management_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.interface_management_profile.list(folder='Texas')
```

### Fetch an Interface Management Profile

```python
# Fetch by name and folder
profile = client.interface_management_profile.fetch(
   name="allow-https-ssh",
   folder="Texas"
)
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.interface_management_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Create an Interface Management Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a profile that enables HTTPS and SSH management
profile_data = {
   "name": "allow-https-ssh",
   "https": True,
   "ssh": True,
   "ping": True,
   "permitted_ip": ["10.0.0.0/24", "192.168.1.0/24"],
   "folder": "Texas"
}

new_profile = client.interface_management_profile.create(profile_data)
print(f"Created profile with ID: {new_profile.id}")

# Create a profile with all management services enabled
full_mgmt_profile = {
   "name": "full-management",
   "http": True,
   "https": True,
   "ssh": True,
   "telnet": False,
   "ping": True,
   "http_ocsp": True,
   "response_pages": True,
   "userid_service": True,
   "userid_syslog_listener_ssl": True,
   "userid_syslog_listener_udp": False,
   "permitted_ip": ["10.0.0.0/8"],
   "folder": "Texas"
}

full_profile = client.interface_management_profile.create(full_mgmt_profile)
print(f"Created full management profile with ID: {full_profile.id}")
```

### Update an Interface Management Profile

```python
# Fetch existing profile
existing_profile = client.interface_management_profile.fetch(
   name="allow-https-ssh",
   folder="Texas"
)

# Enable additional management services
existing_profile.http = True
existing_profile.telnet = False

# Add more permitted IPs
if existing_profile.permitted_ip:
   existing_profile.permitted_ip.append("172.16.0.0/12")
else:
   existing_profile.permitted_ip = ["172.16.0.0/12"]

# Perform update
updated_profile = client.interface_management_profile.update(existing_profile)
```

### Delete an Interface Management Profile

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.interface_management_profile.delete(profile_id)
```

## Use Cases

#### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated interface management profiles",
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
   # Create profile configuration
   profile_config = {
      "name": "test-mgmt-profile",
      "https": True,
      "ssh": True,
      "ping": True,
      "permitted_ip": ["10.0.0.0/24"],
      "folder": "Texas"
   }

   # Create the profile using the unified client interface
   new_profile = client.interface_management_profile.create(profile_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Texas"],
      description="Added test interface management profile",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid profile data: {e.message}")
except NameNotUniqueError as e:
   print(f"Profile name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Profile not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Profile still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Related Topics

- [InterfaceManagementProfileBaseModel](../../models/network/interface_management_profile_models.md#Overview)
- [InterfaceManagementProfileCreateModel](../../models/network/interface_management_profile_models.md#Overview)
- [InterfaceManagementProfileUpdateModel](../../models/network/interface_management_profile_models.md#Overview)
- [InterfaceManagementProfileResponseModel](../../models/network/interface_management_profile_models.md#Overview)
