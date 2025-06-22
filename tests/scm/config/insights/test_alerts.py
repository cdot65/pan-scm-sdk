"""Test suite for Insights Alerts service."""

import pytest
from unittest.mock import Mock, patch
from scm.config.insights.alerts import Alerts
from scm.models.insights.alerts import Alert


class TestAlerts:
    """Tests for the Alerts Insights service."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SCM client."""
        client = Mock()
        client.session = Mock()
        client.session.headers = {"Authorization": "Bearer test-token"}
        client.verify_ssl = True
        # Mock OAuth client for Insights API
        client.oauth_client = Mock()
        client.oauth_client.session = Mock()
        client.oauth_client.session.token = {"access_token": "test-token"}
        client.oauth_client.auth_request = Mock()
        client.oauth_client.auth_request.tsg_id = "test-tsg-id"
        return client

    @pytest.fixture
    def alerts_service(self, mock_client):
        """Create an Alerts service instance."""
        return Alerts(mock_client)

    def test_get_resource_endpoint(self, alerts_service):
        """Test that the correct resource endpoint is returned."""
        assert (
            alerts_service.get_resource_endpoint()
            == "resource/query/prisma_sase_external_alerts_current"
        )

    @patch("requests.post")
    def test_list_alerts_basic(self, mock_post, alerts_service):
        """Test basic alert listing."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 2,
                "requestId": "test-request-1",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [
                {
                    "alert_id": "test-alert-1",
                    "severity": "high",
                    "message": "Test alert 1",
                    "state": "Raised",
                    "raised_time": "2024-01-20T10:00:00Z",
                },
                {
                    "alert_id": "test-alert-2",
                    "severity": "medium",
                    "message": "Test alert 2",
                    "state": "Cleared",
                    "raised_time": "2024-01-20T11:00:00Z",
                },
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call list method
        alerts = alerts_service.list()

        # Verify request
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Check URL
        assert (
            call_args[0][0]
            == "https://api.strata.paloaltonetworks.com/insights/v3.0/resource/query/prisma_sase_external_alerts_current"
        )

        # Check headers
        assert call_args[1]["headers"]["X-PANW-Region"] == "americas"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"

        # Check payload
        payload = call_args[1]["json"]
        assert "properties" in payload
        assert "count" in payload
        assert payload["count"] == 100

        # Verify results
        assert len(alerts) == 2
        assert isinstance(alerts[0], Alert)
        assert alerts[0].id == "test-alert-1"
        assert alerts[0].severity == "high"

    @patch("requests.post")
    def test_list_alerts_with_filters(self, mock_post, alerts_service):
        """Test alert listing with filters."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 0,
                "requestId": "test-request-2",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call list with filters
        alerts_service.list(
            severity=["critical", "high"],
            status=["Raised"],
            start_time=7,
            category="Remote Networks",
            max_results=50,
        )

        # Check payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        # Verify filters
        assert "filter" in payload
        filter_rules = payload["filter"]["rules"]

        # Check severity filter
        severity_filter = next(r for r in filter_rules if r["property"] == "severity")
        assert severity_filter["operator"] == "in"
        assert severity_filter["values"] == ["critical", "high"]

        # Check status filter
        status_filter = next(r for r in filter_rules if r["property"] == "state")
        assert status_filter["operator"] == "in"
        assert status_filter["values"] == ["Raised"]

        # Check time filter
        time_filter = next(r for r in filter_rules if r["property"] == "updated_time")
        assert time_filter["operator"] == "last_n_days"
        assert time_filter["values"] == [7]

        # Check count
        assert payload["count"] == 50

    @patch("requests.post")
    def test_get_alert(self, mock_post, alerts_service):
        """Test getting a specific alert by ID."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 1,
                "requestId": "test-request-3",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [
                {
                    "alert_id": "test-alert-123",
                    "severity": "critical",
                    "message": "Critical test alert",
                    "state": "Raised",
                }
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Get specific alert
        alert = alerts_service.get("test-alert-123")

        # Verify request
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        # Check filter for specific ID
        assert "filter" in payload
        id_filter = payload["filter"]["rules"][0]
        assert id_filter["property"] == "alert_id"
        assert id_filter["operator"] == "equals"
        assert id_filter["values"] == ["test-alert-123"]
        assert payload["count"] == 1

        # Verify result
        assert isinstance(alert, Alert)
        assert alert.id == "test-alert-123"
        assert alert.severity == "critical"

    @patch("requests.post")
    def test_get_statistics(self, mock_post, alerts_service):
        """Test getting alert statistics."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 3,
                "requestId": "test-request-4",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [
                {"severity": "high", "count": 5},
                {"severity": "medium", "count": 10},
                {"severity": "low", "count": 3},
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Get statistics
        alerts_service.get_statistics(time_range=30, group_by="severity")

        # Verify request
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        # Check properties
        props = payload["properties"]
        assert any(p["property"] == "severity" for p in props)
        assert any(p.get("function") == "distinct_count" for p in props)

        # Check filter
        time_filter = payload["filter"]["rules"][0]
        assert time_filter["operator"] == "last_n_days"
        assert time_filter["values"] == [30]

    @patch("requests.post")
    def test_get_timeline(self, mock_post, alerts_service):
        """Test getting alert timeline data."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 2,
                "requestId": "test-request-5",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [
                {"time": "2024-01-20T10:00:00Z", "count": 5},
                {"time": "2024-01-20T11:00:00Z", "count": 3},
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Get timeline
        alerts_service.get_timeline(time_range=7, interval="hour", status="Raised")

        # Verify request
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        # Check histogram
        assert "histogram" in payload
        histogram = payload["histogram"]
        assert histogram["property"] == "raised_time"
        assert histogram["range"] == "hour"
        assert histogram["enableEmptyInterval"] is True

    def test_create_not_supported(self, alerts_service):
        """Test that create raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Create operation is not supported"):
            alerts_service.create({})

    def test_update_not_supported(self, alerts_service):
        """Test that update raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Update operation is not supported"):
            alerts_service.update("id", {})

    def test_delete_not_supported(self, alerts_service):
        """Test that delete raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Delete operation is not supported"):
            alerts_service.delete("id")

    @patch("requests.post")
    def test_list_with_timestamp_filters(self, mock_post, alerts_service):
        """Test alert listing with timestamp start_time and end_time."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 0,
                "requestId": "test-request-timestamp",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call list with timestamp filters
        start_timestamp = 1705744800  # 2024-01-20 10:00:00
        end_timestamp = 1705748400  # 2024-01-20 11:00:00

        alerts_service.list(start_time=start_timestamp, end_time=end_timestamp)

        # Check payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        # Verify filters
        assert "filter" in payload
        filter_rules = payload["filter"]["rules"]

        # Check start time filter
        start_filter = next(
            r
            for r in filter_rules
            if r["property"] == "updated_time" and r["operator"] == "greater_or_equal"
        )
        assert start_filter["values"] == [start_timestamp]

        # Check end time filter
        end_filter = next(
            r
            for r in filter_rules
            if r["property"] == "updated_time" and r["operator"] == "less_or_equal"
        )
        assert end_filter["values"] == [end_timestamp]

    @patch("requests.post")
    def test_list_error_handling_with_dict(self, mock_post, alerts_service):
        """Test that list method handles exceptions when parsing alerts with dict data."""
        # Mock response with data that will trigger the exception handler
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 2,
                "requestId": "test-request-error",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [
                {
                    "alert_id": "valid-alert",
                    "severity": "high",
                    "message": "Valid alert",
                    "state": "Raised",
                },
                {
                    # Dict with required fields having None values
                    # This will fail Alert validation and trigger lines 157-158
                    "alert_id": None,
                    "severity": None,
                    "message": None,
                    "state": None,
                    "extra_field": "value",
                },
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Patch Alert to raise exception for None alert_id
        with patch("scm.config.insights.alerts.Alert") as mock_alert:
            # First call succeeds
            alert1 = Mock()
            alert1.id = "valid-alert"

            # Track calls
            results = []

            # Return alert for first call, then mock for second (after exception)
            def side_effect(**kwargs):
                if len(results) == 0:
                    results.append(alert1)
                    return alert1
                elif len(results) == 1:
                    # First attempt on second item - raise exception
                    results.append("exception")
                    raise ValueError("Test exception")
                else:
                    # Second attempt on second item (filtered) - return mock
                    mock_alert2 = Mock()
                    mock_alert2.id = "filtered"
                    results.append(mock_alert2)
                    return mock_alert2

            mock_alert.side_effect = side_effect

            # Call list - should handle exceptions gracefully
            alerts = alerts_service.list()

            # Should return 2 items
            assert len(alerts) == 2

            # First is the first alert
            assert alerts[0] == alert1

            # Second should be the result from filtered dict
            assert hasattr(alerts[1], "id")
            assert alerts[1].id == "filtered"

            # Verify Alert was called 3 times
            # 1. First item (success)
            # 2. Second item (exception)
            # 3. Second item with filtered data (success)
            assert mock_alert.call_count == 3

            # The third call should have filtered out None values
            third_call_kwargs = mock_alert.call_args_list[2][1]
            assert "alert_id" not in third_call_kwargs  # None values filtered out
            assert third_call_kwargs["extra_field"] == "value"

    @patch("requests.post")
    def test_list_error_handling_non_dict(self, mock_post, alerts_service):
        """Test list method when data contains non-dict items."""
        # We need to ensure InsightsResponse accepts the data first
        # So we'll patch it to allow non-dict items

        # Create a mock InsightsResponse that allows our test data
        mock_insights_response = Mock()
        mock_insights_response.data = [
            {"alert_id": "test-1", "severity": "high", "message": "Test", "state": "Raised"},
            "not a dict",  # This will trigger line 160
        ]

        with patch("scm.config.insights.InsightsResponse") as mock_resp_class:
            mock_resp_class.return_value = mock_insights_response

            # Mock the query method to return our mock response
            with patch.object(alerts_service, "query", return_value=mock_insights_response):
                # Call list method
                alerts = alerts_service.list()

                # Should have processed both items
                assert len(alerts) == 2

                # First should be an Alert object
                assert hasattr(alerts[0], "id")

                # Second should be the raw string (line 160)
                assert alerts[1] == "not a dict"

    @patch("requests.post")
    def test_get_alert_not_found(self, mock_post, alerts_service):
        """Test getting an alert that doesn't exist."""
        # Mock empty response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 0,
                "requestId": "test-request-notfound",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Should raise ValueError
        with pytest.raises(ValueError, match="Alert with ID 'nonexistent-alert' not found"):
            alerts_service.get("nonexistent-alert")
