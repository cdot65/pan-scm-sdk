# tests/test_addresses.py

from scm.client import Scm
from scm.config.objects import Addresses
from scm.models.address import Address


def test_list_addresses(load_env, mocker):
    """
    Integration test for listing addresses.
    This test requires valid API credentials and a reachable API endpoint.
    """
    client_id = load_env["client_id"]
    client_secret = load_env["client_secret"]
    tsg_id = load_env["tsg_id"]

    # Initialize the API client
    api_client = Scm(client_id=client_id, client_secret=client_secret, tsg_id=tsg_id)

    # Mock the API client's get method if you don't want to make real API calls
    mock_response = {
        "data": [
            {
                "id": "123e4567-e89b-12d3-a456-426655440000",
                "name": "Address1",
                "ip_netmask": "192.168.1.1/32",
                "folder": "MainFolder",
            },
            {
                "id": "223e4567-e89b-12d3-a456-426655440001",
                "name": "Address2",
                "ip_netmask": "192.168.1.2/32",
                "folder": "MainFolder",
            },
        ]
    }

    mocked_get = mocker.patch.object(api_client, "get", return_value=mock_response)

    # Create an instance of Addresses
    addresses_client = Addresses(api_client)

    # Call the list method
    addresses = addresses_client.list(folder="MainFolder")

    # Assertions
    mocked_get.assert_called_once_with(
        "/config/objects/v1/addresses", params={"folder": "MainFolder"}
    )
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], Address)
    assert len(addresses) == 2
    assert addresses[0].name == "Address1"
    assert addresses[1].ip_netmask == "192.168.1.2/32"
