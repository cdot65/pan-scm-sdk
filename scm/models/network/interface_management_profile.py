"""Interface Management Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing interface management profile objects and related data.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InterfaceManagementProfileBaseModel(BaseModel):
    """Base model for Interface Management Profiles containing fields common to all operations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the interface management profile",
        pattern=r"^[0-9a-zA-Z._\- ]+$",
        max_length=63,
    )
    http: Optional[bool] = Field(
        None,
        description="Enable HTTP management",
    )
    https: Optional[bool] = Field(
        None,
        description="Enable HTTPS management",
    )
    telnet: Optional[bool] = Field(
        None,
        description="Enable Telnet management",
    )
    ssh: Optional[bool] = Field(
        None,
        description="Enable SSH management",
    )
    ping: Optional[bool] = Field(
        None,
        description="Enable ping",
    )
    snmp: Optional[bool] = Field(
        None,
        description="Enable SNMP management",
    )
    http_ocsp: Optional[bool] = Field(
        None,
        alias="http-ocsp",
        description="Enable HTTP OCSP",
    )
    response_pages: Optional[bool] = Field(
        None,
        alias="response-pages",
        description="Enable response pages",
    )
    userid_service: Optional[bool] = Field(
        None,
        alias="userid-service",
        description="Enable User-ID service",
    )
    userid_syslog_listener_ssl: Optional[bool] = Field(
        None,
        alias="userid-syslog-listener-ssl",
        description="Enable User-ID syslog listener SSL",
    )
    userid_syslog_listener_udp: Optional[bool] = Field(
        None,
        alias="userid-syslog-listener-udp",
        description="Enable User-ID syslog listener UDP",
    )
    permitted_ip: Optional[List[str]] = Field(
        None,
        alias="permitted-ip",
        description="List of permitted IP addresses",
    )

    # Container fields
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
    )


class InterfaceManagementProfileCreateModel(InterfaceManagementProfileBaseModel):
    """Model for creating new Interface Management Profiles."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "InterfaceManagementProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            InterfaceManagementProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class InterfaceManagementProfileUpdateModel(InterfaceManagementProfileBaseModel):
    """Model for updating existing Interface Management Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the interface management profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class InterfaceManagementProfileResponseModel(InterfaceManagementProfileBaseModel):
    """Model for Interface Management Profile responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the interface management profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
