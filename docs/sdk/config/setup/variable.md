# Variable Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Variable Model Attributes](#variable-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Variables](#creating-variables)
    - [Retrieving Variables](#retrieving-variables)
    - [Fetching a Variable by Name](#fetching-a-variable-by-name)
    - [Updating Variables](#updating-variables)
    - [Listing Variables](#listing-variables)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Variables](#deleting-variables)
7. [Container Associations](#container-associations)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Variable` class provides methods for creating, retrieving, updating, and deleting variable resources in Palo Alto Networks' Strata Cloud Manager. Variables are used to define reusable values that can be referenced across configurations. The API supports advanced filtering, pagination, and container associations (folder, snippet, or device).

## Core Methods

| Method     | Description                     | Parameters                      | Return Type                      |
|------------|-------------------------------|----------------------------------|---------------------------------|
| `create()` | Creates a new variable          | `data: Dict[str, Any]`           | `VariableResponseModel`          |
| `get()`    | Retrieves a variable by ID      | `variable_id: Union[str, UUID]`  | `VariableResponseModel`          |
| `update()` | Updates an existing variable    | `variable: VariableUpdateModel`  | `VariableResponseModel`          |
| `delete()` | Deletes a variable              | `variable_id: Union[str, UUID]`  | `None`                           |
| `list()`   | Lists variables with filtering  | `**filters`                      | `List[VariableResponseModel]`    |
| `fetch()`  | Gets a variable by its name     | `name: str, folder: str`         | `Optional[VariableResponseModel]`|

## Variable Model Attributes

| Attribute       | Type      | Required | Default | Description                                              |
|-----------------|-----------|----------|---------|----------------------------------------------------------|
| `name`          | str       | Yes      | None    | Name of the variable. Max length: 63 chars               |
| `type`          | str       | Yes      | None    | Variable type (see Variable Types below)                 |
| `value`         | str       | Yes      | None    | Value of the variable                                    |
| `id`            | UUID      | Yes*     | None    | Unique identifier (*response/update only)                |
| `description`   | str       | No       | None    | Optional description of the variable                     |
| `folder`        | str       | No**     | None    | Folder in which the variable is defined. Max: 64 chars   |
| `snippet`       | str       | No**     | None    | Snippet in which the variable is defined. Max: 64 chars  |
| `device`        | str       | No**     | None    | Device in which the variable is defined. Max: 64 chars   |
| `overridden`    | bool      | No       | None    | Indicates if the variable is overridden (response only)  |
| `labels`        | List[str] | No       | None    | Optional list of labels (response only)                  |
| `parent`        | str       | No       | None    | Parent folder or container (response only)               |
| `snippets`      | List[str] | No       | None    | Snippets associated with the variable (response only)    |
| `model`         | str       | No       | None    | Device model information (response only)                 |
| `serial_number` | str       | No       | None    | Device serial number (response only)                     |
| `device_only`   | bool      | No       | None    | Whether variable is device-only (response only)          |

\* Only required for response and update models

\*\* Exactly one of `folder`, `snippet`, or `device` must be provided

### Variable Types

The `type` field must be one of the following values:

| Type            | Description                    |
|-----------------|--------------------------------|
| `percent`       | Percentage value               |
| `count`         | Count/number value             |
| `ip-netmask`    | IP address with subnet mask    |
| `zone`          | Security zone                  |
| `ip-range`      | IP address range               |
| `ip-wildcard`   | IP wildcard mask               |
| `device-priority` | Device priority value        |
| `device-id`     | Device identifier              |
| `egress-max`    | Maximum egress value           |
| `as-number`     | AS number                      |
| `fqdn`          | Fully qualified domain name    |
| `port`          | Port number                    |
| `link-tag`      | Link tag                       |
| `group-id`      | Group identifier               |
| `rate`          | Rate value                     |
| `router-id`     | Router identifier              |
| `qos-profile`   | QoS profile                    |
| `timer`         | Timer value                    |

### Filter Parameters

The `list()` method supports the following filters:

| Parameter       | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `folder`        | str        | Filter by folder (server-side)           |
| `labels`        | List[str]  | Filter by labels (client-side, any match)|
| `parent`        | str        | Filter by parent (client-side, exact)    |
| `type`          | str        | Filter by type (client-side, exact)      |
| `snippets`      | List[str]  | Filter by snippets (client-side, any)    |
| `model`         | str        | Filter by device model (client-side)     |
| `serial_number` | str        | Filter by serial number (client-side)    |
| `device_only`   | bool       | Filter device-only entries (client-side) |

## Exceptions

| Exception                | HTTP Code | Description                                   |
|--------------------------|-----------|-----------------------------------------------|
| `InvalidObjectError`     | 400       | Invalid variable data or format               |
| `ObjectNotPresentError`  | 404       | Requested variable not found                  |
| `APIError`               | Various   | General API communication error               |
| `AuthenticationError`    | 401       | Authentication failed                         |
| `ServerError`            | 500       | Internal server error                         |

## Basic Configuration

The Variable service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Variable service directly through the client
# No need to create a separate Variable instance
variables = client.variable
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.setup.variable import Variable

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Variable object explicitly
variables = Variable(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Variables
```python
variable_data = {
    "name": "subnet-variable",
    "type": "ip-netmask",
    "value": "192.168.1.0/24",
    "description": "Network subnet for department A",
    "folder": "department-a"  # One of folder, snippet, or device must be provided
}
created = variables.create(variable_data)
print(created.id, created.name, created.value)
```

### Retrieving Variables
```python
variable = variables.get("12345678-1234-1234-1234-123456789012")
print(variable.name, variable.type, variable.value)
```

### Fetching a Variable by Name
```python
variable_by_name = variables.fetch(name="subnet-variable", folder="department-a")
if variable_by_name:
    print(variable_by_name.id, variable_by_name.value)
```

### Updating Variables

```python
# Fetch existing variable
existing = client.variable.fetch(name="subnet-variable", folder="department-a")

# Modify attributes using dot notation
existing.value = "10.0.0.0/16"  # Updated value
existing.description = "Updated network subnet"

# Pass modified object to update()
updated = client.variable.update(existing)
print(f"Updated value: {updated.value}")
```

### Listing Variables
```python
all_variables = variables.list()
ip_variables = variables.list(type="ip-netmask")
folder_variables = variables.list(parent="department-a")
```

### Filtering Responses
```python
# Filter variables by type
ip_variables = variables.list(type="ip-netmask")

# Filter variables by labels
labeled_variables = variables.list(labels=["network"])

# Filter variables by parent folder
folder_variables = variables.list(parent="department-a")

# Filter variables by snippet
snippet_variables = variables.list(snippets=["security-snippet"])

# Filter by device model
model_variables = variables.list(model="PA-VM")

# Filter by device serial number
device_variables = variables.list(serial_number="001122334455")

# Filter device-only variables
device_only_variables = variables.list(device_only=True)
```

### Controlling Pagination with max_limit

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.variable.max_limit = 100

# List all variables - auto-paginates through results
all_variables = client.variable.list()

# The variables are fetched in chunks according to the max_limit setting.
```

### Deleting Variables
```python
variables.delete("12345678-1234-1234-1234-123456789012")
```

## Container Associations

Variables must be associated with exactly one container type:

```python
# Variable associated with a folder
folder_variable = {
    "name": "folder-var",
    "type": "ip-netmask",
    "value": "192.168.1.0/24",
    "folder": "department-a"
}
variables.create(folder_variable)

# Variable associated with a snippet
snippet_variable = {
    "name": "snippet-var",
    "type": "port",
    "value": "8080",
    "snippet": "web-servers"
}
variables.create(snippet_variable)

# Variable associated with a device
device_variable = {
    "name": "device-var",
    "type": "ip-netmask",
    "value": "10.0.0.1/32",
    "device": "001122334455"
}
variables.create(device_variable)
```

## Error Handling

```python
from scm.exceptions import ObjectNotPresentError, InvalidObjectError
try:
    variables.get("nonexistent-id")
except ObjectNotPresentError:
    print("Variable not found!")

try:
    # Missing required container (folder, snippet, or device)
    variables.create({
        "name": "invalid-var",
        "type": "ip-netmask",
        "value": "192.168.1.0/24"
    })
except InvalidObjectError as e:
    print("Validation error:", e)
```

## Best Practices
- Always provide exactly one container field (`folder`, `snippet`, or `device`).
- Use appropriate variable types for values (e.g., "ip-netmask" for IP addresses with subnet masks).
- Use labels to organize and filter variables.
- Handle exceptions for robust automation.
- Use pagination (`max_limit`) for large variable sets.

## Full Script Examples

```python
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError

# Initialize the client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Create a new IP variable
    variable_data = {
        "name": "web-servers",
        "type": "ip-netmask",
        "value": "10.0.1.0/24",
        "description": "Web server subnet",
        "folder": "web-infrastructure",
    }
    new_variable = client.variable.create(variable_data)
    print(f"Created variable: {new_variable.id}")
    print(f"Name: {new_variable.name}")
    print(f"Type: {new_variable.type}")
    print(f"Value: {new_variable.value}")

    # Update the variable with a new value using fetch → update workflow
    existing = client.variable.fetch(name="web-servers", folder="web-infrastructure")
    existing.value = "10.0.1.0/23"  # Updated subnet
    existing.description = "Updated web server subnet"
    updated = client.variable.update(existing)
    print(f"Updated value: {updated.value}")

    # List all variables of a specific type
    print("Listing all IP variables:")
    ip_variables = client.variable.list(type="ip-netmask")
    for var in ip_variables:
        print(f"- {var.name}: {var.value}")

    # Delete a variable
    client.variable.delete(new_variable.id)
    print(f"Deleted variable: {new_variable.id}")

except InvalidObjectError as e:
    print(f"Invalid variable data: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Related Models

- [VariableBaseModel](../../models/setup/variable_models.md#Overview)
- [VariableCreateModel](../../models/setup/variable_models.md#Overview)
- [VariableUpdateModel](../../models/setup/variable_models.md#Overview)
- [VariableResponseModel](../../models/setup/variable_models.md#Overview)
