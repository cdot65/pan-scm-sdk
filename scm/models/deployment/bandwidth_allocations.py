"""Bandwidth Allocations models for Strata Cloud Manager SDK.

Contains Pydantic models for representing bandwidth allocation objects and related data.
"""

# scm/models/deployment/bandwidth_allocations.py

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QosModel(BaseModel):
    """QoS configuration for bandwidth allocations."""

    enabled: Optional[bool] = Field(None, description="Enable QoS for bandwidth allocation")
    customized: Optional[bool] = Field(None, description="Use customized QoS settings")
    profile: Optional[str] = Field(None, description="QoS profile name")
    guaranteed_ratio: Optional[float] = Field(None, description="Guaranteed ratio for bandwidth")


class BandwidthAllocationBaseModel(BaseModel):
    """Base model for Bandwidth Allocation objects containing fields common to all CRUD operations."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        description="Name of the aggregated bandwidth region",
        max_length=63,
        pattern=r"^[0-9a-zA-Z._\- ]+$",  # Common pattern seen in other models
    )
    allocated_bandwidth: float = Field(
        ...,
        description="Bandwidth to allocate in Mbps",
        gt=0,
    )

    # Optional fields
    spn_name_list: Optional[List[str]] = Field(
        None,
        description="List of SPN names for this region",
    )
    qos: Optional[QosModel] = Field(
        None,
        description="QoS configuration for bandwidth allocation",
    )


class BandwidthAllocationCreateModel(BandwidthAllocationBaseModel):
    """Model for creating a new Bandwidth Allocation."""

    # Unlike other models, bandwidth allocations don't have an ID field
    # They are identified by name and spn_name_list in the API
    pass


class BandwidthAllocationUpdateModel(BandwidthAllocationBaseModel):
    """Model for updating an existing Bandwidth Allocation."""

    # Unlike other models, bandwidth allocations don't have an ID field
    # Updates are done based on name and spn_name_list
    pass


class BandwidthAllocationResponseModel(BandwidthAllocationBaseModel):
    """Model for Bandwidth Allocation API responses."""

    # Unlike other models, bandwidth allocations don't include an ID in responses
    # based on the OpenAPI specification
    pass


class BandwidthAllocationListResponseModel(BaseModel):
    """Model for the list response from the Bandwidth Allocations API."""

    data: List[BandwidthAllocationResponseModel] = Field(
        ..., description="List of bandwidth allocations"
    )
    limit: int = Field(200, description="The maximum number of results per page")
    offset: int = Field(0, description="The offset into the list of results returned")
    total: int = Field(..., description="Total number of bandwidth allocations")
