"""
Integration tests for bandwidth allocations service.

These tests verify that the different components of the SDK
work together correctly to handle bandwidth allocations.
"""

from unittest.mock import MagicMock, patch

import pytest

from scm.client import ScmClient
from scm.models.deployment import BandwidthAllocationCreateModel, BandwidthAllocationResponseModel


@pytest.mark.integration
class TestBandwidthAllocationIntegration:
    """
    Integration tests for the bandwidth allocations service.

    These tests focus on the integration between the client, service,
    and models rather than the API interactions.
    """

    @pytest.fixture
    def mock_client(self):
        """Create a mocked API client."""
        with patch("scm.client.OAuth2Client") as MockOAuth2Client:
            # Set up mock OAuth client
            mock_oauth_client = MagicMock()
            mock_oauth_client.session = MagicMock()
            mock_oauth_client.is_expired = False
            MockOAuth2Client.return_value = mock_oauth_client

            # Create client with mocked auth
            client = ScmClient(
                client_id="test_client_id",
                client_secret="test_client_secret",
                tsg_id="test_tsg_id",
            )

            # Mock HTTP methods
            client.get = MagicMock()
            client.post = MagicMock()
            client.put = MagicMock()
            client.delete = MagicMock()

            # Clear the services cache to ensure lazy loading works correctly
            client._services = {}

            yield client

    def test_unified_client_access(self, mock_client):
        """Test that the unified client access pattern works for bandwidth allocations."""
        # Make sure _services is empty initially
        assert not mock_client._services, "services cache should be empty initially"

        # The client should provide access to the bandwidth_allocation service
        assert hasattr(mock_client, "bandwidth_allocation")

        # The service should be lazily loaded, so now it should be in _services
        assert "bandwidth_allocation" in mock_client._services

        # Access the service
        service = mock_client.bandwidth_allocation

        # The service should be cached
        assert mock_client._services["bandwidth_allocation"] == service

    def test_model_serialization_deserialization(self, mock_client):
        """Test that the models properly serialize and deserialize data."""
        # Create test data
        test_data = {
            "name": "test-region",
            "allocated_bandwidth": 100.5,
            "spn_name_list": ["spn1", "spn2"],
            "qos": {
                "enabled": True,
                "customized": True,
                "profile": "high-priority",
                "guaranteed_ratio": 0.8,
            },
        }

        # Create a model instance
        create_model = BandwidthAllocationCreateModel(**test_data)

        # Verify model values
        assert create_model.name == "test-region"
        assert create_model.allocated_bandwidth == 100.5
        assert create_model.spn_name_list == ["spn1", "spn2"]
        assert create_model.qos.enabled is True
        assert create_model.qos.profile == "high-priority"

        # Serialize model to dict
        serialized = create_model.model_dump(exclude_unset=True)

        # Verify serialized data
        assert serialized["name"] == "test-region"
        assert serialized["allocated_bandwidth"] == 100.5
        assert serialized["spn_name_list"] == ["spn1", "spn2"]
        assert serialized["qos"]["enabled"] is True

        # Deserialize to response model
        response_model = BandwidthAllocationResponseModel(**serialized)

        # Verify response model
        assert response_model.name == "test-region"
        assert response_model.allocated_bandwidth == 100.5
        assert response_model.spn_name_list == ["spn1", "spn2"]
        assert response_model.qos.enabled is True

    def test_client_service_model_integration(self, mock_client):
        """Test the integration between client, service, and models."""
        # Set up test data
        test_data = {
            "name": "integration-test-region",
            "allocated_bandwidth": 150,
            "spn_name_list": ["spn1", "spn2"],
        }

        # Mock API response
        mock_client.post.return_value = test_data

        # Use the service to create an allocation
        service = mock_client.bandwidth_allocation
        result = service.create(test_data)

        # Verify client was called with correct parameters
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args[0]
        assert call_args[0] == "/config/deployment/v1/bandwidth-allocations"

        # Verify result is a model instance
        assert isinstance(result, BandwidthAllocationResponseModel)
        assert result.name == "integration-test-region"
        assert result.allocated_bandwidth == 150
        assert result.spn_name_list == ["spn1", "spn2"]

    def test_update_workflow(self, mock_client):
        """Test the entire update workflow from model creation to API call."""
        # Initial test data
        initial_data = {
            "name": "update-test-region",
            "allocated_bandwidth": 100,
            "spn_name_list": ["spn1", "spn2"],
        }

        # Mock get/list API response for initial data
        mock_client.get.return_value = {
            "data": [initial_data],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }

        # Get the current allocation
        service = mock_client.bandwidth_allocation
        allocation = service.get("update-test-region")

        # Create update data from current allocation
        update_data = {
            "name": allocation.name,
            "allocated_bandwidth": allocation.allocated_bandwidth + 50,  # Increase by 50
            "spn_name_list": allocation.spn_name_list + ["spn3"],  # Add spn3
        }

        # Mock API response for update
        mock_client.put.return_value = {
            "name": update_data["name"],
            "allocated_bandwidth": update_data["allocated_bandwidth"],
            "spn_name_list": update_data["spn_name_list"],
        }

        # Update the allocation
        updated = service.update(update_data)

        # Verify client was called with correct parameters
        mock_client.put.assert_called_once()

        # Verify the update was successful
        assert updated.allocated_bandwidth == 150
        assert "spn3" in updated.spn_name_list
        assert len(updated.spn_name_list) == 3

    def test_list_filter_workflow(self, mock_client):
        """Test the list and filter workflow with pagination."""
        # Set up service with a small max_limit to force pagination
        service = mock_client.bandwidth_allocation
        service.max_limit = 2

        # Mock API responses for pagination
        # We need to provide enough responses for all the API calls
        responses = [
            # First page - initial list call
            {
                "data": [
                    {
                        "name": "region1",
                        "allocated_bandwidth": 100,
                        "spn_name_list": ["spn1", "spn2"],
                    },
                    {
                        "name": "region2",
                        "allocated_bandwidth": 200,
                        "spn_name_list": ["spn3", "spn4"],
                    },
                ],
                "limit": 2,
                "offset": 0,
                "total": 4,
            },
            # Second page - second list call
            {
                "data": [
                    {
                        "name": "region3",
                        "allocated_bandwidth": 300,
                        "spn_name_list": ["spn5", "spn6"],
                    },
                    {
                        "name": "region4",
                        "allocated_bandwidth": 400,
                        "spn_name_list": ["spn7", "spn8"],
                    },
                ],
                "limit": 2,
                "offset": 2,
                "total": 4,
            },
            # No more data - third list call returns empty
            {"data": [], "limit": 2, "offset": 4, "total": 4},
        ]

        # Configure the mock to return our predefined responses
        mock_client.get.side_effect = responses

        # List all allocations
        all_allocations = service.list()

        # Verify we got all allocations from both pages
        assert len(all_allocations) == 4
        assert all_allocations[0].name == "region1"
        assert all_allocations[1].name == "region2"
        assert all_allocations[2].name == "region3"
        assert all_allocations[3].name == "region4"

        # Verify client was called for each page
        assert mock_client.get.call_count == 3  # First page, second page, and third (empty) page

        # Reset mock for next test
        mock_client.get.reset_mock()

        # Important: Clear the side_effect to prevent StopIteration error
        mock_client.get.side_effect = None

        # Mock response for filtering
        mock_client.get.return_value = {
            "data": [
                {"name": "region1", "allocated_bandwidth": 100, "spn_name_list": ["spn1", "spn2"]},
                {"name": "region2", "allocated_bandwidth": 200, "spn_name_list": ["spn3", "spn4"]},
                {"name": "region3", "allocated_bandwidth": 300, "spn_name_list": ["spn5", "spn6"]},
                {"name": "region4", "allocated_bandwidth": 400, "spn_name_list": ["spn7", "spn8"]},
            ],
            "limit": 200,
            "offset": 0,
            "total": 4,
        }

        # Reset max_limit to default
        service.max_limit = 200

        # Test filtering by allocated_bandwidth
        filtered = service.list(allocated_bandwidth=300)

        # Verify filter worked correctly
        assert len(filtered) == 1
        assert filtered[0].name == "region3"
        assert filtered[0].allocated_bandwidth == 300


if __name__ == "__main__":
    pytest.main(["-v", "test_bandwidth_allocations_integration.py"])
