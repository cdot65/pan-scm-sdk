"""Application Group models for Strata Cloud Manager SDK.

Contains Pydantic models for representing application group objects and related data.
"""

# scm/models/objects/application_group.py

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApplicationGroupBaseModel(BaseModel):
    """Base model for Application Group objects containing fields common to all CRUD operations.

    This model serves as the foundation for create, update, and response models,
    containing all shared fields and validation logic.

    Attributes:
        name (str): The name of the application group.
        members (List[str]): List of application / group / filter names.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        max_length=63,
        description="The name of the application group",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )

    members: List[str] = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="List of application / group / filter names",
        examples=[["office365-consumer-access", "office365-enterprise-access"]],
    )

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


class ApplicationGroupCreateModel(ApplicationGroupBaseModel):
    """Model for creating a new Application Group.

    Inherits from ApplicationGroupBaseModel and adds container type validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "ApplicationGroupCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            ApplicationGroupCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class ApplicationGroupUpdateModel(ApplicationGroupBaseModel):
    """Model for updating an existing Application Group.

    All fields are optional to allow partial updates.
    """

    id: Optional[UUID] = Field(
        ...,
        description="The UUID of the application group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ApplicationGroupResponseModel(ApplicationGroupBaseModel):
    """Model for Application Group responses.

    Includes all base fields plus the id field.
    """

    id: UUID = Field(
        ...,
        description="The UUID of the application group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
