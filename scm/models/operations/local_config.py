"""Local configuration version models for Operations API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LocalConfigVersionModel(BaseModel):
    """Represents a local configuration version entry for a device."""

    id: int = Field(..., description="Unique identifier for this configuration version entry.")
    serial: str = Field(..., description="Device serial number (14-15 digits).")
    local_version: str = Field(..., description="Local configuration version identifier.")
    timestamp: datetime = Field(..., description="When this configuration version was created.")
    xfmed_version: str = Field(..., description="Transformed configuration version identifier.")
    md5: Optional[str] = Field(default=None, description="MD5 hash of the configuration.")

    model_config = ConfigDict(populate_by_name=True)
