# Variable Models

## Table of Contents

1. [Overview](#overview)
2. [Models](#models)
    - [VariableBaseModel](#variablebasemodel)
    - [VariableCreateModel](#variablecreatemodel)
    - [VariableUpdateModel](#variableupdatemodel)
    - [VariableResponseModel](#variableresponsemodel)
3. [Model Validation Rules](#model-validation-rules)
4. [Variable Types](#variable-types)
5. [Container Validation](#container-validation)
6. [Usage Examples](#usage-examples)
    - [Creating Model Instances](#creating-model-instances)
    - [Model Validation](#model-validation)
    - [Model Serialization](#model-serialization)
    - [API Integration Examples](#api-integration-examples)

## Overview

This page documents the Pydantic models used for variable operations in the Strata Cloud Manager SDK. These models provide structured data validation and serialization for variable creation, updates, and API responses.

## Models

### VariableBaseModel

The base model for variable resources containing common fields.

```python
class VariableBaseModel(BaseModel):
    name: str
    type: str
    value: str
    description: Optional[str] = None
    folder: Optional[str] = None
    snippet: Optional[str] = None
    device: Optional[str] = None

    @model_validator(mode="after")
    def validate_container(self) -> 'VariableBaseModel':
        """Ensure exactly one container is specified"""
        # Validation logic omitted for brevity
```

### VariableCreateModel

Model for creating new variable resources.

```python
class VariableCreateModel(VariableBaseModel):
    pass  # Inherits all fields from VariableBaseModel
```

### VariableUpdateModel

Model for updating existing variable resources.

```python
class VariableUpdateModel(VariableBaseModel):
    id: UUID
```

### VariableResponseModel

Model for variable responses from the API.

```python
class VariableResponseModel(VariableBaseModel):
    id: UUID
    overridden: Optional[bool] = None
    labels: Optional[List[str]] = None
    parent: Optional[str] = None
    snippets: Optional[List[str]] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    device_only: Optional[bool] = None
```

## Model Validation Rules

| Field           | Validation Rules                                           |
|-----------------|------------------------------------------------------------|
| `name`          | Non-empty string, max 63 characters                        |
| `type`          | Must be one of the supported variable types                |
| `value`         | String value appropriate for the selected type             |
| `id`            | Valid UUID format (required in response and update models) |
| `description`   | Optional text description                                  |
| `folder`        | Optional string, container validation applies              |
| `snippet`       | Optional string, container validation applies              |
| `device`        | Optional string, container validation applies              |
| `overridden`    | Optional boolean (response only)                           |
| `labels`        | Optional list of string labels (response only)             |
| `parent`        | Optional string (response only)                            |
| `snippets`      | Optional list of string IDs (response only)                |
| `model`         | Optional string (response only)                            |
| `serial_number` | Optional string (response only)                            |
| `device_only`   | Optional boolean (response only)                           |

## Variable Types

The `type` field in variable models must be one of the following supported values:

- `percent`
- `count`
- `ip-netmask`
- `zone`
- `ip-range`
- `ip-wildcard`
- `device-priority`
- `device-id`
- `egress-max`
- `as-number`
- `fqdn`
- `port`
- `link-tag`
- `group-id`
- `rate`
- `router-id`
- `qos-profile`
- `timer`

## Container Validation

Variables must have exactly one container field set:
- `folder`: The folder in which the variable is defined
- `snippet`: The snippet in which the variable is defined
- `device`: The device in which the variable is defined

The model validator ensures that exactly one of these three fields is provided:

```python
@model_validator(mode="after")
def validate_container(self) -> 'VariableBaseModel':
    """Ensure exactly one container is specified"""
    containers = [self.folder, self.snippet, self.device]
    specified = sum(1 for c in containers if c is not None)

    if specified != 1:
        raise ValueError("Exactly one of folder, snippet, or device must be specified")

    return self
```

## Usage Examples

### Creating Model Instances

```python
from uuid import UUID
from scm.models.setup.variable import (
    VariableBaseModel,
    VariableCreateModel,
    VariableUpdateModel,
    VariableResponseModel
)

# Create a base variable model
base_variable = VariableBaseModel(
    name="subnet-var",
    type="ip-netmask",
    value="192.168.1.0/24",
    description="Subnet variable",
    folder="network"
)

# Create a variable creation model
create_variable = VariableCreateModel(
    name="port-var",
    type="port",
    value="8080",
    description="Web server port",
    snippet="web-config"
)

# Create a variable update model
update_variable = VariableUpdateModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="port-var",
    type="port",
    value="8443",  # Updated port
    description="Updated web server port",
    snippet="web-config"
)

# Create a variable response model
response_variable = VariableResponseModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="subnet-var",
    type="ip-netmask",
    value="192.168.1.0/24",
    description="Subnet variable",
    folder="network",
    overridden=False,
    labels=["network", "infrastructure"],
    parent="root",
    snippets=["web-config", "security-config"],
    device_only=False
)
```

### Model Validation

```python
from pydantic_core import ValidationError
try:
    # Error: No container specified
    VariableCreateModel(
        name="invalid-var",
        type="ip-netmask",
        value="192.168.1.0/24"
    )
except ValidationError as e:
    print("Validation error:", e)

try:
    # Error: Multiple containers specified
    VariableCreateModel(
        name="invalid-var",
        type="ip-netmask",
        value="192.168.1.0/24",
        folder="network",
        snippet="web-config"
    )
except ValidationError as e:
    print("Validation error:", e)

try:
    # Error: Invalid variable type
    VariableCreateModel(
        name="invalid-var",
        type="invalid-type",
        value="192.168.1.0/24",
        folder="network"
    )
except ValidationError as e:
    print("Validation error:", e)
```

### Model Serialization

```python
variable = VariableResponseModel(
    id=UUID("12345678-1234-1234-1234-123456789012"),
    name="subnet-var",
    type="ip-netmask",
    value="192.168.1.0/24",
    description="Subnet variable",
    folder="network"
)
# Convert to dict
variable_dict = variable.model_dump()
# Convert to JSON
variable_json = variable.model_dump_json()
```

### API Integration Examples

```python
from scm.config.setup.variable import Variable
from scm.models.setup.variable import VariableCreateModel, VariableUpdateModel
variables = Variable(client)

# Create and send a variable
new_variable = VariableCreateModel(
    name="web-port",
    type="port",
    value="8080",
    description="Web server port",
    folder="network-services"
)
created = variables.create(new_variable.model_dump(exclude_unset=True))

# Update a variable
update = VariableUpdateModel(
    id=created.id,
    name="web-port",
    type="port",
    value="8443",  # Changed port to HTTPS
    description="Secure web server port",
    folder="network-services"
)
updated = variables.update(update)

# List variables of a specific type
port_variables = variables.list(type="port")
for var in port_variables:
    print(f"{var.name}: {var.value}")
```
