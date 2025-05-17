"""Dynamic User Group models for Strata Cloud Manager SDK.

Contains Pydantic models for representing dynamic user group objects and related data.
"""

# scm/models/objects/dynamic_user_group.py

# Standard library imports
from typing import List, Optional
from uuid import UUID

# External libraries
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    constr,
    field_validator,
    model_validator,
)

TagString = constr(max_length=127)


class DynamicUserGroupBaseModel(BaseModel):
    """Base model for Dynamic User Group objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the dynamic user group.
        filter (str): The tag-based filter for the dynamic user group.
        description (Optional[str]): The description of the dynamic user group.
        tag (Optional[List[TagString]]): Tags associated with the dynamic user group.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    """

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the dynamic user group",
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    filter: str = Field(
        ...,
        max_length=2047,
        description="The tag-based filter for the dynamic user group",
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="The description of the dynamic user group",
    )
    tag: Optional[List[TagString]] = Field(  # type: ignore
        None,
        description="Tags associated with the dynamic user group",
        max_length=64,
    )

    # Container Types
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["My Folder"],
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
        examples=["My Snippet"],
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
        examples=["My Device"],
    )

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Custom Validators
    @field_validator("tag", mode="before")
    def ensure_list_of_strings(cls, v):  # noqa
        if isinstance(v, str):
            return [v]
        elif isinstance(v, list):
            return v
        else:
            raise ValueError("Tag must be a string or a list of strings")

    @field_validator("tag")
    def ensure_unique_items(cls, v):  # noqa
        if v is not None and len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


class DynamicUserGroupCreateModel(DynamicUserGroupBaseModel):
    """Represents the creation of a new Dynamic User Group object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a DynamicUserGroupCreateModel object,
    it inherits all fields from the DynamicUserGroupBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.

    """

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "DynamicUserGroupCreateModel":
        """Validate that exactly one container type is provided."""
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class DynamicUserGroupUpdateModel(DynamicUserGroupBaseModel):
    """Represents the update of an existing Dynamic User Group object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a DynamicUserGroupUpdateModel object,
    and includes an optional id field.
    """

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the dynamic user group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class DynamicUserGroupResponseModel(DynamicUserGroupBaseModel):
    """Represents the response model for a Dynamic User Group object from Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a DynamicUserGroupResponseModel object,
    it inherits all fields from the DynamicUserGroupBaseModel class, and adds its own attribute for the
    id field.

    Attributes:
        id (UUID): The UUID of the dynamic user group.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the dynamic user group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
