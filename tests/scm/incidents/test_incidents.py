"""Tests for Incidents service."""

from unittest.mock import MagicMock

import pytest

from scm.incidents.incidents import Incidents
from scm.models.incidents.incidents import (
    IncidentDetailModel,
    IncidentSearchResponseModel,
)


class TestIncidents:
    """Tests for the Incidents service."""

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.get = MagicMock()
        client.post = MagicMock()
        client.region = "americas"
        client.oauth_client = MagicMock()
        client.oauth_client.auth_request.tsg_id = "test-tsg-123"
        return client

    @pytest.fixture
    def incidents_service(self, mock_client):
        return Incidents(mock_client)

    def test_get_headers(self, incidents_service):
        headers = incidents_service._get_headers()
        assert headers["X-PANW-Region"] == "americas"
        assert headers["prisma-tenant"] == "test-tsg-123"

    def test_get_headers_no_oauth(self, incidents_service):
        incidents_service.api_client.oauth_client = None
        headers = incidents_service._get_headers()
        assert headers["X-PANW-Region"] == "americas"
        assert "prisma-tenant" not in headers

    def test_get_headers_custom_region(self, incidents_service):
        incidents_service.api_client.region = "europe"
        headers = incidents_service._get_headers()
        assert headers["X-PANW-Region"] == "europe"

    def test_search_basic(self, incidents_service, mock_client):
        mock_client.post.return_value = {
            "header": {
                "createdAt": "2026-03-12T19:38:43Z",
                "dataCount": 1,
                "requestId": "test-req-1",
            },
            "data": [{
                "incident_id": "inc-123",
                "title": "Test incident",
                "severity": "High",
                "status": "Raised",
                "product": "NGFW",
            }],
        }
        result = incidents_service.search()
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/incidents/v1/search"
        assert call_args[1]["headers"]["X-PANW-Region"] == "americas"
        assert isinstance(result, IncidentSearchResponseModel)
        assert len(result.data) == 1
        assert result.data[0].incident_id == "inc-123"

    def test_search_with_filters(self, incidents_service, mock_client):
        mock_client.post.return_value = {
            "header": {"createdAt": "2026-03-12T19:38:43Z", "dataCount": 0, "requestId": "r2"},
            "data": [],
        }
        incidents_service.search(
            status=["Raised"], severity=["Critical", "High"],
            product=["Prisma Access", "NGFW"],
        )
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        rules = payload["filter"]["rules"]
        status_rule = next(r for r in rules if r["property"] == "status")
        assert status_rule["operator"] == "in"
        assert status_rule["values"] == ["Raised"]
        severity_rule = next(r for r in rules if r["property"] == "severity")
        assert severity_rule["values"] == ["Critical", "High"]
        product_rule = next(r for r in rules if r["property"] == "product")
        assert product_rule["values"] == ["Prisma Access", "NGFW"]

    def test_search_with_raw_filter_rules(self, incidents_service, mock_client):
        mock_client.post.return_value = {
            "header": {"createdAt": "2026-03-12T19:38:43Z", "dataCount": 0, "requestId": "r3"},
            "data": [],
        }
        custom_rules = [{"property": "release_state", "operator": "in", "values": ["Released"]}]
        incidents_service.search(filter_rules=custom_rules)
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        rules = payload["filter"]["rules"]
        assert len(rules) == 1
        assert rules[0]["property"] == "release_state"

    def test_search_pagination(self, incidents_service, mock_client):
        mock_client.post.return_value = {
            "header": {"createdAt": "2026-03-12T19:38:43Z", "dataCount": 0, "requestId": "r4"},
            "data": [],
        }
        incidents_service.search(page_size=25, page_number=3)
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["pagination"]["page_size"] == 25
        assert payload["pagination"]["page_number"] == 3

    def test_search_order_by(self, incidents_service, mock_client):
        mock_client.post.return_value = {
            "header": {"createdAt": "2026-03-12T19:38:43Z", "dataCount": 0, "requestId": "r5"},
            "data": [],
        }
        incidents_service.search(order_by=[{"property": "updated_time", "order": "desc"}])
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["pagination"]["order_by"] == [{"property": "updated_time", "order": "desc"}]

    def test_get_details(self, incidents_service, mock_client):
        mock_client.get.return_value = {
            "incident_id": "inc-456",
            "title": "Detailed incident",
            "severity": "Critical",
            "status": "Raised",
            "product": "NGFW",
            "description": "This is a test description.",
            "alerts": [{
                "alert_id": "alert-1", "severity": "Critical",
                "state": "Raised", "title": "Alert 1", "updated_time": 1765468859684,
            }],
        }
        result = incidents_service.get_details("inc-456")
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/incidents/v1/details/inc-456"
        assert call_args[1]["headers"]["X-PANW-Region"] == "americas"
        assert isinstance(result, IncidentDetailModel)
        assert result.description == "This is a test description."
        assert len(result.alerts) == 1

    def test_search_defaults(self, incidents_service, mock_client):
        mock_client.post.return_value = {
            "header": {"createdAt": "2026-03-12T19:38:43Z", "dataCount": 0, "requestId": "r6"},
            "data": [],
        }
        incidents_service.search()
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["pagination"]["page_size"] == 50
        assert payload["pagination"]["page_number"] == 1
