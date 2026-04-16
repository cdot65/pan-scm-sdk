"""Incident models for the Unified Incident Framework API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FilterRuleModel(BaseModel):
    """A single filter rule for incident search."""

    property: str = Field(..., description="The property to filter on.")
    operator: str = Field(..., description="The filter operator (e.g., 'in', 'equals').")
    values: List[Any] = Field(..., description="The values to filter by.")

    model_config = ConfigDict(populate_by_name=True)


class FilterObjectModel(BaseModel):
    """Container for filter rules."""

    rules: List[FilterRuleModel] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class PaginationModel(BaseModel):
    """Pagination parameters for incident search."""

    page_size: int = Field(default=50, description="Number of results per page.")
    page_number: int = Field(default=1, description="Page number to retrieve.")
    order_by: Optional[List[Dict[str, str]]] = Field(default=None, description="Ordering specification.")

    model_config = ConfigDict(populate_by_name=True)


class IncidentSearchRequestModel(BaseModel):
    """Request body for incident search."""

    filter: Optional[FilterObjectModel] = Field(default=None)
    pagination: Optional[PaginationModel] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class ImpactedObjectsModel(BaseModel):
    """Impacted objects associated with an incident."""

    agent_ids: Optional[List[str]] = None
    aggr_locations: Optional[List[str]] = None
    app_names: Optional[List[str]] = None
    asn_org_names: Optional[List[str]] = None
    auth_server_profiles: Optional[List[str]] = None
    auth_servers: Optional[List[str]] = None
    bgp_peer_names: Optional[List[str]] = None
    certificate_names: Optional[List[str]] = None
    cluster_names: Optional[List[str]] = None
    cves: Optional[List[str]] = None
    device_ids: Optional[List[str]] = None
    directory_ids: Optional[List[str]] = None
    dns_servers: Optional[List[str]] = None
    gp_versions: Optional[List[str]] = None
    gre_tunnel_names: Optional[List[str]] = None
    host_names: Optional[List[str]] = None
    ike_gateway_names: Optional[List[str]] = None
    interfaces: Optional[List[str]] = None
    licenses: Optional[List[str]] = None
    link_names: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    log_receivers: Optional[List[str]] = None
    nat_policies: Optional[List[str]] = None
    packages: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    security_checks: Optional[List[str]] = None
    security_objects: Optional[List[str]] = None
    security_types: Optional[List[str]] = None
    sha256s: Optional[List[str]] = None
    site_names: Optional[List[str]] = None
    slots: Optional[List[str]] = None
    spn_names: Optional[List[str]] = None
    theaters: Optional[List[str]] = None
    tunnel_names: Optional[List[str]] = None
    user_locations: Optional[List[str]] = None
    zones: Optional[List[str]] = None

    model_config = ConfigDict(populate_by_name=True)


class IncidentModel(BaseModel):
    """Represents an incident from search results."""

    incident_id: str = Field(..., description="Unique incident identifier.")
    title: str = Field(..., description="Incident title.")
    severity: str = Field(..., description="Severity level.")
    severity_id: Optional[int] = Field(default=None)
    status: str = Field(..., description="Incident status.")
    priority: Optional[str] = Field(default=None)
    priority_id: Optional[int] = Field(default=None)
    product: str = Field(..., description="Product that generated the incident.")
    category: Optional[str] = Field(default=None)
    sub_category: Optional[str] = Field(default=None)
    code: Optional[str] = Field(default=None)
    raised_time: Optional[int] = Field(default=None)
    updated_time: Optional[int] = Field(default=None)
    cleared_time: Optional[int] = Field(default=None)
    release_state: Optional[str] = Field(default=None)
    incident_type: Optional[str] = Field(default=None)
    designation: Optional[str] = Field(default=None)
    acknowledged: Optional[bool] = Field(default=None)
    acknowledged_by: Optional[str] = Field(default=None)
    primary_impacted_objects: Optional[ImpactedObjectsModel] = Field(default=None)
    related_impacted_objects: Optional[ImpactedObjectsModel] = Field(default=None)
    snow_assignee: Optional[str] = Field(default=None)
    snow_priority: Optional[str] = Field(default=None)
    snow_status: Optional[str] = Field(default=None)
    snow_ticket_id: Optional[str] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class AlertModel(BaseModel):
    """Represents an alert within an incident detail."""

    alert_id: str = Field(..., description="Unique alert identifier.")
    processed_alert_id: Optional[str] = Field(default=None)
    severity: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    updated_time: Optional[int] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    inc_prop: Optional[int] = Field(default=None)
    ctx_only_alert: Optional[bool] = Field(default=None)
    code: Optional[str] = Field(default=None)
    resource_keys: Optional[str] = Field(default=None)
    release_state: Optional[str] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class IncidentDetailModel(IncidentModel):
    """Extended incident information from the details endpoint."""

    description: Optional[str] = Field(default=None)
    description_locale_key: Optional[str] = Field(default=None)
    remediations: Optional[str] = Field(default=None)
    detail: Optional[str] = Field(default=None)
    alerts: Optional[List[AlertModel]] = Field(default=None)
    resource_keys: Optional[str] = Field(default=None)
    resource_context: Optional[str] = Field(default=None)
    incident_code: Optional[str] = Field(default=None)
    incident_settings_id: Optional[str] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class IncidentSearchResponseHeaderModel(BaseModel):
    """Response header metadata from incident search."""

    createdAt: Optional[str] = Field(default=None)
    dataCount: Optional[int] = Field(default=None)
    requestId: Optional[str] = Field(default=None)
    queryInput: Optional[Dict[str, Any]] = Field(default=None)
    isResourceDataOverridden: Optional[bool] = Field(default=None)
    fieldList: Optional[List[Dict[str, Any]]] = Field(default=None)
    status: Optional[Dict[str, Any]] = Field(default=None)
    pagination: Optional[Dict[str, Any]] = Field(default=None)
    name: Optional[str] = Field(default=None)
    cache_operation: Optional[str] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class IncidentSearchResponseModel(BaseModel):
    """Full response from incident search."""

    header: IncidentSearchResponseHeaderModel = Field(..., description="Response metadata.")
    data: List[IncidentModel] = Field(default_factory=list, description="List of incidents.")

    model_config = ConfigDict(populate_by_name=True)
