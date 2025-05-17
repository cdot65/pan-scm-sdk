"""Application models for Strata Cloud Manager SDK.

Contains Pydantic models for representing application objects and related data.
"""

# scm/models/objects/application.py

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApplicationBaseModel(BaseModel):
    """Base model for Application objects containing fields common to all CRUD operations.

    This model serves as the foundation for create, update, and response models,
    containing all shared fields and validation logic.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the application.",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
        examples=["100bao"],
    )
    category: str = Field(
        ...,
        max_length=50,
        description="High-level category to which the application belongs.",
        examples=["general-internet"],
    )
    subcategory: str = Field(
        ...,
        max_length=50,
        description="Specific sub-category within the high-level category.",
        examples=["file-sharing"],
    )
    technology: str = Field(
        ...,
        max_length=50,
        description="The underlying technology utilized by the application.",
        examples=["peer-to-peer"],
    )
    risk: int = Field(
        ...,
        description="The risk level associated with the application.",
        examples=[5],
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="Description for the application.",
        examples=[
            '100bao (literally translated as "100 treasures") is a free Chinese P2P file-sharing program.'
        ],
    )
    ports: Optional[List[str]] = Field(
        None,
        description="List of TCP/UDP ports associated with the application.",
        examples=[["tcp/3468,6346,11300"]],
    )
    folder: Optional[str] = Field(
        None,
        max_length=64,
        description="The folder where the application configuration is stored.",
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        examples=["Production"],
    )
    snippet: Optional[str] = Field(
        None,
        max_length=64,
        description="The configuration snippet for the application.",
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        examples=["predefined-snippet"],
    )

    # Boolean attributes
    evasive: Optional[bool] = Field(
        False,
        description="Indicates if the application uses evasive techniques.",
    )
    pervasive: Optional[bool] = Field(
        False,
        description="Indicates if the application is widely used.",
    )
    excessive_bandwidth_use: Optional[bool] = Field(
        False,
        description="Indicates if the application uses excessive bandwidth.",
    )
    used_by_malware: Optional[bool] = Field(
        False,
        description="Indicates if the application is commonly used by malware.",
    )
    transfers_files: Optional[bool] = Field(
        False,
        description="Indicates if the application transfers files.",
    )
    has_known_vulnerabilities: Optional[bool] = Field(
        False,
        description="Indicates if the application has known vulnerabilities.",
    )
    tunnels_other_apps: Optional[bool] = Field(
        False,
        description="Indicates if the application tunnels other applications.",
    )
    prone_to_misuse: Optional[bool] = Field(
        False,
        description="Indicates if the application is prone to misuse.",
    )
    no_certifications: Optional[bool] = Field(
        False,
        description="Indicates if the application lacks certifications.",
    )


class ApplicationCreateModel(ApplicationBaseModel):
    """Model for creating a new Application.

    Inherits from ApplicationBaseModel and adds container type validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "ApplicationCreateModel":
        """Ensure exactly one container field (folder or snippet) is set.

        Returns:
            ApplicationCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = [
            "folder",
            "snippet",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder' or 'snippet' must be provided.")
        return self


class ApplicationUpdateModel(ApplicationBaseModel):
    """Model for updating an existing Application.

    All fields are optional to allow partial updates.
    """

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the application",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ApplicationResponseModel(ApplicationBaseModel):
    """Model for Application responses.

    Includes all base fields plus the id field.
    Updates the description field to have a length of 4096 characters. tsk tsk.
    Updates the subcategory field to be optional to account for `unknown-tcp` app-id. tsk tsk.
    Updates the technology field to be optional to account for `unknown-tcp` app-id. tsk tsk.
    """

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the application",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    description: Optional[str] = Field(
        None,
        max_length=4094,
        description="Description for the application.",
        examples=[
            '100bao (literally translated as "100 treasures") is a free Chinese P2P file-sharing program.'
        ],
    )
    subcategory: Optional[str] = Field(
        None,
        max_length=50,
        description="Specific sub-category within the high-level category.",
        examples=["file-sharing"],
    )
    technology: Optional[str] = Field(
        None,
        max_length=50,
        description="The underlying technology utilized by the application.",
        examples=["peer-to-peer"],
    )
