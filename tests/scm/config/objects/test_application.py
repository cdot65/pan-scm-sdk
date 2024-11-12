# tests/scm/config/objects/test_application.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import Application
from scm.exceptions import (
    ValidationError,
    ObjectNotPresentError,
    ReferenceNotZeroError,
    EmptyFieldError,
    ObjectAlreadyExistsError,
    MalformedRequestError,
    FolderNotFoundError,
    BadResponseError,
)
from scm.models.objects import (
    ApplicationResponseModel,
    ApplicationCreateModel,
)

from tests.factories import ApplicationFactory

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestApplicationBase:
    """Base class for Application tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Application(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestApplicationModelValidation(TestApplicationBase):
    """Tests for object model validation."""

    def test_object_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "internal-chat",
            "category": "collaboration",
            "subcategory": "instant-messaging",
            "technology": "client-server",
            "risk": 2,
            "description": "Internal chat application",
            "ports": ["tcp/8443"],
            "folder": "Texas",
            "snippet": "Test123",
            "transfers_files": True,
            "has_known_vulnerabilities": False,
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided." in str(
            exc_info.value
        )

    def test_object_model_create_no_container(self):
        """Test validation when no container is provided."""
        data = {
            "name": "internal-chat",
            "category": "collaboration",
            "subcategory": "instant-messaging",
            "technology": "client-server",
            "risk": 2,
            "description": "Internal chat application",
            "ports": ["tcp/8443"],
            "transfers_files": True,
            "has_known_vulnerabilities": False,
        }

        with pytest.raises(ValueError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided." in str(
            exc_info.value
        )

    def test_object_model_create_model_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "internal-chat",
            "folder": "MainFolder",
            "category": "collaboration",
            "subcategory": "instant-messaging",
            "technology": "client-server",
            "risk": 2,
            "description": "Internal chat application",
            "ports": ["tcp/8443"],
            "transfers_files": True,
            "has_known_vulnerabilities": False,
        }
        model = ApplicationCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.category == data["category"]
        assert model.subcategory == data["subcategory"]
        assert model.technology == data["technology"]
        assert model.risk == data["risk"]
        assert model.description == data["description"]
        assert model.ports == data["ports"]
        assert model.transfers_files == data["transfers_files"]
        assert model.has_known_vulnerabilities == data["has_known_vulnerabilities"]


class TestApplicationList(TestApplicationBase):
    """Tests for listing Application objects."""

    def test_list_objects(self):
        """
        **Objective:** Test listing all objects.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing objects.
            2. Calls the `list` method of `self.client` with a filter parameter.
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of objects, checking their types and attributes.
        """
        mock_response = {
            "data": [
                {
                    "name": "100bao",
                    "description": "100bao is a free Chinese P2P file-sharing program",
                    "ports": ["tcp/3468,6346,11300"],
                    "category": "general-internet",
                    "subcategory": "file-sharing",
                    "technology": "peer-to-peer",
                    "risk": 5,
                    "evasive": True,
                    "pervasive": True,
                    "folder": "All",
                    "snippet": "predefined-snippet",
                },
                {
                    "name": "104apci-supervisory",
                    "container": "iec-60870-5-104",
                    "description": "IEC 60870-5-104 protocol",
                    "ports": ["tcp/2404"],
                    "category": "business-systems",
                    "subcategory": "ics-protocols",
                    "technology": "client-server",
                    "risk": 2,
                    "folder": "All",
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="MainFolder")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "limit": 10000,
                "folder": "MainFolder",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], ApplicationResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "100bao"
        assert existing_objects[0].ports == ["tcp/3468,6346,11300"]

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestApplicationCreate(TestApplicationBase):
    """Tests for creating Application objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new object.
        **Workflow:**
            1. Creates test data using ApplicationFactory.
            2. Mocks the API response.
            3. Calls create method and validates the result.
        """
        test_object = ApplicationFactory()
        mock_response = test_object.model_dump()
        mock_response["name"] = "ValidApplication"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_app = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert created_app.name == test_object.name
        assert created_app.description == test_object.description
        assert created_app.category == test_object.category

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = ApplicationFactory()

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
        test_data = ApplicationFactory()

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
        test_data = ApplicationFactory()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(PydanticValidationError):
            self.client.create(test_data.model_dump())


class TestApplicationGet(TestApplicationBase):
    """Tests for retrieving a specific Application object."""

    def test_get_object(self):
        """
        **Objective:** Test fetching a specific object.
        **Workflow:**
            1. Mocks the API response for a specific object.
            2. Calls get method and validates the result.
        """
        mock_response = {
            "name": "TestApp",
            "folder": "Shared",
            "description": "A test application",
            "category": "networking",
            "subcategory": "networking",
            "technology": "client-server",
            "risk": 2,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        app_name = "TestApp"
        get_object = self.client.get(app_name)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{app_name}"
        )
        assert isinstance(get_object, ApplicationResponseModel)
        assert get_object.name == "TestApp"
        assert get_object.category == "networking"

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


class TestApplicationUpdate(TestApplicationBase):
    """Tests for updating Application objects."""

    def test_update_object(self):
        """
        **Objective:** Test updating a specific object.
        **Workflow:**
        1. Sets up the update data for the object.
        2. Sets up a mock response that includes the updated data.
        3. Calls the `update` method of the `self.client` with the update data.
        4. Asserts that the mocked service was called with the correct URL and data.
        5. Validates the updated object's attributes.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = {
            "id": object_id,
            "name": "TestApp",
            "description": "A test application",
            "category": "networking",
            "subcategory": "networking",
            "technology": "client-server",
            "risk": 2,
        }

        mock_response = update_data.copy()

        self.mock_scm.put.return_value = mock_response  # noqa
        updated_object = self.client.update(update_data)

        # Prepare the expected payload by exluding `id`
        expected_payload = update_data.copy()
        expected_payload.pop("id")

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{object_id}",
            json=expected_payload,
        )
        assert isinstance(updated_object, ApplicationResponseModel)
        assert updated_object.name == "TestApp"
        assert updated_object.category == "networking"
        assert updated_object.subcategory == "networking"
        assert updated_object.technology == "client-server"

    def test_update_object_error_handling(self):
        """
        **Objective:** Test error handling during object update method.
        **Workflow:**
        1. Mocks an error response from the API
        2. Attempts to update an object
        3. Verifies proper error handling and exception raising
        """
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestApp",
            "description": "A test application",
            "category": "networking",
            "subcategory": "networking",
            "technology": "client-server",
            "risk": 2,
            "folder": "Shared",
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
            return_value=mock_error_response,
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

    def test_payload_construction(self):
        """
        **Objective:** Test payload construction using model_dump
        **Workflow:**
            1. Tests that unset values are properly excluded
            2. Verifies the payload matches expected structure
        """
        test_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedApp",
            "folder": "Shared",
            "members": ["app1", "app2"],
            "undefined_field": None,  # Should be excluded
            "category": "networking",
            "subcategory": "web",
            "technology": "client-server",
            "risk": 2,
        }

        # Mock response to prevent actual API call
        mock_response = {
            "id": test_data["id"],
            "name": test_data["name"],
            "folder": test_data["folder"],
            "members": test_data["members"],
            "category": test_data["category"],
            "subcategory": test_data["subcategory"],
            "technology": test_data["technology"],
            "risk": test_data["risk"],
        }
        self.mock_scm.put.return_value = mock_response  # noqa

        # Call update method
        self.client.update(test_data)

        # Verify the payload sent to put() has excluded None values
        actual_payload = self.mock_scm.put.call_args[1]["json"]  # noqa
        expected_payload = {
            "name": "UpdatedApp",
            "folder": "Shared",
            "category": "networking",
            "subcategory": "web",
            "technology": "client-server",
            "risk": 2,
        }
        assert actual_payload == expected_payload
        assert "description" not in actual_payload
        assert "undefined_field" not in actual_payload
        assert "id" not in actual_payload  # ID should not be in payload


class TestApplicationDelete(TestApplicationBase):
    """Tests for deleting Application objects."""

    def test_delete_referenced_object(self):
        """
        **Objective:** Test deleting an object that is referenced by another group.

        **Workflow:**
        1. Sets up a mock error response for a referenced object deletion attempt
        2. Attempts to delete an object that is reference by a group
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

        # Attempt to delete the object and expect ReferenceNotZeroError
        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(object_id)

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


class TestApplicationFetch(TestApplicationBase):
    """Tests for fetching Application objects by name."""

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
            "id": "7b949f50-922c-4677-8696-868bff22f707",
            "name": "test123",
            "folder": "All",
            "category": "business-systems",
            "subcategory": "database",
            "technology": "network-protocol",
            "risk": 1,
            "description": "test123",
            "used_by_malware": False,
            "prone_to_misuse": False,
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        address = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        # Validate the returned address
        assert isinstance(address, dict)
        assert address["name"] == mock_response["name"]
        assert address["description"] == mock_response["description"]
        assert address["category"] == mock_response["category"]

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
        **Objective:** Test fetch method with empty name parameter.
        **Workflow:**
            1. Attempts to fetch with empty name
            2. Verifies ValidationError is raised
        """
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="", folder="Shared")
        assert "Field 'name' cannot be empty" in str(exc_info.value)

    def test_fetch_container_validation(self):
        """
        **Objective:** Test container parameter validation in fetch method.
        **Workflow:**
            1. Tests various invalid container combinations
            2. Verifies proper error handling
        """
        # Test empty folder
        with pytest.raises(EmptyFieldError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test no container
        with pytest.raises(ValidationError):
            self.client.fetch(name="test")

        # Test multiple containers
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test", folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(exc_info.value)
        )

        # Test with device container
        with pytest.raises(ValidationError):
            self.client.fetch(name="test", folder="Shared", device="device1")

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
        assert "4 validation errors for ApplicationResponseModel" in str(exc_info.value)
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


class TestApplicationListFilters(TestApplicationBase):
    """Tests for filtering during listing Application objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        filters = {
            "category": ["type1", "type2"],
            "subcategory": ["value1", "value2"],
            "technology": ["tag1", "tag2"],
            "risk": ["tag1", "tag2"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )

    def test_list_filters_type_validation(self):
        """
        **Objective:** Test validation of filter category in list method.
        **Workflow:**
            1. Tests various invalid filter type scenarios
            2. Verifies ValidationError is raised with correct message
            3. Tests valid filter types pass validation
        """
        mock_response = {
            "data": [
                {
                    "id": "7b949f50-922c-4677-8696-868bff22f707",
                    "name": "test123",
                    "folder": "All",
                    "category": "business-systems",
                    "subcategory": "database",
                    "technology": "network-protocol",
                    "risk": 1,
                    "description": "test123",
                    "used_by_malware": False,
                    "prone_to_misuse": False,
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid category filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", category="business-systems")
        assert str(exc_info.value) == "'category' filter must be a list"

        # Test invalid category filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", category={"value": "business-systems"})
        assert str(exc_info.value) == "'category' filter must be a list"

        # Test invalid subcategory filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", subcategory="database")
        assert str(exc_info.value) == "'subcategory' filter must be a list"

        # Test invalid subcategory filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", subcategory={"value": "database"})
        assert str(exc_info.value) == "'subcategory' filter must be a list"

        # Test invalid risks filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", risk={"value": "1"})
        assert str(exc_info.value) == "'risk' filter must be a list"

        # Test invalid types risks (integer instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", risk=123)
        assert str(exc_info.value) == "'risk' filter must be a list"

        # Test invalid technology filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", technology={"value": "database"})
        assert str(exc_info.value) == "'technology' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                category=["business-systems"],
                subcategory=["database"],
                technology=["network-protocol"],
                risks=["1"],
            )
        except ValidationError:
            pytest.fail("Unexpected ValidationError raised with valid list filters")

    def test_list_filters_type_values(self):
        """Test listing objects with values filter."""
        mock_response = {
            "data": [
                {
                    "name": "App1",
                    "folder": "Shared",
                    "ports": ["80"],
                    "category": "web",
                    "subcategory": "web",
                    "technology": "client-server",
                    "risk": 10,  # Invalid risk level
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {
            "folder": "Shared",
            "values": ["80"],
        }
        filtered_objects = self.client.list(**filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert len(filtered_objects) == 1

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
                    "name": "100bao",
                    "description": '100bao (literally translated as "100 treasures") is a free Chinese P2P file-sharing program that supports Windows 98, 2000, and XP operating systems.',
                    "ports": ["tcp/3468,6346,11300"],
                    "category": "general-internet",
                    "subcategory": "file-sharing",
                    "technology": "peer-to-peer",
                    "risk": "5",
                    "evasive": True,
                    "pervasive": True,
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "excessive_bandwidth_use": True,
                    "used_by_malware": True,
                    "transfers_files": True,
                    "has_known_vulnerabilities": True,
                    "tunnels_other_apps": False,
                    "prone_to_misuse": True,
                    "no_certifications": False,
                },
                {
                    "name": "104apci-supervisory",
                    "container": "iec-60870-5-104",
                    "description": "IEC 60870-5-104 enables communication between control station and substation via a standard TCP/IP network. The functional app identifies application protocol control information (APCI) for supervisory function. This control format does not contain any application service data units (ASDUs).",
                    "ports": ["tcp/2404"],
                    "category": "business-systems",
                    "subcategory": "ics-protocols",
                    "technology": "client-server",
                    "risk": "2",
                    "evasive": False,
                    "pervasive": True,
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "depends_on": ["iec-60870-5-104-base"],
                    "excessive_bandwidth_use": False,
                    "used_by_malware": False,
                    "transfers_files": False,
                    "has_known_vulnerabilities": True,
                    "tunnels_other_apps": True,
                    "prone_to_misuse": False,
                    "no_certifications": False,
                },
                {
                    "name": "104apci-unnumbered",
                    "container": "iec-60870-5-104",
                    "description": "IEC 60870-5-104 enables communication between control station and substation via a standard TCP/IP network. The functional app identifies application protocol control information (APCI) for the unnumbered control format. This control format is used as a start-stop mechanism for information flow. There are no sequence numbers. This control field may also be used where more than one connection is available between stations, and a changeover between connections is to be made without loss of data. This control format does not contain any application service data units (ASDUs).",
                    "ports": ["tcp/2404"],
                    "category": "business-systems",
                    "subcategory": "ics-protocols",
                    "technology": "client-server",
                    "risk": "2",
                    "evasive": False,
                    "pervasive": True,
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "depends_on": ["iec-60870-5-104-base"],
                    "excessive_bandwidth_use": False,
                    "used_by_malware": False,
                    "transfers_files": False,
                    "has_known_vulnerabilities": True,
                    "tunnels_other_apps": True,
                    "prone_to_misuse": False,
                    "no_certifications": False,
                },
                {
                    "name": "104apci-unnumbered-startdt-act",
                    "container": "iec-60870-5-104",
                    "description": "IEC 60870-5-104 enables communication between control station and substation via a standard TCP/IP network. This functional app detects apci unnumbered frame - start data transfer activation.",
                    "ports": ["tcp/2404"],
                    "category": "business-systems",
                    "subcategory": "ics-protocols",
                    "technology": "client-server",
                    "risk": "1",
                    "evasive": False,
                    "pervasive": False,
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "depends_on": ["iec-60870-5-104-base"],
                    "excessive_bandwidth_use": False,
                    "used_by_malware": False,
                    "transfers_files": False,
                    "has_known_vulnerabilities": True,
                    "tunnels_other_apps": False,
                    "prone_to_misuse": False,
                    "can_disable": True,
                    "no_certifications": False,
                },
            ],
            "offset": 0,
            "total": 4867,
            "limit": "4",
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Shared",
            category=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            subcategory=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            technology=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            risk=[],
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
