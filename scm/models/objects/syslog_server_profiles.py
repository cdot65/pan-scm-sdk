"""Syslog Server Profiles models for Strata Cloud Manager SDK.

Contains Pydantic models for representing syslog server profile objects and related data.
"""

# scm/models/objects/syslog_server_profiles.py

# Standard library imports
from typing import List, Literal, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field, model_validator


class EscapingModel(BaseModel):
    """Model for character escaping configuration in syslog server profiles.

    Attributes:
        escape_character (Optional[str]): Escape sequence delimiter.
        escaped_characters (Optional[str]): A list of all the characters to be escaped (without spaces).

    """

    escape_character: Optional[str] = Field(
        None, max_length=1, description="Escape sequence delimiter"
    )
    escaped_characters: Optional[str] = Field(
        None,
        max_length=255,
        description="A list of all the characters to be escaped (without spaces)",
    )


class FormatModel(BaseModel):
    """Model for log format configuration in syslog server profiles.

    Attributes:
        escaping (Optional[EscapingModel]): Character escaping configuration.
        traffic (Optional[str]): Format for traffic logs.
        threat (Optional[str]): Format for threat logs.
        wildfire (Optional[str]): Format for wildfire logs.
        url (Optional[str]): Format for URL logs.
        data (Optional[str]): Format for data logs.
        gtp (Optional[str]): Format for GTP logs.
        sctp (Optional[str]): Format for SCTP logs.
        tunnel (Optional[str]): Format for tunnel logs.
        auth (Optional[str]): Format for authentication logs.
        userid (Optional[str]): Format for user ID logs.
        iptag (Optional[str]): Format for IP tag logs.
        decryption (Optional[str]): Format for decryption logs.
        config (Optional[str]): Format for configuration logs.
        system (Optional[str]): Format for system logs.
        globalprotect (Optional[str]): Format for GlobalProtect logs.
        hip_match (Optional[str]): Format for HIP match logs.
        correlation (Optional[str]): Format for correlation logs.

    """

    escaping: Optional[EscapingModel] = Field(None, description="Character escaping configuration")
    traffic: Optional[str] = Field(None, description="Format for traffic logs")
    threat: Optional[str] = Field(None, description="Format for threat logs")
    wildfire: Optional[str] = Field(None, description="Format for wildfire logs")
    url: Optional[str] = Field(None, description="Format for URL logs")
    data: Optional[str] = Field(None, description="Format for data logs")
    gtp: Optional[str] = Field(None, description="Format for GTP logs")
    sctp: Optional[str] = Field(None, description="Format for SCTP logs")
    tunnel: Optional[str] = Field(None, description="Format for tunnel logs")
    auth: Optional[str] = Field(None, description="Format for authentication logs")
    userid: Optional[str] = Field(None, description="Format for user ID logs")
    iptag: Optional[str] = Field(None, description="Format for IP tag logs")
    decryption: Optional[str] = Field(None, description="Format for decryption logs")
    config: Optional[str] = Field(None, description="Format for configuration logs")
    system: Optional[str] = Field(None, description="Format for system logs")
    globalprotect: Optional[str] = Field(None, description="Format for GlobalProtect logs")
    hip_match: Optional[str] = Field(None, description="Format for HIP match logs")
    correlation: Optional[str] = Field(None, description="Format for correlation logs")


class SyslogServerModel(BaseModel):
    """Model for syslog server configuration in a syslog server profile.

    Attributes:
        name (str): Syslog server name.
        server (str): Syslog server address.
        transport (Literal["UDP", "TCP"]): Transport protocol for the syslog server.
        port (int): Syslog server port.
        format (Literal["BSD", "IETF"]): Syslog format.
        facility (Literal["LOG_USER", "LOG_LOCAL0", "LOG_LOCAL1", "LOG_LOCAL2", "LOG_LOCAL3", "LOG_LOCAL4", "LOG_LOCAL5", "LOG_LOCAL6", "LOG_LOCAL7"]):
            Syslog facility.

    """

    name: str = Field(..., description="Syslog server name")
    server: str = Field(..., description="Syslog server address")
    transport: Literal["UDP", "TCP"] = Field(..., description="Transport protocol")
    port: int = Field(..., description="Syslog server port", ge=1, le=65535)
    format: Literal["BSD", "IETF"] = Field(..., description="Syslog format")
    facility: Literal[
        "LOG_USER",
        "LOG_LOCAL0",
        "LOG_LOCAL1",
        "LOG_LOCAL2",
        "LOG_LOCAL3",
        "LOG_LOCAL4",
        "LOG_LOCAL5",
        "LOG_LOCAL6",
        "LOG_LOCAL7",
    ] = Field(..., description="Syslog facility")


class SyslogServerProfileBaseModel(BaseModel):
    """Base model for Syslog Server Profile objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the syslog server profile.
        server (List[SyslogServerModel]): List of server configurations.
        format (Optional[FormatModel]): Format settings for different log types.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    """

    # Required fields
    name: str = Field(..., description="The name of the syslog server profile", max_length=31)

    # Server configurations - can be a dict or list in API
    server: List[SyslogServerModel] = Field(..., description="Syslog server configurations")

    # Optional fields
    format: Optional[FormatModel] = Field(
        None, description="Format settings for different log types"
    )

    # Container Types
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["Shared"],
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
        examples=["My Snippet"],
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
        examples=["My Device"],
    )

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class SyslogServerProfileCreateModel(SyslogServerProfileBaseModel):
    """Represents the creation of a new Syslog Server Profile object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a SyslogServerProfileCreateModel object,
    it inherits all fields from the SyslogServerProfileBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.

    """

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "SyslogServerProfileCreateModel":
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


class SyslogServerProfileUpdateModel(SyslogServerProfileBaseModel):
    """Represents the update of an existing Syslog Server Profile object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a SyslogServerProfileUpdateModel object.

    Attributes:
        id (UUID): The UUID of the syslog server profile.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the syslog server profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class SyslogServerProfileResponseModel(SyslogServerProfileBaseModel):
    """Represents a Syslog Server Profile object response from Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a SyslogServerProfileResponseModel object,
    it inherits all fields from the SyslogServerProfileBaseModel class, and adds an id field.

    Attributes:
        id (UUID): The UUID of the syslog server profile.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the syslog server profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
