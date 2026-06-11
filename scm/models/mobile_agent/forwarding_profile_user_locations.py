"""Forwarding Profile User Location models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect forwarding profile
user locations and related data.
"""

# scm/models/mobile_agent/forwarding_profile_user_locations.py

# Standard library imports
from typing import List, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field, model_validator

# Pattern for user location IP addresses (IPv4 with optional wildcards or CIDR suffix)
USER_LOCATION_IP_PATTERN = (
    r"^(\*|25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    r"\.(\*|25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    r"\.(\*|25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    r"\.((\*|(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))"
    r"|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|[1-2]?[0-9])))$"
)


class UserLocationIpEntry(BaseModel):
    """An IP address entry for a GlobalProtect user location.

    Attributes:
        name (str): The user location IP address.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: str = Field(
        ...,
        description="The user location IP address",
        pattern=USER_LOCATION_IP_PATTERN,
    )


class UserLocationInternalHostDetection(BaseModel):
    """Internal host detection settings for a GlobalProtect user location.

    Attributes:
        ip_address (Optional[str]): The user location IP address.
        fqdn (Optional[str]): The fully qualified domain name.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    ip_address: Optional[str] = Field(
        None,
        description="The user location IP address",
        pattern=USER_LOCATION_IP_PATTERN,
    )
    fqdn: Optional[str] = Field(
        None,
        description="The fully qualified domain name",
        max_length=255,
        pattern=r"^([\*a-zA-Z0-9._-])+$",
    )


class UserLocationChoice(BaseModel):
    """Location matching criteria for a GlobalProtect user location.

    Exactly one of internal_host_detection or ip_addresses must be provided.

    Attributes:
        internal_host_detection (Optional[UserLocationInternalHostDetection]):
            Internal host detection settings.
        ip_addresses (Optional[List[UserLocationIpEntry]]): List of IP address entries.

    Error:
        ValueError: Raised when not exactly one of the choice fields is provided.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    internal_host_detection: Optional[UserLocationInternalHostDetection] = Field(
        None,
        description="Internal host detection settings",
    )
    ip_addresses: Optional[List[UserLocationIpEntry]] = Field(
        None,
        description="List of IP address entries",
    )

    @model_validator(mode="after")
    def validate_choice(self) -> "UserLocationChoice":
        """Validate that exactly one of internal_host_detection or ip_addresses is provided."""
        provided = [
            field
            for field in (self.internal_host_detection, self.ip_addresses)
            if field is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'internal_host_detection' or 'ip_addresses' must be provided."
            )
        return self


class ForwardingProfileUserLocationBaseModel(BaseModel):
    """Base model for GlobalProtect Forwarding Profile User Locations.

    Contains fields common to all CRUD operations.

    Attributes:
        name (str): The name of the user location.
        description (Optional[str]): An optional description.
        choice (UserLocationChoice): The location matching criteria.

    """

    # Pydantic model configuration
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        description="The name of the user location",
        max_length=64,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )
    choice: UserLocationChoice = Field(
        ...,
        description="The location matching criteria",
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        description="An optional description of the user location",
        max_length=1023,
    )


class ForwardingProfileUserLocationCreateModel(ForwardingProfileUserLocationBaseModel):
    """Represents the creation of a new GlobalProtect Forwarding Profile User Location."""


class ForwardingProfileUserLocationUpdateModel(ForwardingProfileUserLocationBaseModel):
    """Represents the update of an existing GlobalProtect Forwarding Profile User Location.

    Attributes:
        id (UUID): The UUID of the user location.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the user location",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ForwardingProfileUserLocationResponseModel(ForwardingProfileUserLocationBaseModel):
    """Represents a GlobalProtect Forwarding Profile User Location returned by the API.

    Attributes:
        id (UUID): The UUID of the user location.

    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the user location",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
