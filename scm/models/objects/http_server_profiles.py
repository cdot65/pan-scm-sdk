"""HTTP Server Profiles models for Strata Cloud Manager SDK.

Contains Pydantic models for representing HTTP server profile objects and related data.
"""

# scm/models/objects/http_server_profiles.py

# Standard library imports
from typing import Dict, List, Literal, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field, model_validator


# Server model for HTTP server profile
class ServerModel(BaseModel):
    """Represents a server configuration within an HTTP server profile.

    Attributes:
        name (str): HTTP server name.
        address (str): HTTP server address.
        protocol (str): HTTP server protocol (HTTP or HTTPS).
        port (int): HTTP server port.
        tls_version (Optional[str]): HTTP server TLS version.
        certificate_profile (Optional[str]): HTTP server certificate profile.
        http_method (Optional[str]): HTTP operation to perform.
        username (Optional[str]): Username for HTTP server authentication.
        password (Optional[str]): Password for HTTP server authentication.

    """

    name: str = Field(..., description="HTTP server name")
    address: str = Field(..., description="HTTP server address")
    protocol: Literal["HTTP", "HTTPS"] = Field(..., description="HTTP server protocol")
    port: int = Field(..., description="HTTP server port")
    tls_version: Optional[Literal["1.0", "1.1", "1.2", "1.3"]] = Field(
        None, description="HTTP server TLS version"
    )
    certificate_profile: Optional[str] = Field(None, description="HTTP server certificate profile")
    http_method: Optional[Literal["GET", "POST", "PUT", "DELETE"]] = Field(
        None, description="HTTP operation to perform"
    )
    username: Optional[str] = Field(None, description="Username for HTTP server authentication")
    password: Optional[str] = Field(None, description="Password for HTTP server authentication")


# PayloadFormat model for HTTP server profile
class PayloadFormatModel(BaseModel):
    """Represents the payload format configuration for a specific log type.

    Attributes:
        name (Optional[str]): The name of the payload format. Default is "Default".
        url_format (Optional[str]): The URL path of the HTTP server.
        headers (Optional[List[Dict[str, str]]]): List of HTTP headers to include in the request.
        params (Optional[List[Dict[str, str]]]): List of HTTP parameters to include in the request.
        payload (Optional[str]): The log payload format. Contains log field values.

    """

    name: Optional[str] = Field("Default", description="The name of the payload format")
    url_format: Optional[str] = Field(None, description="The URL path of the HTTP server")
    headers: Optional[List[Dict[str, str]]] = Field(
        None, description="List of HTTP headers to include in the request"
    )
    params: Optional[List[Dict[str, str]]] = Field(
        None, description="List of HTTP parameters to include in the request"
    )
    payload: Optional[str] = Field(
        None, description="The log payload format containing log field values"
    )


class HTTPServerProfileBaseModel(BaseModel):
    """Base model for HTTP Server Profile objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the HTTP server profile.
        server (List[ServerModel]): List of server configurations.
        tag_registration (Optional[bool]): Whether to register tags on match.
        format (Optional[Dict]): Format settings for different log types.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.
        description (Optional[str]): A description of the HTTP server profile.

    """

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the HTTP server profile",
    )

    # Server configurations
    server: List[ServerModel] = Field(
        ...,
        description="List of server configurations",
    )

    # Optional fields
    tag_registration: Optional[bool] = Field(
        None,
        description="Register tags on match",
    )

    description: Optional[str] = Field(
        None,
        description="Description of the HTTP server profile",
    )

    # Format settings for different log types
    format: Optional[Dict[str, PayloadFormatModel]] = Field(
        None,
        description="Format settings for different log types (config, system, traffic, threat, wildfire, url, data, gtp, sctp, tunnel, auth, userid, iptag, decryption, globalprotect, hip_match, correlation)",
    )

    # Container Types
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["Prisma Access"],
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


class HTTPServerProfileCreateModel(HTTPServerProfileBaseModel):
    """Represents the creation of a new HTTP Server Profile object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an HTTPServerProfileCreateModel object,
    it inherits all fields from the HTTPServerProfileBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.

    """

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "HTTPServerProfileCreateModel":
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


class HTTPServerProfileUpdateModel(HTTPServerProfileBaseModel):
    """Represents the update of an existing HTTP Server Profile object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an HTTPServerProfileUpdateModel object.

    Attributes:
        id (UUID): The UUID of the HTTP server profile.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the HTTP server profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class HTTPServerProfileResponseModel(HTTPServerProfileBaseModel):
    """Represents the response model for a HTTP Server Profile object from Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an HTTPServerProfileResponseModel object,
    it inherits all fields from the HTTPServerProfileBaseModel class, and adds its own attribute for the
    id field.

    Attributes:
        id (UUID): The UUID of the HTTP server profile.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the HTTP server profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
