"""Jobs operations models for Strata Cloud Manager SDK.

Contains Pydantic models for representing job operation objects and related data.
"""

# scm/models/operations/jobs.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class JobDetails(BaseModel):
    """Model for job details JSON string."""

    info: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class JobStatusData(BaseModel):
    """Model for individual job status data."""

    cfg_id: str = Field(default="")
    details: str
    dev_serial: str = Field(default="")
    dev_uuid: str = Field(default="")
    device_name: str = Field(default="")
    device_type: str = Field(default="")
    end_ts: Optional[datetime] = None
    id: str
    insert_ts: datetime
    job_result: str
    job_status: str
    job_type: str
    last_update: datetime
    opaque_int: str = Field(default="0")
    opaque_str: str = Field(default="")
    owner: str
    parent_id: str = Field(default="0")
    percent: str
    result_i: str
    result_str: str
    session_id: str = Field(default="")
    start_ts: datetime
    status_i: str
    status_str: str
    summary: str = Field(default="")
    type_i: str
    type_str: str
    uname: str

    model_config = ConfigDict(populate_by_name=True)

    @field_serializer(
        "end_ts",
        "insert_ts",
        "last_update",
        "start_ts",
    )
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Serialize datetime fields to ISO format."""
        return dt.isoformat() if dt else None


class JobStatusResponse(BaseModel):
    """Model for job status response."""

    data: List[JobStatusData]

    model_config = ConfigDict(populate_by_name=True)


class JobListItem(BaseModel):
    """Model for individual job in list response."""

    device_name: str = Field(default="")
    end_ts: Optional[str] = Field(default=None)
    id: str
    job_result: str
    job_status: str
    job_type: str
    parent_id: str
    percent: str = Field(default="")
    result_str: str
    start_ts: str
    status_str: str
    summary: str = Field(default="")
    type_str: str
    uname: str
    description: str = Field(default="")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "end_ts",
        "start_ts",
    )
    def validate_timestamp(cls, v: Optional[str]) -> Optional[str]:
        """Validate timestamp fields, allowing empty strings."""
        if v == "":
            return None
        return v


class JobListResponse(BaseModel):
    """Model for jobs list response with pagination."""

    data: List[JobListItem]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(populate_by_name=True)
