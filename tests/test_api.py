# tests/test_api.py

import pytest
from scm.client import Scm

pytestmark = pytest.mark.api


def test_auth(load_env):
    client_id = load_env["client_id"]
    client_secret = load_env["client_secret"]
    tsg_id = load_env["tsg_id"]

    # Initialize the API client
    api_client = Scm(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id,
    )

    # Assertions
    assert api_client.session.access_token is not None
    assert isinstance(api_client.session.access_token, str)

    assert api_client.session.token is not None
    assert isinstance(api_client.session.access_token, str)
