# tests/test_addresses.py
import uuid

import pytest
from unittest.mock import MagicMock

from scm.config.objects import Address
from scm.exceptions import ValidationError
from scm.models.objects import AddressResponseModel, AddressRequestModel
from tests.factories import AddressFactory, AddressResponseFactory
from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestAddressBase:
    """Base class for Address tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.client = Address(self.mock_scm)


class TestAddressAPI(TestAddressBase):
    """Tests for Address API operations."""

    def test_list_addresses(self):
        """Test listing addresses."""
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

        self.mock_scm.get.return_value = mock_response
        addresses = self.client.list(folder="MainFolder")

        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/addresses", params={"folder": "MainFolder"}
        )
        assert isinstance(addresses, list)
        assert isinstance(addresses[0], AddressResponseModel)
        assert len(addresses) == 2
        assert addresses[0].name == "Address1"
        assert addresses[1].ip_netmask == "192.168.1.2/32"

    def test_create_address(self):
        """Test creating an address."""
        test_address = AddressFactory()
        mock_response = test_address.model_dump()
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.post.return_value = mock_response
        created_address = self.client.create(
            test_address.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/addresses",
            json=test_address.model_dump(exclude_unset=True),
        )
        assert created_address.id == "123e4567-e89b-12d3-a456-426655440000"
        assert created_address.name == test_address.name
        assert created_address.description == test_address.description
        assert created_address.ip_netmask == test_address.ip_netmask
        assert created_address.folder == test_address.folder

    def test_get_address(self):
        """Test retrieving an address by ID."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestAddress",
            "folder": "Shared",
            "description": "A test address",
            "ip_netmask": "192.168.1.1/32",
        }
        self.mock_scm.get.return_value = mock_response

        address_id = "123e4567-e89b-12d3-a456-426655440000"
        address = self.client.get(address_id)

        self.mock_scm.get.assert_called_once_with(
            f"/config/objects/v1/addresses/{address_id}"
        )
        assert isinstance(address, AddressResponseModel)
        assert address.id == address_id
        assert address.name == "TestAddress"
        assert address.ip_netmask == "192.168.1.1/32"

    def test_update_address(self):
        """Test updating an address."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedAddress",
            "folder": "Shared",
            "description": "An updated address",
            "ip_netmask": "192.168.1.2/32",
        }
        self.mock_scm.put.return_value = mock_response

        address_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = {
            "name": "UpdatedAddress",
            "folder": "Shared",
            "description": "An updated address",
            "ip_netmask": "192.168.1.2/32",
        }

        updated_address = self.client.update(address_id, update_data)

        self.mock_scm.put.assert_called_once_with(
            f"/config/objects/v1/addresses/{address_id}",
            json=update_data,
        )
        assert isinstance(updated_address, AddressResponseModel)
        assert updated_address.id == address_id
        assert updated_address.name == "UpdatedAddress"
        assert updated_address.ip_netmask == "192.168.1.2/32"


class TestAddressValidation(TestAddressBase):
    """Tests for Address validation."""

    def test_address_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_address_request_model_invalid_uuid(self):
        """Test validation for invalid UUID."""
        invalid_data = {
            "id": "invalid-uuid",
            "name": "TestAddress",
            "ip_netmask": "192.168.1.1/32",
            "folder": "Shared",
        }
        with pytest.raises(ValueError) as exc_info:
            AddressRequestModel(**invalid_data)
        assert "Invalid UUID format for 'id'" in str(exc_info.value)

    def test_address_request_model_no_address_type_provided(self):
        """Test validation when no address type is provided."""
        data = {
            "name": "TestAddress",
            "folder": "Shared",
        }
        with pytest.raises(ValueError) as exc_info:
            AddressRequestModel(**data)
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_address_request_model_multiple_address_types_provided(self):
        """Test validation when multiple address types are provided."""
        data = {
            "name": "TestAddress",
            "folder": "Shared",
            "ip_netmask": "192.168.1.1/32",
            "fqdn": "example.com",
        }
        with pytest.raises(ValueError) as exc_info:
            AddressRequestModel(**data)
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_address_request_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "TestAddress",
            "ip_netmask": "192.168.1.1/32",
        }
        with pytest.raises(ValueError) as exc_info:
            AddressRequestModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_address_request_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "TestAddress",
            "ip_netmask": "192.168.1.1/32",
            "folder": "Shared",
            "device": "Device1",
        }
        with pytest.raises(ValueError) as exc_info:
            AddressRequestModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestAddressFilters(TestAddressBase):
    """Tests for Address filtering functionality."""

    def test_address_list_with_filters(self):
        """Test listing addresses with filters."""
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
        self.mock_scm.get.return_value = mock_response

        filters = {
            "folder": "Shared",
            "names": ["Address1", "Address2"],
            "tags": ["Tag1", "Tag2"],
        }
        addresses = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "name": "Address1,Address2",
            "tag": "Tag1,Tag2",
        }
        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/addresses",
            params=expected_params,
        )
        assert len(addresses) == 2

    def test_address_list_with_types_filter(self):
        """Test listing addresses with types filter."""
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
        self.mock_scm.get.return_value = mock_response

        filters = {
            "folder": "Shared",
            "types": ["ip-netmask", "fqdn"],
        }
        addresses = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "type": "ip-netmask,fqdn",
        }
        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/addresses",
            params=expected_params,
        )
        assert len(addresses) == 2

    def test_address_list_with_values_filter(self):
        """Test listing addresses with values filter."""
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
        self.mock_scm.get.return_value = mock_response

        filters = {
            "folder": "Shared",
            "values": ["192.168.1.1/32"],
        }
        addresses = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "value": "192.168.1.1/32",
        }
        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/addresses",
            params=expected_params,
        )
        assert len(addresses) == 1


class TestAddressModels(TestAddressBase):
    """Tests for Address model validation and behavior."""

    def test_address_request_model_validation(self):
        """Test comprehensive validation in AddressRequestModel."""
        # Valid input with exactly one address type
        valid_data = {
            "name": "TestAddress",
            "ip_netmask": "192.168.1.1/24",
            "folder": "Shared",
        }
        address = AddressRequestModel(**valid_data)
        assert address.name == "TestAddress"
        assert address.ip_netmask == "192.168.1.1/24"

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

    def test_address_response_model_validation(self):
        """Test validation in AddressResponseModel."""
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


class TestAddressCustomValidators(TestAddressBase):
    """Tests for custom validators in Address models."""

    def test_uuid_validator_response_model(self):
        """Test the UUID validator for AddressResponseModel."""
        # Test cases for invalid UUIDs
        invalid_uuids = [
            "not-a-uuid",
            "123",
            "12345678-1234-1234-1234",  # Too short
            "12345678-1234-1234-1234-1234567890ab-extra",  # Too long
            "12345678x1234x1234x1234x1234567890ab",  # Invalid format
        ]

        for invalid_uuid in invalid_uuids:
            response_data = {
                "id": invalid_uuid,
                "name": "TestAddress",
                "ip_netmask": "192.168.1.1/32",
                "folder": "Shared",
            }
            with pytest.raises(ValueError) as exc_info:
                AddressResponseModel(**response_data)
            assert "Invalid UUID format for 'id'" in str(exc_info.value)

        # Test valid UUID formats
        valid_uuids = [
            "123e4567-e89b-12d3-a456-426655440000",
            "00000000-0000-0000-0000-000000000000",
            "ffffffff-ffff-ffff-ffff-ffffffffffff",
        ]

        for valid_uuid in valid_uuids:
            response_data = {
                "id": valid_uuid,
                "name": "TestAddress",
                "ip_netmask": "192.168.1.1/32",
                "folder": "Shared",
            }
            response_model = AddressResponseModel(**response_data)
            assert response_model.id == valid_uuid

        # Test with None value
        none_uuid_data = {
            "id": None,
            "name": "TestAddress",
            "ip_netmask": "192.168.1.1/32",
            "folder": "Shared",
        }
        response_model = AddressResponseModel(**none_uuid_data)
        assert response_model.id is None

        # Test without ID field
        no_uuid_data = {
            "name": "TestAddress",
            "ip_netmask": "192.168.1.1/32",
            "folder": "Shared",
        }
        response_model = AddressResponseModel(**no_uuid_data)
        assert (
            response_model.id is None
        )  # Response model should set id to None when not provided

    def test_request_model_has_no_id(self):
        """Test that AddressRequestModel does not accept an id field."""
        request_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",  # This should be ignored or raise an error
            "name": "TestAddress",
            "ip_netmask": "192.168.1.1/32",
            "folder": "Shared",
        }

        # The model should either ignore the id field or raise an error
        request_model = AddressRequestModel(**request_data)
        assert not hasattr(
            request_model, "id"
        ), "AddressRequestModel should not have an id field"


class TestSuite(
    TestAddressAPI,
    TestAddressValidation,
    TestAddressFilters,
    TestAddressModels,
    TestAddressCustomValidators,
):
    """Main test suite that combines all test classes."""

    pass
