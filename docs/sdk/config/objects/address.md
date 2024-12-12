# Address Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Address Model Attributes](#address-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Address Objects](#creating-address-objects)
    - [Retrieving Addresses](#retrieving-addresses)
    - [Updating Addresses](#updating-addresses)
    - [Listing Addresses](#listing-addresses)
    - [Filtering Responses](#filtering-responses)
    - [Deleting Addresses](#deleting-addresses)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Address` class provides functionality to manage address objects in Palo Alto Networks' Strata Cloud Manager. This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting address objects
of various types including IP/Netmask, IP Range, IP Wildcard, and FQDN (Fully Qualified Domain Name).

## Core Methods

| Method     | Description                        | Parameters                    | Return Type                  |
|------------|------------------------------------|-------------------------------|------------------------------|
| `create()` | Creates a new address object       | `data: Dict[str, Any]`        | `AddressResponseModel`       |
| `get()`    | Retrieves an address by ID         | `object_id: str`              | `AddressResponseModel`       |
| `update()` | Updates an existing address        | `address: AddressUpdateModel` | `AddressResponseModel`       |
| `delete()` | Deletes an address                 | `object_id: str`              | `None`                       |
| `list()`   | Lists addresses with filtering     | `folder: str`, `**filters`    | `List[AddressResponseModel]` |
| `fetch()`  | Gets address by name and container | `name: str`, `folder: str`    | `AddressResponseModel`       |

## Address Model Attributes

| Attribute     | Type      | Required     | Description                                 |
|---------------|-----------|--------------|---------------------------------------------|
| `name`        | str       | Yes          | Name of address object (max 63 chars)       |
| `id`          | UUID      | Yes*         | Unique identifier (*response only)          |
| `ip_netmask`  | str       | One Required | IP address with CIDR notation               |
| `ip_range`    | str       | One Required | IP address range format                     |
| `ip_wildcard` | str       | One Required | IP wildcard mask format                     |
| `fqdn`        | str       | One Required | Fully qualified domain name                 |
| `description` | str       | No           | Object description (max 1023 chars)         |
| `tag`         | List[str] | No           | List of tags (max 64 chars each)            |
| `folder`      | str       | Yes**        | Folder location (**one container required)  |
| `snippet`     | str       | Yes**        | Snippet location (**one container required) |
| `device`      | str       | Yes**        | Device location (**one container required)  |

## Exceptions

| Exception                    | HTTP Code | Description                    |
|------------------------------|-----------|--------------------------------|
| `InvalidObjectError`         | 400       | Invalid address data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters    |
| `NameNotUniqueError`         | 409       | Address name already exists    |
| `ObjectNotPresentError`      | 404       | Address not found              |
| `ReferenceNotZeroError`      | 409       | Address still referenced       |
| `AuthenticationError`        | 401       | Authentication failed          |
| `ServerError`                | 500       | Internal server error          |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Address object
addresses = Address(client)
```

</div>

## Usage Examples

### Creating Address Objects

<div class="termy">

<!-- termynal -->

```python
# Prepare IP/Netmask address configuration
netmask_config = {
    "name": "internal_network",
    "ip_netmask": "192.168.1.0/24",
    "description": "Internal network segment",
    "folder": "Texas",
    "tag": ["Python", "Automation"]
}

# Create the address object
netmask_address = addresses.create(netmask_config)

# Prepare FQDN address configuration
fqdn_config = {
    "name": "example_site",
    "fqdn": "example.com",
    "folder": "Texas",
    "description": "Example website"
}

# Create the FQDN address object
fqdn_address = addresses.create(fqdn_config)

# Prepare IP Range address configuration
range_config = {
    "name": "dhcp_pool",
    "ip_range": "192.168.1.100-192.168.1.200",
    "folder": "Texas",
    "description": "DHCP address pool"
}

# Create the IP Range address object
range_address = addresses.create(range_config)
```

</div>

### Retrieving Addresses

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
address = addresses.fetch(name="internal_network", folder="Texas")
print(f"Found address: {address.name}")

# Get by ID
address_by_id = addresses.get(address.id)
print(f"Retrieved address: {address_by_id.name}")
```

</div>

### Updating Addresses

<div class="termy">

<!-- termynal -->

```python
# Fetch existing address
existing_address = addresses.fetch(name="internal_network", folder="Texas")

# Update specific attributes
existing_address.description = "Updated network segment"
existing_address.tag = ["Network", "Internal", "Updated"]

# Perform update
updated_address = addresses.update(existing_address)
```

</div>

### Listing Addresses

<div class="termy">

<!-- termynal -->

```python
# Pass filters directly into the list method
filtered_addresses = addresses.list(
    folder='Texas',
    types=['fqdn'],
    tags=['Automation']
)

# Process results
for addr in filtered_addresses:
    print(f"Name: {addr.name}, Value: {addr.fqdn}")

# Define filter parameters as a dictionary
list_params = {
    "folder": "Texas",
    "types": ["netmask"],
    "tags": ["Production"]
}

# List addresses with filters as kwargs
filtered_addresses = addresses.list(**list_params)

# Process results
for addr in filtered_addresses:
    print(f"Name: {addr.name}, Value: {addr.ip_netmask}")
```

</div>

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**
- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

<div class="termy">

<!-- termynal -->

```python
# Only return addresses defined exactly in 'Texas'
exact_addresses = addresses.list(
  folder='Texas',
  exact_match=True
)

for addr in exact_addresses:
  print(f"Exact match: {addr.name} in {addr.folder}")

# Exclude all addresses from the 'All' folder
no_all_addresses = addresses.list(
  folder='Texas',
  exclude_folders=['All']
)

for addr in no_all_addresses:
  assert addr.folder != 'All'
  print(f"Filtered out 'All': {addr.name}")

# Exclude addresses that come from 'default' snippet
no_default_snippet = addresses.list(
  folder='Texas',
  exclude_snippets=['default']
)

for addr in no_default_snippet:
  assert addr.snippet != 'default'
  print(f"Filtered out 'default' snippet: {addr.name}")

# Exclude addresses associated with 'DeviceA'
no_deviceA = addresses.list(
  folder='Texas',
  exclude_devices=['DeviceA']
)

for addr in no_deviceA:
  assert addr.device != 'DeviceA'
  print(f"Filtered out 'DeviceA': {addr.name}")

# Combine exact_match with multiple exclusions
combined_filters = addresses.list(
  folder='Texas',
  exact_match=True,
  exclude_folders=['All'],
  exclude_snippets=['default'],
  exclude_devices=['DeviceA']
)

for addr in combined_filters:
  print(f"Combined filters result: {addr.name} in {addr.folder}")
```

</div>

### Deleting Addresses

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
address_id = "123e4567-e89b-12d3-a456-426655440000"
addresses.delete(address_id)
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
    "description": "Added new network addresses",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = addresses.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = addresses.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = addresses.list_jobs(limit=10)
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
    ObjectNotPresentError
)

try:
    # Create address configuration
    address_config = {
        "name": "test_address",
        "ip_netmask": "192.168.1.0/24",
        "folder": "Texas",
        "description": "Test network segment",
        "tag": ["Test"]
    }

    # Create the address
    new_address = addresses.create(address_config)

    # Commit changes
    result = addresses.commit(
        folders=["Texas"],
        description="Added test address",
        sync=True
    )

    # Check job status
    status = addresses.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid address data: {e.message}")
except NameNotUniqueError as e:
    print(f"Address name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Address not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names across operations
    - Validate container existence before operations

2. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

3. **Address Types**
    - Specify exactly one address type per object
    - Use appropriate address format for each type
    - Validate address formats before creation
    - Consider FQDN resolution time in automation scripts

4. **Performance**
    - Reuse client instances
    - Use appropriate pagination for list operations
    - Implement proper retry mechanisms
    - Cache frequently accessed objects

5. **Security**
    - Follow least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication handling

## Full script examples

Refer to
the [address.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/address.py).

## Related Models

- [AddressCreateModel](../../models/objects/address_models.md#Overview)
- [AddressUpdateModel](../../models/objects/address_models.md#Overview)
- [AddressResponseModel](../../models/objects/address_models.md#Overview)