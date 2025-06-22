"""scm.models.setup: Setup-related models."""

from .device import DeviceCreateModel, DeviceResponseModel, DeviceUpdateModel
from .folder import FolderCreateModel, FolderResponseModel, FolderUpdateModel
from .label import LabelCreateModel, LabelResponseModel, LabelUpdateModel
from .snippet import (
    FolderReference,
    SnippetBaseModel,
    SnippetCreateModel,
    SnippetResponseModel,
    SnippetUpdateModel,
)
from .variable import VariableCreateModel, VariableResponseModel, VariableUpdateModel

__all__ = [
    "DeviceCreateModel",
    "DeviceResponseModel",
    "DeviceUpdateModel",
    "FolderCreateModel",
    "FolderResponseModel",
    "FolderUpdateModel",
    "FolderReference",
    "LabelCreateModel",
    "LabelResponseModel",
    "LabelUpdateModel",
    "SnippetBaseModel",
    "SnippetCreateModel",
    "SnippetResponseModel",
    "SnippetUpdateModel",
    "VariableCreateModel",
    "VariableResponseModel",
    "VariableUpdateModel",
]
