"""HIP Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing HIP profile objects and related data.
"""

# scm/models/objects/hip_profile.py

# Standard library imports
from typing import Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field, model_validator


class HIPProfileBaseModel(BaseModel):
    """Base model for HIP Profile objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the HIP profile.
        description (Optional[str]): The description of the HIP profile.
        match (str): The match criteria for the HIP profile.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    """

    # Required fields
    name: str = Field(
        ...,
        max_length=31,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        description="The name of the HIP profile",
    )
    match: str = Field(
        ...,
        max_length=2048,
        description="The match criteria for the HIP profile",
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="The description of the HIP profile",
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


class HIPProfileCreateModel(HIPProfileBaseModel):
    """Represents the creation of a new HIP Profile object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a HIPProfileCreateModel object,
    it inherits all fields from the HIPProfileBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.

    """

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "HIPProfileCreateModel":
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


class HIPProfileUpdateModel(HIPProfileBaseModel):
    """Represents the update of an existing HIP Profile object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a HIPProfileUpdateModel object.
    """

    id: Optional[UUID] = Field(
        ...,  # This makes it optional
        description="The UUID of the HIP profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class HIPProfileResponseModel(HIPProfileBaseModel):
    """Represents the response model for a HIP Profile object from Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a HIPProfileResponseModel object,
    it inherits all fields from the HIPProfileBaseModel class, and adds its own attribute for the
    id field.

    Attributes:
        id (UUID): The UUID of the HIP profile.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the HIP profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
