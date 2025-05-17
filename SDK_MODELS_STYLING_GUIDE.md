# SDK Pydantic Model Styling Guide

This guide defines standards for all Pydantic models in the pan-scm-sdk project.

---

## 1. File & Class Structure
- One resource per file, named after the resource (pluralized as needed).
- File-level docstring: Google-style, describing the resource and modeling purpose.
- Standard library imports first, then Pydantic, then enums, then typing.
- Enums defined at the top if needed, with clear docstrings.
- All models inherit from Pydantic `BaseModel`.
- Always define `BaseModel`, `CreateModel`, `UpdateModel`, `ResponseModel` (and `MoveModel` if needed).
- Each model class must have a Google-style docstring with Args/Attributes, Returns, Raises as needed.
- Use `ConfigDict`/`model_config` for settings: `validate_assignment`, `populate_by_name`, `arbitrary_types_allowed`, `extra="forbid"`.

## 2. Field/Attribute Conventions
- Use `Field(...)` with type hints, description, and constraints (`min_length`, `max_length`, `pattern`, `examples`).
- snake_case for all fields and models.
- ID fields always present in `UpdateModel` and `ResponseModel` (`UUID` or `str` if legacy).
- Container fields (`folder`, `snippet`, `device`) must always be validated for exclusivity.
- Tag fields are lists of strings, validated for uniqueness.

## 3. Validation & Logic
- Use `@field_validator` and `@model_validator` for:
  - Ensuring exactly one of a set of mutually exclusive fields is set (e.g., address type, container, group type).
  - Ensuring lists are unique and/or always lists of strings.
  - Enum/boolean conversions.
  - Complex resource-specific logic (e.g., NAT/SECURITY move validation).
- Always raise `ValueError` with clear, actionable messages in validators.

## 4. Docstrings & Documentation
- Google-style docstrings for all models and validators.
- Attributes section always lists all fields with types and descriptions.
- Validation logic clearly described in docstrings.

## 5. Formatting & Style
- Line length: 88 chars (ruff default).
- Blank lines between class-level constants, classes, and methods.
- Imports grouped and sorted.
- No extra fields: `extra="forbid"` in model config unless otherwise required.

## 6. Example Skeleton

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

For more details, see `CLAUDE_MODELS.md`, `SDK_MODELS_TEMPLATE.py`, and the real models in `scm/models/`.
