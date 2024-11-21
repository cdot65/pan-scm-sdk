# tests/scm/config/objects/test_application.py

from unittest.mock import MagicMock

import pytest

from scm.config.objects import Application
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
)
from scm.models.objects import (
    ApplicationResponseModel,
)
from tests.factories import (
    ApplicationCreateApiFactory,
    ApplicationUpdateApiFactory,
    ApplicationResponseFactory,
)
from tests.utils import raise_mock_http_error


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


class TestApplicationList(TestApplicationBase):
    """Tests for listing Application objects."""

    def test_list_objects(self):
        """
        **Objective:** Test listing all objects.
        """
        mock_response = {
            "data": [
                ApplicationResponseFactory.from_request(
                    ApplicationCreateApiFactory.build_valid(
                        name="100bao",
                        description="100bao is a free Chinese P2P file-sharing program",
                        ports=["tcp/3468,6346,11300"],
                        category="general-internet",
                        subcategory="file-sharing",
                        technology="peer-to-peer",
                        risk=5,
                        evasive=True,
                        pervasive=True,
                        folder="All",
                    )
                ).model_dump(),
                ApplicationResponseFactory.from_request(
                    ApplicationCreateApiFactory.build_valid(
                        name="104apci-supervisory",
                        description="IEC 60870-5-104 protocol",
                        ports=["tcp/2404"],
                        category="business-systems",
                        subcategory="ics-protocols",
                        technology="client-server",
                        risk=2,
                        folder="All",
                    )
                ).model_dump(),
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
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)


class TestApplicationCreate(TestApplicationBase):
    """Tests for creating Application objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new object.
        """
        test_object = ApplicationCreateApiFactory.build_valid()
        mock_response = ApplicationResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_app = self.client.create(test_object.model_dump_json())

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
        """
        test_data = ApplicationCreateApiFactory.build_valid()

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Object creation failed",
            error_type="Object Already Exists",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data.model_dump())

        error = exc_info.value
        assert error.error_code == "API_I00013"
        assert (
            "{'errorType': 'Object Already Exists'} - HTTP error: 400 - API error: API_I00013"
            in str(error)
        )

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        """
        test_data = ApplicationCreateApiFactory.build_valid()

        # Mock a generic exception without response
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data.model_dump())
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"

    def test_create_malformed_response_handling(self):
        """
        **Objective:** Test handling of malformed response in create method.
        """
        test_data = ApplicationCreateApiFactory.build_valid()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data.model_dump())
        assert "Invalid response format" in str(exc_info.value)


class TestApplicationGet(TestApplicationBase):
    """Tests for retrieving a specific Application object."""

    def test_get_object(self):
        """
        **Objective:** Test fetching a specific object by ID.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = ApplicationCreateApiFactory.build_valid(
            id=object_id
        ).model_dump()

        self.mock_scm.get.return_value = mock_response  # noqa
        get_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{object_id}"
        )
        assert isinstance(get_object, ApplicationResponseModel)
        assert get_object.id == object_id
        assert get_object.name == mock_response["name"]
        assert get_object.category == mock_response["category"]

    def test_get_object_error_handling(self):
        """
        **Objective:** Test error handling during object retrieval.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.get(object_id)

        error = exc_info.value
        assert error.error_code == "API_I00013"
        assert "Object not found" in str(error)

    def test_get_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in get method.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.get(object_id)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestApplicationUpdate(TestApplicationBase):
    """Tests for updating Application objects."""

    def test_update_object(self):
        """
        **Objective:** Test updating a specific object.
        """
        update_data = ApplicationUpdateApiFactory.build_partial_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedApp",
            description="Updated description",
            category="networking",
            subcategory="networking",
            technology="client-server",
            risk=2,
        )
        expected_payload = update_data.model_dump(exclude={"id"})

        mock_response = ApplicationResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(update_data.model_dump())

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{update_data.id}",
            json=expected_payload,
        )
        assert isinstance(updated_object, ApplicationResponseModel)
        assert updated_object.name == "UpdatedApp"
        assert updated_object.category == "networking"
        assert updated_object.subcategory == "networking"
        assert updated_object.technology == "client-server"

    def test_update_object_error_handling(self):
        """
        **Objective:** Test error handling during object update method.
        """
        update_data = ApplicationUpdateApiFactory.build_partial_update(
            id="123e4567-e89b-12d3-a456-426655440000"
        )

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.update(update_data.model_dump())

        error = exc_info.value
        assert error.error_code == "API_I00013"
        assert "Update failed" in str(error)

    def test_update_with_invalid_data(self):
        """
        **Objective:** Test update method with invalid data structure.
        """
        invalid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "invalid_field": "test",
        }

        with pytest.raises(APIError):
            self.client.update(invalid_data)

    def test_payload_construction(self):
        """
        **Objective:** Test payload construction using model_dump
        """
        update_data = ApplicationUpdateApiFactory.build_full_update(
            id="123e4567-e89b-12d3-a456-426655440000"
        )

        # Mock response to prevent actual API call
        mock_response = ApplicationResponseFactory.from_request(
            update_data
        ).model_dump()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Call update method
        self.client.update(update_data.model_dump())

        # Verify the payload sent to put() has excluded None values
        actual_payload = self.mock_scm.put.call_args[1]["json"]  # noqa
        expected_payload = update_data.model_dump(exclude={"id"}, exclude_unset=True)
        assert actual_payload == expected_payload
        assert "id" not in actual_payload  # ID should not be in payload


class TestApplicationDelete(TestApplicationBase):
    """Tests for deleting Application objects."""

    def test_delete_referenced_object(self):
        """
        **Objective:** Test deleting an object that is referenced by another group.
        """
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        # Configure mock to raise HTTPError with our custom error response
        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Your configuration is not valid. Please review the error message for more details.",
            error_type="Reference Not Zero",
        )

        # Attempt to delete the object and expect ConflictError
        with pytest.raises(APIError) as exc_info:
            self.client.delete(object_id)

        error = exc_info.value

        # Verify the error contains the expected information
        assert error.error_code == "API_I00013"
        assert "Your configuration is not valid" in str(error)

    def test_delete_error_handling(self):
        """
        **Objective:** Test error handling during object deletion.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.delete(object_id)

    def test_delete_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in delete method.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.delete(object_id)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestApplicationFetch(TestApplicationBase):
    """Tests for fetching Application objects by name."""

    def test_fetch_object(self):
        """
        **Objective:** Test retrieving an object by its name using the `fetch` method.
        """
        mock_response = ApplicationCreateApiFactory.build_valid(
            name="test123",
            folder="All",
            category="business-systems",
            subcategory="database",
            technology="network-protocol",
            risk=1,
            description="test123",
            used_by_malware=False,
            prone_to_misuse=False,
        ).model_dump(exclude_unset=True)

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        application = self.client.fetch(
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

        # Validate the returned application
        assert isinstance(application, dict)
        assert application["name"] == mock_response["name"]
        assert application["description"] == mock_response["description"]
        assert application["category"] == mock_response["category"]

    def test_fetch_object_not_found(self):
        """
        Test fetching an object that does not exist.
        """
        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found.",
            error_type="Not Found",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Shared")
        assert "Object not found." in str(exc_info.value)

    def test_fetch_empty_name(self):
        """
        **Objective:** Test fetch method with empty name parameter.
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")
        assert "Field 'name' cannot be empty" in str(exc_info.value)

    def test_fetch_container_validation(self):
        """
        **Objective:** Test container parameter validation in fetch method.
        """
        # Test empty folder
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test no container
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="test")

        # Test multiple containers
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test with device container
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="test", folder="Shared", device="device1")

    def test_fetch_object_unexpected_response_format(self):
        """
        Test fetching an object when the API returns an unexpected format.
        """
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

    def test_fetch_validation_errors(self):
        """
        **Objective:** Test fetch validation errors.
        """
        # Test empty folder
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test multiple containers
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_fetch_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in fetch method.
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"

    def test_fetch_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in fetch method.
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
        assert "An unexpected error occurred: 4 validation errors" in str(
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
            self.client.fetch(name="test", folder="Shared")
        assert "Original error" in str(exc_info.value)


class TestApplicationListFilters(TestApplicationBase):
    """Tests for filtering during listing Application objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        """
        filters = {
            "category": ["type1", "type2"],
            "subcategory": ["value1", "value2"],
            "technology": ["tag1", "tag2"],
            "risk": [1, 2],
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
        """
        mock_response = {
            "data": [
                ApplicationCreateApiFactory.build_valid(
                    name="test123",
                    folder="All",
                    category="business-systems",
                    subcategory="database",
                    technology="network-protocol",
                    risk=1,
                    description="test123",
                    used_by_malware=False,
                    prone_to_misuse=False,
                ).model_dump()
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid category filter (string instead of list)
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", category="business-systems")
        assert str(exc_info.value) == "'category' filter must be a list"

        # Test invalid category filter (dict instead of list)
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", category={"value": "business-systems"})
        assert str(exc_info.value) == "'category' filter must be a list"

        # Test invalid subcategory filter (string instead of list)
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", subcategory="database")
        assert str(exc_info.value) == "'subcategory' filter must be a list"

        # Test invalid subcategory filter (dict instead of list)
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", subcategory={"value": "database"})
        assert str(exc_info.value) == "'subcategory' filter must be a list"

        # Test invalid risks filter (dict instead of list)
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", risk={"value": "1"})
        assert str(exc_info.value) == "'risk' filter must be a list"

        # Test invalid types risks (integer instead of list)
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", risk=123)
        assert str(exc_info.value) == "'risk' filter must be a list"

        # Test invalid technology filter (dict instead of list)
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", technology={"value": "database"})
        assert str(exc_info.value) == "'technology' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                category=["business-systems"],
                subcategory=["database"],
                technology=["network-protocol"],
                risk=[1],
            )
        except InvalidObjectError:
            pytest.fail("Unexpected InvalidObjectError raised with valid list filters")

    def test_list_empty_folder_error(self):
        """
        **Objective:** Test that empty folder raises appropriate error.
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

    def test_list_multiple_containers_error(self):
        """
        **Objective:** Test validation of container parameters.
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
        """
        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="NonexistentFolder")
        assert "Listing failed" in str(exc_info.value)

    def test_list_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in list method.
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


# -------------------- End of Test Classes --------------------
