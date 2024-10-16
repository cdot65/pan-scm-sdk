# scm/models/service.py
import uuid
from typing import Optional, List

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
)


class Override(BaseModel):
    timeout: Optional[int] = Field(
        None,
        description="Timeout in seconds.",
        examples=[10],
    )
    halfclose_timeout: Optional[int] = Field(
        None,
        description="Half-close timeout in seconds.",
        examples=[10],
    )
    timewait_timeout: Optional[int] = Field(
        None,
        description="Time-wait timeout in seconds.",
        examples=[10],
    )


class TCPProtocol(BaseModel):
    port: str = Field(
        ...,
        description="TCP port(s) associated with the service.",
        examples=["80", "80,8080"],
    )
    override: Optional[Override] = Field(
        None,
        description="Override settings for the TCP protocol.",
    )


class UDPProtocol(BaseModel):
    port: str = Field(
        ...,
        description="UDP port(s) associated with the service.",
        examples=["53", "67,68"],
    )
    override: Optional[Override] = Field(
        None,
        description="Override settings for the UDP protocol.",
    )


class Protocol(BaseModel):
    tcp: Optional[TCPProtocol] = None
    udp: Optional[UDPProtocol] = None

    @model_validator(mode="after")
    def validate_protocol(self) -> "Protocol":
        protocol_fields = ["tcp", "udp"]
        provided = [
            field for field in protocol_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'."
            )
        return self


class ServiceRequestModel(BaseModel):
    """
    Represents a Service creation for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for creating a Service,
    including required fields, optional fields, and various attributes defining
    the application's characteristics and behaviors.

    Attributes:
        name (str): The name of the service.
        protocol (str): Detailed information about the service.
        description (Optional[str]): Description about the service.
        protocol (str): The protocol (tcp or udp) associated with the service.
        tag (Optional[str]): The tag(s) associated with the service.
        folder (Optional[str]): The folder where the service configuration is stored.
        snippet (Optional[str]): The configuration snippet for the service.
    """

    # Model configuration
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the service.",
        examples=["service-http"],
    )
    protocol: Protocol = Field(
        ...,
        description="The protocol (tcp or udp) and associated ports.",
        examples=[
            {"tcp": {"port": "80"}},
            {"udp": {"port": "53,67"}},
        ],
    )
    # Optional fields
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="Description about the service.",
    )
    tag: Optional[List[str]] = Field(
        None,
        description="The tag(s) associated with the service.",
    )

    # Container Types
    folder: Optional[str] = Field(
        None,
        max_length=64,
        description="The folder where the service is defined.",
    )
    snippet: Optional[str] = Field(
        None,
        max_length=64,
        description="The snippet where the service is defined.",
    )
    device: Optional[str] = Field(
        None,
        max_length=64,
        description="The device where the service is defined.",
    )

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "ServiceRequestModel":
        container_fields = ["folder", "snippet", "device"]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class ServiceResponseModel(BaseModel):
    """
    Represents a Service response for Palo Alto Networks' Strata Cloud Manager.
    """

    # Model configuration
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Optional 'id' field
    id: Optional[str] = Field(
        None,
        description="The UUID of the service.",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the service.",
        examples=["service-http"],
    )
    protocol: Protocol = Field(
        ...,
        description="The protocol (tcp or udp) and associated ports.",
        examples=[
            {"tcp": {"port": "80"}},
            {"udp": {"port": "53,67"}},
        ],
    )
    folder: str = Field(
        ...,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder where the service is defined.",
        examples=["Shared"],
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="Description about the service.",
        examples=["HTTP service for web traffic."],
    )
    tag: Optional[List[str]] = Field(
        None,
        description="The tag(s) associated with the service.",
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet where the service is defined.",
        examples=["predefined-snippet"],
    )

    # Custom Validators
    @model_validator(mode="before")
    def validate_uuid(cls, values):
        if "id" in values and values["id"] is not None:
            try:
                uuid.UUID(values["id"])
            except (ValueError, TypeError):
                raise ValueError("Invalid UUID format for 'id'")
        return values
