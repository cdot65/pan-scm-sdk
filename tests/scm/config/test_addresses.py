# tests/test_addresses.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import Address
from scm.exceptions import (
    ValidationError,
    APIError,
    ObjectNotPresentError,
    ReferenceNotZeroError,
    EmptyFieldError,
    ObjectAlreadyExistsError,
    MalformedRequestError,
    FolderNotFoundError,
)
from scm.models.objects import (
    AddressCreateModel,
    AddressResponseModel,
)

from tests.factories import (
    AddressCreateIpNetmaskFactory,
    AddressCreateFqdnFactory,
    AddressCreateIpRangeFactory,
    AddressCreateIpWildcardFactory,
)

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestAddressBase:
    """Base class for Address Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Address(self.mock_scm)  # noqa


class TestAddressAPI(TestAddressBase):
    """Tests for Address API operations."""

    # test to retrieve all instances of addresses
    def test_list_addresses(self):
        """
        **Objective:** Test listing all addresses.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing addresses.
            2. Calls the `list` method of `self.client` with a filter parameter (`folder="All"`).
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of addresses, checking their types and attributes.
        """
        mock_response = {
            "data": [
                {
                    "id": "cd7583dd-7efb-46e4-9eb8-a87437da3a0d",
                    "name": "Palo Alto Networks Sinkhole",
                    "folder": "All",
                    "snippet": "default",
                    "fqdn": "sinkhole.paloaltonetworks.com",
                    "description": "Palo Alto Networks sinkhole",
                },
                {
                    "id": "3fecfe58-af0c-472b-85cf-437bb6df2929",
                    "name": "dallas-desktop1",
                    "folder": "cdot65",
                    "snippet": "cdot.io Best Practices",
                    "ip_netmask": "10.5.0.11",
                    "description": "test123456",
                    "tag": ["Decrypted"],
                },
                {
                    "id": "c33fa16a-939a-4ac5-a45b-a9902f30752a",
                    "name": "dallas-desktop2",
                    "folder": "cdot65",
                    "snippet": "cdot.io Best Practices",
                    "description": "RHEL9 desktop",
                    "ip_netmask": "10.5.0.12",
                    "tag": ["Decrypted"],
                },
                {
                    "id": "a3754e04-919a-455a-8c87-09fb6fa6db63",
                    "name": "dallas-desktop3",
                    "folder": "cdot65",
                    "snippet": "cdot.io Best Practices",
                    "description": "Windows 11 Desktop",
                    "ip_netmask": "10.5.0.100",
                    "tag": ["Decrypted"],
                },
            ],
            "offset": 0,
            "total": 4,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        addresses = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            params={"folder": "All"},
        )
        assert isinstance(addresses, list)
        assert isinstance(addresses[0], AddressResponseModel)
        assert len(addresses) == 4
        assert addresses[0].name == "Palo Alto Networks Sinkhole"

    # tests to create all variations of addresses
    def test_create_address_of_type_ip_netmask(self):
        """
        **Objective:** Test creating an address object of type ip-netmask.
        **Workflow:**
            1. Uses `AddressCreateIpNetmaskFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the address data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created address group's attributes.
        """
        test_address_ip_netmask = AddressCreateIpNetmaskFactory()
        mock_response = test_address_ip_netmask.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_address_ip_netmask.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_address_ip_netmask.model_dump(exclude_unset=True),
        )
        assert created_group.id == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_address_ip_netmask.name
        assert created_group.ip_netmask == test_address_ip_netmask.ip_netmask
        assert created_group.folder == test_address_ip_netmask.folder

    def test_create_address_of_type_fdqn(self):
        """
        **Objective:** Test creating an address object of type fqdn.
        **Workflow:**
            1. Uses `AddressCreateFqdnFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the address data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created address group's attributes.
        """
        test_address_fqdn = AddressCreateFqdnFactory()
        mock_response = test_address_fqdn.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_address_fqdn.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_address_fqdn.model_dump(exclude_unset=True),
        )
        assert created_group.id == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_address_fqdn.name
        assert created_group.fqdn == test_address_fqdn.fqdn
        assert created_group.folder == test_address_fqdn.folder

    def test_create_address_of_type_ip_range(self):
        """
        **Objective:** Test creating an address object of type ip-range.
        **Workflow:**
            1. Uses `AddressCreateIpRangeFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the address data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created address group's attributes.
        """
        test_address_ip_range = AddressCreateIpRangeFactory()
        mock_response = test_address_ip_range.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_address_ip_range.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_address_ip_range.model_dump(exclude_unset=True),
        )
        assert created_group.id == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_address_ip_range.name
        assert created_group.ip_range == test_address_ip_range.ip_range
        assert created_group.folder == test_address_ip_range.folder

    def test_create_address_of_type_ip_wildcard(self):
        """
        **Objective:** Test creating an address object of type ip-wildcard.
        **Workflow:**
            1. Uses `AddressCreateIpWildcardFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the address data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created address group's attributes.
        """
        test_address_ip_wildcard = AddressCreateIpWildcardFactory()
        mock_response = test_address_ip_wildcard.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_address_ip_wildcard.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_address_ip_wildcard.model_dump(exclude_unset=True),
        )
        assert created_group.id == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_address_ip_wildcard.name
        assert created_group.ip_wildcard == test_address_ip_wildcard.ip_wildcard
        assert created_group.folder == test_address_ip_wildcard.folder

    # test to retrieve a specific address object by ID
    def test_get_address(self):
        """
        **Objective:** Test retrieving an address by its ID.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an address by ID.
            2. Calls the `get` method of `self.client` with a specific group ID.
            3. Asserts that the mocked service was called with the correct URL.
            4. Validates the returned address group's attributes.
        """
        address_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": address_id,
            "name": "dallas-desktop1",
            "snippet": "cdot.io Best Practices",
            "ip_netmask": "10.5.0.11",
            "description": "test123456",
            "tag": ["Decrypted"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        address = self.client.get(address_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{address_id}"
        )
        assert isinstance(address, AddressResponseModel)
        assert address.id == address_id
        assert address.name == "dallas-desktop1"
        assert address.description == "test123456"
        assert address.ip_netmask == "10.5.0.11"
        assert isinstance(address.tag, list)
        assert address.tag[0] == "Decrypted"

    # test the update method on an existing address object
    def test_update_address(self):
        """
        **Objective:** Test updating an existing object.
        **Workflow:**
            1. Sets up the update data for the object.
            2. Sets up a mock response that includes the updated data.
            3. Calls the `update` method of `self.client` with the update data.
            4. Asserts that the mocked service was called with the correct URL and data.
            5. Validates the updated object's attributes.
        """
        address_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = {
            "id": address_id,
            "name": "dallas-desktop1",
            "snippet": "cdot.io Best Practices",
            "ip_netmask": "10.5.0.11",
            "description": "test123456",
            "tag": ["Decrypted"],
        }

        mock_response = update_data.copy()

        self.mock_scm.put.return_value = mock_response  # noqa
        updated_address = self.client.update(update_data)

        # Prepare the expected payload by excluding 'id'
        expected_payload = update_data.copy()
        expected_payload.pop("id")

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{address_id}",
            json=expected_payload,
        )
        assert isinstance(updated_address, AddressResponseModel)
        assert updated_address.id == update_data["id"]
        assert updated_address.name == "dallas-desktop1"
        assert updated_address.description == "test123456"
        assert updated_address.tag[0] == "Decrypted"

    def test_fetch_address(self):
        """
        **Objective:** Test retrieving an object by its name using the `fetch` method.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an object by name.
            2. Calls the `fetch` method of `self.client` with a specific name and container.
            3. Asserts that the mocked service was called with the correct URL and parameters.
            4. Validates the returned object's attributes.
        """
        address_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": address_id,
            "name": "dallas-desktop1",
            "folder": "Texas",
            "ip_netmask": "10.5.0.11",
            "description": "test123456",
            "tag": ["Decrypted"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        address = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        # Validate the returned address
        assert isinstance(address, dict)
        assert address["id"] == mock_response["id"]
        assert address["name"] == mock_response["name"]
        assert address["description"] == mock_response["description"]
        assert address["tag"][0] == mock_response["tag"][0]

    # test exception types
    def test_fetch_address_not_found(self):
        """
        Test fetching an object by name that does not exist.

        **Objective:** Test that fetching a non-existent object raises NotFoundError.
        **Workflow:**
            1. Mocks the API response to return an empty 'data' list.
            2. Calls the `fetch` method with a name that does not exist.
            3. Asserts that NotFoundError is raised.
        """
        address_name = "NonExistent"
        folder_name = "Shared"
        mock_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Your configuration is not valid. Please review the error message for more details.",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "12282b0f-eace-41c3-a8e2-4b28992979c4",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method and expect a NotFoundError
        with pytest.raises(ObjectNotPresentError) as exc_info:  # noqa
            self.client.fetch(
                name=address_name,
                folder=folder_name,
            )

    def test_fetch_address_no_name(self):
        """
        Test fetching an address without providing the 'name' parameter.

        **Objective:** Ensure that the fetch method raises ValidationError when 'name' is not provided.
        **Workflow:**
            1. Calls the `fetch` method without the 'name' parameter.
            2. Asserts that ValidationError is raised.
        """
        folder_name = "Shared"
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(folder=folder_name, name="")
        assert str(exc_info.value) == "Field 'name' cannot be empty"

    def test_fetch_address_unexpected_response_format(self):
        """
        Test fetching an address group when the API returns an unexpected response format.

        **Objective:** Ensure that the fetch method raises APIError when the response format is not as expected.
        **Workflow:**
            1. Mocks the API response to return an unexpected format.
            2. Calls the `fetch` method.
            3. Asserts that APIError is raised.
        """
        group_name = "TestGroup"
        folder_name = "Shared"
        # Mocking an unexpected response format
        mock_response = {"unexpected_key": "unexpected_value"}
        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name=group_name, folder=folder_name)
        assert str(exc_info.value) == "Unexpected response format."

    def test_delete_referenced_object(self):
        """
        Test deleting an address that is referenced by other objects.

        **Objective:** Verify that attempting to delete an address that is referenced
        by other objects raises a ReferenceNotZeroError with proper reference details.

        **Workflow:**
            1. Sets up a mock error response for a referenced object deletion attempt
            2. Attempts to delete an address that is referenced by other objects
            3. Validates that ReferenceNotZeroError is raised with correct details
            4. Verifies the error contains proper reference information
        """
        address_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        # Mock the API error response
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Your configuration is not valid. Please review the error message for more details.",
                    "details": {
                        "errorType": "Reference Not Zero",
                        "message": [
                            " snippet -> cdot.io Best Practices -> address-group -> Developer Desktops -> static"
                        ],
                        "errors": [
                            {
                                "type": "NON_ZERO_REFS",
                                "message": "Node cannot be deleted because of references from",
                                "params": ["dallas-desktop1"],
                                "extra": [
                                    "snippet/[cdot.io Best Practices]/address-group/[Developer Desktops]/static/[dallas-desktop1]"
                                ],
                            }
                        ],
                    },
                }
            ],
            "_request_id": "8fe3b025-feb7-41d9-bf88-3938c0b33116",
        }

        # Configure mock to raise HTTPError with our custom error response
        self.mock_scm.delete.side_effect = Exception()  # noqa
        self.mock_scm.delete.side_effect.response = MagicMock()  # noqa
        self.mock_scm.delete.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        # Attempt to delete the address and expect ReferenceNotZeroError
        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(address_id)

        error = exc_info.value

        # Verify the error contains the expected information
        assert error.error_code == "API_I00013"
        assert "dallas-desktop1" in error.references
        assert any("cdot.io Best Practices" in path for path in error.reference_paths)
        assert "Cannot delete object due to existing references" in str(error)

        # Verify the delete method was called with correct endpoint
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{address_id}"
        )

        # Verify detailed error message includes reference path
        assert "Developer Desktops" in error.detailed_message
        assert "snippet/[cdot.io Best Practices]" in error.detailed_message


class TestAddressValidation(TestAddressBase):
    """Tests for Address validation."""

    def test_address_create_model_no_type_provided(self):
        """Test validation when no type is provided."""
        data = {
            "name": "Test123",
            "folder": "Shared",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "1 validation error for AddressCreateModel" in str(exc_info.value)
        assert (
            "Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_address_create_model_multiple_types_provided(self):
        """Test validation when multiple types are provided."""
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "fqdn": "test.com",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_address_create_model_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
        }
        model = AddressCreateModel(**data)
        assert model.name == "Test123"
        assert model.folder == "Shared"
        assert model.ip_netmask == "10.5.0.11"

    def test_address_create_model_invalid_container(self):
        """Test validation with multiple container types."""
        data = {
            "name": "Test123",
            "folder": "Shared",
            "snippet": "TestSnippet",
            "ip_netmask": "10.5.0.11",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_tag_string_to_list_conversion(self):
        """
        Test tag field validator converting a string to a list.

        **Objective:** Verify that a single string tag is properly converted to a list.
        **Workflow:**
            1. Creates an address with a single string tag
            2. Validates the tag is converted to a single-item list
        """
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "tag": "TestTag",
        }
        model = AddressCreateModel(**data)
        assert isinstance(model.tag, list)
        assert model.tag == ["TestTag"]

    def test_tag_list_passed_through(self):
        """
        Test tag field validator passing through a list.

        **Objective:** Verify that a list of tags is properly handled.
        **Workflow:**
            1. Creates an address with multiple tags as a list
            2. Validates the tags remain as a list
        """
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "tag": ["Tag1", "Tag2"],
        }
        model = AddressCreateModel(**data)
        assert isinstance(model.tag, list)
        assert model.tag == ["Tag1", "Tag2"]

    def test_tag_invalid_type(self):
        """
        Test tag field validator with invalid type.

        **Objective:** Verify that non-string/non-list tag values raise ValueError.
        **Workflow:**
            1. Attempts to create an address with an invalid tag type (dict)
            2. Validates that appropriate error is raised
        """
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "tag": {"invalid": "type"},
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_duplicate_items(self):
        """
        Test tag uniqueness validator.

        **Objective:** Verify that duplicate tags raise ValueError.
        **Workflow:**
            1. Attempts to create an address with duplicate tags
            2. Validates that appropriate error is raised
        """
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "tag": ["TestTag", "TestTag"],
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)

    def test_invalid_uuid_format(self):
        """
        Test UUID format validator.

        **Objective:** Verify that invalid UUID formats raise ValueError.
        **Workflow:**
            1. Attempts to create/update an address with invalid UUID
            2. Validates that appropriate error is raised
        """
        data = {
            "id": "not-a-uuid",
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressResponseModel(**data)
        assert "Invalid UUID format for 'id'" in str(exc_info.value)

    def test_valid_uuid_format(self):
        """
        Test valid UUID format.

        **Objective:** Verify that valid UUID formats are accepted.
        **Workflow:**
            1. Creates/updates an address with valid UUID
            2. Validates that the UUID is accepted
        """
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
        }
        model = AddressResponseModel(**data)
        assert model.id == "123e4567-e89b-12d3-a456-426655440000"

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = AddressCreateIpNetmaskFactory()

        # Mock error response
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Object creation failed",
                    "details": {"errorType": "Object Already Exists"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Configure mock to raise exception
        self.mock_scm.post.side_effect = Exception()  # noqa
        self.mock_scm.post.side_effect.response = MagicMock()  # noqa
        self.mock_scm.post.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(ObjectAlreadyExistsError):
            self.client.create(test_data.model_dump())

    def test_get_object_error_handling(self):
        """
        **Objective:** Test error handling during object retrieval.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to get an object
            3. Verifies proper error handling and exception raising
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Object not found",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.get.side_effect = Exception()  # noqa
        self.mock_scm.get.side_effect.response = MagicMock()  # noqa
        self.mock_scm.get.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.get(object_id)

    def test_update_object_error_handling(self):
        """
        **Objective:** Test error handling during object update.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to update an object
            3. Verifies proper error handling and exception raising
        """
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-address",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
        }

        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Update failed",
                    "details": {"errorType": "Malformed Command"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.put.side_effect = Exception()  # noqa
        self.mock_scm.put.side_effect.response = MagicMock()  # noqa
        self.mock_scm.put.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(MalformedRequestError):
            self.client.update(update_data)

    def test_list_empty_folder_error(self):
        """
        **Objective:** Test that empty folder raises appropriate error.
        **Workflow:**
            1. Attempts to list objects with empty folder
            2. Verifies EmptyFieldError is raised
        """
        with pytest.raises(EmptyFieldError) as exc_info:
            self.client.list(folder="")
        assert str(exc_info.value) == "Field 'folder' cannot be empty"

    def test_list_multiple_containers_error(self):
        """
        **Objective:** Test validation of container parameters.
        **Workflow:**
            1. Attempts to list with multiple containers
            2. Verifies ValidationError is raised
        """
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")
        assert (
            str(exc_info.value)
            == "Exactly one of 'folder', 'snippet', or 'device' must be provided."
        )

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        filters = {
            "types": ["type1", "type2"],
            "values": ["value1", "value2"],
            "names": ["name1", "name2"],
            "tags": ["tag1", "tag2"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            params={
                "folder": "Shared",
                "type": "type1,type2",
                "value": "value1,value2",
                "name": "name1,name2",
                "tag": "tag1,tag2",
            },
        )

    def test_list_error_handling(self):
        """
        **Objective:** Test error handling in list operation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to list objects
            3. Verifies proper error handling
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Listing failed",
                    "details": {"errorType": "Operation Impossible"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.get.side_effect = Exception()  # noqa
        self.mock_scm.get.side_effect.response = MagicMock()  # noqa
        self.mock_scm.get.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(FolderNotFoundError):
            self.client.list(folder="NonexistentFolder")

    def test_fetch_additional_scenarios(self):
        """
        **Objective:** Test additional fetch scenarios including multiple results and empty results.
        **Workflow:**
            1. Tests various response scenarios
            2. Verifies correct handling of each case
        """
        # Test multiple results
        mock_response_multiple = {
            "data": [{"id": "id1", "name": "test1"}, {"id": "id2", "name": "test2"}]
        }
        self.mock_scm.get.return_value = mock_response_multiple  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Multiple address groups found" in str(exc_info.value)

        # Test single result
        mock_response_single = {"data": [{"id": "id1", "name": "test1"}]}
        self.mock_scm.get.return_value = mock_response_single  # noqa

        result = self.client.fetch(name="test1", folder="Shared")
        assert result["id"] == "id1"

        # Test empty result
        mock_response_empty = {"data": []}
        self.mock_scm.get.return_value = mock_response_empty  # noqa

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Shared")
        assert "not found" in str(exc_info.value)

    def test_fetch_validation_errors(self):
        """
        **Objective:** Test fetch validation errors.
        **Workflow:**
            1. Tests various invalid input scenarios
            2. Verifies appropriate error handling
        """
        # Test empty folder
        with pytest.raises(EmptyFieldError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test multiple containers
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test", folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(exc_info.value)
        )

    def test_delete_error_handling(self):
        """
        **Objective:** Test error handling during object deletion.
        **Workflow:**
            1. Mocks various error scenarios
            2. Verifies proper error handling for each case
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Test object not found
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Object not found",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.delete.side_effect = Exception()  # noqa
        self.mock_scm.delete.side_effect.response = MagicMock()  # noqa
        self.mock_scm.delete.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.delete(object_id)

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        test_data = AddressCreateIpNetmaskFactory()

        # Mock a generic exception without response
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(test_data.model_dump())
        assert str(exc_info.value) == "Generic error"

    def test_get_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in get method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get(object_id)
        assert str(exc_info.value) == "Generic error"

    def test_update_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in update method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-address",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_list_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in list method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.list(folder="Shared")
        assert str(exc_info.value) == "Generic error"

    def test_fetch_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in fetch method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert str(exc_info.value) == "Generic error"

    def test_delete_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in delete method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.delete(object_id)
        assert str(exc_info.value) == "Generic error"

    def test_create_malformed_response_handling(self):
        """
        **Objective:** Test handling of malformed response in create method.
        **Workflow:**
            1. Mocks a response that would cause a parsing error
            2. Verifies appropriate error handling
        """
        test_data = AddressCreateIpNetmaskFactory()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(PydanticValidationError):
            self.client.create(test_data.model_dump())

    def test_fetch_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in fetch method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response without expected fields
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Unexpected response format" in str(exc_info.value)

        # Test response with both id and data fields (invalid format)
        self.mock_scm.get.return_value = {  # noqa
            "id": "some-id",
            "data": [{"some": "data"}],
        }  # noqa

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "2 validation errors for AddressResponseModel" in str(exc_info.value)
        assert "name\n  Field required" in str(exc_info.value)
        assert "id\n  Value error, Invalid UUID format for 'id'" in str(exc_info.value)

    def test_list_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in list method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response
        self.mock_scm.get.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(APIError):
            self.client.list(folder="Shared")

        # Test invalid data format
        self.mock_scm.get.return_value = {"data": "not-a-list"}  # noqa

        with pytest.raises(APIError):
            self.client.list(folder="Shared")

    def test_error_handler_raise_through(self):
        """
        **Objective:** Test that ErrorHandler properly raises through original exceptions.
        **Workflow:**
            1. Mocks various exception scenarios
            2. Verifies exceptions are properly propagated
        """

        # Test with non-JSON response
        class MockResponse:
            def json(self):
                raise ValueError("API Error")

        mock_exception = Exception("API Error")
        mock_exception.response = MockResponse()

        self.mock_scm.get.side_effect = mock_exception  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get("test-id")
        assert "API Error" in str(exc_info.value)

    def test_list_non_dict_response(self):
        """
        **Objective:** Test list method handling of non-dictionary response.
        **Workflow:**
            1. Mocks a non-dictionary response from the API
            2. Verifies that APIError is raised with correct message
            3. Tests different non-dict response types
        """
        # Test with list response
        self.mock_scm.get.return_value = ["not", "a", "dict"]  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with string response
        self.mock_scm.get.return_value = "string response"  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with None response
        self.mock_scm.get.return_value = None  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

    def test_fetch_error_handler_json_error(self):
        """
        **Objective:** Test fetch method error handling when json() raises an error.
        **Workflow:**
            1. Mocks an exception with a response that raises error on json()
            2. Verifies the original exception is re-raised
        """

        class MockResponse:
            @property
            def response(self):
                return self

            def json(self):
                raise ValueError("Original error")

        # Create mock exception with our special response
        mock_exception = Exception("Original error")
        mock_exception.response = MockResponse()

        # Configure mock to raise our custom exception
        self.mock_scm.get.side_effect = mock_exception  # noqa

        # The original exception should be raised since json() failed
        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Original error" in str(exc_info.value)


class TestSuite(
    TestAddressAPI,
    TestAddressValidation,
):
    """Main test suite that combines all test classes."""

    pass
