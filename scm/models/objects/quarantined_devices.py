"""Quarantined Devices models for Strata Cloud Manager SDK.

Contains Pydantic models for representing quarantined device objects and related data.
"""

# scm/models/objects/quarantined_devices.py

# Standard library imports
from typing import Optional

# External libraries
from pydantic import BaseModel, ConfigDict, Field


class QuarantinedDevicesBaseModel(BaseModel):
    """Base model for Quarantined Devices objects containing fields common to all CRUD operations.

    Attributes:
        host_id (str): Device host ID.
        serial_number (Optional[str]): Device serial number.

    """

    # Required fields
    host_id: str = Field(
        ...,
        description="Device host ID",
    )

    # Optional fields
    serial_number: Optional[str] = Field(
        None,
        description="Device serial number",
    )

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class QuarantinedDevicesCreateModel(QuarantinedDevicesBaseModel):
    """Represents the creation of a new Quarantined Devices object for Palo Alto Networks' Strata Cloud Manager."""


class QuarantinedDevicesResponseModel(QuarantinedDevicesBaseModel):
    """Represents the response from creating or retrieving a Quarantined Devices object."""


class QuarantinedDevicesListParamsModel(BaseModel):
    """Parameters for listing Quarantined Devices.

    Attributes:
        host_id (Optional[str]): Filter by device host ID.
        serial_number (Optional[str]): Filter by device serial number.

    """

    host_id: Optional[str] = Field(
        None,
        description="Filter by device host ID",
    )
    serial_number: Optional[str] = Field(
        None,
        description="Filter by device serial number",
    )
