# tests/test_addresses.py
import uuid

import pytest

from scm.config.objects import Address
from scm.exceptions import ValidationError
from scm.models.objects import AddressResponseModel, AddressRequestModel
from tests.factories import AddressFactory
from unittest.mock import MagicMock


def test_list_addresses(load_env, mock_scm):
    """
    Test for listing addresses.
    """
    # Mock the API client's get method to prevent from making real API calls
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

    # Configure the mock_scm.get method to return the mock_response
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Address with the mocked Scm
    addresses_client = Address(mock_scm)

    # Call the list method
    addresses = addresses_client.list(folder="MainFolder")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/addresses", params={"folder": "MainFolder"}
    )
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], AddressResponseModel)
    assert len(addresses) == 2
    assert addresses[0].name == "Address1"
    assert addresses[1].ip_netmask == "192.168.1.2/32"


def test_create_addresses(load_env, mock_scm):
    # Create a test AddressRequestModel instance using Factory Boy
    test_address = AddressFactory()

    # Mock the API client's post method
    mock_response = test_address.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID

    # Configure the mock_scm.post method to return the mock_response
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of Address with the mocked Scm
    address_client = Address(mock_scm)

    # Call the create method
    created_address = address_client.create(test_address.model_dump(exclude_unset=True))

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/objects/v1/addresses",
        json=test_address.model_dump(exclude_unset=True),
    )
    assert created_address.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_address.name == test_address.name
    assert created_address.description == test_address.description
    assert created_address.ip_netmask == test_address.ip_netmask
    assert created_address.folder == test_address.folder


def test_get_address(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "id": "123e4567-e89b-12d3-a456-426655440000",
        "name": "TestAddress",
        "folder": "Shared",
        "description": "A test address",
        "ip_netmask": "192.168.1.1/32",
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Address with the mocked Scm
    address_client = Address(mock_scm)

    # Call the get method
    address_id = "123e4567-e89b-12d3-a456-426655440000"
    address = address_client.get(address_id)

    # Assertions
    mock_scm.get.assert_called_once_with(f"/config/objects/v1/addresses/{address_id}")
    assert isinstance(address, AddressResponseModel)
    assert address.id == address_id
    assert address.name == "TestAddress"
    assert address.ip_netmask == "192.168.1.1/32"


def test_update_address(load_env, mock_scm):
    # Mock the API client's put method
    mock_response = {
        "id": "123e4567-e89b-12d3-a456-426655440000",
        "name": "UpdatedAddress",
        "folder": "Shared",
        "description": "An updated address",
        "ip_netmask": "192.168.1.2/32",
    }
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of Address with the mocked Scm
    address_client = Address(mock_scm)

    # Prepare data for update
    address_id = "123e4567-e89b-12d3-a456-426655440000"
    update_data = {
        "name": "UpdatedAddress",
        "folder": "Shared",
        "description": "An updated address",
        "ip_netmask": "192.168.1.2/32",
    }

    # Call the update method
    updated_address = address_client.update(address_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/objects/v1/addresses/{address_id}",
        json=update_data,
    )
    assert isinstance(updated_address, AddressResponseModel)
    assert updated_address.id == address_id
    assert updated_address.name == "UpdatedAddress"
    assert updated_address.ip_netmask == "192.168.1.2/32"


def test_address_list_validation_error(load_env, mock_scm):
    # Create an instance of Address with the mocked Scm
    address_client = Address(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(ValidationError) as exc_info:
        address_client.list(folder="Shared", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_address_list_with_filters(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "id": "123e4567-e89b-12d3-a456-426655440000",
                "name": "Address1",
                "folder": "Shared",
                "ip_netmask": "192.168.1.1/32",
            },
            {
                "id": "123e4567-e89b-12d3-a456-426655440001",
                "name": "Address2",
                "folder": "Shared",
                "ip_netmask": "192.168.1.2/32",
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Address with the mocked Scm
    address_client = Address(mock_scm)

    # Call the list method with filters
    filters = {
        "folder": "Shared",
        "names": ["Address1", "Address2"],
        "tags": ["Tag1", "Tag2"],
    }
    addresses = address_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "name": "Address1,Address2",
        "tag": "Tag1,Tag2",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/addresses",
        params=expected_params,
    )
    assert len(addresses) == 2


def test_address_list_with_types_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "id": "12345678-1234-5678-1234-567812345678",
                "name": "Address1",
                "folder": "Shared",
                "type": "ip-netmask",
                "ip_netmask": "192.168.1.1/32",
            },
            {
                "id": "12345678-1234-5678-1234-567812345679",
                "name": "Address2",
                "folder": "Shared",
                "type": "fqdn",
                "fqdn": "example.com",
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Address with the mocked Scm
    address_client = Address(mock_scm)

    # Call the list method with 'types' filter
    filters = {
        "folder": "Shared",
        "types": ["ip-netmask", "fqdn"],
    }
    addresses = address_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "type": "ip-netmask,fqdn",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/addresses",
        params=expected_params,
    )
    assert len(addresses) == 2


def test_address_list_with_values_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "id": "12345678-1234-5678-1234-567812345678",
                "name": "Address1",
                "folder": "Shared",
                "ip_netmask": "192.168.1.1/32",
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Address with the mocked Scm
    address_client = Address(mock_scm)

    # Call the list method with 'values' filter
    filters = {
        "folder": "Shared",
        "values": ["192.168.1.1/32"],
    }
    addresses = address_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "value": "192.168.1.1/32",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/addresses",
        params=expected_params,
    )
    assert len(addresses) == 1


def test_address_request_model_invalid_uuid():
    # Invalid UUID
    invalid_data = {
        "id": "invalid-uuid",
        "name": "TestAddress",
        "ip_netmask": "192.168.1.1/32",
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**invalid_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_address_request_model_no_address_type_provided():
    data = {
        "name": "TestAddress",
        "folder": "Shared",
        # No address type provided
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**data)
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )


def test_address_request_model_multiple_address_types_provided():
    data = {
        "name": "TestAddress",
        "folder": "Shared",
        "ip_netmask": "192.168.1.1/32",
        "fqdn": "example.com",
        # Multiple address types provided
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**data)
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )


def test_address_request_model_no_container_provided():
    data = {
        "name": "TestAddress",
        "ip_netmask": "192.168.1.1/32",
        # No container provided
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_address_request_model_multiple_containers_provided():
    data = {
        "name": "TestAddress",
        "ip_netmask": "192.168.1.1/32",
        "folder": "Shared",
        "device": "Device1",
        # Multiple containers provided
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_address_response_model_invalid_uuid():
    # Invalid UUID in response model
    invalid_data = {
        "id": "invalid-uuid",
        "name": "TestAddress",
        "ip_netmask": "192.168.1.1/32",
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressResponseModel(**invalid_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_address_request_model_with_device_container():
    # 'device' provided as the container
    data = {
        "name": "TestAddress",
        "ip_netmask": "192.168.1.1/32",
        "device": "Device1",
    }
    model = AddressRequestModel(**data)
    assert model.device == "Device1"


def test_address_request_model_multiple_containers_with_device():
    # Multiple containers including 'device' provided
    data = {
        "name": "TestAddress",
        "ip_netmask": "192.168.1.1/32",
        "folder": "Shared",
        "device": "Device1",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_address_request_model_validation():
    """
    Test validation in AddressRequestModel.
    """
    # Valid input with exactly one address type
    valid_data = {
        "name": "TestAddress",
        "ip_netmask": "192.168.1.1/24",
        "folder": "Shared",
    }
    address = AddressRequestModel(**valid_data)
    assert address.name == "TestAddress"
    assert address.ip_netmask == "192.168.1.1/24"

    # No address type provided
    invalid_data_no_address = {
        "name": "InvalidAddress",
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**invalid_data_no_address)
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )

    # Multiple address types provided
    invalid_data_multiple_addresses = {
        "name": "InvalidAddress",
        "ip_netmask": "192.168.1.1/24",
        "fqdn": "example.com",
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**invalid_data_multiple_addresses)
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )

    # Test each address type individually
    address_types = ["ip_netmask", "ip_range", "ip_wildcard", "fqdn"]
    for address_type in address_types:
        valid_data = {
            "name": f"TestAddress_{address_type}",
            address_type: "test_value",
            "folder": "Shared",
        }
        address = AddressRequestModel(**valid_data)
        assert getattr(address, address_type) == "test_value"

    # Test valid UUID
    valid_uuid = str(uuid.uuid4())
    valid_uuid_data = {
        "id": valid_uuid,
        "name": "ValidUUIDAddress",
        "ip_netmask": "192.168.1.1/24",
        "folder": "Shared",
    }
    address = AddressResponseModel(**valid_uuid_data)
    assert address.id == valid_uuid

    # Test invalid UUID
    invalid_uuid_data = {
        "id": "invalid-uuid",
        "name": "InvalidUUIDAddress",
        "ip_netmask": "192.168.1.1/24",
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(**invalid_uuid_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)

    # Test with None UUID
    none_uuid_data = {
        "id": None,
        "name": "NoneUUIDAddress",
        "ip_netmask": "192.168.1.1/24",
        "folder": "Shared",
    }
    address = AddressResponseModel(**none_uuid_data)
    assert address.id is None

    # Test without UUID field
    no_uuid_data = {
        "name": "NoUUIDAddress",
        "ip_netmask": "192.168.1.1/24",
        "folder": "Shared",
    }
    address = AddressRequestModel(**no_uuid_data)
    assert not hasattr(address, "id")


def test_address_request_model_address_type_validation():
    """
    Test the custom validator for address type in AddressRequestModel.
    """
    # Test with no address type provided
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(name="TestAddress", folder="Shared")
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )

    # Test with multiple address types provided
    with pytest.raises(ValueError) as exc_info:
        AddressRequestModel(
            name="TestAddress",
            folder="Shared",
            ip_netmask="192.168.1.1/24",
            fqdn="example.com",
        )
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )

    # Test with each valid address type
    valid_address_types = {
        "ip_netmask": "192.168.1.1/24",
        "ip_range": "192.168.1.1-192.168.1.10",
        "ip_wildcard": "192.168.1.0/0.0.0.255",
        "fqdn": "example.com",
    }

    for address_type, value in valid_address_types.items():
        valid_data = {
            "name": f"TestAddress_{address_type}",
            "folder": "Shared",
            address_type: value,
        }
        model = AddressRequestModel(**valid_data)
        assert getattr(model, address_type) == value
