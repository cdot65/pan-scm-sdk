"""Integration tests for bearer token authentication.

These tests require a valid bearer token in the SCM_ACCESS_TOKEN environment variable.
They are skipped by default and can be enabled by setting the SCM_RUN_INTEGRATION_TESTS
environment variable to 'true'.

To run these tests:
1. Get a valid access token for SCM
2. Set environment variables:
   export SCM_ACCESS_TOKEN="your_bearer_token"
   export SCM_RUN_INTEGRATION_TESTS="true"
3. Run pytest with the integration flag:
   pytest -xvs tests/scm/integration/test_bearer_token_integration.py
"""

import os
import unittest

import pytest

from scm.client import ScmClient
from scm.exceptions import APIError


@pytest.mark.integration
class TestBearerTokenIntegration(unittest.TestCase):
    """Integration tests for bearer token authentication."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        # Check if integration tests should be run
        cls.run_tests = os.environ.get("SCM_RUN_INTEGRATION_TESTS", "").lower() == "true"
        if not cls.run_tests:
            return

        # Get bearer token from environment
        cls.token = os.environ.get("SCM_ACCESS_TOKEN")
        if not cls.token:
            raise ValueError("SCM_ACCESS_TOKEN environment variable is required")

        # Initialize client
        cls.client = ScmClient(access_token=cls.token)

    def setUp(self):
        """Set up the test."""
        if not self.run_tests:
            self.skipTest("Integration tests disabled. Set SCM_RUN_INTEGRATION_TESTS=true to run.")

    def test_folder_list(self):
        """Test that folder listing works with bearer token."""
        folders = self.client.folder.list()
        self.assertIsNotNone(folders)
        self.assertIsInstance(folders, list)

        # Basic validation that we got folder objects
        if folders:
            folder = folders[0]
            self.assertTrue(hasattr(folder, "name"))
            self.assertTrue(hasattr(folder, "id"))

    def test_address_operations(self):
        """Test basic address operations with bearer token."""
        # Get first folder to use for testing
        folders = self.client.folder.list()
        if not folders:
            self.skipTest("No folders available for testing")

        folder_name = folders[0].name

        # List addresses in the folder
        addresses = self.client.address.list(folder=folder_name)
        self.assertIsNotNone(addresses)
        self.assertIsInstance(addresses, list)

        # Skip detailed testing if no addresses
        if not addresses:
            return

        # Get first address
        address = addresses[0]

        # Fetch specific address by name
        fetched = self.client.address.fetch(name=address.name, folder=folder_name)
        self.assertEqual(fetched.id, address.id)
        self.assertEqual(fetched.name, address.name)

    def test_error_handling(self):
        """Test error handling with bearer token."""
        # Try to access a non-existent folder
        with self.assertRaises(APIError):
            self.client.address.list(folder="non_existent_folder_12345")


if __name__ == "__main__":
    unittest.main()
