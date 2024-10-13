# tests/test_address_groups.py
import pytest

from scm.config.objects import AddressGroup
from scm.exceptions import ValidationError
from scm.models import AddressGroupResponseModel, AddressGroupRequestModel
from scm.models.address_group import DynamicFilter
from tests.factories import AddressGroupStaticFactory, AddressGroupDynamicFactory
from unittest.mock import MagicMock


def test_list_address_groups(load_env, mock_scm):
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

    # Mock the get method on the Scm instance
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroups with the mocked Scm
    address_groups_client = AddressGroups(mock_scm)

    # Call the list method
    address_groups = address_groups_client.list(folder="All")

    # Assertions
    mock_scm.get.assert_called_once_with(
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


def test_create_address_group_with_dynamic_filter(load_env, mock_scm):
    """
    Test creating an address group with a dynamic filter.
    """
    # Create a test AddressGroup instance using Factory Boy
    test_address_group = AddressGroupDynamicFactory()

    # Define the mock response for the post method
    mock_response = test_address_group.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID

    # Mock the get method on the Scm instance
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroups with the mocked Scm
    address_groups_client = AddressGroups(mock_scm)

    # Call the create method
    created_group = address_groups_client.create(
        test_address_group.model_dump(exclude_unset=True)
    )

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/objects/v1/address-groups",
        json=test_address_group.model_dump(exclude_unset=True),
    )
    assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_group.name == test_address_group.name
    assert created_group.dynamic.filter == test_address_group.dynamic.filter
    assert created_group.folder == test_address_group.folder


def test_create_address_group_with_static_entries(load_env, mock_scm):
    """
    Test creating an address group with static entries.
    """
    # Create a test AddressGroup instance using Factory Boy
    test_address_group = AddressGroupStaticFactory()

    # Define the mock response for the post method
    mock_response = test_address_group.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID

    # Configure the mock_scm.post method to return the mock_response
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroups with the mocked Scm
    address_groups_client = AddressGroups(mock_scm)

    # Call the create method
    created_group = address_groups_client.create(
        test_address_group.model_dump(exclude_unset=True)
    )

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/objects/v1/address-groups",
        json=test_address_group.model_dump(exclude_unset=True),
    )
    assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_group.name == test_address_group.name
    assert created_group.folder == test_address_group.folder


def test_get_address_group(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "id": "123e4567-e89b-12d3-a456-426655440000",
        "name": "TestGroup",
        "folder": "Shared",
        "description": "A test address group",
        "static": ["Address1", "Address2"],
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroup with the mocked Scm
    address_groups_client = AddressGroup(mock_scm)

    # Call the get method
    group_id = "123e4567-e89b-12d3-a456-426655440000"
    address_group = address_groups_client.get(group_id)

    # Assertions
    mock_scm.get.assert_called_once_with(
        f"/config/objects/v1/address-groups/{group_id}"
    )
    assert isinstance(address_group, AddressGroupResponseModel)
    assert address_group.id == group_id
    assert address_group.name == "TestGroup"
    assert address_group.description == "A test address group"
    assert address_group.static == ["Address1", "Address2"]


def test_update_address_group(load_env, mock_scm):
    # Mock the API client's put method
    mock_response = {
        "id": "123e4567-e89b-12d3-a456-426655440000",
        "name": "UpdatedGroup",
        "folder": "Shared",
        "description": "An updated address group",
        "static": ["Address3", "Address4"],
    }
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroup with the mocked Scm
    address_groups_client = AddressGroup(mock_scm)

    # Prepare data for update
    group_id = "123e4567-e89b-12d3-a456-426655440000"
    update_data = {
        "name": "UpdatedGroup",
        "folder": "Shared",
        "description": "An updated address group",
        "static": ["Address3", "Address4"],
    }

    # Call the update method
    updated_group = address_groups_client.update(group_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/objects/v1/address-groups/{group_id}",
        json=update_data,
    )
    assert isinstance(updated_group, AddressGroupResponseModel)
    assert updated_group.id == group_id
    assert updated_group.name == "UpdatedGroup"
    assert updated_group.description == "An updated address group"
    assert updated_group.static == ["Address3", "Address4"]


def test_address_group_list_validation_error(load_env, mock_scm):
    # Create an instance of AddressGroup with the mocked Scm
    address_groups_client = AddressGroup(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(ValidationError) as exc_info:
        address_groups_client.list(folder="Shared", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_address_group_list_with_filters(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "id": "12345678-1234-5678-1234-567812345678",
                "name": "Group1",
                "folder": "Shared",
                "static": ["Address1"],
            },
            {
                "id": "12345678-1234-5678-1234-567812345679",
                "name": "Group2",
                "folder": "Shared",
                "static": ["Address2"],
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroup with the mocked Scm
    address_groups_client = AddressGroup(mock_scm)

    # Call the list method with filters
    filters = {
        "folder": "Shared",
        "names": ["Group1", "Group2"],
        "tags": ["Tag1", "Tag2"],
    }
    address_groups = address_groups_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "name": "Group1,Group2",
        "tag": "Tag1,Tag2",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/address-groups",
        params=expected_params,
    )
    assert len(address_groups) == 2


def test_address_group_list_with_types_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "id": "12345678-1234-5678-1234-567812345678",
                "name": "DynamicGroup",
                "folder": "Shared",
                "type": "dynamic",
                "dynamic": {"filter": "'Tag1'"},
            },
            {
                "id": "12345678-1234-5678-1234-567812345679",
                "name": "StaticGroup",
                "folder": "Shared",
                "type": "static",
                "static": ["Address1"],
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroup with the mocked Scm
    address_groups_client = AddressGroup(mock_scm)

    # Call the list method with 'types' filter
    filters = {
        "folder": "Shared",
        "types": ["dynamic", "static"],
    }
    address_groups = address_groups_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "type": "dynamic,static",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/address-groups",
        params=expected_params,
    )
    assert len(address_groups) == 2


def test_address_group_list_with_values_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "id": "12345678-1234-5678-1234-567812345678",
                "name": "Group1",
                "folder": "Shared",
                "static": ["Address1", "Address2"],
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroup with the mocked Scm
    address_groups_client = AddressGroup(mock_scm)

    # Call the list method with 'values' filter
    filters = {
        "folder": "Shared",
        "values": ["Address1", "Address2"],
    }
    address_groups = address_groups_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "value": "Address1,Address2",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/address-groups",
        params=expected_params,
    )
    assert len(address_groups) == 1


def test_address_group_request_model_invalid_uuid():
    # Invalid UUID
    invalid_data = {
        "id": "invalid-uuid",
        "name": "TestGroup",
        "static": ["Address1"],
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressGroupRequestModel(**invalid_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_address_group_request_model_no_type_provided():
    # Neither 'static' nor 'dynamic' provided
    data = {
        "name": "TestGroup",
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressGroupRequestModel(**data)
    assert "Exactly one of 'static' or 'dynamic' must be provided." in str(
        exc_info.value
    )


def test_address_group_request_model_both_types_provided():
    # Both 'static' and 'dynamic' provided
    data = {
        "name": "TestGroup",
        "folder": "Shared",
        "static": ["Address1"],
        "dynamic": DynamicFilter(filter="'Tag1'"),
    }
    with pytest.raises(ValueError) as exc_info:
        AddressGroupRequestModel(**data)
    assert "Exactly one of 'static' or 'dynamic' must be provided." in str(
        exc_info.value
    )


def test_address_group_request_model_no_container_provided():
    # Neither 'folder', 'snippet', nor 'device' provided
    data = {
        "name": "TestGroup",
        "static": ["Address1"],
        # No container provided
    }
    with pytest.raises(ValueError) as exc_info:
        AddressGroupRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_address_group_request_model_multiple_containers_provided():
    # More than one of 'folder', 'snippet', 'device' provided
    data = {
        "name": "TestGroup",
        "static": ["Address1"],
        "folder": "Shared",
        "snippet": "Snippet1",
        # Multiple containers provided
    }
    with pytest.raises(ValueError) as exc_info:
        AddressGroupRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_address_group_response_model_invalid_uuid():
    # Invalid UUID in response model
    invalid_data = {
        "id": "invalid-uuid",
        "name": "TestGroup",
        "static": ["Address1"],
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressGroupResponseModel(**invalid_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_address_group_response_model_no_type_provided():
    # Neither 'static' nor 'dynamic' provided in response model
    data = {
        "id": "123e4567-e89b-12d3-a456-426655440000",
        "name": "TestGroup",
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressGroupResponseModel(**data)
    assert "Exactly one of 'static' or 'dynamic' must be provided." in str(
        exc_info.value
    )


def test_address_group_request_model_with_device_container():
    # 'device' provided as the container
    data = {
        "name": "TestGroup",
        "static": ["Address1"],
        "device": "Device1",
    }
    model = AddressGroupRequestModel(**data)
    assert model.device == "Device1"


def test_address_group_request_model_multiple_containers_with_device():
    # Multiple containers including 'device' provided
    data = {
        "name": "TestGroup",
        "static": ["Address1"],
        "snippet": "Snippet1",
        "device": "Device1",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressGroupRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )
