# tests/test_address_groups.py

from scm.client import Scm
from scm.config.objects import AddressGroups
from scm.models import AddressGroup
from tests.factories import AddressGroupStaticFactory, AddressGroupDynamicFactory


def test_list_address_groups(load_env, mocker):
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
                "id": "a952ca48-9127-4012-be3b-71741ddd5767",
                "name": "DAG_test",
                "folder": "All",
                "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            },
            {
                "id": "54b2087b-b733-46d9-a0ff-fe9ee4bdcbac",
                "name": "Moishy_Test",
                "folder": "Shared",
                "description": "test",
                "dynamic": {"filter": "'Api test' or 'Hamuzim' and 'best-practice'"},
            },
            {
                "id": "b2a7a7a1-cb15-463d-88be-80729bb1be37",
                "name": "Moishy Api",
                "folder": "Shared",
                "description": "test",
                "static": ["shachar_test2"],
            },
            {
                "id": "78c37e81-6f08-4857-b12b-d63aa809c526",
                "name": "Sashas DNS Servers",
                "folder": "Shared",
                "dynamic": {"filter": "'Microsoft 365' and 'Hamuzim'"},
            },
            {
                "id": "dcf82c68-fcc6-407d-aecf-a7ba75bdb3ea",
                "name": "Moishy Api2",
                "folder": "Shared",
                "dynamic": {"filter": "'Microsoft 365' and 'Hamuzim' or 'Api test'"},
            },
            {
                "id": "3a63aa1f-6223-40ed-8c8b-6e55ed82b6f3",
                "name": "Block IP - Hamuzim",
                "folder": "Shared",
                "static": ["test_sasha"],
            },
            {
                "id": "36338efa-1ef7-4cad-a4b6-ea25976ac5a6",
                "name": "Block IP group - Created by XSOAR",
                "folder": "Shared",
                "static": ["80.66.75.36"],
            },
        ],
        "offset": 0,
        "total": 7,
        "limit": 200,
    }

    mocked_get = mocker.patch.object(api_client, "get", return_value=mock_response)

    # Create an instance of Addresses
    address_groups_client = AddressGroups(api_client)

    # Call the list method
    address_groups = address_groups_client.list(folder="All")

    # Assertions
    mocked_get.assert_called_once_with(
        "/config/objects/v1/address-groups", params={"folder": "All"}
    )
    assert isinstance(address_groups, list)
    assert isinstance(address_groups[0], AddressGroup)
    assert len(address_groups) == 7
    assert address_groups[0].name == "DAG_test"
    assert (
        address_groups[0].dynamic.filter
        == "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
    )
    assert address_groups[1].name == "Moishy_Test"
    assert address_groups[1].description == "test"

    assert address_groups[2].name == "Moishy Api"
    assert address_groups[2].folder == "Shared"
    assert address_groups[2].description == "test"
    assert address_groups[2].static == ["shachar_test2"]


def test_create_address_group_with_dynamic_filter(load_env, mocker):
    # Initialize the API client
    api_client = Scm(
        client_id=load_env["client_id"],
        client_secret=load_env["client_secret"],
        tsg_id=load_env["tsg_id"],
    )

    # Create an instance of AddressGroups
    address_groups_client = AddressGroups(api_client)

    # Create a test AddressGroup instance using Factory Boy
    test_address_group = AddressGroupDynamicFactory()

    # Mock the API client's post method
    mock_response = test_address_group.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID
    mocked_post = mocker.patch.object(
        api_client,
        "post",
        return_value=mock_response,
    )

    # Call the create method
    created_group = address_groups_client.create(
        test_address_group.model_dump(exclude_unset=True)
    )

    # Assertions
    mocked_post.assert_called_once_with(
        "/config/objects/v1/address-groups",
        json=test_address_group.model_dump(exclude_unset=True),
    )
    assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_group.name == test_address_group.name
    assert created_group.dynamic.filter == test_address_group.dynamic.filter
    assert created_group.folder == test_address_group.folder


def test_create_address_group_with_static_entries(load_env, mocker):
    # Initialize the API client
    api_client = Scm(
        client_id=load_env["client_id"],
        client_secret=load_env["client_secret"],
        tsg_id=load_env["tsg_id"],
    )

    # Create an instance of AddressGroups
    address_groups_client = AddressGroups(api_client)

    # Create a test AddressGroup instance using Factory Boy
    test_address_group = AddressGroupStaticFactory()

    # Mock the API client's post method
    mock_response = test_address_group.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID
    mocked_post = mocker.patch.object(
        api_client,
        "post",
        return_value=mock_response,
    )

    # Call the create method
    created_group = address_groups_client.create(
        test_address_group.model_dump(exclude_unset=True)
    )

    # Assertions
    mocked_post.assert_called_once_with(
        "/config/objects/v1/address-groups",
        json=test_address_group.model_dump(exclude_unset=True),
    )
    assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_group.name == test_address_group.name
    assert created_group.folder == test_address_group.folder
