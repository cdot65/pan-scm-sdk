# scm/models/operations/candidate_push.py

from typing import List

from pydantic import BaseModel, Field, ConfigDict, field_validator


class CandidatePushRequestModel(BaseModel):
    """
    Represents a commit request for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for commit requests,
    including folder selection, admin users, and commit description.

    Attributes:
        folders (List[str]): List of folders to commit changes from.
        admin (List[str]): List of admin email addresses authorized for the commit.
        description (str): Description of the commit changes.

    Error:
        ValueError: Raised when validation fails for folders, admin, or description.
    """

    folders: List[str] = Field(
        ...,
        min_length=1,
        description="List of folders to commit changes from",
        examples=[["Texas", "Production"]],
    )
    admin: List[str] = Field(
        ...,
        min_length=1,
        description="List of admin email addresses",
        examples=[["admin@example.com"]],
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Description of the commit changes",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
    )

    @field_validator("folders")
    def validate_folders(cls, v):
        """Ensure folders list is not empty and contains valid strings."""
        if not v:
            raise ValueError("At least one folder must be specified")
        if not all(isinstance(folder, str) and folder.strip() for folder in v):
            raise ValueError("All folders must be non-empty strings")
        return v

    @field_validator("admin")
    def validate_admin(cls, v):
        """Ensure admin list is not empty and contains valid email addresses."""
        if not v:
            raise ValueError("At least one admin must be specified")
        if not all(isinstance(admin, str) and "@" in admin for admin in v):
            raise ValueError("All admin entries must be valid email addresses")
        return v


class CandidatePushResponseModel(BaseModel):
    """
    Represents a commit response from Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure for commit operation responses,
    including success status, job ID, and response message.

    Attributes:
        success (bool): Whether the commit operation was successfully initiated.
        job_id (str): The ID of the commit job.
        message (str): Detailed message about the commit operation.
    """

    success: bool = Field(
        ...,
        description="Whether the commit operation was successfully initiated",
    )
    job_id: str = Field(
        ...,
        description="The ID of the commit job",
        examples=["1586"],
    )
    message: str = Field(
        ...,
        description="Detailed message about the commit operation",
        examples=["CommitAndPush job enqueued with jobid 1586"],
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )
