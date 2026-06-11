"""Forwarding Profile Destination models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect forwarding profile destinations
and related data.
"""

# scm/models/mobile_agent/forwarding_profile_destinations.py

# Standard library imports
from typing import List, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field

# IP address with wildcards and CIDR notation support, per the SCM mobile-agent API spec
IP_ENTRY_PATTERN = (
    r"^(\*|25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    r"\.(\*|25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    r"\.(\*|25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    r"\.(((\*|(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))"
    r"|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|[1-2]?[0-9]))))$"
)


class DestinationFqdnEntry(BaseModel):
    """FQDN entry for a GlobalProtect forwarding profile destination.

    Attributes:
        name (str): The FQDN, supporting wildcards and at most one $ at the end.
        port (Optional[int]): The port number.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: str = Field(
        ...,
        description="alphanumeric string [*0-9a-zA-Z._-] and at most one $ by the end",
        max_length=255,
        pattern=r"^([\*a-zA-Z0-9._-])+\$?$",
    )
    port: Optional[int] = Field(
        default=None,
        description="Port number",
        ge=1,
        le=65535,
    )


class DestinationIpEntry(BaseModel):
    """IP address entry for a GlobalProtect forwarding profile destination.

    Attributes:
        name (str): The IP address, with wildcards and CIDR notation support.
        port (Optional[int]): The port number.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: str = Field(
        ...,
        description="IP address with wildcards and CIDR notation support",
        pattern=IP_ENTRY_PATTERN,
    )
    port: Optional[int] = Field(
        default=None,
        description="Port number",
        ge=1,
        le=65535,
    )


class ForwardingProfileDestinationBaseModel(BaseModel):
    """Base model for GlobalProtect Forwarding Profile Destinations containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the destination.
        description (Optional[str]): The description of the destination.
        fqdn (Optional[List[DestinationFqdnEntry]]): The FQDN entries for the destination.
        ip_addresses (Optional[List[DestinationIpEntry]]): The IP address entries for the destination.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the destination",
        max_length=64,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )
    description: Optional[str] = Field(
        default=None,
        description="The description of the destination",
        max_length=1023,
    )
    fqdn: Optional[List[DestinationFqdnEntry]] = Field(
        default=None,
        description="The FQDN entries for the destination",
    )
    ip_addresses: Optional[List[DestinationIpEntry]] = Field(
        default=None,
        description="The IP address entries for the destination",
    )


class ForwardingProfileDestinationCreateModel(ForwardingProfileDestinationBaseModel):
    """Represents the creation of a new GlobalProtect Forwarding Profile Destination.

    This class defines the structure and validation rules for creating destinations.
    The folder is supplied as a query parameter by the service class, not in the request body.
    """


class ForwardingProfileDestinationUpdateModel(ForwardingProfileDestinationBaseModel):
    """Represents the update of an existing GlobalProtect Forwarding Profile Destination.

    This class defines the structure and validation rules for updating destinations.
    The object ID is supplied in the URL path by the service class; if provided here it is
    removed from the request payload.

    Attributes:
        id (Optional[UUID]): The UUID of the destination.

    """

    id: Optional[UUID] = Field(
        default=None,
        description="The UUID of the destination",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ForwardingProfileDestinationResponseModel(ForwardingProfileDestinationBaseModel):
    """Represents the response model for GlobalProtect Forwarding Profile Destinations.

    This class defines the structure for destinations returned by the API.

    Attributes:
        id (Optional[UUID]): The UUID of the destination.

    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: Optional[UUID] = Field(
        default=None,
        description="The UUID of the destination",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
