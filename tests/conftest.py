# tests/conftest.py

import os
from dotenv import load_dotenv
import pytest
from unittest.mock import MagicMock, patch

from scm.client import Scm

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
def mock_scm():
    """
    Fixture to provide a mocked Scm instance with mocked OAuth2Client and session.
    """
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
