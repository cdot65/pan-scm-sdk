"""Common models for Insights API responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class InsightsResponseHeader(BaseModel):
    """Response header from Insights API."""

    createdAt: str
    dataCount: int
    requestId: str
    queryInput: Dict[str, Any]
    isResourceDataOverridden: bool
    fieldList: List[Dict[str, Any]]
    status: Dict[str, Any]
    name: str
    cache_operation: Optional[str] = None


class InsightsResponse(BaseModel):
    """Full response structure from Insights API."""

    header: InsightsResponseHeader
    data: List[Dict[str, Any]]
