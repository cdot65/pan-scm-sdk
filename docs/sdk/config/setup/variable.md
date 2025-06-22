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

| Attribute       | Type                | Required | Description                                              |
|-----------------|---------------------|----------|----------------------------------------------------------|
| `name`          | str                 | Yes      | Name of the variable (max 63 characters)                 |
| `type`          | str                 | Yes      | Variable type (e.g., "ip-netmask", "count", "percent")   |
| `value`         | str                 | Yes      | Value of the variable                                    |
| `id`            | UUID                | Yes*     | Unique identifier (*response only)                       |
| `description`   | Optional[str]       | No       | Optional description of the variable                     |
| `folder`        | Optional[str]       | No**     | Folder in which the variable is defined                  |
| `snippet`       | Optional[str]       | No**     | Snippet in which the variable is defined                 |
| `device`        | Optional[str]       | No**     | Device in which the variable is defined                  |
| `overridden`    | Optional[bool]      | No       | Indicates if the variable is overridden (response only)  |
| `labels`        | Optional[List[str]] | No       | Optional list of labels (response only)                  |
| `parent`        | Optional[str]       | No       | Parent folder or container (response only)               |
| `snippets`      | Optional[List[str]] | No       | Snippets associated with the variable (response only)    |
| `model`         | Optional[str]       | No       | Device model information (response only)                 |
| `serial_number` | Optional[str]       | No       | Device serial number (response only)                     |
| `device_only`   | Optional[bool]      | No       | Whether variable is device-only (response only)          |

** Exactly one of `folder`, `snippet`, or `device` must be provided

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
from scm.models.setup.variable import VariableUpdateModel
update_model = VariableUpdateModel(
    id="12345678-1234-1234-1234-123456789012",
    name="subnet-variable",
    type="ip-netmask",
    value="10.0.0.0/16",  # Updated value
    folder="department-a"
)
updated = variables.update(update_model)
print(updated.value)
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
variables = Variable(client, max_limit=100)
results = variables.list()
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
from scm.client import Scm
from scm.config.setup.variable import Variable
from scm.models.setup.variable import VariableUpdateModel
from scm.exceptions import APIError, InvalidObjectError

# Initialize the client and service
client = Scm(api_key="your-api-key")
variables = Variable(client)

try:
    # Create a new IP variable
    variable_data = {
        "name": "web-servers",
        "type": "ip-netmask",
        "value": "10.0.1.0/24",
        "description": "Web server subnet",
        "folder": "web-infrastructure",
    }
    new_variable = variables.create(variable_data)
    print(f"Created variable: {new_variable.id}")
    print(f"Name: {new_variable.name}")
    print(f"Type: {new_variable.type}")
    print(f"Value: {new_variable.value}")

    # Update the variable with a new value
    update_model = VariableUpdateModel(
        id=new_variable.id,
        name=new_variable.name,
        type=new_variable.type,
        value="10.0.1.0/23",  # Updated subnet
        description="Updated web server subnet",
        folder="web-infrastructure"
    )
    updated = variables.update(update_model)
    print(f"Updated value: {updated.value}")

    # List all variables of a specific type
    print("Listing all IP variables:")
    ip_variables = variables.list(type="ip-netmask")
    for var in ip_variables:
        print(f"- {var.name}: {var.value}")

except InvalidObjectError as e:
    print(f"Invalid variable data: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Related Models
- See [Variable Models](../../models/setup/variable_models.md) for model details.
