"""Network Locations models for Strata Cloud Manager SDK.

Contains Pydantic models for representing network location objects and related data.
"""

# scm/models/deployment/network_locations.py

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NetworkLocationModel(BaseModel):
    """Model for Network Location objects.

    Network Locations are read-only resources in the Strata Cloud Manager API,
    only supporting list/get operations.

    Attributes:
        value (str): The system value of the location (e.g., 'us-west-1')
        display (str): The human-readable display name of the location
        continent (str): The continent in which the location exists
        latitude (float): The latitudinal position of the location (-90 to 90)
        longitude (float): The longitudinal position of the location (-180 to 180)
        region (str): The region code of the location
        aggregate_region (str): The aggregate region identifier

    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
    )

    value: str = Field(
        ...,
        description="The system value of the location",
        examples=["us-west-1"],
    )

    display: str = Field(
        ...,
        description="The location as displayed in the Strata Cloud Manager portal",
        examples=["US West"],
    )

    continent: Optional[str] = Field(
        None,
        description="The continent in which the location exists",
        examples=["North America"],
    )

    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="The latitudinal position of the location",
        examples=[37.38314],
    )

    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="The longitudinal position of the location",
        examples=[-121.98306],
    )

    region: Optional[str] = Field(
        None,
        description="The region code of the location",
        examples=["us-west-1"],
    )

    aggregate_region: Optional[str] = Field(
        None,
        description="The aggregate region identifier",
        examples=["us-southwest"],
    )
