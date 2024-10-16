# scm/models/objects/application_group.py

import uuid
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator, ConfigDict


class ApplicationGroupRequestModel(BaseModel):
    """
    Represents an Application Group for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an Application Group,
    including required fields, optional fields, address types, and container types.

    Attributes:
        name (str): The name of the application group.
        members (List[str]): List of application / group / filter names.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    Error:
        ValueError: Raised when address type or container type validation fails.
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
        description="The name of the application group",
    )

    members: List[str] = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="List of application / group / filter names",
        examples=[["office365-consumer-access", "office365-enterprise-access"]],
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

    @model_validator(mode="after")
    def validate_container_type(self) -> "ApplicationGroupRequestModel":
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class ApplicationGroupResponseModel(BaseModel):
    """
    Represents an ApplicationGroup response for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an Application Group,
    including required fields, optional fields, address types, and container types.

    Attributes:
        id (UUID): The UUID of the application group.
        name (str): The name of the application group.
        members (List[str]): List of application / group / filter names.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    Error:
        ValueError: Raised when address type or container type validation fails.

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
        description="The name of the application group",
    )

    members: List[str] = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="List of application / group / filter names",
        examples=[["office365-consumer-access", "office365-enterprise-access"]],
    )

    # Optional fields
    id: Optional[str] = Field(
        None,
        description="The UUID of the application group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
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

    # Custom Validators
    @model_validator(mode="before")
    def validate_uuid(cls, values):
        if "id" in values and values["id"] is not None:
            try:
                uuid.UUID(values["id"])
            except ValueError:
                raise ValueError("Invalid UUID format for 'id'")
        return values
