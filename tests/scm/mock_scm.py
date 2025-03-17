"""
Base mock implementation of the Scm client for testing.

This module provides a mock Scm class that can be used in tests to simulate
API responses without making actual API calls. It can be imported and used
in any test file that needs to mock the Scm client.
"""

from unittest.mock import MagicMock
from scm.client import Scm


class MockScm(MagicMock, Scm):
    """
    A mock implementation of the Scm client that inherits from both MagicMock and Scm.

    This allows the mock to pass isinstance(api_client, Scm) checks while still
    providing the mocking functionality of MagicMock.

    Example usage:

    ```python
    from tests.scm.mock_scm import MockScm

    # In your test setup
    def setUp(self):
        self.api_client = MockScm()
        self.service = YourService(self.api_client)

        # Configure mock responses
        self.api_client.get.return_value = {"your": "mock_data"}
    ```
    """

    def __init__(self, *args, **kwargs):
        MagicMock.__init__(self, *args, **kwargs)
        # Skip the Scm.__init__ since it would require real authentication credentials

        # Setup default mock behaviors
        self.oauth_client = MagicMock()
        self.oauth_client.is_expired = False
        self.get = MagicMock(return_value=None)
        self.post = MagicMock(return_value=None)
        self.put = MagicMock(return_value=None)
        self.delete = MagicMock(return_value=None)

        # Services cache
        self._services = {}
