# Variable Service (`scm.config.setup.variable`)

This page documents the Variable service in the SDK configuration layer.

## Overview
The `Variable` class provides methods for creating, retrieving, updating, and deleting variable resources in the SCM API. It supports client-side filtering, pagination, and variable management operations.

## Main Class
- **Variable**: Main entry point for variable operations.

## Key Methods
- `create(data)`: Create a new variable in Strata Cloud Manager.
- `get(variable_id)`: Get a variable by its ID.
- `update(variable)`: Update an existing variable.
- `delete(variable_id)`: Delete a variable.
- `list(**filters)`: List variables with optional filters. Supports pagination and client-side filtering.
- `fetch(name)`: Get a variable by its name (exact match).
- `_apply_filters(data, filters)`: Internal method to apply client-side filters to a list of variables.

## Filters Supported
- `labels`: Filter by one or more labels (intersection matching).
- `parent`: Filter by parent folder or container (exact match).
- `type`: Filter by variable type (exact match).
- `snippets`: Filter by one or more snippets (intersection matching).
- `model`: Filter by device model (exact match).
- `serial_number`: Filter by device serial number (exact match).
- `device_only`: Filter by the device_only attribute (boolean match).

## Example Usage
```python
from scm.config.setup.variable import Variable
from scm.client import Scm

api_client = Scm(api_key="<your-api-key>")
variable_service = Variable(api_client)

# Create a new variable
variable_data = {
    "name": "my-ip-variable",
    "type": "ip-netmask",
    "value": "10.0.0.0/24",
    "description": "Network subnet for department A",
    "folder": "department-a"  # One of folder, snippet, or device must be provided
}
new_variable = variable_service.create(variable_data)
print(f"Created variable: {new_variable.id}, Name: {new_variable.name}")

# List variables filtered by type
ip_variables = variable_service.list(type="ip-netmask")
for var in ip_variables:
    print(f"ID: {var.id}, Name: {var.name}, Value: {var.value}")

# Get variable by name
my_var = variable_service.fetch("my-ip-variable")
if my_var:
    print(f"Found variable: {my_var.name}, Value: {my_var.value}")

# Update a variable
from scm.models.setup.variable import VariableUpdateModel
update_data = VariableUpdateModel(
    id=my_var.id,
    name=my_var.name,
    type=my_var.type,
    value="10.0.0.0/16",  # Updated value
    folder="department-a"
)
updated_var = variable_service.update(update_data)
print(f"Updated variable value: {updated_var.value}")

# Delete a variable
variable_service.delete(my_var.id)
print(f"Deleted variable: {my_var.name}")
```

## Related Models
See [VariableResponseModel](../../models/setup/variable_models.md) for the variable data structure.