"""Models for SCM Devices Endpoint.

Ref: https://pan.dev/sase/api/config/v1/resources/devices/
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InstalledLicenseModel(BaseModel):
    """Represents an installed license on a device."""

    # TODO: Add fields based on actual API response
    pass


class AvailableLicenseModel(BaseModel):
    """Represents an available license for a device."""

    # TODO: Add fields based on actual API response
    pass
    # Note: Alias might be needed if API response has typo 'available_licensess'
    # example_field: Optional[str] = Field(alias="available_licensess", default=None)


class DeviceGetResponseModel(BaseModel):
    """Represents the response model for a GET request to the /devices endpoint."""

    id: str
    name: str
    display_name: Optional[str] = Field(alias="displayName", default=None)
    hostname: Optional[str] = None
    description: Optional[str] = None
    serial_number: Optional[str] = Field(alias="serialNumber", default=None)
    folder: Optional[str] = None
    type: Optional[str] = None  # e.g., 'Prisma Access'
    family: Optional[str] = None  # e.g., 'Cloud Service'
    model: Optional[str] = None  # e.g., 'Prisma Access GW'
    is_connected: Optional[bool] = Field(alias="isConnected", default=None)
    connected_since: Optional[str] = Field(
        alias="connectedSince", default=None
    )  # Consider datetime conversion?

    # Placeholder for nested models - will be filled in later
    installed_licenses: Optional[List[InstalledLicenseModel]] = Field(
        alias="installedLicenses", default=None
    )
    available_licenses: Optional[List[AvailableLicenseModel]] = Field(
        alias="available_licensess", default=None
    )  # Check API for correct key
    # TODO: Add other potential fields from API response

    # Pydantic v2 model configuration
    model_config = ConfigDict(
        # Allow extra fields if the API adds new ones
        extra="allow"
    )
