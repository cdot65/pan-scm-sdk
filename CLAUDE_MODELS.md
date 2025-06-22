# Claude Code Model Styling Guidelines

> **Canonical template:** See [SDK_MODELS_TEMPLATE.py](./SDK_MODELS_TEMPLATE.py) for the official model skeleton.
> **Markdown style guide:** See [SDK_MODELS_STYLING_GUIDE.md](./SDK_MODELS_STYLING_GUIDE.md) for markdown rules and patterns.

This document provides canonical, code-backed guidance for creating Pydantic models in the SDK. These rules are harmonized from real project models, the new `SDK_MODELS_TEMPLATE.py`, and the `SDK_MODELS_STYLING_GUIDE.md`. Follow these standards for all new and existing SDK models.

---

## 1. File & Class Structure
- **One resource per file**, named after the resource (pluralized as needed).
- **File-level docstring**: Google-style, describing the resource and modeling purpose.
- **Import order**: Standard library, then Pydantic, then enums, then typing.
- **Enums**: Defined at the top if needed, with clear docstrings.
- **Model classes**: Always define `BaseModel`, `CreateModel`, `UpdateModel`, `ResponseModel` (and `MoveModel` if needed).
- **Class-level docstrings**: Google-style, with Args/Attributes, Returns, Raises as needed.
- **Model config**: Use `ConfigDict`/`model_config` for settings (`validate_assignment`, `populate_by_name`, `arbitrary_types_allowed`, `extra="forbid"`).

## 2. Field/Attribute Conventions
- **Field definitions**: Always use `Field(...)` with type hints, description, and constraints (`min_length`, `max_length`, `pattern`, `examples`).
- **snake_case** for all fields and models.
- **ID fields**: Always present in `UpdateModel` and `ResponseModel`, type `UUID` (or `str` if legacy).
- **Container fields**: `folder`, `snippet`, `device`—always validated for exclusivity.
- **Tag fields**: List of strings, validated for uniqueness.

## 3. Validation & Logic
- **Custom validators**: Use `@field_validator` and `@model_validator` for:
  - Ensuring exactly one of a set of mutually exclusive fields is set (e.g., address type, container, group type).
  - Ensuring lists are unique and/or always lists of strings.
  - Enum/boolean conversions.
  - Complex resource-specific logic (e.g., NAT/SECURITY move validation).
- **Error handling**: Always raise `ValueError` with clear, actionable messages in validators.

## 4. Docstrings & Documentation
- **Google-style docstrings**: For all models and validators.
- **Attributes section**: Always lists all fields with types and descriptions.
- **Validation logic**: Clearly described in docstrings.

## 5. Formatting & Style
- **Line length**: 88 chars (ruff default).
- **Blank lines**: Between class-level constants, classes, methods.
- **Imports**: Grouped and sorted.
- **No extra fields**: `extra="forbid"` in model config unless otherwise required.

---

## 6. Canonical Example Skeleton

```python
"""<Resource> models for Strata Cloud Manager SDK.

Contains Pydantic models for representing <resource> objects and related data.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class <Resource>BaseModel(BaseModel):
    """Base model for <Resource> objects containing fields common to all CRUD operations.

    Attributes:
        name (str): Name of the <resource>.
        ...
    """
    # ...fields and validators...

class <Resource>CreateModel(<Resource>BaseModel):
    """Model for creating a new <resource>. Inherits all fields and validators."""
    pass

class <Resource>UpdateModel(<Resource>BaseModel):
    """Model for updating an existing <resource>. Requires id field."""
    id: UUID = Field(..., description="UUID of the <resource>")

class <Resource>ResponseModel(<Resource>BaseModel):
    """Model for <resource> API responses. Includes id field."""
    id: UUID = Field(..., description="UUID of the <resource>")
```

---

## 7. Real-World Patterns
- See `scm/models/objects/address.py`, `scm/models/objects/address_group.py`, `scm/models/network/nat_rules.py`, and `scm/models/security/security_rules.py` for canonical field/validator logic.
- Always validate container exclusivity, tag uniqueness, and mutually exclusive resource types.
- Use `model_dump(exclude_unset=True)` for API payloads.

---

## 8. Further Reading
- [SDK_MODELS_STYLING_GUIDE.md](./SDK_MODELS_STYLING_GUIDE.md): Markdown style guide for all SDK models.
- [SDK_MODELS_TEMPLATE.py](./SDK_MODELS_TEMPLATE.py): Canonical template for new models.
- [WINDSURF_RULES.md](./WINDSURF_RULES.md): Project-wide coding and modeling standards.
- [CLAUDE.md](../cdot65.scm/CLAUDE.md): AI/codegen guidance for model and service files.

---

## Reviewer/Contributor Checklist
- [ ] File/class structure matches `SDK_MODELS_TEMPLATE.py`
- [ ] All fields use `Field(...)` with full type hints, constraints, and descriptions
- [ ] All container/tag fields validated for exclusivity/uniqueness
- [ ] All custom logic uses `@field_validator`/`@model_validator` as required
- [ ] Docstrings are Google-style and complete
- [ ] No extra fields unless explicitly allowed in config
- [ ] All standards in `WINDSURF_RULES.md` and `SDK_MODELS_STYLING_GUIDE.md` are followed

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
