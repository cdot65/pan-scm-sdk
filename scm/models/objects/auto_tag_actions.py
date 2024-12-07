# scm/models/objects/auto_tag_actions.py

# Standard library imports
from typing import Optional, List
from uuid import UUID

# External libraries
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict,
    constr,
)

TagString = constr(max_length=127)


class TaggingModel(BaseModel):
    """
    Base model for Address objects containing fields common to all CRUD operations.

    Attributes:
        target (str): Source or Destination Address, User, X-Forwarded-For Address.
        action (str): Add or Remove tag option.
        timeout (Optional[int]): Timeout value.
        tags (Optional[TagString]): Tags for address object.
    """

    # Required fields
    target: str = Field(
        ...,
        description="Source or Destination Address, User, X-Forwarded-For Address",
    )
    action: str = Field(
        ...,
        description="Add or Remove tag option",
        pattern=r"^(add-tag|remove-tag)$",
    )
    timeout: Optional[int] = Field(
        None,
        description="Timeout value",
    )
    tags: Optional[List[TagString]] = Field(
        None,
        description="Tags for address object",
    )


class ActionTypeModel(BaseModel):
    tagging: TaggingModel = Field(
        ...,
        description="Tagging configuration",
    )


class ActionModel(BaseModel):
    name: str = Field(
        ...,
        description="Name of the action",
        max_length=63,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )
    type: ActionTypeModel = Field(
        ...,
        description="Type configuration for the action",
    )


class AutoTagActionBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Alphanumeric string [ 0-9a-zA-Z._-]",
        max_length=63,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
        max_length=1023,
    )
    filter: str = Field(
        ...,
        description="Tag based filter defining group membership",
        max_length=2047,
    )
    send_to_panorama: Optional[bool] = Field(
        None,
        description="Send to Panorama",
    )
    quarantine: Optional[bool] = Field(
        None,
        description="Quarantine option",
    )
    actions: Optional[List[ActionModel]] = Field(
        None,
        description="List of actions",
    )
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
    )


class AutoTagActionCreateModel(AutoTagActionBaseModel):
    @model_validator(mode="after")
    def validate_container_type(self) -> "AutoTagActionCreateModel":
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


class AutoTagActionUpdateModel(AutoTagActionBaseModel):
    id: Optional[UUID] = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class AutoTagActionResponseModel(AutoTagActionBaseModel):
    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    log_type: str = Field(
        ...,
        description="Log type of the resource",
    )
