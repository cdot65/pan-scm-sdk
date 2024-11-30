# scm/models/operations/jobs.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


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

    model_config = ConfigDict(
        populate_by_name=True, json_encoders={datetime: lambda dt: dt.isoformat()}
    )


class JobStatusResponse(BaseModel):
    """Model for job status response."""

    data: List[JobStatusData]

    model_config = ConfigDict(populate_by_name=True)
