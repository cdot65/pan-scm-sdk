"""Internal DNS Servers models for Strata Cloud Manager SDK.

Contains Pydantic models for representing internal DNS server objects and related data.
"""

# scm/models/deployment/internal_dns_servers.py

from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    IPvAnyAddress,
    field_serializer,
    field_validator,
    model_validator,
)


class InternalDnsServersBaseModel(BaseModel):
    """Base model for Internal DNS Servers containing fields common to all operations.

    Attributes:
        name (str): The name of the internal DNS server resource.
        domain_name (List[str]): The DNS domain name(s).
        primary (str): The IP address of the primary DNS server.
        secondary (Optional[str]): The IP address of the secondary DNS server.

    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the internal DNS server resource",
        pattern=r"^[0-9a-zA-Z._\- ]+$",
        max_length=63,
    )

    domain_name: List[str] = Field(
        ...,
        description="The DNS domain name(s)",
        min_length=1,  # Ensure the list is not empty
    )

    primary: IPvAnyAddress = Field(
        ...,
        description="The IP address of the primary DNS server",
    )

    secondary: Optional[IPvAnyAddress] = Field(
        None,
        description="The IP address of the secondary DNS server",
    )

    @field_serializer("primary", "secondary")
    def serialize_ip_address(self, value, _info):
        """Convert IP address objects to strings for JSON serialization."""
        if value is None:
            return None
        return str(value)

    @field_validator("domain_name", mode="before")
    @classmethod
    def validate_domain_name(cls, v):
        """Ensure domain_name is a list."""
        if v is None:
            return []

        if isinstance(v, str):
            return [v]

        if not isinstance(v, list):
            raise ValueError("domain_name must be a list of strings")

        return v

    @field_validator("domain_name", mode="after")
    @classmethod
    def validate_domain_name_not_empty(cls, v):
        """Ensure domain_name is not empty."""
        if not v:
            raise ValueError("domain_name must not be empty")
        return v


class InternalDnsServersCreateModel(InternalDnsServersBaseModel):
    """Model for creating new Internal DNS Servers."""

    @model_validator(mode="after")
    def validate_create_model(self) -> "InternalDnsServersCreateModel":
        """Validate the create model.

        1. Ensures domain_name is not empty
        """
        if not self.domain_name:
            raise ValueError("domain_name must not be empty")

        return self


class InternalDnsServersUpdateModel(InternalDnsServersBaseModel):
    """Model for updating existing Internal DNS Servers.

    All fields are optional to support partial updates, except for id which is required.
    """

    id: UUID = Field(
        ...,
        description="The UUID of the internal DNS server",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    name: Optional[str] = Field(
        None,
        description="The name of the internal DNS server resource",
        pattern=r"^[0-9a-zA-Z._\- ]+$",
        max_length=63,
    )

    domain_name: Optional[List[str]] = Field(
        None,
        description="The DNS domain name(s)",
    )

    primary: Optional[IPvAnyAddress] = Field(
        None,
        description="The IP address of the primary DNS server",
    )

    secondary: Optional[IPvAnyAddress] = Field(
        None,
        description="The IP address of the secondary DNS server",
    )

    @model_validator(mode="after")
    def validate_update_model(self) -> "InternalDnsServersUpdateModel":
        """Validate the update model.

        1. Ensures at least one field other than id is set for update
        2. Ensures domain_name is not empty if provided
        """
        # Ensure at least one field other than id is set for update
        field_count = sum(
            1 for f in [self.name, self.domain_name, self.primary, self.secondary] if f is not None
        )

        if field_count == 0:
            raise ValueError("At least one field must be specified for update")

        # Ensure domain_name is not empty if provided
        if self.domain_name is not None and not self.domain_name:
            raise ValueError("domain_name must not be empty if provided")

        return self


class InternalDnsServersResponseModel(InternalDnsServersBaseModel):
    """Model for Internal DNS Servers API responses.

    Includes id as a required field.
    """

    id: UUID = Field(
        ...,
        description="The UUID of the internal DNS server",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    @model_validator(mode="after")
    def validate_response_model(self) -> "InternalDnsServersResponseModel":
        """Validate the response model.

        1. Ensures domain_name is not empty
        """
        if not self.domain_name:
            raise ValueError("domain_name must not be empty in response")

        return self
