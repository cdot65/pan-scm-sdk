# tests/conftest.py

"""Configuration and fixtures for the test suite."""

import os
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv
import pytest

from scm.client import Scm

# Load environment variables from .env file
load_dotenv()


# Register custom markers
def pytest_configure(config):
    """Configure pytest with custom test markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions and classes in isolation"
    )
    config.addinivalue_line("markers", "integration: Tests how components work together")
    config.addinivalue_line("markers", "functional: Tests complete features from end to end")
    config.addinivalue_line("markers", "mock: Tests that simulate external dependencies")
    config.addinivalue_line(
        "markers", "parametrized: Tests that run the same test with different inputs"
    )
    config.addinivalue_line(
        "markers", "configuration: Tests verifying SDK behavior with different configurations"
    )
    config.addinivalue_line(
        "markers", "documentation: Tests ensuring examples in documentation work"
    )
    config.addinivalue_line("markers", "e2e: End-to-end tests that validate complete workflows")
    config.addinivalue_line(
        "markers", "real_api: Tests that interact with the real API (requires credentials)"
    )


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Pytest fixture to load environment variables from a .env file.

    This fixture is automatically used by all tests.
    """
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    tsg_id = os.getenv("TSG_ID")

    if not all([client_id, client_secret, tsg_id]):
        raise EnvironmentError(
            "Missing one or more required environment variables: CLIENT_ID, CLIENT_SECRET, TSG_ID"
        )

    return {"client_id": client_id, "client_secret": client_secret, "tsg_id": tsg_id}


@pytest.fixture
def mock_scm():
    """Fixture to provide a mocked Scm instance with mocked OAuth2Client and session."""
    with patch("scm.client.OAuth2Client") as MockOAuth2Client:
        mock_oauth2client_instance = MagicMock()
        mock_session = MagicMock()
        mock_oauth2client_instance.session = mock_session
        mock_oauth2client_instance.is_expired = False  # Default to not expired
        MockOAuth2Client.return_value = mock_oauth2client_instance

        scm = Scm(
            client_id="test_client_id",
            client_secret="test_client_secret",
            tsg_id="test_tsg_id",
        )
        yield scm  # Only yield the Scm instance
