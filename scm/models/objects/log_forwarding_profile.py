"""Log Forwarding Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing log forwarding profile objects and related data.
"""

# scm/models/objects/log_forwarding_profile.py

# Standard library imports
from typing import List, Literal, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field, model_validator


class MatchListItem(BaseModel):
    """Represents a match profile configuration within a log forwarding profile.

    Attributes:
        name (str): Name of the match profile.
        action_desc (Optional[str]): Match profile description.
        log_type (str): Log type for matching (traffic, threat, wildfire, url, data, tunnel, auth, decryption, dns-security).
        filter (Optional[str]): Filter match criteria.
        send_http (Optional[List[str]]): A list of HTTP server profiles.
        send_syslog (Optional[List[str]]): A list of syslog server profiles.
        send_to_panorama (Optional[bool]): Flag to send logs to Panorama.
        quarantine (Optional[bool]): Flag to quarantine matching logs.

    """

    name: str = Field(..., description="Name of the match profile", max_length=63)
    action_desc: Optional[str] = Field(
        None, description="Match profile description", max_length=255
    )
    log_type: Literal[
        "traffic",
        "threat",
        "wildfire",
        "url",
        "data",
        "tunnel",
        "auth",
        "decryption",
        "dns-security",
    ] = Field(..., description="Log type")
    filter: Optional[str] = Field(None, description="Filter match criteria", max_length=65535)
    send_http: Optional[List[str]] = Field(None, description="A list of HTTP server profiles")
    send_syslog: Optional[List[str]] = Field(None, description="A list of syslog server profiles")
    send_to_panorama: Optional[bool] = Field(None, description="Flag to send logs to Panorama")
    quarantine: Optional[bool] = Field(False, description="Flag to quarantine matching logs")

    # Pydantic model configuration to allow for more flexible deserialization
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",  # Ignore extra fields not defined in the model
    )


class LogForwardingProfileBaseModel(BaseModel):
    """Base model for Log Forwarding Profile objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the log forwarding profile.
        description (Optional[str]): Log forwarding profile description.
        match_list (Optional[List[MatchListItem]]): List of match profile configurations.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.
        enhanced_application_logging (Optional[bool]): Flag for enhanced application logging.

    """

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the log forwarding profile",
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        description="Log forwarding profile description",
        max_length=255,
    )

    match_list: Optional[List[MatchListItem]] = Field(
        None,
        description="List of match profile configurations",
    )

    enhanced_application_logging: Optional[bool] = Field(
        None,
        description="Flag for enhanced application logging",
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
        description="The snippet in which the resource is defined",
        examples=["My Snippet", "predefined-snippet"],
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
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
        extra="ignore",  # Ignore extra fields not defined in the model
    )


class LogForwardingProfileCreateModel(LogForwardingProfileBaseModel):
    """Represents the creation of a new Log Forwarding Profile object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a LogForwardingProfileCreateModel object,
    it inherits all fields from the LogForwardingProfileBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.

    """

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "LogForwardingProfileCreateModel":
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


class LogForwardingProfileUpdateModel(LogForwardingProfileBaseModel):
    """Represents the update of an existing Log Forwarding Profile object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a LogForwardingProfileUpdateModel object.

    Attributes:
        id (UUID): The UUID of the log forwarding profile.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the log forwarding profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class LogForwardingProfileResponseModel(LogForwardingProfileBaseModel):
    """Represents the response model for a Log Forwarding Profile object from Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a LogForwardingProfileResponseModel object,
    it inherits all fields from the LogForwardingProfileBaseModel class, and adds its own attribute for the
    id field.

    Attributes:
        id (Optional[UUID]): The UUID of the log forwarding profile. Not required for predefined snippets.

    """

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the log forwarding profile. Not required for predefined snippets.",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    @model_validator(mode="after")
    def validate_id_for_non_predefined(self) -> "LogForwardingProfileResponseModel":
        """Validate that non-predefined profiles have an ID."""
        # Skip validation if snippet is "predefined-snippet"
        if self.snippet == "predefined-snippet":
            return self

        # For normal profiles in folders, ensure ID is present
        if not self.id and self.snippet != "predefined-snippet" and self.folder is not None:
            raise ValueError("ID is required for non-predefined profiles")

        return self
