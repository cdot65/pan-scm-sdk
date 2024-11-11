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
        **Objective:** Test listing all services.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing services.
            2. Calls the `list` method with a filter parameter.
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of services.
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
        services = self.client.list(folder="Prisma Access")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params={
                "limit": 10000,
                "folder": "Prisma Access",
            },
        )
        assert isinstance(services, list)
        assert isinstance(services[0], ServiceResponseModel)
        assert len(services) == 3
        assert services[0].name == "service-http"


class TestServiceCreate(TestServiceBase):
    """Tests for creating Service objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new service.
        **Workflow:**
            1. Creates test data using ServiceFactory.
            2. Mocks the API response.
            3. Calls create method and validates the result.
        """
        test_service = ServiceFactory()
        mock_response = test_service.model_dump()
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_service = self.client.create(
            test_service.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            json=test_service.model_dump(exclude_unset=True),
        )
        assert created_service.name == test_service.name
        assert created_service.description == test_service.description
        assert created_service.protocol == test_service.protocol
        assert created_service.folder == test_service.folder

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
        **Objective:** Test retrieving a specific service.
        **Workflow:**
            1. Mocks the API response for a specific service.
            2. Calls get method and validates the result.
        """
        service_id = "5e7600f1-8681-4048-973b-4117da7e446c"
        mock_response = {
            "id": service_id,
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
        service = self.client.get(service_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/services/{service_id}"
        )
        assert isinstance(service, ServiceResponseModel)
        assert service.name == "Test"
        assert service.protocol.tcp.port == "4433,4333,4999,9443"

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
        **Objective:** Test updating a service.
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
        updated_service = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/services/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_service, ServiceResponseModel)
        assert isinstance(updated_service.id, UUID)
        assert str(updated_service.id) == update_data["id"]
        assert updated_service.name == "UpdatedService"
        assert updated_service.description == "An updated service"
        assert updated_service.protocol.tcp.port == "4433,4333,4999,9443"

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
        **Objective:** Test successful fetch of a service.
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
        # Test no container provided
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
            "folder": "Shared",
            "names": ["service-http", "service-https"],
            "tags": ["Tag1", "Tag2"],
        }
        services = self.client.list(**filters)

        expected_params = {
            "limit": 10000,
            "folder": "Shared",
        }
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params=expected_params,
        )
        assert len(services) == 2

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


# -------------------- End of Test Classes --------------------
