# tests/conftest.py

import os
from dotenv import load_dotenv
import pytest

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

    # Optionally, expose these variables to other fixtures or tests
    return {"client_id": client_id, "client_secret": client_secret, "tsg_id": tsg_id}
