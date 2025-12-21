# Variable Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Variable Types](#variable-types)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Variable models provide a structured way to manage variable resources in Palo Alto Networks' Strata Cloud Manager.
These models represent reusable values that can be referenced across configurations. The models handle validation
of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `VariableBaseModel`: Base model with fields common to all variable operations
- `VariableCreateModel`: Model for creating new variables
- `VariableUpdateModel`: Model for updating existing variables
- `VariableResponseModel`: Response model for variable operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### VariableBaseModel

| Attribute   | Type | Required | Default | Description                                       |
|-------------|------|----------|---------|---------------------------------------------------|
| name        | str  | Yes      | None    | Name of the variable. Max length: 63 chars        |
| type        | str  | Yes      | None    | Variable type (see Variable Types)                |
| value       | str  | Yes      | None    | Value of the variable                             |
| description | str  | No       | None    | Description of the variable                       |
| folder      | str  | No*      | None    | Folder scope. Pattern: `^[a-zA-Z0-9\-_. ]+$`. Max: 64 |
| snippet     | str  | No*      | None    | Snippet scope. Pattern: `^[a-zA-Z0-9\-_. ]+$`. Max: 64 |
| device      | str  | No*      | None    | Device scope. Pattern: `^[a-zA-Z0-9\-_. ]+$`. Max: 64 |

\* Exactly one of `folder`, `snippet`, or `device` must be provided

### VariableCreateModel

Inherits all fields from `VariableBaseModel` without additional fields. Includes container validation.

### VariableUpdateModel

Extends `VariableBaseModel` by adding:

| Attribute | Type | Required | Default | Description                            |
|-----------|------|----------|---------|----------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the variable  |

### VariableResponseModel

Extends `VariableBaseModel` by adding:

| Attribute     | Type      | Required | Default | Description                              |
|---------------|-----------|----------|---------|------------------------------------------|
| id            | UUID      | Yes      | None    | The unique identifier of the variable    |
| overridden    | bool      | No       | None    | Whether the variable is overridden       |
| labels        | List[str] | No       | None    | Labels assigned to the variable          |
| parent        | str       | No       | None    | Parent folder or container               |
| snippets      | List[str] | No       | None    | Snippets associated with the variable    |
| model         | str       | No       | None    | Device model information                 |
| serial_number | str       | No       | None    | Device serial number                     |
| device_only   | bool      | No       | None    | Whether variable is device-only          |

## Variable Types

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

## Exceptions

The Variable models can raise the following exceptions during validation:

- **ValueError**: Raised when field validation fails (e.g., invalid type, missing container)
- **ValidationError**: Raised by Pydantic when model validation fails

## Model Validators

### Type Validation

The `type` field is validated to ensure it matches one of the allowed variable types:

```python
from scm.models.setup.variable import VariableCreateModel

# This will raise a validation error
try:
    variable = VariableCreateModel(
        name="test-var",
        type="invalid-type",
        value="test",
        folder="Texas"
    )
except ValueError as e:
    print(f"Validation error: {e}")
    # Output: type must be one of [...], got invalid-type
```

### Container Validation

Variables must have exactly one container field set (`folder`, `snippet`, or `device`):

```python
from scm.models.setup.variable import VariableCreateModel

# Error: No container specified
try:
    VariableCreateModel(
        name="test-var",
        type="ip-netmask",
        value="192.168.1.0/24"
    )
except ValueError as e:
    print(f"Error: {e}")

# Error: Multiple containers specified
try:
    VariableCreateModel(
        name="test-var",
        type="ip-netmask",
        value="192.168.1.0/24",
        folder="Texas",
        snippet="web-config"
    )
except ValueError as e:
    print(f"Error: {e}")
```

## Usage Examples

### Creating a Variable

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
variable_data = {
    "name": "subnet-variable",
    "type": "ip-netmask",
    "value": "192.168.1.0/24",
    "description": "Network subnet for department A",
    "folder": "Texas"
}

response = client.variable.create(variable_data)
print(f"Created variable: {response.name} with ID: {response.id}")
```

### Updating a Variable

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing variable
existing = client.variable.fetch(name="subnet-variable", folder="Texas")

# Modify attributes using dot notation
existing.value = "10.0.0.0/16"
existing.description = "Updated network subnet"

# Pass modified object to update()
updated = client.variable.update(existing)
print(f"Updated variable: {updated.name}")
```

### Listing Variables

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List all variables
all_variables = client.variable.list()

for variable in all_variables:
    print(f"Variable: {variable.name}")
    print(f"Type: {variable.type}")
    print(f"Value: {variable.value}")

# Filter by type
ip_variables = client.variable.list(type="ip-netmask")

# Filter by labels
labeled_variables = client.variable.list(labels=["network"])
```

### Fetching a Variable by Name

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch variable by name and folder
variable = client.variable.fetch(name="subnet-variable", folder="Texas")
if variable:
    print(f"Found variable: {variable.name}")
    print(f"ID: {variable.id}")
    print(f"Type: {variable.type}")
    print(f"Value: {variable.value}")
else:
    print("Variable not found")
```

