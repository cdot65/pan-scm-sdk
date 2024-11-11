# tests/scm/config/objects/test_service.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import Service
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
    ServiceCreateModel,
    ServiceResponseModel,
)

from tests.factories import ServiceFactory

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestServiceBase:
    """Base class for Service tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Service(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestServiceList(TestServiceBase):
    """Tests for listing Service objects."""

    def test_list_objects(self):
        """
        **Objective:** Test listing all objects.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing objects.
            2. Calls the `list` method with a filter parameter.
            3. Asserts that the mocked object was called correctly.
            4. Validates the returned list of objects.
        """
        mock_response = {
            "data": [
                {
                    "name": "service-http",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "protocol": {"tcp": {"port": "80,8080"}},
                },
                {
                    "name": "service-https",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "protocol": {"tcp": {"port": "443"}},
                },
                {
                    "id": "5e7600f1-8681-4048-973b-4117da7e446c",
                    "name": "Test",
                    "folder": "Shared",
                    "description": "This is just a test",
                    "protocol": {
                        "tcp": {
                            "port": "4433,4333,4999,9443",
                            "override": {
                                "timeout": 10,
                                "halfclose_timeout": 10,
                                "timewait_timeout": 10,
                            },
                        }
                    },
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Prisma Access")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params={
                "limit": 10000,
                "folder": "Prisma Access",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], ServiceResponseModel)
        assert len(existing_objects) == 3
        assert existing_objects[0].name == "service-http"


class TestServiceCreate(TestServiceBase):
    """Tests for creating Service objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new object.
        **Workflow:**
            1. Creates test data using ServiceFactory.
            2. Mocks the API response.
            3. Calls create method and validates the result.
        """
        test_object = ServiceFactory()
        mock_response = test_object.model_dump()
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert created_object.name == test_object.name
        assert created_object.description == test_object.description
        assert created_object.protocol == test_object.protocol
        assert created_object.folder == test_object.folder

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = ServiceFactory()

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
        test_data = ServiceFactory()

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
        test_data = ServiceFactory()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(PydanticValidationError):
            self.client.create(test_data.model_dump())


class TestServiceGet(TestServiceBase):
    """Tests for retrieving a specific Service object."""

    def test_get_object(self):
        """
        **Objective:** Test retrieving a specific object.
        **Workflow:**
            1. Mocks the API response for a specific object.
            2. Calls get method and validates the result.
        """
        object_id = "5e7600f1-8681-4048-973b-4117da7e446c"
        mock_response = {
            "id": object_id,
            "name": "Test",
            "folder": "Shared",
            "description": "This is just a test",
            "protocol": {
                "tcp": {
                    "port": "4433,4333,4999,9443",
                },
            },
            "tag": ["Automation"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        get_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/services/{object_id}"
        )
        assert isinstance(get_object, ServiceResponseModel)
        assert get_object.name == "Test"
        assert get_object.protocol.tcp.port == "4433,4333,4999,9443"

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


class TestServiceUpdate(TestServiceBase):
    """Tests for updating Service objects."""

    def test_update_object(self):
        """
        **Objective:** Test updating an object.
        **Workflow:**
            1. Prepares update data and mocks response
            2. Verifies the update request and response
            3. Ensures payload transformation is correct
        """
        from uuid import UUID

        # Test data including ID
        update_data = {
            "id": "5e7600f1-8681-4048-973b-4117da7e446c",
            "name": "UpdatedService",
            "folder": "Shared",
            "description": "An updated service",
            "protocol": {
                "tcp": {
                    "port": "4433,4333,4999,9443",
                }
            },
        }

        # Expected payload should not include the ID
        expected_payload = {
            "name": "UpdatedService",
            "folder": "Shared",
            "description": "An updated service",
            "protocol": {
                "tcp": {
                    "port": "4433,4333,4999,9443",
                }
            },
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_object = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/services/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_object, ServiceResponseModel)
        assert isinstance(updated_object.id, UUID)
        assert str(updated_object.id) == update_data["id"]
        assert updated_object.name == "UpdatedService"
        assert updated_object.description == "An updated service"
        assert updated_object.protocol.tcp.port == "4433,4333,4999,9443"

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
            "name": "test-service",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80"}},
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
            "name": "test-service",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80"}},
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"


class TestServiceDelete(TestServiceBase):
    """Tests for deleting Service objects."""

    def test_delete_referenced_object(self):
        """
        **Objective:** Test deleting an application that is referenced by another group.

        **Workflow:**
        1. Sets up a mock error response for a referenced object deletion attempt
        2. Attempts to delete an application that is reference by a group
        3. Validates that ReferenceNotZeroError is raised with correct details
        4. Verifies the error contains proper reference information
        """
        application_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        # Mock the API error response
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Your configuration is not valid. Please review the error message for more details.",
                    "details": {
                        "errorType": "Reference Not Zero",
                        "message": [
                            " container -> Texas -> application-group -> custom-group -> members"
                        ],
                        "errors": [
                            {
                                "type": "NON_ZERO_REFS",
                                "message": "Node cannot be deleted because of references from",
                                "params": ["custom-app"],
                                "extra": [
                                    "container/[Texas]/application-group/[custom-group]/s/[custom-app]"
                                ],
                            }
                        ],
                    },
                }
            ],
            "_request_id": "c318dcbf-4678-4ff5-acf8-e55df7fca081",
        }

        # Configure mock to raise HTTPError with our custom error response
        self.mock_scm.delete.side_effect = Exception()  # noqa
        self.mock_scm.delete.side_effect.response = MagicMock()  # noqa
        self.mock_scm.delete.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response,
        )

        # Attempt to delete the application and expect ReferenceNotZeroError
        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(application_id)

        error = exc_info.value

        # Verify the error contains the expected information
        assert error.error_code == "API_I00013"
        assert "custom-app" in error.references
        assert any("Texas" in path for path in error.reference_paths)
        assert "Cannot delete object due to existing references" in str(error)

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


class TestServiceFetch(TestServiceBase):
    """Tests for fetching Service objects by name."""

    def test_fetch_object(self):
        """
        **Objective:** Test successful fetch of an object.
        **Workflow:**
            1. Mocks API response for a successful fetch
            2. Verifies correct parameter handling
            3. Validates response transformation
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "web-browsing",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80,443"}},
            "description": None,  # Should be excluded in the result
            "tag": ["web"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="web-browsing", folder="Shared")

        # Verify API call
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params={
                "folder": "Shared",
                "name": "web-browsing",
            },
        )

        # Verify result
        assert isinstance(result, dict)
        assert "id" in result
        assert result["name"] == "web-browsing"
        assert result["protocol"]["tcp"]["port"] == "80,443"
        assert "description" not in result  # None values should be excluded
        assert result["tag"] == ["web"]

    def test_fetch_object_not_found(self):
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

    def test_fetch_empty_name(self):
        """
        **Objective:** Test fetch with empty name parameter.
        **Workflow:**
            1. Attempts to fetch with empty name
            2. Verifies ValidationError is raised
        """
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="", folder="Shared")
        assert "Field 'name' cannot be empty" in str(exc_info.value)

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

        # Test no container
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test-service")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(
                name="test-service", folder="Shared", snippet="TestSnippet"
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_fetch_response_handling(self):
        """
        **Objective:** Test fetch method's response handling.
        **Workflow:**
            1. Tests various response scenarios
            2. Verifies proper response transformation
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestService",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80", "override": None}},  # Should be excluded
            "description": None,  # Should be excluded
            "tag": None,  # Should be excluded
            "snippet": None,  # Should be excluded
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="TestService", folder="Shared")

        # Verify None values are excluded
        assert "description" not in result
        assert "tag" not in result
        assert "snippet" not in result
        assert "override" not in result["protocol"]["tcp"]

        # Verify required fields are present
        assert "id" in result
        assert "name" in result
        assert "protocol" in result
        assert result["protocol"]["tcp"]["port"] == "80"

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

    def test_fetch_unexpected_response_format(self):
        """
        Test fetching an application when the API returns an unexpected response format.

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
        assert "3 validation errors for ServiceResponseMode" in str(exc_info.value)

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


class TestServiceValidation(TestServiceBase):
    """Tests for Service validation."""

    def test_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_request_model_no_protocol_provided(self):
        """Test validation when no protocol is provided."""
        data = {
            "name": "TestService",
            "folder": "Shared",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert "Field required" in str(exc_info.value)

    def test_request_model_multiple_protocols_provided(self):
        """Test validation when multiple protocols are provided."""
        data = {
            "name": "TestService",
            "folder": "Shared",
            "protocol": {
                "tcp": {"port": "80"},
                "udp": {"port": "53"},
            },
        }
        with pytest.raises(ValueError) as exc_info:
            ServiceCreateModel(**data)
        assert "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'." in str(
            exc_info.value
        )

    def test_request_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "TestService",
            "protocol": {"tcp": {"port": "80"}},
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_request_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "TestService",
            "protocol": {"tcp": {"port": "80"}},
            "folder": "Shared",
            "snippet": "TestSnippet",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_response_model_invalid_uuid(self):
        """Test validation of UUID format in response model."""
        invalid_data = {
            "id": "invalid-uuid",
            "name": "TestService",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80"}},
        }
        with pytest.raises(ValueError) as exc_info:
            ServiceResponseModel(**invalid_data)
        assert "1 validation error for ServiceResponseModel" in str(exc_info.value)
        assert "Input should be a valid UUID, invalid character" in str(exc_info.value)


class TestServiceListFilters(TestServiceBase):
    """Tests for filtering during listing Service objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        mock_response = {
            "data": [
                {
                    "name": "service-http",
                    "folder": "Shared",
                    "protocol": {"tcp": {"port": "80,8080"}},
                },
                {
                    "name": "service-https",
                    "folder": "Shared",
                    "protocol": {"tcp": {"port": "443"}},
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {
            "folder": "Shared",  # Added this
            "protocols": ["tcp", "udp"],
            "tags": ["Tag1", "Tag2"],
        }
        filtered_objects = self.client.list(**filters)

        expected_params = {
            "limit": 10000,
            "folder": "Shared",
        }
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params=expected_params,
        )
        assert len(filtered_objects) == 2

    def test_list_filters_protocol_validation(self):
        """
        **Objective:** Test validation of filter protocol in list method.
        **Workflow:**
            1. Tests various invalid filter type scenarios
            2. Verifies ValidationError is raised with correct message
            3. Tests valid filter types pass validation
        """
        mock_response = {
            "data": [
                {
                    "name": "service-http",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "protocol": {"tcp": {"port": "80,8080"}},
                },
                {
                    "name": "service-https",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "protocol": {"tcp": {"port": "443"}},
                },
                {
                    "id": "7242be61-ba51-4862-95b1-b24b20acf9b4",
                    "name": "web-service",
                    "folder": "Texas",
                    "protocol": {
                        "tcp": {
                            "port": "80,443",
                            "override": {
                                "timeout": 60,
                                "halfclose_timeout": 30,
                            },
                        }
                    },
                    "description": "Web service for HTTP/HTTPS",
                    "tag": ["Automation"],
                },
                {
                    "id": "28832824-2775-4eb7-bd38-ca70ad6d9ba5",
                    "name": "dns-service",
                    "folder": "Texas",
                    "protocol": {"udp": {"port": "53"}},
                    "description": "DNS service",
                },
            ],
            "offset": 0,
            "total": 4,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid protocol filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", protocol="tcp")
        assert str(exc_info.value) == "'protocol' filter must be a list"

        # Test invalid protocol filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", protocol={"value": "tcp"})
        assert str(exc_info.value) == "'protocol' filter must be a list"

        # Test invalid tag filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", tag="database")
        assert str(exc_info.value) == "'tag' filter must be a list"

        # Test invalid tag filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", tag={"value": "database"})
        assert str(exc_info.value) == "'tag' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                tag=["database"],
            )
        except ValidationError:
            pytest.fail("Unexpected ValidationError raised with valid list filters")

    def test_list_protocol_filtering(self):
        """
        **Objective:** Test filtering objects by protocol type.
        **Workflow:**
            1. Sets up mock response with mixed protocol objects
            2. Tests filtering for TCP and UDP protocols
            3. Verifies correct objects are returned based on protocol
        """
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "http-service",
                    "folder": "Shared",
                    "protocol": {"tcp": {"port": "80,8080"}},
                },
                {
                    "id": "123e4567-e89b-12d3-a456-426655440001",
                    "name": "dns-service",
                    "folder": "Shared",
                    "protocol": {"udp": {"port": "53"}},
                },
                {
                    "id": "123e4567-e89b-12d3-a456-426655440002",
                    "name": "https-service",
                    "folder": "Shared",
                    "protocol": {"tcp": {"port": "443"}},
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test TCP protocol filter
        tcp_objects = self.client.list(folder="Shared", protocol=["tcp"])
        assert len(tcp_objects) == 2
        assert all(svc.protocol.tcp is not None for svc in tcp_objects)
        assert all(svc.name in ["http-service", "https-service"] for svc in tcp_objects)

        # Test UDP protocol filter
        udp_objects = self.client.list(folder="Shared", protocol=["udp"])
        assert len(udp_objects) == 1
        assert all(svc.protocol.udp is not None for svc in udp_objects)
        assert udp_objects[0].name == "dns-service"

        # Test multiple protocol filter
        all_objects = self.client.list(folder="Shared", protocol=["tcp", "udp"])
        assert len(all_objects) == 3
        assert any(svc.protocol.tcp is not None for svc in all_objects)
        assert any(svc.protocol.udp is not None for svc in all_objects)

        # Verify API was called correctly
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/services",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )

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


# -------------------- End of Test Classes --------------------
