# scm/models/application.py

from typing import Optional, List
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
)


class ApplicationRequestModel(BaseModel):
    """
    Represents an Application creation for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for creating an Application,
    including required fields, optional fields, and various attributes defining
    the application's characteristics and behaviors.

    Attributes:
        name (str): The name of the application.
        description (Optional[str]): Detailed information about the application.
        ports (Optional[List[str]]): List of TCP/UDP ports associated with the application.
        category (str): High-level category to which the application belongs.
        subcategory (str): Specific sub-category within the high-level category.
        technology (str): The underlying technology utilized by the application.
        risk (str): The risk level associated with the application.
        evasive (bool): Indicates if the application uses evasive techniques.
        pervasive (bool): Indicates if the application is widely used.
        folder (str): The folder where the application configuration is stored.
        snippet (str): The configuration snippet for the application.
        excessive_bandwidth_use (bool): Indicates if the application uses excessive bandwidth.
        used_by_malware (bool): Indicates if the application is commonly used by malware.
        transfers_files (bool): Indicates if the application transfers files.
        has_known_vulnerabilities (bool): Indicates if the application has known vulnerabilities.
        tunnels_other_apps (bool): Indicates if the application tunnels other applications.
        prone_to_misuse (bool): Indicates if the application is prone to misuse.
        no_certifications (bool): Indicates if the application lacks certifications.
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
        description="The name of the application.",
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
            '100bao (literally translated as "100 treasures") is a free Chinese P2P file-sharing program that supports Windows 98, 2000, and XP operating systems.'
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

    @model_validator(mode="after")
    def validate_container_type(self) -> "ApplicationRequestModel":
        container_fields = [
            "folder",
            "snippet",
        ]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder' or 'snippet' must be provided.")
        return self


class ApplicationResponseModel(BaseModel):
    """
    Represents an Application response for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for listing existing Applications,
    including required fields, optional fields, and various attributes defining
    the application's characteristics and behaviors.

    Attributes:
        id (UUID): UUID of the application.
        name (str): The name of the application.
        description (Optional[str]): Detailed information about the application.
        ports (Optional[List[str]]): List of TCP/UDP ports associated with the application.
        category (str): High-level category to which the application belongs.
        subcategory (str): Specific sub-category within the high-level category.
        technology (str): The underlying technology utilized by the application.
        risk (str): The risk level associated with the application.
        evasive (bool): Indicates if the application uses evasive techniques.
        pervasive (bool): Indicates if the application is widely used.
        folder (str): The folder where the application configuration is stored.
        snippet (str): The configuration snippet for the application.
        excessive_bandwidth_use (bool): Indicates if the application uses excessive bandwidth.
        used_by_malware (bool): Indicates if the application is commonly used by malware.
        transfers_files (bool): Indicates if the application transfers files.
        has_known_vulnerabilities (bool): Indicates if the application has known vulnerabilities.
        tunnels_other_apps (bool): Indicates if the application tunnels other applications.
        prone_to_misuse (bool): Indicates if the application is prone to misuse.
        no_certifications (bool): Indicates if the application lacks certifications.
    """

    # Model configuration
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    id: UUID = Field(
        None,
        description="The UUID of the address object",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    name: str = Field(
        ...,
        max_length=63,
        description="The name of the application.",
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
            '100bao (literally translated as "100 treasures") is a free Chinese P2P file-sharing program that supports Windows 98, 2000, and XP operating systems.'
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
