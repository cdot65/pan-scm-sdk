"""Device operations models for Operations API."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceOperationsRequestModel(BaseModel):
    """Validates device serial numbers for job dispatch."""

    devices: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="List of 1-5 device serial numbers.",
    )

    @field_validator("devices")
    @classmethod
    def validate_serial_numbers(cls, v: List[str]) -> List[str]:
        import re
        pattern = re.compile(r"^\d{14,15}$")
        for serial in v:
            if not pattern.match(serial):
                raise ValueError(f"Invalid device serial number format: {serial}")
        return v

    model_config = ConfigDict(populate_by_name=True)


class JobCreatedModel(BaseModel):
    """Response from job dispatch — contains the job ID for polling."""

    job_id: str = Field(..., description="Unique identifier for the created job.")

    model_config = ConfigDict(populate_by_name=True)


class DeviceJobDetailsModel(BaseModel):
    """Detailed results from a device command execution."""

    msg: str = Field(..., description="Status message from the command execution.")
    result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Result data. Structure varies by command type.",
    )

    model_config = ConfigDict(populate_by_name=True)


class DeviceJobResultModel(BaseModel):
    """Result from a single device within a job."""

    device: str = Field(..., description="Device serial number.")
    state: str = Field(..., description="Job state for this device.")
    created_ts: str = Field(..., description="Timestamp when the job was created.")
    updated_ts: str = Field(..., description="Timestamp when the job was last updated.")
    details: DeviceJobDetailsModel = Field(..., description="Detailed command results.")

    model_config = ConfigDict(populate_by_name=True)


class DeviceJobRequestModel(BaseModel):
    """The original request that initiated the job."""

    command: str = Field(..., description="The command that was executed.")
    devices: List[str] = Field(..., description="Device serial numbers.")

    model_config = ConfigDict(populate_by_name=True)


class DeviceJobStatusModel(BaseModel):
    """Full job status response from the device jobs endpoint."""

    jobId: str = Field(..., description="Unique identifier for the job.")
    progress: int = Field(..., ge=0, le=100, description="Job completion percentage.")
    state: str = Field(..., description="Current state of the job.")
    request: DeviceJobRequestModel = Field(..., description="Original request.")
    results: List[DeviceJobResultModel] = Field(
        default_factory=list, description="Results from each device.",
    )

    model_config = ConfigDict(populate_by_name=True)
