"""Tests for the MockScm class.

This module tests that the MockScm class properly inherits from both MagicMock and Scm,
and that it can be used to mock API responses.
"""

import unittest
from unittest.mock import MagicMock

from scm.client import Scm
from scm.config import BaseObject
from tests.scm.mock_scm import MockScm


class TestMockScm(unittest.TestCase):
    """Test the MockScm class."""

    def test_isinstance_check(self):
        """Test that MockScm passes the isinstance check."""
        # Create a MockScm instance
        mock_scm = MockScm()

        # Verify it's an instance of both MagicMock and Scm
        self.assertIsInstance(mock_scm, MagicMock)
        self.assertIsInstance(mock_scm, Scm)

        # Define a test class that inherits from BaseObject
        class TestObject(BaseObject):
            """A simple test object that uses the BaseObject class."""

            ENDPOINT = "/test/endpoint"

        # Test that it can be used with a BaseObject subclass
        test_object = TestObject(mock_scm)
        self.assertIsNotNone(test_object)

    def test_mock_methods(self):
        """Test that MockScm methods can be mocked."""
        # Create a MockScm instance
        mock_scm = MockScm()

        # Configure mock responses
        mock_scm.get.return_value = {"data": "test"}
        mock_scm.post.return_value = {"created": "item"}

        # Verify the methods return the expected values
        self.assertEqual(mock_scm.get(), {"data": "test"})
        self.assertEqual(mock_scm.post(), {"created": "item"})

        # Call the methods with arguments
        result_get = mock_scm.get("/test", params={"id": "123"})
        result_post = mock_scm.post("/test", json={"name": "test"})

        # Verify the methods return the expected values
        self.assertEqual(result_get, {"data": "test"})
        self.assertEqual(result_post, {"created": "item"})

        # Verify the methods were called with the expected arguments
        mock_scm.get.assert_called_with("/test", params={"id": "123"})
        mock_scm.post.assert_called_with("/test", json={"name": "test"})

    def test_oauth_client(self):
        """Test that the oauth_client is a MagicMock."""
        # Create a MockScm instance
        mock_scm = MockScm()

        # Verify oauth_client is a MagicMock
        self.assertIsInstance(mock_scm.oauth_client, MagicMock)

        # Verify oauth_client.is_expired is False by default
        self.assertFalse(mock_scm.oauth_client.is_expired)

        # Configure is_expired
        mock_scm.oauth_client.is_expired = True

        # Verify the change
        self.assertTrue(mock_scm.oauth_client.is_expired)


if __name__ == "__main__":
    unittest.main()
