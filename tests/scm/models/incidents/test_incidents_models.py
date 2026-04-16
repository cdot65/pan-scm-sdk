"""Tests for incidents models."""


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
    """Tests for FilterRuleModel."""

    def test_valid_rule(self):
        """Test that a valid filter rule is accepted."""
        model = FilterRuleModel(property="status", operator="in", values=["Raised"])
        assert model.property == "status"
        assert model.operator == "in"
        assert model.values == ["Raised"]


class TestPaginationModel:
    """Tests for PaginationModel."""

    def test_defaults(self):
        """Test that defaults are page_size=50 and page_number=1."""
        model = PaginationModel()
        assert model.page_size == 50
        assert model.page_number == 1
        assert model.order_by is None

    def test_custom_values(self):
        """Test that custom pagination values are accepted."""
        model = PaginationModel(
            page_size=25, page_number=3,
            order_by=[{"property": "updated_time", "order": "desc"}],
        )
        assert model.page_size == 25
        assert model.page_number == 3
        assert len(model.order_by) == 1


class TestIncidentSearchRequestModel:
    """Tests for IncidentSearchRequestModel."""

    def test_empty_request(self):
        """Test that an empty request defaults filter and pagination to None."""
        model = IncidentSearchRequestModel()
        assert model.filter is None
        assert model.pagination is None

    def test_with_filter_and_pagination(self):
        """Test that filter and pagination are set when provided."""
        model = IncidentSearchRequestModel(
            filter={"rules": [{"property": "status", "operator": "in", "values": ["Raised"]}]},
            pagination={"page_size": 25, "page_number": 1},
        )
        assert model.filter is not None
        assert model.pagination is not None


class TestImpactedObjectsModel:
    """Tests for ImpactedObjectsModel."""

    def test_all_defaults_empty(self):
        """Test that all fields default to None."""
        model = ImpactedObjectsModel()
        assert model.device_ids is None
        assert model.host_names is None
        assert model.interfaces is None

    def test_with_values(self):
        """Test that provided values are stored correctly."""
        model = ImpactedObjectsModel(
            device_ids=["dev-1", "dev-2"], host_names=["host-1"], zones=["zone-a"],
        )
        assert model.device_ids == ["dev-1", "dev-2"]
        assert model.host_names == ["host-1"]
        assert model.zones == ["zone-a"]


class TestIncidentModel:
    """Tests for IncidentModel."""

    def test_valid_incident(self):
        """Test that a valid incident is accepted."""
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
        """Test that primary_impacted_objects is parsed correctly."""
        model = IncidentModel(
            incident_id="test-id", title="Test", severity="High",
            status="Raised", product="NGFW",
            primary_impacted_objects={"device_ids": ["dev-1"]},
        )
        assert model.primary_impacted_objects.device_ids == ["dev-1"]

    def test_optional_fields_default_none(self):
        """Test that optional fields default to None."""
        model = IncidentModel(
            incident_id="test-id", title="Test", severity="High",
            status="Raised", product="NGFW",
        )
        assert model.sub_category is None
        assert model.cleared_time is None
        assert model.snow_ticket_id is None
        assert model.acknowledged is None


class TestAlertModel:
    """Tests for AlertModel."""

    def test_valid_alert(self):
        """Test that a valid alert is accepted."""
        model = AlertModel(
            alert_id="0a887db4-d760-4dc2-bb14-04c5e120b811",
            severity="Critical", state="Raised",
            title="Alert title", updated_time=1765468859684,
        )
        assert model.alert_id == "0a887db4-d760-4dc2-bb14-04c5e120b811"
        assert model.severity == "Critical"


class TestIncidentDetailModel:
    """Tests for IncidentDetailModel."""

    def test_extends_incident_model(self):
        """Test that detail model includes description and alerts."""
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
        """Test that optional detail fields default to None."""
        model = IncidentDetailModel(
            incident_id="test-id", title="Test", severity="High",
            status="Raised", product="NGFW",
        )
        assert model.description is None
        assert model.remediations is None
        assert model.alerts is None
        assert model.resource_context is None


class TestIncidentSearchResponseModel:
    """Tests for IncidentSearchResponseModel."""

    def test_valid_response(self):
        """Test that a valid response with data is parsed correctly."""
        model = IncidentSearchResponseModel(
            header={"createdAt": "2026-03-12T19:38:43Z", "dataCount": 1, "requestId": "test-123"},
            data=[{"incident_id": "test-id", "title": "Test", "severity": "High", "status": "Raised", "product": "NGFW"}],
        )
        assert len(model.data) == 1
        assert model.data[0].incident_id == "test-id"

    def test_empty_data(self):
        """Test that an empty data list is accepted."""
        model = IncidentSearchResponseModel(
            header={"createdAt": "2026-03-12T19:38:43Z", "dataCount": 0, "requestId": "test-123"},
            data=[],
        )
        assert len(model.data) == 0
