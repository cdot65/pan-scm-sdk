"""Auth Settings models for Strata Cloud Manager SDK.

Contains Pydantic models for representing mobile agent authentication settings and related data.
"""

# scm/models/mobile_agent/auth_settings.py

# Standard library imports
from enum import Enum
from typing import Optional

# External libraries
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OperatingSystem(str, Enum):
    """Available operating systems for GlobalProtect authentication settings."""

    ANY = "Any"
    ANDROID = "Android"
    BROWSER = "Browser"
    CHROME = "Chrome"
    IOT = "IoT"
    LINUX = "Linux"
    MAC = "Mac"
    SATELLITE = "Satellite"
    WINDOWS = "Windows"
    WINDOWS_UWP = "WindowsUWP"
    IOS = "iOS"


class AuthSettingsBaseModel(BaseModel):
    """Base model for GlobalProtect Authentication Settings containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the authentication settings.
        authentication_profile (str): The authentication profile to use.
        os (OperatingSystem): The operating system this authentication setting applies to.
        user_credential_or_client_cert_required (bool): Whether user credentials or client certificate is required.
        folder (Optional[str]): The folder in which the resource is defined (must be 'Mobile Users').

    Error:
        ValueError: Raised when validation fails for any field or when folder is not 'Mobile Users'.

    """

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        description="The name of the authentication settings",
        max_length=63,
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )
    authentication_profile: str = Field(
        ...,
        description="The authentication profile to use",
    )
    os: OperatingSystem = Field(
        default=OperatingSystem.ANY,
        description="The operating system this authentication setting applies to",
    )
    user_credential_or_client_cert_required: Optional[bool] = Field(
        None,
        description="Whether user credentials or client certificate is required",
    )

    # Container fields
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["Mobile Users"],
    )

    @field_validator("folder")
    def validate_folder(cls, v):  # noqa
        """Validate that folder is 'Mobile Users' if provided."""
        if v is not None and v != "Mobile Users":
            raise ValueError(
                "Folder must be 'Mobile Users' for GlobalProtect Authentication Settings"
            )
        return v


class AuthSettingsCreateModel(AuthSettingsBaseModel):
    """Represents the creation of a new GlobalProtect Authentication Settings.

    This class defines the structure and validation rules for creating authentication settings,
    ensuring that folder is set to 'Mobile Users'.

    Error:
        ValueError: Raised when folder is not provided or not set to 'Mobile Users'.

    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "AuthSettingsCreateModel":
        """Validate that folder is provided and set to 'Mobile Users'."""
        if not self.folder:
            raise ValueError("Folder is required for GlobalProtect Authentication Settings")
        return self


class AuthSettingsUpdateModel(BaseModel):
    """Represents the update of an existing GlobalProtect Authentication Settings.

    This class defines the structure and validation rules for updating authentication settings.
    Only fields that need to be updated can be provided.

    Attributes:
        name (Optional[str]): The name of the authentication settings.
        authentication_profile (Optional[str]): The authentication profile to use.
        os (Optional[OperatingSystem]): The operating system this authentication setting applies to.
        user_credential_or_client_cert_required (Optional[bool]): Whether user credentials or client certificate is required.
        folder (Optional[str]): The folder in which the resource is defined (must be 'Mobile Users').

    """

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Optional fields for update
    name: Optional[str] = Field(
        None,
        description="The name of the authentication settings",
        max_length=63,
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )
    authentication_profile: Optional[str] = Field(
        None,
        description="The authentication profile to use",
    )
    os: Optional[OperatingSystem] = Field(
        None,
        description="The operating system this authentication setting applies to",
    )
    user_credential_or_client_cert_required: Optional[bool] = Field(
        None,
        description="Whether user credentials or client certificate is required",
    )
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["Mobile Users"],
    )

    @field_validator("folder")
    def validate_folder(cls, v):  # noqa
        """Validate that folder is 'Mobile Users' if provided."""
        if v is not None and v != "Mobile Users":
            raise ValueError(
                "Folder must be 'Mobile Users' for GlobalProtect Authentication Settings"
            )
        return v


class AuthSettingsResponseModel(AuthSettingsBaseModel):
    """Represents the response model for GlobalProtect Authentication Settings.

    This class defines the structure for authentication settings returned by the API.
    """


class MovePosition(str, Enum):
    """Available positions for moving authentication settings."""

    BEFORE = "before"
    AFTER = "after"
    TOP = "top"
    BOTTOM = "bottom"


class AuthSettingsMoveModel(BaseModel):
    """Represents the model for moving GlobalProtect Authentication Settings in the configuration.

    This class defines the structure and validation rules for moving authentication settings
    to a different position within the configuration.

    Attributes:
        name (str): The name of the authentication settings to move.
        where (MovePosition): The position to move to (before, after, top, bottom).
        destination (Optional[str]): The name of the destination authentication settings
                                     (required for before/after).

    Error:
        ValueError: Raised when destination is not provided for 'before' or 'after' positions.

    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
    )

    name: str = Field(
        ...,
        description="The name of the authentication settings to move",
    )
    where: MovePosition = Field(
        ...,
        description="The position to move to",
    )
    destination: Optional[str] = Field(
        None,
        description="The name of the destination authentication settings (required for before/after)",
    )

    @model_validator(mode="after")
    def validate_destination_required(self) -> "AuthSettingsMoveModel":
        """Validate that destination is provided when required."""
        if self.where in [MovePosition.BEFORE, MovePosition.AFTER] and not self.destination:
            raise ValueError("Destination is required when where is 'before' or 'after'")
        if self.where in [MovePosition.TOP, MovePosition.BOTTOM] and self.destination:
            raise ValueError("Destination should not be provided when where is 'top' or 'bottom'")
        return self
