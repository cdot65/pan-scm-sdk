# scm/models/address_group.py

import uuid
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator, ConfigDict


class DynamicFilter(BaseModel):
    """
    Represents the dynamic filter for an AddressRequestModel Group in Palo Alto Networks' Strata Cloud Manager.

    Attributes:
        filter (str): Tag-based filter defining group membership.
    """

    filter: str = Field(
        ...,
        max_length=1024,
        description="Tag based filter defining group membership",
        examples=["'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"],
    )


class AddressGroupRequestModel(BaseModel):
    """
    Represents an Address Group for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an Address Group,
    including required fields, optional fields, address types, and container types.

    Attributes:
        name (str): The name of the address object.
        description (Optional[str]): The description of the address object.
        tag (Optional[List[str]]): Tags associated with the address object.
        dynamic (Optional[DynamicFilter]): Dynamic filter defining group membership.
        static (str):Container type of Static AddressRequestModel Group.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    Error:
        ValueError: Raised when address type or container type validation fails.

    """

    # Model configuration
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the address object",
    )

    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="The description of the address object",
    )
    tag: Optional[List[str]] = Field(
        None,
        max_length=64,
        description="Tags associated with the address object",
    )

    # AddressRequestModel Types
    dynamic: Optional[DynamicFilter] = Field(
        None,
        description="Dynamic filter defining group membership",
    )
    static: Optional[List[str]] = Field(
        None,
        description="Container type of Static AddressRequestModel Group",
        min_length=1,
        max_length=255,
        examples=["database-servers"],
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

    # Custom Validators
    @model_validator(mode="before")
    def validate_uuid(cls, values):
        if "id" in values and values["id"] is not None:
            try:
                uuid.UUID(values["id"])
            except ValueError:
                raise ValueError("Invalid UUID format for 'id'")
        return values

    @model_validator(mode="after")
    def validate_address_group_type(self) -> "AddressGroupRequestModel":
        group_type_fields = [
            "dynamic",
            "static",
        ]
        provided = [
            field for field in group_type_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'static' or 'dynamic' must be provided.")
        return self

    @model_validator(mode="after")
    def validate_container_type(self) -> "AddressGroupRequestModel":
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


class AddressGroupResponseModel(BaseModel):
    """
    Represents an AddressGroup response for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an Address Group,
    including required fields, optional fields, address types, and container types.

    Attributes:
        id (UUID): The UUID of the address object.
        name (str): The name of the address object.
        description (Optional[str]): The description of the address object.
        tag (Optional[List[str]]): Tags associated with the address object.
        dynamic (Optional[DynamicFilter]): Dynamic filter defining group membership.
        static (str):Container type of Static AddressRequestModel Group.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    Error:
        ValueError: Raised when address type or container type validation fails.

    """

    # Model configuration
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the address object",
    )

    # Optional fields
    id: Optional[str] = Field(
        None,
        description="The UUID of the address object",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="The description of the address object",
    )
    tag: Optional[List[str]] = Field(
        None,
        max_length=64,
        description="Tags associated with the address object",
    )

    # AddressRequestModel Types
    dynamic: Optional[DynamicFilter] = Field(
        None,
        description="Dynamic filter defining group membership",
    )
    static: Optional[List[str]] = Field(
        None,
        description="Container type of Static AddressRequestModel Group",
        min_length=1,
        max_length=255,
        examples=["database-servers"],
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

    # Custom Validators
    @model_validator(mode="before")
    def validate_uuid(cls, values):
        if "id" in values and values["id"] is not None:
            try:
                uuid.UUID(values["id"])
            except ValueError:
                raise ValueError("Invalid UUID format for 'id'")
        return values

    @model_validator(mode="after")
    def validate_address_group_type(self) -> "AddressGroupRequestModel":
        group_type_fields = [
            "dynamic",
            "static",
        ]
        provided = [
            field for field in group_type_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'static' or 'dynamic' must be provided.")
        return self

    @model_validator(mode="after")
    def validate_container_type(self) -> "AddressGroupRequestModel":
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
