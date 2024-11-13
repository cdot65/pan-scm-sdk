# tests/scm/config/objects/test_application_group.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import ApplicationGroup
from scm.exceptions import (
    APIError,
    BadRequestError,
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
    ConflictError,
)
from scm.models.objects import (
    ApplicationGroupCreateModel,
    ApplicationGroupResponseModel,
)

from tests.factories import ApplicationGroupFactory

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestApplicationGroupBase:
    """Base class for Application Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = ApplicationGroup(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestApplicationGroupList(TestApplicationGroupBase):
    """Tests for listing Application Group objects."""

    def test_list_objects(self):
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
                    "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
                    "name": "Microsoft 365 Access",
                    "folder": "Shared",
                    "snippet": "office365",
                    "members": [
                        "office365-consumer-access",
                        "office365-enterprise-access",
                    ],
                },
                {
                    "id": "0b12a889-4220-4cdd-b95f-506e0351a5e4",
                    "name": "Microsoft 365 Services",
                    "folder": "Shared",
                    "snippet": "office365",
                    "members": [
                        "ms-office365",
                        "ms-onedrive",
                        "ms-onenote",
                        "ms-lync-base",
                        "skype",
                    ],
                },
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Prisma Access")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/application-groups",
            params={
                "limit": 10000,
                "folder": "Prisma Access",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], ApplicationGroupResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "Microsoft 365 Access"
        assert existing_objects[0].members == [
            "office365-consumer-access",
            "office365-enterprise-access",
        ]


class TestApplicationGroupCreate(TestApplicationGroupBase):
    """Tests for creating Application Group objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating an object.
        **Workflow:**
            1. Uses ApplicationGroupFactory to create test data.
            2. Mocks the API response.
            3. Verifies the creation request and response.
        """
        test_object = ApplicationGroupFactory()
        mock_response = test_object.model_dump()
        mock_response["name"] = "ValidStaticApplicationGroup"
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/application-groups",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_group.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_object.name
        assert created_group.members == test_object.members
        assert created_group.folder == test_object.folder

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = ApplicationGroupFactory()

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

        with pytest.raises(APIError):
            self.client.create(test_data.model_dump())

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        test_data = ApplicationGroupFactory()

        # Mock a generic exception without response
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data.model_dump())
        assert str(exc_info.value) == "An unexpected error occurred"

    def test_create_malformed_response_handling(self):
        """
        **Objective:** Test handling of malformed response in create method.
        **Workflow:**
            1. Mocks a response that would cause a parsing error
            2. Verifies appropriate error handling
        """
        test_data = ApplicationGroupFactory()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(APIError):
            self.client.create(test_data.model_dump())


class TestApplicationGroupGet(TestApplicationGroupBase):
    """Tests for retrieving a specific Application Group object."""

    def test_get_object(self):
        """
        **Objective:** Test retrieving a specific object.
        **Workflow:**
            1. Mocks the API response for a specific group.
            2. Verifies the get request and response handling.
        """
        mock_response = {
            "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
            "name": "TestAppGroup",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        app_group_name = "TestAppGroup"
        get_object = self.client.get(app_group_name)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/application-groups/{app_group_name}"
        )
        assert isinstance(get_object, ApplicationGroupResponseModel)
        assert get_object.name == "TestAppGroup"
        assert get_object.members == [
            "office365-consumer-access",
            "office365-enterprise-access",
        ]

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
            2. Verifies APIError is raised with correct message
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.get(object_id)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestApplicationGroupUpdate(TestApplicationGroupBase):
    """Tests for updating Application Group objects."""

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
            "id": str(test_uuid),  # Use string for input data as it would come from API
            "name": "TestAppGroup",
            "folder": "Prisma Access",
            "members": [
                "office365-consumer-access",
                "office365-enterprise-access",
                "test123",
            ],
        }

        # Expected payload should not include the ID
        expected_payload = {
            "name": "TestAppGroup",
            "folder": "Prisma Access",
            "members": [
                "office365-consumer-access",
                "office365-enterprise-access",
                "test123",
            ],
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_group = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/application-groups/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_group, ApplicationGroupResponseModel)
        assert isinstance(updated_group.id, UUID)  # Verify it's a UUID object
        assert updated_group.id == test_uuid  # Compare against UUID object
        assert (
            str(updated_group.id) == update_data["id"]
        )  # Compare string representations
        assert updated_group.name == "TestAppGroup"
        assert "test123" in updated_group.members
        assert updated_group.folder == "Prisma Access"

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
            "name": "test-group",
            "folder": "Shared",
            "members": ["app1", "app2"],
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

        with pytest.raises(MalformedCommandError):
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

        with pytest.raises(APIError):
            self.client.update(invalid_data)

    def test_update_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in update method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-group",
            "folder": "Shared",
            "members": ["app1", "app2"],
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestApplicationGroupDelete(TestApplicationGroupBase):
    """Tests for deleting Application Group objects."""

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
            2. Verifies APIError is raised with correct message
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.delete(object_id)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestApplicationGroupFetch(TestApplicationGroupBase):
    """Tests for fetching an object by name."""

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
            "name": "Microsoft Office",
            "folder": "Shared",
            "members": ["office365", "ms-office"],
            "description": None,  # Should be excluded in the result
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/application-groups",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        # Verify result
        assert isinstance(fetched_object, dict)
        assert str(fetched_object["id"]) == mock_response["id"]
        assert fetched_object["name"] == mock_response["name"]
        assert fetched_object["members"] == mock_response["members"]

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
        with pytest.raises(APIError) as exc_info:  # noqa
            self.client.fetch(
                name=object_name,
                folder=folder_name,
            )

    def test_fetch_empty_name(self):
        """
        **Objective:** Test fetch with empty name parameter.
        **Workflow:**
            1. Attempts to fetch with empty name
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
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
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test no container provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-group")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-group", folder="Shared", snippet="TestSnippet")
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
            "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
            "name": "Microsoft 365 Access",
            "folder": "Shared",
            "snippet": "office365",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="TestApp", folder="Shared")

        # Verify None values are excluded
        assert "description" not in result
        assert result["name"] == mock_response["name"]
        assert result["folder"] == mock_response["folder"]

    def test_fetch_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in fetch method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"

    def test_fetch_unexpected_response_format(self):
        """
        Test fetching an object when the API returns an unexpected response format.

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
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

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
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

        # Test response with both id and data fields (invalid format)
        self.mock_scm.get.return_value = {  # noqa
            "id": "some-id",
            "data": [{"some": "data"}],
        }  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "An unexpected error occurred: 3 validation errors" in str(
            exc_info.value
        )

        # Test malformed response in list format
        self.mock_scm.get.return_value = [{"unexpected": "format"}]  # noqa
        with pytest.raises(APIError) as exc_info:
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
        with pytest.raises(ValueError) as exc_info:
            self.client.fetch(
                name="test",
                folder="Shared",
            )
        assert "Original error" in str(exc_info.value)


class TestApplicationGroupValidation(TestApplicationGroupBase):
    """Tests for Application Group validation."""

    def test_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_create_no_container(self):
        """Test validation when no container is provided."""
        data = {
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_create_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "Microsoft 365 Access",
            "folder": "Shared",
            "snippet": "office365",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_response_model_invalid_uuid(self):
        """Test validation of UUID format in response model."""
        invalid_data = {
            "id": "invalid-uuid",
            "name": "TestAppGroup",
            "members": ["app1", "app2"],
            "folder": "Shared",
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationGroupResponseModel(**invalid_data)
        assert "1 validation error for ApplicationGroupResponseModel" in str(
            exc_info.value
        )
        assert "Input should be a valid UUID, invalid character" in str(exc_info.value)


class TestApplicationGroupListFilters(TestApplicationGroupBase):
    """Tests for filtering during listing Application Group objects."""

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
            "/config/objects/v1/application-groups",
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
            2. Verifies BadRequestError is raised with correct message
            3. Tests valid filter types pass validation
        """
        mock_response = {
            "data": [
                {
                    "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
                    "name": "Microsoft 365 Access",
                    "folder": "Shared",
                    "snippet": "office365",
                    "members": [
                        "office365-consumer-access",
                        "office365-enterprise-access",
                    ],
                },
                {
                    "id": "0b12a889-4220-4cdd-b95f-506e0351a5e4",
                    "name": "Microsoft 365 Services",
                    "folder": "Shared",
                    "snippet": "office365",
                    "members": [
                        "ms-office365",
                        "ms-onedrive",
                        "ms-onenote",
                        "ms-lync-base",
                        "skype",
                    ],
                },
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid members filter (string instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", members="business-systems")
        assert str(exc_info.value) == "'members' filter must be a list"

        # Test invalid members filter (dict instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", members={"value": "business-systems"})
        assert str(exc_info.value) == "'members' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                members=["office365-consumer-access"],
            )
        except BadRequestError:
            pytest.fail("Unexpected BadRequestError raised with valid list filters")

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
                    "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
                    "name": "Microsoft 365 Access",
                    "folder": "Shared",
                    "snippet": "office365",
                    "members": [
                        "office365-consumer-access",
                        "office365-enterprise-access",
                    ],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Texas",
            members=[],
        )
        assert len(filtered_objects) == 0

    def test_list_empty_folder_error(self):
        """
        **Objective:** Test that empty folder raises appropriate error.
        **Workflow:**
            1. Attempts to list objects with empty folder
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

    def test_list_multiple_containers_error(self):
        """
        **Objective:** Test validation of container parameters.
        **Workflow:**
            1. Attempts to list with multiple containers
            2. Verifies InvalidObjectError is raised
        """
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
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

        with pytest.raises(APIError):
            self.client.list(folder="Shared")

        # Test invalid data format
        self.mock_scm.get.return_value = {"data": "not-a-list"}  # noqa

        with pytest.raises(APIError):
            self.client.list(folder="Shared")

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

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="NonexistentFolder")
        assert str(exc_info.value) == "An unexpected error occurred"

    def test_list_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in list method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert str(exc_info.value) == "An unexpected error occurred"


# -------------------- End of Test Classes --------------------
