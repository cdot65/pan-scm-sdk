# scm/models/objects/address_group.py

import uuid
from typing import Optional, List

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
    constr,
)


TagString = constr(max_length=64)


class DynamicFilter(BaseModel):
    """
    Represents the dynamic filter for an Address Group in Palo Alto Networks' Strata Cloud Manager.

    Attributes:
        filter (str): Tag-based filter defining group membership.
    """

    filter: str = Field(
        ...,
        max_length=1024,
        description="Tag based filter defining group membership",
        examples=["'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"],
    )


class AddressGroupBaseModel(BaseModel):
    """
    Base model for Address Group objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the address group.
        description (Optional[str]): The description of the address group.
        tag (Optional[List[TagString]]): Tags associated with the address group.
        dynamic (Optional[DynamicFilter]): Dynamic filter defining group membership.
        static (Optional[List[str]]): List of static addresses in the group.
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
        description="The name of the address group",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="The description of the address group",
    )
    tag: Optional[List[TagString]] = Field(
        None,
        description="Tags associated with the address group",
    )
    dynamic: Optional[DynamicFilter] = Field(
        None,
        description="Dynamic filter defining group membership",
    )
    static: Optional[List[str]] = Field(
        None,
        description="Container type of Static Address Group",
        min_length=1,
        max_length=255,
        examples=["database-servers"],
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

    @model_validator(mode="after")
    def validate_address_group_type(self) -> "AddressGroupBaseModel":
        group_type_fields = ["dynamic", "static"]
        provided = [
            field for field in group_type_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'static' or 'dynamic' must be provided.")
        return self


class AddressGroupCreateModel(AddressGroupBaseModel):
    """
    Model for creating a new Address Group.
    Inherits from AddressGroupBase and adds container type validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "AddressGroupCreateModel":
        container_fields = ["folder", "snippet", "device"]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class AddressGroupUpdateModel(AddressGroupBaseModel):
    """
    Model for updating an existing Address Group.
    All fields are optional to allow partial updates.
    """

    name: Optional[str] = Field(
        None,
        max_length=63,
        description="The name of the address group",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )


class AddressGroupResponseModel(AddressGroupBaseModel):
    """
    Model for Address Group responses.
    Includes all base fields plus the id field.
    """

    id: str = Field(
        ...,
        description="The UUID of the address group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    @field_validator("id")
    def validate_uuid(cls, v):  # noqa
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format for 'id'")
        return v
