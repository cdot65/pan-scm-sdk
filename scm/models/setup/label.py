"""Models for interacting with Labels in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Label resources in the Strata Cloud Manager.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LabelBaseModel(BaseModel):
    """Base model for Label resources per OpenAPI spec."""

    name: str = Field(
        ...,  # required
        description="The name of the label",
        max_length=63,
    )
    description: Optional[str] = Field(
        default=None,
        description="An optional description of the label",
    )


class LabelCreateModel(LabelBaseModel):
    """Model for creating new Label resources."""

    pass


class LabelUpdateModel(LabelBaseModel):
    """Model for updating existing Label resources."""

    id: UUID = Field(
        ...,  # required for update
        description="The unique identifier of the label",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class LabelResponseModel(LabelBaseModel):
    """Model for Label responses from the API."""

    id: UUID = Field(
        ...,  # required, readOnly
        description="The unique identifier of the label",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
