"""Global Settings models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect global settings and related data.
"""

# scm/models/mobile_agent/global_settings.py

# Standard library imports
from typing import List, Optional

# External libraries
from pydantic import BaseModel, ConfigDict, Field


class ManualGatewayRegion(BaseModel):
    """Manual gateway region entry for GlobalProtect global settings.

    Attributes:
        name (Optional[str]): The name of the region.
        locations (Optional[List[str]]): The locations within the region.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the region",
    )
    locations: Optional[List[str]] = Field(
        None,
        description="The locations within the region",
    )


class ManualGateway(BaseModel):
    """Manual gateway configuration for GlobalProtect global settings.

    Use the locations from the GET /infrastructure-settings deployment field
    to set up manual gateways.

    Attributes:
        region (Optional[List[ManualGatewayRegion]]): The manual gateway regions.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    region: Optional[List[ManualGatewayRegion]] = Field(
        None,
        description="The manual gateway regions",
    )


class GlobalSettingsBaseModel(BaseModel):
    """Base model for GlobalProtect Global Settings.

    Global settings are a singleton configuration object with only GET and PUT
    operations; there is no create, delete, or list-of-many.

    Attributes:
        agent_version (Optional[str]): The GlobalProtect agent version.
        manual_gateway (Optional[ManualGateway]): The manual gateway configuration.

    """

    # Pydantic model configuration
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    agent_version: Optional[str] = Field(
        None,
        description="The GlobalProtect agent version",
    )
    manual_gateway: Optional[ManualGateway] = Field(
        None,
        description="The manual gateway configuration",
    )


class GlobalSettingsUpdateModel(GlobalSettingsBaseModel):
    """Represents the update of the GlobalProtect Global Settings singleton."""


class GlobalSettingsResponseModel(GlobalSettingsBaseModel):
    """Represents the response model for GlobalProtect Global Settings."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )
