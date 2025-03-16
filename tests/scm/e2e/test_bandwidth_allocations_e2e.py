"""
End-to-end tests for bandwidth allocations service.

These tests verify that the bandwidth allocations service properly
interacts with the SCM API to perform CRUD operations.
"""

import os
import unittest
import pytest
from unittest.mock import patch

from scm.client import ScmClient
from scm.config.deployment import BandwidthAllocations
from scm.models.deployment import (
    BandwidthAllocationCreateModel,
    BandwidthAllocationResponseModel,
    BandwidthAllocationListResponseModel,
)
from tests.scm.mock_scm import MockScm


@pytest.mark.e2e
class TestBandwidthAllocationsE2E(unittest.TestCase):
    """
    End-to-end tests for bandwidth allocations service.
    
    These tests are designed to validate the complete CRUD cycle using mocked API responses.
    This ensures that the service properly interacts with its models and handles API responses.
    """
    
    def setUp(self):
        """Set up the test environment."""
        # Create a mock API client that inherits from Scm
        self.api_client = MockScm()
        
        # Create the service
        self.service = BandwidthAllocations(self.api_client)
        
        # Set up test data
        self.test_create_data = {
            "name": "test-region-e2e",
            "allocated_bandwidth": 150.5,
            "spn_name_list": ["spn1", "spn2"],
            "qos": {
                "enabled": True,
                "customized": True,
                "profile": "high-priority",
                "guaranteed_ratio": 0.7
            }
        }
        
        self.test_update_data = {
            "name": "test-region-e2e",
            "allocated_bandwidth": 200.0,
            "spn_name_list": ["spn1", "spn2", "spn3"],
            "qos": {
                "enabled": True,
                "customized": False,
                "profile": "standard",
                "guaranteed_ratio": 0.5
            }
        }
        
        self.test_mock_response = {
            "name": "test-region-e2e",
            "allocated_bandwidth": 150.5,
            "spn_name_list": ["spn1", "spn2"],
            "qos": {
                "enabled": True,
                "customized": True,
                "profile": "high-priority",
                "guaranteed_ratio": 0.7
            }
        }
        
        self.test_list_response = {
            "data": [
                self.test_mock_response,
                {
                    "name": "another-region",
                    "allocated_bandwidth": 100.0,
                    "spn_name_list": ["spn3", "spn4"]
                }
            ],
            "limit": 200,
            "offset": 0,
            "total": 2
        }

    def test_e2e_create_bandwidth_allocation(self):
        """Test creating a bandwidth allocation."""
        # Mock the API response
        self.api_client.post.return_value = self.test_mock_response
        
        # Call the create method
        result = self.service.create(self.test_create_data)
        
        # Verify the API client was called with the correct parameters
        self.api_client.post.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            json=self.test_create_data
        )
        
        # Verify the result is a model instance with the expected values
        self.assertIsInstance(result, BandwidthAllocationResponseModel)
        self.assertEqual(result.name, "test-region-e2e")
        self.assertEqual(result.allocated_bandwidth, 150.5)
        self.assertEqual(result.spn_name_list, ["spn1", "spn2"])
        self.assertEqual(result.qos.enabled, True)
        self.assertEqual(result.qos.profile, "high-priority")
        self.assertEqual(result.qos.guaranteed_ratio, 0.7)

    def test_e2e_update_bandwidth_allocation(self):
        """Test updating a bandwidth allocation."""
        # Mock the updated API response
        updated_response = {
            "name": "test-region-e2e",
            "allocated_bandwidth": 200.0,
            "spn_name_list": ["spn1", "spn2", "spn3"],
            "qos": {
                "enabled": True,
                "customized": False,
                "profile": "standard",
                "guaranteed_ratio": 0.5
            }
        }
        self.api_client.put.return_value = updated_response
        
        # Call the update method
        result = self.service.update(self.test_update_data)
        
        # Verify the API client was called with the correct parameters
        self.api_client.put.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            json=self.test_update_data
        )
        
        # Verify the result is a model instance with the expected values
        self.assertIsInstance(result, BandwidthAllocationResponseModel)
        self.assertEqual(result.name, "test-region-e2e")
        self.assertEqual(result.allocated_bandwidth, 200.0)
        self.assertEqual(result.spn_name_list, ["spn1", "spn2", "spn3"])
        self.assertEqual(result.qos.enabled, True)
        self.assertEqual(result.qos.customized, False)
        self.assertEqual(result.qos.profile, "standard")
        self.assertEqual(result.qos.guaranteed_ratio, 0.5)

    def test_e2e_list_bandwidth_allocations(self):
        """Test listing bandwidth allocations."""
        # Mock the API response
        self.api_client.get.return_value = self.test_list_response
        
        # Call the list method
        result = self.service.list()
        
        # Verify the API client was called with the correct parameters
        self.api_client.get.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={
                "limit": 200,
                "offset": 0,
            }
        )
        
        # Verify the result is a list of model instances
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], BandwidthAllocationResponseModel)
        self.assertEqual(result[0].name, "test-region-e2e")
        self.assertIsInstance(result[1], BandwidthAllocationResponseModel)
        self.assertEqual(result[1].name, "another-region")

    def test_e2e_get_bandwidth_allocation(self):
        """Test getting a bandwidth allocation by name."""
        # Mock the API response
        self.api_client.get.return_value = {
            "data": [self.test_mock_response],
            "limit": 200,
            "offset": 0,
            "total": 1
        }
        
        # Call the get method
        result = self.service.get("test-region-e2e")
        
        # Verify the API client was called with the correct parameters
        self.api_client.get.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={"name": "test-region-e2e"}
        )
        
        # Verify the result is a model instance with the expected values
        self.assertIsInstance(result, BandwidthAllocationResponseModel)
        self.assertEqual(result.name, "test-region-e2e")
        self.assertEqual(result.allocated_bandwidth, 150.5)
        self.assertEqual(result.spn_name_list, ["spn1", "spn2"])

    def test_e2e_get_nonexistent_bandwidth_allocation(self):
        """Test getting a nonexistent bandwidth allocation."""
        # Mock the API response
        self.api_client.get.return_value = {
            "data": [],
            "limit": 200,
            "offset": 0,
            "total": 0
        }
        
        # Call the get method
        result = self.service.get("nonexistent-region")
        
        # Verify the result is None
        self.assertIsNone(result)

    def test_e2e_fetch_bandwidth_allocation(self):
        """Test fetching a bandwidth allocation by name."""
        # Mock the API response
        self.api_client.get.return_value = {
            "data": [self.test_mock_response],
            "limit": 200,
            "offset": 0,
            "total": 1
        }
        
        # Call the fetch method
        result = self.service.fetch("test-region-e2e")
        
        # Verify the API client was called with the correct parameters
        self.api_client.get.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={"name": "test-region-e2e"}
        )
        
        # Verify the result is a model instance with the expected values
        self.assertIsInstance(result, BandwidthAllocationResponseModel)
        self.assertEqual(result.name, "test-region-e2e")
        self.assertEqual(result.allocated_bandwidth, 150.5)
        self.assertEqual(result.spn_name_list, ["spn1", "spn2"])

    def test_e2e_delete_bandwidth_allocation(self):
        """Test deleting a bandwidth allocation."""
        # Call the delete method
        self.service.delete("test-region-e2e", "spn1,spn2")
        
        # Verify the API client was called with the correct parameters
        self.api_client.delete.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={
                "name": "test-region-e2e",
                "spn_name_list": "spn1,spn2"
            }
        )

    def test_e2e_filter_by_name(self):
        """Test filtering bandwidth allocations by name."""
        # Mock the API response
        self.api_client.get.return_value = self.test_list_response
        
        # Call the list method with name filter
        result = self.service.list(name="test-region-e2e")
        
        # Verify the result is filtered correctly
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "test-region-e2e")

    def test_e2e_filter_by_bandwidth(self):
        """Test filtering bandwidth allocations by allocated bandwidth."""
        # Mock the API response
        self.api_client.get.return_value = self.test_list_response
        
        # Call the list method with allocated_bandwidth filter
        result = self.service.list(allocated_bandwidth=100.0)
        
        # Verify the result is filtered correctly
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "another-region")

    def test_e2e_filter_by_spn_name(self):
        """Test filtering bandwidth allocations by SPN name."""
        # Mock the API response
        self.api_client.get.return_value = self.test_list_response
        
        # Call the list method with spn_name_list filter
        result = self.service.list(spn_name_list="spn1")
        
        # Verify the result is filtered correctly
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "test-region-e2e")
        
    def test_simulated_api_full_crud_cycle(self):
        """Simulate a complete CRUD cycle against the API."""
        # Define the region name for this test
        region_name = "test-region-e2e"
        
        # Configure mock responses for each stage of the test
        
        # Step 1: Create - Mock successful creation
        create_response = self.test_create_data.copy()
        self.api_client.post.return_value = create_response
        
        # Step 2: Get - Mock get after creation
        get_response_after_create = {
            "data": [self.test_create_data.copy()],
            "limit": 200,
            "offset": 0,
            "total": 1
        }
        
        # Step 3: Update - Mock successful update
        update_response = self.test_update_data.copy()
        self.api_client.put.return_value = update_response
        
        # Step 4: List - Mock list with our test item included
        list_response = {
            "data": [
                self.test_update_data.copy(),
                {
                    "name": "another-test-region",
                    "allocated_bandwidth": 300.0,
                    "spn_name_list": ["spn4", "spn5"]
                }
            ],
            "limit": 200,
            "offset": 0,
            "total": 2
        }
        
        # Step 5: Get after delete - Mock empty response
        get_response_after_delete = {
            "data": [],
            "limit": 200,
            "offset": 0,
            "total": 0
        }
        
        # Set up a side_effect to return different responses for subsequent get calls
        self.api_client.get.side_effect = [
            get_response_after_create,  # First get call
            list_response,             # List call
            list_response,             # Filtered list call
            get_response_after_delete  # Final get after delete
        ]
        
        # EXECUTION PHASE
        
        # Step 1: Create a bandwidth allocation
        created = self.service.create(self.test_create_data)
        self.assertEqual(created.name, region_name)
        self.assertEqual(created.allocated_bandwidth, 150.5)
        self.assertEqual(created.spn_name_list, ["spn1", "spn2"])
        
        # Verify post was called correctly
        self.api_client.post.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            json=self.test_create_data
        )
        
        # Step 2: Get the bandwidth allocation
        retrieved = self.service.get(region_name)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, region_name)
        
        # Verify get was called correctly
        self.assertEqual(self.api_client.get.call_count, 1)
        
        # Step 3: Update the bandwidth allocation
        updated = self.service.update(self.test_update_data)
        self.assertEqual(updated.name, region_name)
        self.assertEqual(updated.allocated_bandwidth, 200.0)
        self.assertEqual(updated.spn_name_list, ["spn1", "spn2", "spn3"])
        
        # Verify put was called correctly
        self.api_client.put.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            json=self.test_update_data
        )
        
        # Step 4: List the bandwidth allocations
        all_allocations = self.service.list()
        found = False
        for allocation in all_allocations:
            if allocation.name == region_name:
                found = True
                break
        self.assertTrue(found, "Created allocation not found in list")
        
        # Verify get was called for list
        self.assertEqual(self.api_client.get.call_count, 2)
        
        # Step 5: Filter the bandwidth allocations
        filtered = self.service.list(name=region_name)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].name, region_name)
        
        # Verify get was called for filtered list
        self.assertEqual(self.api_client.get.call_count, 3)
        
        # Step 6: Delete the bandwidth allocation
        spn_list = ",".join(self.test_update_data["spn_name_list"])
        self.service.delete(region_name, spn_list)
        
        # Verify delete was called correctly
        self.api_client.delete.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={
                "name": region_name,
                "spn_name_list": spn_list
            }
        )
        
        # Verify the deletion by checking get returns None
        deleted = self.service.get(region_name)
        self.assertIsNone(deleted, "Bandwidth allocation was not properly deleted")
        
        # Verify final get call
        self.assertEqual(self.api_client.get.call_count, 4)


if __name__ == "__main__":
    pytest.main(["-v", "test_bandwidth_allocations_e2e.py"])
