from typing import Optional, List

from pydantic import BaseModel, Field, model_validator, ConfigDict


class Address(BaseModel):
    """
    Represents an Address object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an Address object,
    including required fields, optional fields, address types, and container types.

    Attributes:
        id (str): The UUID of the address object.
        name (str): The name of the address object.
        description (Optional[str]): The description of the address object.
        tag (Optional[List[str]]): Tags associated with the address object.
        ip_netmask (str): IP address with or without CIDR notation.
        ip_range (str): IP address range.
        ip_wildcard (str): IP wildcard mask.
        fqdn (str): Fully qualified domain name.
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
    id: str = Field(
        ...,
        description="The UUID of the address object",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the address object",
    )

    # Optional fields
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

    # Address Types
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

    # Container Types
    folder: str = Field(
        ...,
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
    @model_validator(mode="after")
    def validate_address_type(self) -> "Address":
        address_fields = [
            "ip_netmask",
            "ip_range",
            "ip_wildcard",
            "fqdn",
        ]
        provided = [
            field for field in address_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            )
        return self

    @model_validator(mode="after")
    def validate_container_type(self) -> "Address":
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
