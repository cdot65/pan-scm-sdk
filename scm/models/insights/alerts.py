"""Pydantic models for Strata Cloud Manager insights alerts."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AlertSeverity:
    """Alert severity levels - Note: API returns capitalized values."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"
    NOTIFICATION = "Notification"


class AlertStatus:
    """Alert status values."""

    RAISED = "Raised"
    RAISED_CHILD = "RaisedChild"
    CLEARED = "Cleared"


class Alert(BaseModel):
    """Alert response model."""

    id: str = Field(None, alias="alert_id")
    name: Optional[str] = Field(None, alias="message")
    severity: Optional[str] = None
    severity_id: Optional[int] = None
    status: Optional[str] = Field(None, alias="state")
    timestamp: Optional[str] = Field(None, alias="raised_time")
    updated_time: Optional[str] = None
    description: Optional[str] = None
    folder: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    impacted_resources: Optional[List[str]] = Field(None, alias="primary_impacted_objects")
    metadata: Optional[Dict[str, Any]] = Field(None, alias="resource_context")
    clear_reason: Optional[str] = None
    age: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("impacted_resources", "metadata", mode="before")
    def parse_json_string(cls, v):
        """Parse JSON string fields if needed."""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v


class AlertFilter(BaseModel):
    """Alert filter parameters."""

    folder: Optional[str] = None
    severity: Optional[List[str]] = None
    start_time: Optional[int] = None  # Unix timestamp or relative days
    end_time: Optional[int] = None
    status: Optional[List[str]] = None
    category: Optional[str] = None
    max_results: Optional[int] = Field(100, ge=1, le=1000)


class AlertQueryProperty(BaseModel):
    """Property specification for alert queries."""

    property: str
    alias: Optional[str] = None
    function: Optional[str] = None  # sum, min, max, avg, count, distinct_count, distinct
    sort: Optional[Dict[str, Any]] = None


class AlertQueryFilter(BaseModel):
    """Filter specification for alert queries."""

    operator: Optional[str] = "AND"  # AND or OR
    rules: List[Dict[str, Any]]


class AlertQuery(BaseModel):
    """Full alert query specification."""

    properties: Optional[List[AlertQueryProperty]] = None
    filter: Optional[AlertQueryFilter] = None
    count: Optional[int] = Field(100, ge=1, le=1000)
    histogram: Optional[Dict[str, Any]] = None


class AlertStatistic(BaseModel):
    """Alert statistic response model."""

    severity: Optional[str] = None
    severity_id: Optional[int] = None
    category: Optional[str] = None
    state: Optional[str] = None
    count: Optional[int] = None

    model_config = ConfigDict(extra="allow")  # Allow additional fields that might be returned
