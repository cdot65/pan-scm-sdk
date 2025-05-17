"""Application Filters models for Strata Cloud Manager SDK.

Contains Pydantic models for representing application filter objects and related data.
"""

# scm/models/objects/application_filters.py

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApplicationFiltersBaseModel(BaseModel):
    """Base model for Application filter objects containing fields common to all CRUD operations.

    This model serves as the foundation for create, update, and response models,
    containing all shared fields and validation logic.
    """

    # Required fields
    name: str = Field(
        ...,
        max_length=31,
        description="The name of the application filter.",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
        examples=["100bao"],
    )

    # Optional fields
    category: Optional[List[str]] = Field(
        None,
        max_length=128,
        description="List of the categories within the application filter.",
        examples=[
            [
                "business-systems",
                "collaboration",
            ]
        ],
    )

    sub_category: Optional[List[str]] = Field(
        None,
        max_length=128,
        description="List of the sub categories within the application filter.",
        examples=[["tcp/3468,6346,11300"]],
    )

    technology: Optional[List[str]] = Field(
        None,
        max_length=128,
        description="List of the technologies within the application filter.",
        examples=[["tcp/3468,6346,11300"]],
    )

    evasive: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify evasive applications.",
    )

    used_by_malware: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify applications used by malware.",
    )

    transfers_files: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify application transfers files.",
    )

    has_known_vulnerabilities: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify applications with known vulnerabilities.",
    )

    tunnels_other_apps: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify applications that can tunnel other applications.",
    )

    prone_to_misuse: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify applications that are prone to misuse.",
    )

    pervasive: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify applications that are pervasive.",
    )

    is_saas: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify applications that are SaaS based.",
    )

    new_appid: Optional[bool] = Field(
        False,
        description="Indicates if the application filter should specify applications with a new AppID.",
    )

    risk: Optional[List[int]] = Field(
        None,
        description="Indicates if the application filter should specify applications with a risk (integer).",
    )

    saas_certifications: Optional[List[str]] = Field(
        None,
        max_length=128,
        description="List of the SaaS Certifications.",
    )

    saas_risk: Optional[List[str]] = Field(
        None,
        description="Indicates if the application filter should specify applications with a SaaS risk.",
    )

    # Configuration Container
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

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class ApplicationFiltersCreateModel(ApplicationFiltersBaseModel):
    """Model for creating a new application filter.

    Inherits from ApplicationFiltersBaseModel and adds container type validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "ApplicationFiltersCreateModel":
        """Ensure exactly one container field (folder or snippet) is set.

        Returns:
            ApplicationFiltersCreateModel: The validated model instance.

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


class ApplicationFiltersUpdateModel(ApplicationFiltersBaseModel):
    """Model for updating an existing application filter.

    All fields are optional to allow partial updates.
    """

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the application",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ApplicationFiltersResponseModel(ApplicationFiltersBaseModel):
    """Model for application filter responses.

    Includes all base fields plus the (optional!) id field.
    """

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the application",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
