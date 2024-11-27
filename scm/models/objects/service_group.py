# scm/models/objects/service_group.py

from typing import Optional, List
from uuid import UUID

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
        description (Optional[str]): The description of the service group.
        tag (Optional[List[TagString]]): Tags associated with the service group.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        max_length=63,
        description="The name of the service group",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="The description of the service group",
    )
    tag: Optional[List[TagString]] = Field(  # type: ignore
        None,
        description="Tags associated with the service group",
    )
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
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


class ServiceGroupCreateModel(ServiceGroupBaseModel):
    """
    Model for creating a new Service Group.
    Inherits from ServiceGroupBase and adds container type validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "ServiceGroupCreateModel":
        container_fields = ["folder", "snippet", "device"]
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
    Model for updating an existing Service Group.
    All fields are optional to allow partial updates.
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
