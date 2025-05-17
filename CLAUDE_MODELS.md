# Claude Code Model Styling Guidelines

This document provides specific guidance for creating Pydantic models in the SDK.

## Model File Structure

Each model file should follow this pattern:

```python
"""Models for <Resource> objects in Strata Cloud Manager.

Defines Pydantic models for request and response validation.
"""

from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Base model with shared fields
class ResourceBaseModel(BaseModel):
    """Base model for Resource containing common fields."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="The name of the resource",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Description of the resource",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="List of tags associated with the resource",
    )

# Create model (for POST requests)
class ResourceCreateModel(ResourceBaseModel):
    """Model used for creating new resources."""
    
    # Required fields for creation
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The name of the resource (required)",
    )
    
    # Container field - exactly one required
    folder: Optional[str] = Field(None, description="Folder name")
    snippet: Optional[str] = Field(None, description="Snippet name")
    device: Optional[str] = Field(None, description="Device name")
    
    @field_validator("folder", "snippet", "device")
    def container_validator(cls, v, info):
        """Ensure exactly one container is specified."""
        containers = [info.data.get("folder"), info.data.get("snippet"), info.data.get("device")]
        if sum(bool(c) for c in containers) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be specified")
        return v
    
    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
    )

# Update model (for PUT requests)
class ResourceUpdateModel(ResourceBaseModel):
    """Model used for updating existing resources."""
    
    id: UUID = Field(..., description="Resource ID (required)")
    
    model_config = ConfigDict(
        extra="forbid",
    )

# Response model (from API responses)
class ResourceResponseModel(ResourceBaseModel):
    """Model representing API response for resources."""
    
    id: UUID = Field(..., description="Resource ID")
    
    # Container metadata
    folder: Optional[str] = Field(None, description="Folder containing this resource")
    snippet: Optional[str] = Field(None, description="Snippet containing this resource")
    device: Optional[str] = Field(None, description="Device containing this resource")
    
    model_config = ConfigDict(
        extra="allow",  # Allow extra fields from API
    )
```

## Model Patterns

### 1. Field Definitions

```python
# Simple field with description
field_name: str = Field(..., description="Field description")

# Optional field with default
field_name: Optional[str] = Field(None, description="Field description")

# Field with constraints
field_name: str = Field(
    ...,
    min_length=1,
    max_length=255,
    description="Field description",
)

# Field with pattern validation
field_name: str = Field(
    ...,
    pattern=r"^[a-zA-Z0-9_-]+$",
    description="Field description",
)
```

### 2. Complex Fields

```python
# Lists
items: List[str] = Field(
    default_factory=list,
    description="List of items",
)

# Dictionaries
metadata: Dict[str, str] = Field(
    default_factory=dict,
    description="Metadata key-value pairs",
)

# Nested models
config: ConfigModel = Field(
    ...,
    description="Configuration settings",
)

# Union types
value: Union[str, int] = Field(
    ...,
    description="Value can be string or integer",
)
```

### 3. Validators

```python
# Field validator
@field_validator("field_name")
def validate_field(cls, v):
    """Validate specific field."""
    if v and not v.strip():
        raise ValueError("Field cannot be empty string")
    return v

# Cross-field validator
@field_validator("field1", "field2")
def validate_combination(cls, v, info):
    """Validate field combinations."""
    field1 = info.data.get("field1")
    field2 = info.data.get("field2")
    
    if field1 and field2:
        raise ValueError("Cannot specify both field1 and field2")
    return v
```

### 4. Model Configuration

```python
model_config = ConfigDict(
    extra="forbid",  # For CreateModel/UpdateModel
    extra="allow",   # For ResponseModel
    populate_by_name=True,  # Allow field aliases
    use_enum_values=True,   # Use enum values directly
)
```

## Resource-Specific Patterns

### 1. Address Models
```python
# Address can be one of several types
ip_netmask: Optional[str] = Field(None, description="IP address with netmask")
ip_range: Optional[str] = Field(None, description="IP address range")
ip_wildcard: Optional[str] = Field(None, description="IP wildcard mask")
fqdn: Optional[str] = Field(None, description="Fully qualified domain name")

@field_validator("ip_netmask", "ip_range", "ip_wildcard", "fqdn")
def ensure_single_type(cls, v, info):
    """Ensure only one address type is specified."""
    types = ["ip_netmask", "ip_range", "ip_wildcard", "fqdn"]
    specified = sum(bool(info.data.get(t)) for t in types)
    if specified > 1:
        raise ValueError("Only one address type can be specified")
    return v
```

### 2. Security Rule Models
```python
# Enum for rulebase
class SecurityRuleRulebase(str, Enum):
    pre = "pre"
    post = "post"

# Complex nested structure
profile_setting: Optional[ProfileSettingModel] = Field(
    None,
    description="Security profile settings",
)

# Special fields with aliases
destination_hip: Optional[List[str]] = Field(
    None,
    alias="destination_hip",
    description="Destination HIP profiles",
)
```

### 3. Service Connection Models
```python
# Required fields with defaults
folder: str = Field(
    default="Service Connections",
    description="Folder name (always Service Connections)",
)

# Complex nested structures
bgp: Optional[BGPConfigModel] = Field(
    None,
    description="BGP configuration",
)

ipsec_tunnel: Optional[IPSecTunnelModel] = Field(
    None,
    description="IPSec tunnel configuration",
)
```

## Documentation Guidelines

1. **Module Docstring**: Describe what models are included
2. **Class Docstring**: Describe the model's purpose
3. **Field Descriptions**: Every field must have a description
4. **Validator Docstrings**: Explain validation logic
5. **Complex Fields**: Document nested structures

## Testing Models

Create comprehensive tests for each model:

```python
def test_model_create_valid():
    """Test creating model with valid data."""
    data = {
        "name": "test-resource",
        "folder": "test-folder",
    }
    model = ResourceCreateModel(**data)
    assert model.name == "test-resource"
    assert model.folder == "test-folder"

def test_model_validation_error():
    """Test model validation errors."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateModel(name="")
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("name",)
```