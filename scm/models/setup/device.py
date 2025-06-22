"""Models for interacting with Devices in Palo Alto Networks' Strata Cloud Manager.

Defines Pydantic models for representing Device resources returned by the SCM API.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# TODO: These placeholder models were defined in the incorrect location
# - scm/models/config/setup/devices.py. They need proper implementation:
# class InstalledLicenseModel(BaseModel):
#     """Represents an installed license on a device."""
#     pass
#
# class AvailableLicenseModel(BaseModel):
#     """Represents an available license for a device."""
#     pass


class DeviceLicenseModel(BaseModel):
    """Model for a license entry in available_licenses or installed_licenses."""

    feature: str = Field(..., description="Feature name for the license.")
    expires: str = Field(..., description="Expiration date (YYYY-MM-DD).")
    issued: str = Field(..., description="Issued date (YYYY-MM-DD).")
    expired: Optional[str] = Field(
        default=None, description="Whether the license is expired (yes/no)."
    )
    authcode: Optional[str] = Field(
        default=None, description="Authorization code for the license, if present."
    )


class DeviceBaseModel(BaseModel):
    """Base model for Device resources containing common fields.

    Attributes:
        name: Device name.
        display_name: Display name for the device.
        serial_number: Device serial number.
        family: Device family (e.g., 'vm').
        model: Device model (e.g., 'PA-VM').
        folder: Folder name containing the device.
        hostname: Device hostname.
        type: Device type (e.g., 'on-prem').
        device_only: True if device-only entry.
        is_connected: Connection status.
        description: Device description.

    """

    name: Optional[str] = Field(None, description="Device name.")
    display_name: Optional[str] = Field(
        None, alias="displayName", description="Display name for the device."
    )
    serial_number: Optional[str] = Field(
        None, alias="serialNumber", description="Device serial number."
    )
    family: Optional[str] = Field(None, description="Device family (e.g., 'vm').")
    model: Optional[str] = Field(None, description="Device model (e.g., 'PA-VM').")
    folder: Optional[str] = Field(None, description="Folder name containing the device.")
    hostname: Optional[str] = Field(None, description="Device hostname.")
    type: Optional[str] = Field(None, description="Device type (e.g., 'on-prem').")
    device_only: Optional[bool] = Field(None, description="True if device-only entry.")
    is_connected: Optional[bool] = Field(
        None, alias="isConnected", description="Connection status."
    )
    description: Optional[str] = Field(None, description="Device description.")


class DeviceCreateModel(DeviceBaseModel):
    """Model for creating new Device resources.

    Inherits all fields from DeviceBaseModel without additional fields.
    """

    pass


class DeviceUpdateModel(DeviceBaseModel):
    """Model for updating existing Device resources.

    Attributes:
        id: The unique identifier of the device to update.

    """

    id: str = Field(..., description="Unique device identifier (serial number).")


class DeviceResponseModel(DeviceBaseModel):
    """Model for Device responses from the API.

    Attributes:
        id: Unique device identifier (serial number).
        connected_since: ISO timestamp when connected.
        last_disconnect_time: ISO timestamp when last disconnected.
        last_device_update_time: ISO timestamp of last device update.
        last_das_update_time: ISO timestamp of last DAS update.
        deactivate_wait_hrs: Deactivation wait hours.
        deactivated_by: Who deactivated the device.
        to_be_deactivated_at: Scheduled deactivation time.
        dev_cert_detail: Device certificate detail.
        dev_cert_expiry_date: Device certificate expiry (epoch).
        app_version: App version.
        app_release_date: App release date.
        av_release_date: Antivirus release date.
        anti_virus_version: Antivirus version.
        threat_version: Threat version.
        threat_release_date: Threat release date.
        wf_ver: WildFire version.
        wf_release_date: WildFire release date.
        iot_version: IoT version.
        iot_release_date: IoT release date.
        gp_client_verion: GlobalProtect client version.
        gp_data_version: GlobalProtect data version.
        log_db_version: Log DB version.
        software_version: Software version.
        uptime: Device uptime.
        mac_address: MAC address.
        ip_address: IPv4 address.
        ipV6_address: IPv6 address.
        url_db_ver: URL DB version.
        url_db_type: URL DB type.
        license_match: License match status.
        available_licenses: List of available licenses.
        installed_licenses: List of installed licenses.
        ha_state: HA state.
        ha_peer_state: HA peer state.
        ha_peer_serial: HA peer serial number.
        vm_state: VM state.

    """

    id: str = Field(..., description="Unique device identifier (serial number).")
    connected_since: Optional[str] = Field(
        None, alias="connectedSince", description="ISO timestamp when connected."
    )
    last_disconnect_time: Optional[str] = Field(
        None, description="ISO timestamp when last disconnected."
    )
    last_device_update_time: Optional[str] = Field(
        None, description="ISO timestamp of last device update."
    )
    last_das_update_time: Optional[str] = Field(
        None, description="ISO timestamp of last DAS update."
    )
    deactivate_wait_hrs: Optional[int] = Field(None, description="Deactivation wait hours.")
    deactivated_by: Optional[str] = Field(None, description="Who deactivated the device.")
    to_be_deactivated_at: Optional[str] = Field(None, description="Scheduled deactivation time.")
    dev_cert_detail: Optional[str] = Field(None, description="Device certificate detail.")
    dev_cert_expiry_date: Optional[str] = Field(
        None, description="Device certificate expiry (epoch)."
    )
    app_version: Optional[str] = Field(None, description="App version.")
    app_release_date: Optional[str] = Field(None, description="App release date.")
    av_release_date: Optional[str] = Field(None, description="Antivirus release date.")
    anti_virus_version: Optional[str] = Field(None, description="Antivirus version.")
    threat_version: Optional[str] = Field(None, description="Threat version.")
    threat_release_date: Optional[str] = Field(None, description="Threat release date.")
    wf_ver: Optional[str] = Field(None, description="WildFire version.")
    wf_release_date: Optional[str] = Field(None, description="WildFire release date.")
    iot_version: Optional[str] = Field(None, description="IoT version.")
    iot_release_date: Optional[str] = Field(None, description="IoT release date.")
    gp_client_verion: Optional[str] = Field(None, description="GlobalProtect client version.")
    gp_data_version: Optional[str] = Field(None, description="GlobalProtect data version.")
    log_db_version: Optional[str] = Field(None, description="Log DB version.")
    software_version: Optional[str] = Field(None, description="Software version.")
    uptime: Optional[str] = Field(None, description="Device uptime.")
    mac_address: Optional[str] = Field(None, description="MAC address.")
    ip_address: Optional[str] = Field(None, description="IPv4 address.")
    ipV6_address: Optional[str] = Field(None, description="IPv6 address.")
    url_db_ver: Optional[str] = Field(None, description="URL DB version.")
    url_db_type: Optional[str] = Field(None, description="URL DB type.")
    license_match: Optional[bool] = Field(None, description="License match status.")
    available_licenses: Optional[List[DeviceLicenseModel]] = Field(
        None, alias="availableLicenses", description="List of available licenses."
    )
    installed_licenses: Optional[List[DeviceLicenseModel]] = Field(
        None, alias="installedLicenses", description="List of installed licenses."
    )
    ha_state: Optional[str] = Field(None, description="HA state.")
    ha_peer_state: Optional[str] = Field(None, description="HA peer state.")
    ha_peer_serial: Optional[str] = Field(None, description="HA peer serial number.")
    vm_state: Optional[str] = Field(None, description="VM state.")

    model_config = ConfigDict(
        extra="allow"  # Allow extra fields if the API adds new ones
    )


class DeviceListResponseModel(BaseModel):
    """Model for the paginated response from GET /devices."""

    data: List[DeviceResponseModel] = Field(..., description="List of device objects.")
    limit: int = Field(..., description="Max number of devices returned.")
    offset: int = Field(..., description="Offset for pagination.")
    total: int = Field(..., description="Total number of devices available.")
