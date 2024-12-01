# scm/models/security/url_categories.py

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict,
)


# Enums
class URLCategoriesListTypeEnum(str, Enum):
    """Enumeration of allowed types within a list."""

    url_list = "URL List"
    category_match = "Category Match"


class URLCategoriesBaseModel(BaseModel):
    """URL Category base model."""

    # Required Fields
    name: str = Field(
        ...,
        description="URL Category Name",
    )
    list: List[str] = Field(
        ...,
        description="Lists of URL categories",
    )

    # Optional Fields
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    type: Optional[URLCategoriesListTypeEnum] = Field(
        default=URLCategoriesListTypeEnum.url_list,
        description="Type of the URL category",
    )

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    # Configuration containers
    folder: Optional[str] = Field(
        None,
        description="Folder",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )


class URLCategoriesCreateModel(URLCategoriesBaseModel):
    """Model for creating a new DNS Security Profile."""

    @model_validator(mode="after")
    def validate_container(self) -> "URLCategoriesCreateModel":
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided_containers = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided_containers) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class URLCategoriesUpdateModel(URLCategoriesBaseModel):
    """Model for updating an existing DNS Security Profile."""

    id: Optional[UUID] = Field(
        ...,
        description="UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class URLCategoriesResponseModel(URLCategoriesBaseModel):
    """Model for DNS Security Profile API responses."""

    id: UUID = Field(
        ...,
        description="UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
