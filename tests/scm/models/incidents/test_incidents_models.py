"""Tests for incidents models."""

import pytest
from pydantic import ValidationError

from scm.models.incidents.incidents import (
    AlertModel,
    FilterRuleModel,
    ImpactedObjectsModel,
    IncidentDetailModel,
    IncidentModel,
    IncidentSearchRequestModel,
    IncidentSearchResponseModel,
    PaginationModel,
)


class TestFilterRuleModel:
    def test_valid_rule(self):
        model = FilterRuleModel(property="status", operator="in", values=["Raised"])
        assert model.property == "status"
        assert model.operator == "in"
        assert model.values == ["Raised"]


class TestPaginationModel:
    def test_defaults(self):
        model = PaginationModel()
        assert model.page_size == 50
        assert model.page_number == 1
        assert model.order_by is None

    def test_custom_values(self):
        model = PaginationModel(
            page_size=25, page_number=3,
            order_by=[{"property": "updated_time", "order": "desc"}],
        )
        assert model.page_size == 25
        assert model.page_number == 3
        assert len(model.order_by) == 1


class TestIncidentSearchRequestModel:
    def test_empty_request(self):
        model = IncidentSearchRequestModel()
        assert model.filter is None
        assert model.pagination is None

    def test_with_filter_and_pagination(self):
        model = IncidentSearchRequestModel(
            filter={"rules": [{"property": "status", "operator": "in", "values": ["Raised"]}]},
            pagination={"page_size": 25, "page_number": 1},
        )
        assert model.filter is not None
        assert model.pagination is not None


class TestImpactedObjectsModel:
    def test_all_defaults_empty(self):
        model = ImpactedObjectsModel()
        assert model.device_ids is None
        assert model.host_names is None
        assert model.interfaces is None

    def test_with_values(self):
        model = ImpactedObjectsModel(
            device_ids=["dev-1", "dev-2"], host_names=["host-1"], zones=["zone-a"],
        )
        assert model.device_ids == ["dev-1", "dev-2"]
        assert model.host_names == ["host-1"]
        assert model.zones == ["zone-a"]


class TestIncidentModel:
    def test_valid_incident(self):
        model = IncidentModel(
            incident_id="21818c4a-8353-4d9c-ae3e-ae90004d4662",
            title="Tenant has 14 raised alerts", severity="Informational",
            severity_id=200, status="Raised", priority="Not Set",
            priority_id=0, product="Prisma Access", category="Network",
        )
        assert model.incident_id == "21818c4a-8353-4d9c-ae3e-ae90004d4662"
        assert model.severity == "Informational"
        assert model.status == "Raised"

    def test_with_impacted_objects(self):
        model = IncidentModel(
            incident_id="test-id", title="Test", severity="High",
            status="Raised", product="NGFW",
            primary_impacted_objects={"device_ids": ["dev-1"]},
        )
        assert model.primary_impacted_objects.device_ids == ["dev-1"]

    def test_optional_fields_default_none(self):
        model = IncidentModel(
            incident_id="test-id", title="Test", severity="High",
            status="Raised", product="NGFW",
        )
        assert model.sub_category is None
        assert model.cleared_time is None
        assert model.snow_ticket_id is None
        assert model.acknowledged is None


class TestAlertModel:
    def test_valid_alert(self):
        model = AlertModel(
            alert_id="0a887db4-d760-4dc2-bb14-04c5e120b811",
            severity="Critical", state="Raised",
            title="Alert title", updated_time=1765468859684,
        )
        assert model.alert_id == "0a887db4-d760-4dc2-bb14-04c5e120b811"
        assert model.severity == "Critical"


class TestIncidentDetailModel:
    def test_extends_incident_model(self):
        model = IncidentDetailModel(
            incident_id="test-id", title="Test incident", severity="Critical",
            status="Raised", product="NGFW", description="Test description",
            alerts=[{
                "alert_id": "alert-1", "severity": "Critical",
                "state": "Raised", "title": "Alert 1", "updated_time": 1765468859684,
            }],
        )
        assert model.description == "Test description"
        assert len(model.alerts) == 1
        assert model.alerts[0].alert_id == "alert-1"

    def test_optional_detail_fields(self):
        model = IncidentDetailModel(
            incident_id="test-id", title="Test", severity="High",
            status="Raised", product="NGFW",
        )
        assert model.description is None
        assert model.remediations is None
        assert model.alerts is None
        assert model.resource_context is None


class TestIncidentSearchResponseModel:
    def test_valid_response(self):
        model = IncidentSearchResponseModel(
            header={"createdAt": "2026-03-12T19:38:43Z", "dataCount": 1, "requestId": "test-123"},
            data=[{"incident_id": "test-id", "title": "Test", "severity": "High", "status": "Raised", "product": "NGFW"}],
        )
        assert len(model.data) == 1
        assert model.data[0].incident_id == "test-id"

    def test_empty_data(self):
        model = IncidentSearchResponseModel(
            header={"createdAt": "2026-03-12T19:38:43Z", "dataCount": 0, "requestId": "test-123"},
            data=[],
        )
        assert len(model.data) == 0
