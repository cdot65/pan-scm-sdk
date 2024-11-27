# scm/models/objects/address.py

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


class AddressBaseModel(BaseModel):
    """
    Base model for Address objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the address object.
        description (Optional[str]): The description of the address object.
        tag (Optional[List[TagString]]): Tags associated with the address object.
        ip_netmask (str): IP address with or without CIDR notation.
        ip_range (str): IP address range.
        ip_wildcard (str): IP wildcard mask.
        fqdn (str): Fully qualified domain name.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.
    """

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the address object",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )

    # Address types
    ip_netmask: Optional[str] = Field(
        None,
        description="IP address with or without CIDR notation",
        examples=["192.168.80.0/24"],
    )
    ip_range: Optional[str] = Field(
        None,
        description="IP address range",
        examples=["10.0.0.1-10.0.0.4"],
    )
    ip_wildcard: Optional[str] = Field(
        None,
        description="IP wildcard mask",
        examples=["10.20.1.0/0.0.248.255"],
    )
    fqdn: Optional[str] = Field(
        None,
        description="Fully qualified domain name",
        examples=["some.example.com"],
        min_length=1,
        max_length=255,
        pattern=r"^[a-zA-Z0-9_]([a-zA-Z0-9._-])*[a-zA-Z0-9]$",
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="The description of the address object",
    )
    tag: Optional[List[TagString]] = Field(  # type: ignore
        None,
        description="Tags associated with the address object",
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
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v

    @model_validator(mode="after")
    def validate_address_type(self) -> "AddressBaseModel":
        """Validates that exactly one address type is provided."""
        address_fields = [
            "ip_netmask",
            "ip_range",
            "ip_wildcard",
            "fqdn",
        ]
        provided = [
            field for field in address_fields if getattr(self, field) is not None
        ]

        if len(provided) == 0:
            raise ValueError(
                "Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            )
        elif len(provided) > 1:
            raise ValueError(
                "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            )

        return self


class AddressCreateModel(AddressBaseModel):
    """
    Represents the creation of a new Address object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an AddressCreateModel object,
    it inherits all fields from the AddressBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.
    """

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "AddressCreateModel":
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


class AddressUpdateModel(AddressBaseModel):
    """
    Represents the update of an existing Address object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an AddressUpdateModel object.
    """

    id: Optional[UUID] = Field(
        ...,  # This makes it optional
        description="The UUID of the address object",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class AddressResponseModel(AddressBaseModel):
    """
    Represents the creation of a new Address object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an AddressResponseModel object,
    it inherits all fields from the AddressBaseModel class, adds its own attribute for the
    id field, and provides a custom validator to ensure that it is of the type UUID

    Attributes:
        id (UUID): The UUID of the address object.

    Error:
        ValueError: Raised when container type validation fails.
    """

    id: UUID = Field(
        ...,
        description="The UUID of the application group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
