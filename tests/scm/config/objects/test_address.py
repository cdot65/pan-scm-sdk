# tests/scm/config/objects/test_address.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import Address
from scm.exceptions import (
    ValidationError,
    ObjectNotPresentError,
    EmptyFieldError,
    ObjectAlreadyExistsError,
    MalformedRequestError,
    FolderNotFoundError,
    BadResponseError,
    ReferenceNotZeroError,
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
    """Base class for Address tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Address(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestAddressModelValidation(TestAddressBase):
    """Tests for object model validation."""

    def test_object_model_no_type_provided(self):
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

    def test_object_model_multiple_types(self):
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

    def test_object_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "internal_network",
            "ip_netmask": "192.168.1.0/24",
            "description": "Internal network segment",
            "tag": ["Python", "Automation"],
            "folder": "Shared",
            "snippet": "Test123",
        }
        with pytest.raises(ValueError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "internal_network",
            "ip_netmask": "192.168.1.0/24",
            "description": "Internal network segment",
            "tag": ["Python", "Automation"],
        }

        with pytest.raises(ValueError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_create_model_valid(self):
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


class TestAddressList(TestAddressBase):
    """Tests for listing Address objects."""

    def test_object_list_valid(self):
        """
        **Objective:** Test listing all objects.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing objects.
            2. Calls the `list` method with a filter parameter.
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of objects.
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
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            params={
                "limit": 10000,
                "folder": "All",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], AddressResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "Palo Alto Networks Sinkhole"

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestAddressCreate(TestAddressBase):
    """Tests for creating Address objects."""

    def test_create_object_type_ip_netmask(self):
        """
        **Objective:** Test creating an object.
        **Workflow:**
            1. Uses AddressCreateIpNetmaskFactory to create test data.
            2. Mocks the API response.
            3. Verifies the creation request and response.
        """
        test_objects = AddressCreateIpNetmaskFactory()
        mock_response = test_objects.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_objects = self.client.create(
            test_objects.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_objects.model_dump(exclude_unset=True),
        )
        assert str(created_objects.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_objects.name == test_objects.name
        assert created_objects.ip_netmask == test_objects.ip_netmask
        assert created_objects.folder == test_objects.folder

    def test_create_object_type_fqdn(self):
        """
        **Objective:** Test creating an object of type fqdn.
        **Workflow:**
            1. Uses `AddressCreateFqdnFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the object data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created object's attributes.
        """
        test_objects_fqdn = AddressCreateFqdnFactory()
        mock_response = test_objects_fqdn.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_objects_fqdn.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_objects_fqdn.model_dump(exclude_unset=True),
        )
        assert str(created_group.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_objects_fqdn.name
        assert created_group.fqdn == test_objects_fqdn.fqdn
        assert created_group.folder == test_objects_fqdn.folder

    def test_create_object_type_ip_range(self):
        """
        **Objective:** Test creating an object of type ip-range.
        **Workflow:**
            1. Uses `AddressCreateIpRangeFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the object data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created object's attributes.
        """
        test_objects_ip_range = AddressCreateIpRangeFactory()
        mock_response = test_objects_ip_range.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_objects_ip_range.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_objects_ip_range.model_dump(exclude_unset=True),
        )
        assert str(created_group.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_objects_ip_range.name
        assert created_group.ip_range == test_objects_ip_range.ip_range
        assert created_group.folder == test_objects_ip_range.folder

    def test_create_object_type_ip_wildcard(self):
        """
        **Objective:** Test creating an object of type ip-wildcard.
        **Workflow:**
            1. Uses `AddressCreateIpWildcardFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the object data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created object's attributes.
        """
        test_objects_ip_wildcard = AddressCreateIpWildcardFactory()
        mock_response = test_objects_ip_wildcard.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_objects_ip_wildcard.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_objects_ip_wildcard.model_dump(exclude_unset=True),
        )
        assert str(created_group.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_objects_ip_wildcard.name
        assert created_group.ip_wildcard == test_objects_ip_wildcard.ip_wildcard
        assert created_group.folder == test_objects_ip_wildcard.folder

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


class TestAddressGet(TestAddressBase):
    """Tests for retrieving a specific Address object."""

    def test_get_object(self):
        """
        **Objective:** Test retrieving a specific object.
        **Workflow:**
            1. Mocks the API response for a specific object.
            2. Verifies the get request and response handling.
        """
        mock_response = {
            "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
            "name": "TestAddress",
            "ip_netmask": "10.0.0.0/24",
            "folder": "Shared",
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        object_id = "b44a8c00-7555-4021-96f0-d59deecd54e8"
        get_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{object_id}"
        )
        assert isinstance(get_object, AddressResponseModel)
        assert get_object.name == "TestAddress"
        assert get_object.ip_netmask == "10.0.0.0/24"

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


class TestAddressUpdate(TestAddressBase):
    """Tests for updating Address objects."""

    def test_update_object(self):
        """
        **Objective:** Test updating an object.
        **Workflow:**
            1. Prepares update data and mocks response
            2. Verifies the update request and response
            3. Ensures payload transformation is correct
        """
        from uuid import UUID

        test_uuid = UUID("123e4567-e89b-12d3-a456-426655440000")

        # Test data including ID
        update_data = {
            "id": str(test_uuid),
            "name": "TestAddress",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
            "description": "Updated description",
            "tag": [
                "tag1",
                "tag2",
            ],
        }

        # Expected payload should not include the ID
        expected_payload = {
            "name": "TestAddress",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
            "description": "Updated description",
            "tag": [
                "tag1",
                "tag2",
            ],
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_object = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_object, AddressResponseModel)
        assert isinstance(updated_object.id, UUID)  # Verify it's a UUID object
        assert updated_object.id == test_uuid  # Compare against UUID object
        assert (
            str(updated_object.id) == update_data["id"]
        )  # Compare string representations
        assert updated_object.name == "TestAddress"
        assert updated_object.ip_netmask == "10.0.0.0/24"
        assert updated_object.folder == "Shared"

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

    def test_update_with_invalid_data(self):
        """
        **Objective:** Test update method with invalid data structure.
        **Workflow:**
            1. Attempts to update with invalid data
            2. Verifies proper validation error handling
        """
        invalid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "invalid_field": "test",
        }

        with pytest.raises(PydanticValidationError):
            self.client.update(invalid_data)

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


class TestAddressDelete(TestAddressBase):
    """Tests for deleting Address objects."""

    def test_delete_referenced_object(self):
        """
        Test deleting an object that is referenced by other objects.

        **Objective:** Verify that attempting to delete an object that is referenced
        by other objects raises a ReferenceNotZeroError with proper reference details.

        **Workflow:**
            1. Sets up a mock error response for a referenced object deletion attempt
            2. Attempts to delete an object that is referenced by other objects
            3. Validates that ReferenceNotZeroError is raised with correct details
            4. Verifies the error contains proper reference information
        """
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

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

        # Attempt to delete the object and expect ReferenceNotZeroError
        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(object_id)

        error = exc_info.value

        # Verify the error contains the expected information
        assert error.error_code == "API_I00013"
        assert "dallas-desktop1" in error.references
        assert any("cdot.io Best Practices" in path for path in error.reference_paths)
        assert "Cannot delete object due to existing references" in str(error)

        # Verify the delete method was called with correct endpoint
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{object_id}"
        )

        # Verify detailed error message includes reference path
        assert "Developer Desktops" in error.detailed_message
        assert "snippet/[cdot.io Best Practices]" in error.detailed_message

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


class TestAddressFetch(TestAddressBase):
    """Tests for fetching Address objects by name."""

    def test_fetch_object(self):
        """
        **Objective:** Test retrieving an object by its name using the `fetch` method.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an object by name.
            2. Calls the `fetch` method of `self.client` with a specific name and container.
            3. Asserts that the mocked service was called with the correct URL and parameters.
            4. Validates the returned object's attributes.
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "dallas-desktop1",
            "folder": "Texas",
            "ip_netmask": "10.5.0.11",
            "description": "test123456",
            "tag": ["Decrypted"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
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

        # Validate the returned object
        assert isinstance(fetched_object, dict)
        assert str(fetched_object["id"]) == mock_response["id"]
        assert fetched_object["name"] == mock_response["name"]
        assert fetched_object["description"] == mock_response["description"]
        assert fetched_object["tag"][0] == mock_response["tag"][0]

    def test_fetch_object_not_found(self):
        """
        Test fetching an object by name that does not exist.

        **Objective:** Test that fetching a non-existent object raises NotFoundError.
        **Workflow:**
            1. Mocks the API response to return an empty 'data' list.
            2. Calls the `fetch` method with a name that does not exist.
            3. Asserts that NotFoundError is raised.
        """
        object_name = "NonExistent"
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
                name=object_name,
                folder=folder_name,
            )

    def test_fetch_empty_name(self):
        """
        Test fetching an object without providing the 'name' parameter.

        **Objective:** Ensure that the fetch method raises ValidationError when 'name' is not provided.
        **Workflow:**
            1. Calls the `fetch` method without the 'name' parameter.
            2. Asserts that ValidationError is raised.
        """
        folder_name = "Shared"
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(folder=folder_name, name="")
        assert str(exc_info.value) == "Field 'name' cannot be empty"

    def test_fetch_container_validation(self):
        """
        **Objective:** Test container parameter validation in fetch.
        **Workflow:**
            1. Tests various invalid container combinations
            2. Verifies proper error handling
        """
        # Test empty folder
        with pytest.raises(EmptyFieldError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test no container provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test-group")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test-group", folder="Shared", snippet="TestSnippet")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_fetch_object_unexpected_response_format(self):
        """
        Test fetching an object when the API returns an unexpected response format.

        **Objective:** Ensure that the fetch method raises BadResponseError when the response format is not as expected.
        **Workflow:**
            1. Mocks the API response to return an unexpected format.
            2. Calls the `fetch` method.
            3. Asserts that BadResponseError is raised.
        """
        group_name = "TestGroup"
        folder_name = "Shared"
        # Mocking an unexpected response format
        mock_response = {"unexpected_key": "unexpected_value"}
        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.fetch(name=group_name, folder=folder_name)
        assert str(exc_info.value) == "Invalid response format: missing 'id' field"

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

    def test_fetch_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in fetch method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response without expected fields
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

        # Test response with both id and data fields (invalid format)
        self.mock_scm.get.return_value = {  # noqa
            "id": "some-id",
            "data": [{"some": "data"}],
        }  # noqa

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "2 validation errors for AddressResponseModel" in str(exc_info.value)
        assert "name\n  Field required" in str(exc_info.value)

        # Test malformed response in list format
        self.mock_scm.get.return_value = [{"unexpected": "format"}]  # noqa
        with pytest.raises(BadResponseError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
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


class TestAddressTagValidation(TestAddressBase):
    """Tests for Address tag field validation."""

    def test_tag_string_to_list_conversion(self):
        """
        Test tag field validator converting a string to a list.

        **Objective:** Verify that a single string tag is properly converted to a list.
        **Workflow:**
            1. Creates an object with a single string tag
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
            1. Creates an object with multiple tags as a list
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
            1. Attempts to create an object with an invalid tag type (dict)
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
            1. Attempts to create an object with duplicate tags
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


class TestAddressListFilters(TestAddressBase):
    """Tests for filtering during listing Address objects."""

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
            "tags": ["tag1", "tag2"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )

    def test_list_filters_type_validation(self):
        """
        **Objective:** Test validation of filter types in list method.
        **Workflow:**
            1. Tests various invalid filter type scenarios
            2. Verifies ValidationError is raised with correct message
            3. Tests valid filter types pass validation
        """
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address",
                    "folder": "Shared",
                    "ip_netmask": "10.0.0.0/24",
                    "tag": ["tag1", "tag2"],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid types filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", types="netmask")
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test invalid values filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", values="10.0.0.0/24")
        assert str(exc_info.value) == "'values' filter must be a list"

        # Test invalid tags filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", tags="tag1")
        assert str(exc_info.value) == "'tags' filter must be a list"

        # Test invalid types filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", types={"type": "netmask"})
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test invalid values filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", values={"value": "10.0.0.0/24"})
        assert str(exc_info.value) == "'values' filter must be a list"

        # Test invalid tags filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", tags={"tag": "tag1"})
        assert str(exc_info.value) == "'tags' filter must be a list"

        # Test invalid types filter (integer instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", types=123)
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                types=["netmask"],
                values=["10.0.0.0/24"],
                tags=["tag1"],
            )
        except ValidationError:
            pytest.fail("Unexpected ValidationError raised with valid list filters")

    def test_list_filter_combinations(self):
        """
        **Objective:** Test different combinations of valid filters.
        **Workflow:**
            1. Tests various combinations of valid filters
            2. Verifies filters are properly applied
            3. Checks that filtered results match expected criteria
        """
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address1",
                    "folder": "Shared",
                    "ip_netmask": "10.0.0.0/24",
                    "tag": ["tag1", "tag2"],
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address2",
                    "folder": "Shared",
                    "ip_range": "10.0.0.1-10.0.0.10",
                    "tag": ["tag2", "tag3"],
                },
                {
                    "id": "323e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address3",
                    "folder": "Shared",
                    "fqdn": "test.example.com",
                    "tag": ["tag1", "tag3"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test combining types and tags filters
        filtered_objects = self.client.list(
            folder="Shared",
            types=["netmask"],
            tags=["tag1"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "test-address1"

        # Test combining values and tags filters
        filtered_objects = self.client.list(
            folder="Shared",
            values=["10.0.0.0/24"],
            tags=["tag2"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "test-address1"

        # Test all filters together
        filtered_objects = self.client.list(
            folder="Shared",
            types=["netmask"],
            values=["10.0.0.0/24"],
            tags=["tag1"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "test-address1"

    def test_list_empty_filter_lists(self):
        """
        **Objective:** Test behavior with empty filter lists.
        **Workflow:**
            1. Tests filters with empty lists
            2. Verifies appropriate handling of empty filters
        """
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address",
                    "folder": "Shared",
                    "ip_netmask": "10.0.0.0/24",
                    "tag": ["tag1"],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Shared",
            types=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            values=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            tags=[],
        )
        assert len(filtered_objects) == 0

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

    def test_list_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in list method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response
        self.mock_scm.get.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(BadResponseError):
            self.client.list(folder="Shared")

        # Test invalid data format
        self.mock_scm.get.return_value = {"data": "not-a-list"}  # noqa

        with pytest.raises(BadResponseError):
            self.client.list(folder="Shared")

    def test_list_non_dict_response(self):
        """
        **Objective:** Test list method handling of non-dictionary response.
        **Workflow:**
            1. Mocks a non-dictionary response from the API
            2. Verifies that BadResponseError is raised with correct message
            3. Tests different non-dict response types
        """
        # Test with list response
        self.mock_scm.get.return_value = ["not", "a", "dict"]  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with string response
        self.mock_scm.get.return_value = "string response"  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with None response
        self.mock_scm.get.return_value = None  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
