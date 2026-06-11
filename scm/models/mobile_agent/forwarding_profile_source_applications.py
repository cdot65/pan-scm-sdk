"""Forwarding Profile Source Application models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect forwarding profile
source applications and related data.
"""

# scm/models/mobile_agent/forwarding_profile_source_applications.py

# Standard library imports
from typing import List, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field


class ForwardingProfileSourceApplicationBaseModel(BaseModel):
    """Base model for GlobalProtect Forwarding Profile Source Applications.

    Contains fields common to all CRUD operations.

    Attributes:
        name (str): The name of the source application.
        description (Optional[str]): An optional description.
        applications (List[str]): List of applications.

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
        description="The name of the source application",
        max_length=64,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )
    applications: List[str] = Field(
        ...,
        description="List of applications",
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        description="An optional description of the source application",
        max_length=1023,
    )


class ForwardingProfileSourceApplicationCreateModel(
    ForwardingProfileSourceApplicationBaseModel
):
    """Represents the creation of a new GlobalProtect Forwarding Profile Source Application."""


class ForwardingProfileSourceApplicationUpdateModel(
    ForwardingProfileSourceApplicationBaseModel
):
    """Represents the update of an existing GlobalProtect Forwarding Profile Source Application.

    Attributes:
        id (UUID): The UUID of the source application.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the source application",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ForwardingProfileSourceApplicationResponseModel(
    ForwardingProfileSourceApplicationBaseModel
):
    """Represents a GlobalProtect Forwarding Profile Source Application returned by the API.

    Attributes:
        id (UUID): The UUID of the source application.

    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the source application",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
