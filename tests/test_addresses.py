# tests/test_addresses.py

from scm.client import Scm
from scm.config.objects import Addresses
from scm.models.address import Address
from tests.factories import AddressFactory


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


def test_create_addresses(load_env, mocker):
    # Initialize the API client
    api_client = Scm(
        client_id=load_env["client_id"],
        client_secret=load_env["client_secret"],
        tsg_id=load_env["tsg_id"],
    )

    # Create an instance of AddressGroups
    address_client = Addresses(api_client)

    # Create a test AddressGroup instance using Factory Boy
    test_address = AddressFactory()

    # Mock the API client's post method
    mock_response = test_address.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID
    mocked_post = mocker.patch.object(
        api_client,
        "post",
        return_value=mock_response,
    )

    # Call the create method
    created_group = address_client.create(test_address.model_dump(exclude_unset=True))

    # Assertions
    mocked_post.assert_called_once_with(
        "/config/objects/v1/addresses",
        json=test_address.model_dump(exclude_unset=True),
    )
    assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_group.name == test_address.name
    assert created_group.description == test_address.description
    assert created_group.ip_netmask == test_address.ip_netmask
    assert created_group.folder == test_address.folder
