# scm/models/objects/service_group.py

# Standard library imports
from typing import Optional, List
from uuid import UUID

# External libraries
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
    constr,
)

TagString = constr(max_length=64)


class ServiceGroupBaseModel(BaseModel):
    """
    Base model for Service Group objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the service group.
        tag (Optional[List[TagString]]): Tags associated with the service group.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.
    """

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the service group",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )

    members: List[str] = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="A list of members of the service group.",
        examples=[["custom-service1", "custom-service2"]],
    )

    # Optional fields
    tag: Optional[List[TagString]] = Field(  # type: ignore
        None,
        description="Tags associated with the service group",
    )

    # Container Types
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["Prisma Access"],
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
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    # Custom Validators
    @field_validator(
        "tag",
        "members",
        mode="before",
    )
    def ensure_list_of_strings(cls, v):  # noqa
        if isinstance(v, str):
            return [v]
        elif isinstance(v, list):
            return v
        else:
            raise ValueError("Tag must be a string or a list of strings")

    @field_validator(
        "tag",
        "members",
    )
    def ensure_unique_items(cls, v):  # noqa
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


class ServiceGroupCreateModel(ServiceGroupBaseModel):
    """
    Represents the creation of a new Service Group object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an ServiceGroupCreateModel object,
    it inherits all fields from the ServiceGroupBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "ServiceGroupCreateModel":
        """Validates that exactly one container type is provided."""
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class ServiceGroupUpdateModel(ServiceGroupBaseModel):
    """
    Represents the update of an existing Service Group object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an ServiceGroupUpdateModel object.
    """

    id: Optional[UUID] = Field(
        None,  # This makes it optional
        description="The UUID of the service object",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ServiceGroupResponseModel(ServiceGroupBaseModel):
    """
    Represents the creation of a new ServiceGroup object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a ServiceGroupResponseModel object,
    it inherits all fields from the ServiceGroupBaseModel class, adds its own attribute for the
    id field, and provides a custom validator to ensure that it is of the type UUID

    Attributes:
        id (UUID): The UUID of the service object.

    Error:
        ValueError: Raised when container type validation fails.
    """

    id: UUID = Field(
        ...,
        description="The UUID of the application group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
