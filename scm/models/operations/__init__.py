"""scm.models.operations: Operations-related models."""
# scm/models/operations/__init__.py

from .candidate_push import CandidatePushRequestModel, CandidatePushResponseModel
from .device_operations import (
    DeviceJobDetailsModel,
    DeviceJobRequestModel,
    DeviceJobResultModel,
    DeviceJobStatusModel,
    DeviceOperationsRequestModel,
    JobCreatedModel,
)
from .jobs import (
    JobDetails,
    JobListItem,
    JobListResponse,
    JobStatusData,
    JobStatusResponse,
)
from .local_config import LocalConfigVersionModel

__all__ = [
    "CandidatePushRequestModel",
    "CandidatePushResponseModel",
    "DeviceJobDetailsModel",
    "DeviceJobRequestModel",
    "DeviceJobResultModel",
    "DeviceJobStatusModel",
    "DeviceOperationsRequestModel",
    "JobCreatedModel",
    "JobDetails",
    "JobStatusData",
    "JobStatusResponse",
    "JobListItem",
    "JobListResponse",
    "LocalConfigVersionModel",
]
