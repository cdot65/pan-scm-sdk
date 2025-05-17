"""Models for interacting with Variables in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Variable resources in the Strata Cloud Manager.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class VariableBaseModel(BaseModel):
    """Base model for Variable resources per OpenAPI spec."""

    name: str = Field(
        ...,  # required
        description="The name of the variable",
        max_length=63,
    )
    type: str = Field(
        ...,  # required
        description="The variable type",
        # Enum enforced in validator below
    )
    value: str = Field(
        ...,  # required
        description="The value of the variable",
    )
    description: Optional[str] = Field(
        default=None,
        description="An optional description of the variable",
    )

    # Container fields for scoping (folder, snippet, device)
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_. ]+$",
        max_length=64,
        description="The folder in which the variable is defined",
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_. ]+$",
        max_length=64,
        description="The snippet in which the variable is defined",
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_. ]+$",
        max_length=64,
        description="The device in which the variable is defined",
    )

    @field_validator("type")
    def validate_type_enum(cls, v):
        """Validate that the type is one of the allowed values."""
        allowed = [
            "percent",
            "count",
            "ip-netmask",
            "zone",
            "ip-range",
            "ip-wildcard",
            "device-priority",
            "device-id",
            "egress-max",
            "as-number",
            "fqdn",
            "port",
            "link-tag",
            "group-id",
            "rate",
            "router-id",
            "qos-profile",
            "timer",
        ]
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}, got {v}")
        return v

    @classmethod
    def validate_container_type(cls, values):
        """Validate that exactly one of 'folder', 'snippet', or 'device' is provided."""
        container_fields = [values.get("folder"), values.get("snippet"), values.get("device")]
        set_count = sum(1 for v in container_fields if v is not None)
        if set_count != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return values


class VariableCreateModel(VariableBaseModel):
    """Model for creating new Variable resources."""

    # Validate container type after model creation
    @classmethod
    def model_validate(cls, value):
        """Validate and post-process model creation, ensuring container type is valid.

        Args:
            value (Any): The value to validate and convert.

        Returns:
            VariableCreateModel: The validated model instance.

        """
        model = super().model_validate(value)
        cls.validate_container_type(model.__dict__)
        return model


class VariableUpdateModel(VariableBaseModel):
    """Model for updating existing Variable resources."""

    id: UUID = Field(
        ...,  # required for update
        description="The unique identifier of the variable",
    )

    # Validate container type after model creation
    @classmethod
    def model_validate(cls, value):
        """Validate and post-process model update, ensuring container type is valid.

        Args:
            value (Any): The value to validate and convert.

        Returns:
            VariableUpdateModel: The validated model instance.

        """
        model = super().model_validate(value)
        cls.validate_container_type(model.__dict__)
        return model


class VariableResponseModel(VariableBaseModel):
    """Model for Variable responses from the API."""

    id: UUID = Field(
        ...,  # required, readOnly
        description="The unique identifier of the variable",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    overridden: Optional[bool] = Field(
        default=None,
        description="Is the variable overridden?",
    )

    # Additional fields often present in API responses but not in the OpenAPI spec
    labels: Optional[List[str]] = Field(
        default=None,
        description="Labels assigned to the variable",
    )
    parent: Optional[str] = Field(
        default=None,
        description="The parent folder or container",
    )
    snippets: Optional[List[str]] = Field(
        default=None,
        description="Snippets associated with the variable",
    )
    model: Optional[str] = Field(
        default=None,
        description="Device model information",
    )
    serial_number: Optional[str] = Field(
        default=None,
        description="Device serial number",
    )
    device_only: Optional[bool] = Field(
        default=None,
        description="Whether the variable is only applicable to devices",
    )
