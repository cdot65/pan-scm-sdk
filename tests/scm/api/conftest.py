"""Fixtures for live API tests.

These fixtures create real SCM client connections using credentials from .env file.
Tests will be skipped if credentials are not configured.
"""

import os

from dotenv import load_dotenv
import pytest

from scm.client import Scm

# Load .env file
load_dotenv()


@pytest.fixture(scope="session")
def live_client():
    """Create a live SCM client using credentials from .env.

    Skips tests if credentials are not configured.

    Required environment variables:
        - CLIENT_ID: OAuth2 client ID
        - CLIENT_SECRET: OAuth2 client secret
        - TSG_ID: Tenant Service Group ID

    Returns:
        Scm: Authenticated SCM client instance.
    """
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    tsg_id = os.getenv("TSG_ID")

    if not all([client_id, client_secret, tsg_id]):
        pytest.skip(
            "SCM credentials not configured. "
            "Set CLIENT_ID, CLIENT_SECRET, and TSG_ID in .env file."
        )

    return Scm(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id,
    )


@pytest.fixture(scope="session")
def folder():
    """Default folder for most API tests."""
    return "Texas"


@pytest.fixture(scope="session")
def deployment_folder():
    """Folder for deployment-related API tests."""
    return "Remote Networks"


@pytest.fixture(scope="session")
def service_connections_folder():
    """Folder for service connections API tests."""
    return "Service Connections"
