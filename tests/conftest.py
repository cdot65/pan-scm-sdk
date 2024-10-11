# tests/conftest.py

import os
from dotenv import load_dotenv
import pytest
from unittest.mock import Mock

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    Pytest fixture to load environment variables from a .env file.
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
def mock_scm(mocker):
    """
    Fixture to mock the Scm class to prevent real API calls.
    """
    # Mock the Scm class in the scm.client module
    mock_scm_class = mocker.patch("scm.client.Scm")

    # Create a mock instance of Scm
    mock_scm_instance = Mock()
    mock_scm_class.return_value = mock_scm_instance

    return mock_scm_instance
