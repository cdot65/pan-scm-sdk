"""<Resource> models for Strata Cloud Manager SDK.

Contains Pydantic models for representing <resource> objects and related data.
"""

from typing import List, Optional, Union
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Example Enum (delete if not needed)
class ExampleEnum(str, Enum):
    """Example enum for <resource> type."""
    TYPE1 = "type1"
    TYPE2 = "type2"

# Base model
class <Resource>BaseModel(BaseModel):
    """Base model for <Resource> objects containing fields common to all CRUD operations.

    Attributes:
        name (str): Name of the <resource>.
        description (Optional[str]): Description of the <resource>.
        tag (Optional[List[str]]): Tags associated with the <resource>.
        folder (Optional[str]): Folder in which the resource is defined.
        snippet (Optional[str]): Snippet in which the resource is defined.
        device (Optional[str]): Device in which the resource is defined.
    """

    name: str = Field(..., max_length=63, description="Name of the <resource>")
    description: Optional[str] = Field(None, max_length=1023, description="Description of the <resource>")
    tag: Optional[List[str]] = Field(None, description="Tags associated with the <resource>")
    folder: Optional[str] = Field(None, max_length=64, description="Folder name")
    snippet: Optional[str] = Field(None, max_length=64, description="Snippet name")
    device: Optional[str] = Field(None, max_length=64, description="Device name")

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    # Example validator for tag uniqueness
    @field_validator("tag")
    def ensure_unique_tags(cls, v):
        if v is not None and len(v) != len(set(v)):
            raise ValueError("Tags must be unique")
        return v

    # Example container exclusivity validator
    @model_validator(mode="after")
    def validate_container(self) -> "<Resource>BaseModel":
        containers = [self.folder, self.snippet, self.device]
        if sum(bool(c) for c in containers) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be specified")
        return self

# Create model
class <Resource>CreateModel(<Resource>BaseModel):
    """Model for creating a new <resource>. Inherits all fields and validators."""
    pass

# Update model
class <Resource>UpdateModel(<Resource>BaseModel):
    """Model for updating an existing <resource>. Requires id field."""
    id: UUID = Field(..., description="UUID of the <resource>")

# Response model
class <Resource>ResponseModel(<Resource>BaseModel):
    """Model for <resource> API responses. Includes id field."""
    id: UUID = Field(..., description="UUID of the <resource>")
