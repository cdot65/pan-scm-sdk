# Variable Models (`scm.models.setup.variable`)

This page documents the Pydantic models for Variable resources.

## Main Models
- **VariableBaseModel**: Base model for variable resources with common fields.
- **VariableCreateModel**: Model for creating new variable resources.
- **VariableUpdateModel**: Model for updating existing variable resources.
- **VariableResponseModel**: Represents a variable resource returned by the SCM API.

## Variable Types
The `type` field in variable models accepts the following values:
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

## VariableBaseModel Fields
- `name`: The name of the variable (required, max 63 characters)
- `type`: The variable type (required, must be one of the supported types)
- `value`: The value of the variable (required)
- `description`: An optional description of the variable
- `folder`: The folder in which the variable is defined (optional)
- `snippet`: The snippet in which the variable is defined (optional)
- `device`: The device in which the variable is defined (optional)

## VariableUpdateModel Fields
Includes all fields from VariableBaseModel, plus:
- `id`: The unique identifier of the variable (required for updates)

## VariableResponseModel Fields
Includes all fields from VariableBaseModel, plus:
- `id`: The unique identifier of the variable
- `overridden`: Indicates if the variable is overridden
- `labels`: Labels assigned to the variable
- `parent`: The parent folder or container
- `snippets`: Snippets associated with the variable
- `model`: Device model information
- `serial_number`: Device serial number
- `device_only`: Whether the variable is only applicable to devices

## Example Usage
```python
from scm.models.setup.variable import VariableCreateModel, VariableResponseModel

# Create a new variable
create_data = {
    "name": "subnet-variable",
    "type": "ip-netmask",
    "value": "192.168.1.0/24",
    "description": "Department subnet",
    "folder": "department-a"
}
create_model = VariableCreateModel(**create_data)

# Validate a response model
response_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "subnet-variable",
    "type": "ip-netmask", 
    "value": "192.168.1.0/24",
    "description": "Department subnet",
    "folder": "department-a",
    "overridden": False,
    "labels": ["network", "department-a"]
}
variable = VariableResponseModel.model_validate(response_data)
print(f"Variable ID: {variable.id}")
print(f"Variable Name: {variable.name}")
print(f"Variable Type: {variable.type}")
print(f"Variable Value: {variable.value}")
```

## Model Validation
The Variable models enforce several validations:

1. Type Enumeration: The `type` field must be one of the supported variable types.
2. Container Type: Exactly one of `folder`, `snippet`, or `device` must be provided.
3. Field Constraints: Field patterns, maximum lengths, and required fields are validated.

These validations help ensure that variable data conforms to the requirements of the Strata Cloud Manager API.