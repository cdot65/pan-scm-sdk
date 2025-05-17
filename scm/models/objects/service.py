"""Service models for Strata Cloud Manager SDK.

Contains Pydantic models for representing service objects and related data.
"""

# scm/models/objects/service.py

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Override(BaseModel):
    """Settings for protocol override configurations."""

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
    """TCP protocol configuration."""

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
    """UDP protocol configuration."""

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
    """Protocol configuration with TCP/UDP validation."""

    tcp: Optional[TCPProtocol] = None
    udp: Optional[UDPProtocol] = None

    @model_validator(mode="after")
    def validate_protocol(self) -> "Protocol":
        """Ensure exactly one protocol field (tcp or udp) is set.

        Returns:
            Protocol: The validated protocol instance.

        Raises:
            ValueError: If zero or more than one protocol field is set.

        """
        protocol_fields = ["tcp", "udp"]
        provided = [field for field in protocol_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'tcp' or 'udp' must be provided in 'protocol'.")
        return self


class ServiceBaseModel(BaseModel):
    """Base model for Service objects containing fields common to all CRUD operations.

    This model serves as the foundation for create, update, and response models,
    containing all shared fields and validation logic.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        max_length=63,
        description="The name of the service.",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
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
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="Description about the service.",
    )
    tag: Optional[List[str]] = Field(
        None,
        description="The tag(s) associated with the service.",
    )
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder where the service is defined.",
        examples=["Texas"],
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet where the service is defined.",
        examples=["predefined-snippet"],
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device where the service is defined.",
        examples=["my-device"],
    )


class ServiceCreateModel(ServiceBaseModel):
    """Model for creating a new Service.

    Inherits from ServiceBaseModel and adds container type validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "ServiceCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            ServiceCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class ServiceUpdateModel(ServiceBaseModel):
    """Model for updating an existing Service.

    All fields are optional to allow partial updates.
    """

    id: Optional[UUID] = Field(
        ...,  # This makes it optional
        description="The UUID of the address object",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ServiceResponseModel(ServiceBaseModel):
    """Model for Service responses.

    Includes all base fields plus the optional id field.
    """

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the service.",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
