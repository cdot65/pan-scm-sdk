# tests/scm/config/objects/test_application.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import Application
from scm.exceptions import (
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
)
from scm.models.objects import ApplicationResponseModel
from tests.factories import (
    ApplicationCreateApiFactory,
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

    def test_list_valid(self):
        """Test listing all applications successfully."""
        mock_response = {
            "data": [
                ApplicationResponseFactory(
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
                ).model_dump(),
                ApplicationResponseFactory(
                    name="104apci-supervisory",
                    description="IEC 60870-5-104 protocol",
                    ports=["tcp/2404"],
                    category="business-systems",
                    subcategory="ics-protocols",
                    technology="client-server",
                    risk=2,
                    folder="All",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], ApplicationResponseModel)
        assert len(existing_objects) == 2

    def test_list_folder_empty_error(self):
        """Test that an empty 'folder' parameter raises an error."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert (
            "['\"folder\" is not allowed to be empty'] - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_list_folder_nonexistent_error(self):
        """Test error handling when listing in a nonexistent folder."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.list(folder="NonexistentFolder")

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Operation Impossible'} - HTTP error: 404 - API error: API_I00013"
            in error_msg
        )

    def test_list_container_missing_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_container_multiple_error(self):
        """Test validation of container parameters."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_filters_valid(self):
        """Test that valid filters are processed correctly."""
        filters = {
            "category": ["general-internet"],
            "subcategory": ["file-sharing"],
            "technology": ["peer-to-peer"],
            "risk": [5],
        }

        mock_response = {
            "data": [
                ApplicationResponseFactory(
                    id="123e4567-e89b-12d3-a456-426655440000",
                    name="100bao",
                    folder="All",
                    category="general-internet",
                    subcategory="file-sharing",
                    technology="peer-to-peer",
                    risk=5,
                    description="100bao is a free Chinese P2P file-sharing program",
                    evasive=True,
                    pervasive=True,
                ).model_dump(),
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert len(result) == 1
        assert result[0].name == "100bao"

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                ApplicationResponseFactory(
                    name="test-app",
                    folder="All",
                    category="general-internet",
                    subcategory="file-sharing",
                    technology="peer-to-peer",
                    risk=5,
                ).model_dump(),
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
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

    def test_list_filters_validation(self):
        """Test validation of filter types specifically."""
        mock_applications = []

        # Test with string instead of list for category
        invalid_filters = {"category": "category1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_applications, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

        # Test with string instead of list for subcategory
        invalid_filters = {"subcategory": "subcategory1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_applications, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

        # Test with string instead of list for technology
        invalid_filters = {"technology": "technology1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_applications, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

        # Test with integer instead of list for risk
        invalid_filters = {"risk": 5}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_applications, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when API returns response with missing data field."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when API returns non-list data field."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_list_response_no_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")


class TestApplicationCreate(TestApplicationBase):
    """Tests for creating Application objects."""

    def test_create_valid_object(self):
        """Test creating an application with valid data."""
        test_object = ApplicationCreateApiFactory(
            name="test-app",
            description="Test application",
            category="general-internet",
            subcategory="file-sharing",
            technology="peer-to-peer",
            risk=5,
            ports=["tcp/80,443"],
            folder="Shared",
        )
        mock_response = ApplicationResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name=test_object.name,
            description=test_object.description,
            category=test_object.category,
            subcategory=test_object.subcategory,
            technology=test_object.technology,
            risk=test_object.risk,
            ports=test_object.ports,
            folder=test_object.folder,
        )

        # Mock response needs to be a MagicMock with json method
        mock_api_response = MagicMock()
        mock_api_response.json.return_value = mock_response.model_dump()
        self.mock_scm.post.return_value = mock_api_response  # noqa

        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert isinstance(created_object, ApplicationResponseModel)
        assert created_object.name == test_object.name
        assert created_object.category == test_object.category
        assert created_object.risk == test_object.risk

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {
                    "name": "test",
                    "category": "general-internet",
                    "folder": "test",
                    "technology": "peer-to-peer",
                    "risk": 5,
                    "subcategory": "file-sharing",
                }
            )

    def test_create_error_handler(self):
        """Test error handling with ErrorHandler in create method."""
        test_data = {
            "name": "test-app",
            "description": "Test application",
            "category": "general-internet",
            "subcategory": "file-sharing",
            "technology": "peer-to-peer",
            "risk": 5,
            "folder": "Shared",
        }

        # Create a mock response with properly formatted error content
        mock_error_response = MagicMock()
        mock_error_response.json.return_value = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Error occurred",
                    "details": {"errorType": "Malformed Command"},
                }
            ]
        }
        mock_error_response.status_code = 400
        mock_error_response.content = b"Error content"

        mock_http_error = HTTPError(response=mock_error_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.create(test_data)

        assert (
            "{'errorType': 'Malformed Command'} - HTTP error: 400 - API error: API_I00013"
            in str(exc_info.value)
        )


class TestApplicationGet(TestApplicationBase):
    """Tests for retrieving a specific Application object."""

    def test_get_valid_object(self):
        """Test retrieving a specific application."""
        mock_response = ApplicationResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-app",
            folder="Shared",
            category="general-internet",
            subcategory="file-sharing",
            technology="peer-to-peer",
            risk=5,
        )

        # Mock response needs to be a MagicMock with json method
        mock_api_response = MagicMock()
        mock_api_response.json.return_value = mock_response.model_dump()
        self.mock_scm.get.return_value = mock_api_response  # noqa

        object_id = mock_response.id

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{object_id}"
        )
        assert isinstance(retrieved_object, ApplicationResponseModel)
        assert retrieved_object.id == mock_response.id
        assert retrieved_object.name == mock_response.name
        assert retrieved_object.category == mock_response.category
        assert retrieved_object.risk == mock_response.risk

    def test_get_object_not_present_error(self):
        """Test error handling when the application is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.get(object_id)

        assert (
            "{'errorType': 'Object Not Present'} - HTTP error: 404 - API error: API_I00013"
            in str(exc_info.value)
        )

    def test_get_http_error_no_response_content(self):
        """Test get method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.get(object_id)


class TestApplicationUpdate(TestApplicationBase):
    """Tests for updating Application objects."""

    def test_update_valid_object(self):
        """Test updating an application with valid data."""
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-app",
            "description": "Updated description",
            "category": "networking",
            "subcategory": "networking",
            "technology": "client-server",
            "risk": 2,
        }

        # Create mock response that matches ApplicationResponseModel requirements
        mock_response = {
            "id": update_data["id"],
            "name": update_data["name"],
            "description": update_data["description"],
            "category": update_data["category"],
            "subcategory": update_data["subcategory"],
            "technology": update_data["technology"],
            "risk": update_data["risk"],
            "folder": "Shared",  # Required field
        }

        # Mock response needs to be a MagicMock with json method
        mock_api_response = MagicMock()
        mock_api_response.json.return_value = mock_response
        self.mock_scm.put.return_value = mock_response  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{update_data['id']}",
            json={k: v for k, v in update_data.items() if k != "id"},
        )

        assert isinstance(updated_object, ApplicationResponseModel)
        assert updated_object.name == mock_response["name"]
        assert updated_object.category == mock_response["category"]
        assert updated_object.risk == mock_response["risk"]

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        test_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-app",
            "category": "invalid-category",
            "subcategory": "invalid-subcategory",
            "technology": "client-server",
            "risk": 2,
        }

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.update(test_data)

        assert (
            "{'errorType': 'Malformed Command'} - HTTP error: 400 - API error: API_I00013"
            in str(exc_info.value)
        )

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test",
                    "category": "general-internet",
                    "subcategory": "file-sharing",
                    "technology": "peer-to-peer",
                    "risk": 2,
                }
            )


class TestApplicationDelete(TestApplicationBase):
    """Tests for deleting Application objects."""

    def test_delete_success(self):
        """Test successful deletion of an application."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{object_id}"
        )

    def test_delete_object_not_present_error(self):
        """Test error handling when the application to delete is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.delete(object_id)

        error_message = str(exc_info.value)
        assert "{'errorType': 'Object Not Present'}" in error_message
        assert "HTTP error: 404" in error_message
        assert "API error: API_I00013" in error_message

    def test_delete_http_error_no_response_content(self):
        """Test delete method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.delete(object_id)


class TestApplicationFetch(TestApplicationBase):
    """Tests for fetching Application objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an application by its name."""
        mock_response = ApplicationResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-app",
            folder="Shared",
            category="general-internet",
            subcategory="file-sharing",
            technology="peer-to-peer",
            risk=5,
            description="Test application",
        ).model_dump()

        self.mock_scm.get.return_value = mock_response  # noqa

        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        assert isinstance(fetched_object, dict)
        assert fetched_object["id"] == mock_response["id"]
        assert fetched_object["name"] == mock_response["name"]
        assert fetched_object["category"] == mock_response["category"]

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            "['\"name\" is not allowed to be empty'] - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_fetch_empty_folder_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test-app", folder="")

        error_msg = str(exc_info.value)
        assert (
            "['\"folder\" is not allowed to be empty'] - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-app")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-app",
                folder="Shared",
                snippet="TestSnippet",
            )

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-app", folder="Shared")

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-app", folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_fetch_error_handler(self):
        """Test error handler behavior in fetch method with properly formatted error response."""
        # Create a mock response with properly formatted error content
        mock_error_response = MagicMock()
        mock_error_response.json.return_value = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Object not found",
                    "details": {"errorType": "Object Not Present"},
                }
            ]
        }
        mock_error_response.status_code = 404
        mock_error_response.content = b"Error content"

        # Create HTTPError with our mock response
        mock_http_error = HTTPError(response=mock_error_response)
        mock_http_error.response = mock_error_response

        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Shared")

        error = exc_info.value
        assert isinstance(error, ObjectNotPresentError)
        assert error.error_code == "API_I00013"
        assert error.http_status_code == 404
        assert (
            "{'errorType': 'Object Not Present'} - HTTP error: 404 - API error: API_I00013"
            in str(error)
        )

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-app",
            "folder": "Shared",
            "category": "general-internet",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-app", folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)


# -------------------- End of Test Classes --------------------
