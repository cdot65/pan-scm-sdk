# Pydantic Models Styling Guide

This guide defines the standards and patterns for writing Pydantic models in the pan-scm-sdk project.

## Table of Contents

1. [File Structure](#file-structure)
2. [Model Hierarchy](#model-hierarchy)
3. [Model Configuration](#model-configuration)
4. [Field Definitions](#field-definitions)
5. [Validators](#validators)
6. [Container Validation](#container-validation)
7. [Enum Types](#enum-types)
8. [Supporting Models](#supporting-models)
9. [Import Organization](#import-organization)
10. [Naming Conventions](#naming-conventions)

## File Structure

Each resource's models should be in a single file within the appropriate category:

```
scm/models/
├── __init__.py
├── objects/             # address.py, tag.py, service.py, etc.
├── security/            # security_rule.py, anti_spyware_profile.py, etc.
├── network/             # nat_rules.py, ike_gateway.py, etc.
├── deployment/          # service_connections.py, remote_networks.py, etc.
├── mobile_agent/        # auth_settings.py, agent_versions.py, etc.
└── setup/               # folder.py, snippet.py, variable.py, etc.
```

## Model Hierarchy

Every resource should define four models:

1. **BaseModel** - Common fields shared across all operations
2. **CreateModel** - Fields for creating new resources (inherits from Base)
3. **UpdateModel** - Fields for updating resources (inherits from Base, adds `id`)
4. **ResponseModel** - Fields returned from API (inherits from Base, adds `id` and response-only fields)

```python
class ResourceBaseModel(BaseModel):
    """Base model with common fields."""
    pass

class ResourceCreateModel(ResourceBaseModel):
    """Model for creating new resources."""
    pass

class ResourceUpdateModel(ResourceBaseModel):
    """Model for updating existing resources."""
    id: UUID = Field(...)

class ResourceResponseModel(ResourceBaseModel):
    """Model for API responses."""
    id: UUID = Field(...)
    # Additional response-only fields
```

## Model Configuration

Always use `ConfigDict` with these settings:

```python
from pydantic import BaseModel, ConfigDict

class ResourceBaseModel(BaseModel):
    """Base model for Resource resources."""

    model_config = ConfigDict(
        extra="forbid",          # Reject unknown fields
        populate_by_name=True,   # Allow field aliases
    )
```

### Configuration Options

| Option | Value | Purpose |
|--------|-------|---------|
| `extra` | `"forbid"` | Reject fields not defined in model |
| `populate_by_name` | `True` | Allow using field name or alias |

## Field Definitions

### Required Fields

Use `...` (Ellipsis) to mark required fields:

```python
name: str = Field(
    ...,  # required
    description="The name of the resource",
    max_length=63,
)
```

### Optional Fields

Use `Optional[T]` with `default=None`:

```python
description: Optional[str] = Field(
    default=None,
    description="An optional description",
)
```

### Field Parameters

```python
from pydantic import Field

# String with constraints
name: str = Field(
    ...,
    description="Resource name",
    max_length=63,
    pattern=r"^[a-zA-Z0-9\-_. ]+$",
)

# UUID field
id: UUID = Field(
    ...,
    description="Unique identifier",
    examples=["123e4567-e89b-12d3-a456-426655440000"],
)

# Boolean with default
enabled: bool = Field(
    default=True,
    description="Whether the resource is enabled",
)

# List field
tags: Optional[List[str]] = Field(
    default=None,
    description="List of tags",
)
```

### Common Field Patterns

#### Container Fields (folder/snippet/device)

```python
folder: Optional[str] = Field(
    None,
    pattern=r"^[a-zA-Z0-9\-_. ]+$",
    max_length=64,
    description="The folder in which the resource is defined",
)
snippet: Optional[str] = Field(
    None,
    pattern=r"^[a-zA-Z0-9\-_. ]+$",
    max_length=64,
    description="The snippet in which the resource is defined",
)
device: Optional[str] = Field(
    None,
    pattern=r"^[a-zA-Z0-9\-_. ]+$",
    max_length=64,
    description="The device in which the resource is defined",
)
```

#### Name Field

```python
name: str = Field(
    ...,
    description="The name of the resource",
    max_length=63,
    pattern=r"^[a-zA-Z0-9\-_. ]+$",
)
```

#### ID Field (for Update/Response models)

```python
id: UUID = Field(
    ...,
    description="The unique identifier of the resource",
    examples=["123e4567-e89b-12d3-a456-426655440000"],
)
```

## Validators

### Field Validators

Use `@field_validator` for single-field validation:

```python
from pydantic import field_validator

@field_validator("name")
@classmethod
def validate_name(cls, v):
    """Validate that the name is not empty."""
    if not v or v.strip() == "":
        raise ValueError("Name cannot be empty")
    return v
```

### Enum Validation

When a field must be one of specific values:

```python
@field_validator("type")
@classmethod
def validate_type_enum(cls, v):
    """Validate that the type is one of the allowed values."""
    allowed = ["ip-netmask", "ip-range", "fqdn", "ip-wildcard"]
    if v not in allowed:
        raise ValueError(f"type must be one of {allowed}, got {v}")
    return v
```

### Model Validators

Use `@model_validator` for cross-field validation:

```python
from pydantic import model_validator

@model_validator(mode="after")
def validate_ip_or_fqdn(self) -> "ResourceBaseModel":
    """Ensure exactly one of ip_netmask or fqdn is provided."""
    if self.ip_netmask and self.fqdn:
        raise ValueError("Cannot specify both ip_netmask and fqdn")
    if not self.ip_netmask and not self.fqdn:
        raise ValueError("Must specify either ip_netmask or fqdn")
    return self
```

## Container Validation

For resources requiring exactly one container (folder/snippet/device):

### Method 1: Class Method with model_validate Override

```python
class ResourceBaseModel(BaseModel):
    folder: Optional[str] = Field(None, ...)
    snippet: Optional[str] = Field(None, ...)
    device: Optional[str] = Field(None, ...)

    @classmethod
    def validate_container_type(cls, values):
        """Validate that exactly one container is provided."""
        container_fields = [
            values.get("folder"),
            values.get("snippet"),
            values.get("device")
        ]
        set_count = sum(1 for v in container_fields if v is not None)
        if set_count != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return values


class ResourceCreateModel(ResourceBaseModel):
    @classmethod
    def model_validate(cls, value):
        """Validate model and ensure container type is valid."""
        model = super().model_validate(value)
        cls.validate_container_type(model.__dict__)
        return model
```

### Method 2: Model Validator

```python
@model_validator(mode="after")
def validate_container(self) -> "ResourceBaseModel":
    """Ensure exactly one container is specified."""
    containers = [self.folder, self.snippet, self.device]
    specified = sum(1 for c in containers if c is not None)

    if specified != 1:
        raise ValueError(
            "Exactly one of folder, snippet, or device must be specified"
        )
    return self
```

## Enum Types

### Using Literal for Simple Enums

```python
from typing import Literal

action: Literal["allow", "deny", "drop"] = Field(
    ...,
    description="The action to take",
)
```

### Using Enum Class

For reusable enums:

```python
from enum import Enum

class ActionType(str, Enum):
    """Valid action types."""
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"

action: ActionType = Field(
    ...,
    description="The action to take",
)
```

### Documenting Enum Values

Always document valid values in field description or validator:

```python
type: str = Field(
    ...,
    description="Variable type: percent, count, ip-netmask, zone, ip-range, "
                "ip-wildcard, device-priority, device-id, egress-max, as-number, "
                "fqdn, port, link-tag, group-id, rate, router-id, qos-profile, timer",
)
```

## Supporting Models

For nested structures, define supporting models:

```python
class FolderReference(BaseModel):
    """Reference to a folder."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    id: UUID = Field(..., description="The UUID of the folder")
    name: str = Field(..., description="The name of the folder")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """Validate that the name is not empty."""
        if not value or value.strip() == "":
            raise ValueError("Folder name cannot be empty")
        return value


class ResourceResponseModel(ResourceBaseModel):
    folders: Optional[List[FolderReference]] = Field(
        default=None,
        description="Folders the resource is applied to",
    )
```

## Import Organization

```python
"""Models for Resource in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Resource objects in the Strata Cloud Manager.
"""

from enum import Enum
from typing import List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Base model | `{Resource}BaseModel` | `AddressBaseModel` |
| Create model | `{Resource}CreateModel` | `AddressCreateModel` |
| Update model | `{Resource}UpdateModel` | `AddressUpdateModel` |
| Response model | `{Resource}ResponseModel` | `AddressResponseModel` |
| Enum class | `{Name}Type` or `{Name}Enum` | `ActionType`, `ProtocolEnum` |
| Supporting model | Descriptive name | `FolderReference`, `ThreatEntry` |
| File name | snake_case, singular | `address.py`, `security_rule.py` |

## Complete Example

```python
"""Models for Variable in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Variable resources in the Strata Cloud Manager.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VariableBaseModel(BaseModel):
    """Base model for Variable resources."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="The name of the variable",
        max_length=63,
    )
    type: str = Field(
        ...,
        description="The variable type",
    )
    value: str = Field(
        ...,
        description="The value of the variable",
    )
    description: Optional[str] = Field(
        default=None,
        description="An optional description of the variable",
    )
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_. ]+$",
        max_length=64,
        description="The folder in which the variable is defined",
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_. ]+$",
        max_length=64,
        description="The snippet in which the variable is defined",
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_. ]+$",
        max_length=64,
        description="The device in which the variable is defined",
    )

    @field_validator("type")
    @classmethod
    def validate_type_enum(cls, v):
        """Validate that the type is one of the allowed values."""
        allowed = [
            "percent", "count", "ip-netmask", "zone", "ip-range",
            "ip-wildcard", "device-priority", "device-id", "egress-max",
            "as-number", "fqdn", "port", "link-tag", "group-id",
            "rate", "router-id", "qos-profile", "timer",
        ]
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}, got {v}")
        return v

    @classmethod
    def validate_container_type(cls, values):
        """Validate that exactly one container is provided."""
        container_fields = [
            values.get("folder"),
            values.get("snippet"),
            values.get("device")
        ]
        set_count = sum(1 for v in container_fields if v is not None)
        if set_count != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return values


class VariableCreateModel(VariableBaseModel):
    """Model for creating new Variable resources."""

    @classmethod
    def model_validate(cls, value):
        """Validate model and ensure container type is valid."""
        model = super().model_validate(value)
        cls.validate_container_type(model.__dict__)
        return model


class VariableUpdateModel(VariableBaseModel):
    """Model for updating existing Variable resources."""

    id: UUID = Field(
        ...,
        description="The unique identifier of the variable",
    )

    @classmethod
    def model_validate(cls, value):
        """Validate model and ensure container type is valid."""
        model = super().model_validate(value)
        cls.validate_container_type(model.__dict__)
        return model


class VariableResponseModel(VariableBaseModel):
    """Model for Variable responses from the API."""

    id: UUID = Field(
        ...,
        description="The unique identifier of the variable",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    overridden: Optional[bool] = Field(
        default=None,
        description="Is the variable overridden?",
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="Labels assigned to the variable",
    )
    parent: Optional[str] = Field(
        default=None,
        description="The parent folder or container",
    )
```
