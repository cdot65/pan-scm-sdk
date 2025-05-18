"""Regions models for Strata Cloud Manager SDK.

Contains Pydantic models for representing region objects and related data.
"""

# scm/models/objects/regions.py

# Standard library imports
from typing import List, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GeoLocation(BaseModel):
    """Geographic location model for region objects.

    Attributes:
        latitude (float): The latitudinal position of the region (-90 to 90).
        longitude (float): The longitudinal position of the region (-180 to 180).

    """

    latitude: float = Field(
        ..., description="The latitudinal position of the region", ge=-90, le=90
    )
    longitude: float = Field(
        ..., description="The longitudinal position of the region", ge=-180, le=180
    )


class RegionBaseModel(BaseModel):
    """Base model for Region objects containing fields common to all CRUD operations.

    Note:
        Although this model supports 'description' and 'tag' fields for consistency
        with other object types in the SDK, these fields are not supported by the
        Strata Cloud Manager API for Region objects. They will be automatically
        excluded when sending requests to the API, but can be used locally for
        organizing and managing region objects within your application.

    Attributes:
        name (str): The name of the region.
        description (Optional[str]): A description of the region (not sent to API).
        tag (Optional[List[str]]): A list of tags associated with the region (not sent to API).
        geo_location (Optional[GeoLocation]): The geographic location of the region.
        address (Optional[List[str]]): A list of addresses associated with the region.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    """

    # Required fields
    name: str = Field(
        ...,
        description="The name of the region (may include IPv4, IPv6, ranges, and labels)",
        pattern=r"^[\w .:/\-]+$",
        max_length=64,  # Increase if needed for long IPv6 ranges
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        description="A description of the region",
    )
    tag: Optional[List[str]] = Field(
        None,
        description="A list of tags associated with the region",
    )
    geo_location: Optional[GeoLocation] = Field(
        None,
        description="The geographic location of the region",
    )
    address: Optional[List[str]] = Field(
        None,
        description="A list of addresses associated with the region",
    )

    # Container Types
    folder: Optional[str] = Field(
        None,
        description="The folder in which the resource is defined",
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        examples=["Global"],
    )
    snippet: Optional[str] = Field(
        None,
        description="The snippet in which the resource is defined",
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        examples=["My Snippet"],
    )
    device: Optional[str] = Field(
        None,
        description="The device in which the resource is defined",
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        examples=["My Device"],
    )

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Custom validator to ensure addresses and tags are unique
    @field_validator("address", "tag", mode="before")
    def ensure_list_of_strings(cls, v):  # noqa
        if v is None:
            return v
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return v
        # Catch all other types
        raise ValueError("Value must be a string or a list of strings")

    @field_validator("address")
    def ensure_unique_addresses(cls, v):  # noqa
        if v is not None and len(v) != len(set(v)):
            raise ValueError("List of addresses must contain unique values")
        return v

    @field_validator("tag")
    def ensure_unique_tags(cls, v):  # noqa
        if v is not None and len(v) != len(set(v)):
            raise ValueError("List of tags must contain unique values")
        return v


class RegionCreateModel(RegionBaseModel):
    """Represents the creation of a new Region object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a RegionCreateModel object,
    it inherits all fields from the RegionBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.

    """

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "RegionCreateModel":
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


class RegionUpdateModel(RegionBaseModel):
    """Represents the update of an existing Region object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an RegionUpdateModel object.
    """

    id: UUID = Field(
        ...,
        description="The UUID of the region",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class RegionResponseModel(RegionBaseModel):
    """Represents a Region object response from Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an RegionResponseModel object,
    it inherits all fields from the RegionBaseModel class, adds an id field, and provides
    validation logic for predefined responses.

    Attributes:
        id (Optional[UUID]): The UUID of the region. May be missing for predefined regions.

    """

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the region (may be missing for predefined regions)",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
