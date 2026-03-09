# Variable Configuration Object

Manages variable resources with flexible typing and container associations in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `Variable` class provides CRUD operations for variable resources used to define reusable values that can be referenced across configurations.

### Methods

| Method     | Description                    | Parameters                      | Return Type             |
|------------|--------------------------------|---------------------------------|-------------------------|
| `create()` | Creates a new variable         | `data: Dict[str, Any]`          | `VariableResponseModel` |
| `get()`    | Retrieves a variable by ID     | `variable_id: Union[str, UUID]` | `VariableResponseModel` |
| `update()` | Updates an existing variable   | `variable: VariableUpdateModel` | `VariableResponseModel` |
| `delete()` | Deletes a variable             | `variable_id: Union[str, UUID]` | `None`                  |
| `list()`   | Lists variables with filtering | `**filters`                     | `List[VariableResponseModel]` |
| `fetch()`  | Gets a variable by its name    | `name: str`, `folder: str`      | `VariableResponseModel` |

### Model Attributes

| Attribute       | Type      | Required | Default | Description                                             |
|-----------------|-----------|----------|---------|---------------------------------------------------------|
| `name`          | str       | Yes      | None    | Name of the variable. Max length: 63 chars              |
| `type`          | str       | Yes      | None    | Variable type (see Variable Types below)                |
| `value`         | str       | Yes      | None    | Value of the variable                                   |
| `id`            | UUID      | Yes*     | None    | Unique identifier (*response/update only)               |
| `description`   | str       | No       | None    | Optional description                                    |
| `folder`        | str       | No**     | None    | Folder in which the variable is defined. Max: 64 chars  |
| `snippet`       | str       | No**     | None    | Snippet in which the variable is defined. Max: 64 chars |
| `device`        | str       | No**     | None    | Device in which the variable is defined. Max: 64 chars  |
| `overridden`    | bool      | No       | None    | Whether the variable is overridden (response only)      |
| `labels`        | List[str] | No       | None    | Optional list of labels (response only)                 |

\* Only required for response and update models
\** Exactly one of `folder`, `snippet`, or `device` must be provided

#### Variable Types

| Type              | Description                 |
|-------------------|-----------------------------|
| `percent`         | Percentage value            |
| `count`           | Count/number value          |
| `ip-netmask`      | IP address with subnet mask |
| `zone`            | Security zone               |
| `ip-range`        | IP address range            |
| `ip-wildcard`     | IP wildcard mask            |
| `device-priority` | Device priority value       |
| `device-id`       | Device identifier           |
| `egress-max`      | Maximum egress value        |
| `as-number`       | AS number                   |
| `fqdn`            | Fully qualified domain name |
| `port`            | Port number                 |
| `link-tag`        | Link tag                    |
| `group-id`        | Group identifier            |
| `rate`            | Rate value                  |
| `router-id`       | Router identifier           |
| `qos-profile`     | QoS profile                 |
| `timer`           | Timer value                 |

### Exceptions

| Exception              | HTTP Code | Description                      |
|------------------------|-----------|----------------------------------|
| `InvalidObjectError`   | 400       | Invalid variable data or format  |
| `ObjectNotPresentError`| 404       | Requested variable not found     |
| `APIError`             | Various   | General API communication error  |
| `AuthenticationError`  | 401       | Authentication failed            |
| `ServerError`          | 500       | Internal server error            |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

variables = client.variable
```

## Methods

### List Variables

```python
all_variables = client.variable.list()

for var in all_variables:
    print(f"Variable: {var.name}, Type: {var.type}, Value: {var.value}")
```

**Filtering responses:**

```python
# Filter by type (client-side)
ip_variables = client.variable.list(type="ip-netmask")

# Filter by labels (client-side)
labeled_variables = client.variable.list(labels=["network"])

# Filter by parent folder (client-side)
folder_variables = client.variable.list(parent="department-a")

# Filter by snippet (client-side)
snippet_variables = client.variable.list(snippets=["security-snippet"])
```

**Controlling pagination with max_limit:**

```python
client.variable.max_limit = 100

all_variables = client.variable.list()
```

### Fetch a Variable

```python
variable = client.variable.fetch(name="subnet-variable", folder="department-a")
if variable:
    print(f"Found variable: {variable.name}, Value: {variable.value}")
```

### Create a Variable

```python
# Variable associated with a folder
variable_data = {
    "name": "subnet-variable",
    "type": "ip-netmask",
    "value": "192.168.1.0/24",
    "description": "Network subnet for department A",
    "folder": "department-a"
}
created = client.variable.create(variable_data)

# Variable associated with a snippet
snippet_variable = {
    "name": "snippet-var",
    "type": "port",
    "value": "8080",
    "snippet": "web-servers"
}
client.variable.create(snippet_variable)

# Variable associated with a device
device_variable = {
    "name": "device-var",
    "type": "ip-netmask",
    "value": "10.0.0.1/32",
    "device": "001122334455"
}
client.variable.create(device_variable)
```

### Update a Variable

```python
existing = client.variable.fetch(name="subnet-variable", folder="department-a")

existing.value = "10.0.0.0/16"
existing.description = "Updated network subnet"

updated = client.variable.update(existing)
```

### Delete a Variable

```python
client.variable.delete("12345678-1234-1234-1234-123456789012")
```

### Get a Variable by ID

```python
variable = client.variable.get("12345678-1234-1234-1234-123456789012")
print(f"Variable: {variable.name}, Type: {variable.type}, Value: {variable.value}")
```

## Error Handling

```python
from scm.exceptions import ObjectNotPresentError, InvalidObjectError

try:
    variable = client.variable.get("nonexistent-id")
except ObjectNotPresentError:
    print("Variable not found!")

try:
    # Missing required container (folder, snippet, or device)
    client.variable.create({
        "name": "invalid-var",
        "type": "ip-netmask",
        "value": "192.168.1.0/24"
    })
except InvalidObjectError as e:
    print(f"Validation error: {e}")
```

## Related Topics

- [Variable Models](../../models/setup/variable_models.md#Overview)
- [Setup Overview](index.md)
- [API Client](../../client.md)
