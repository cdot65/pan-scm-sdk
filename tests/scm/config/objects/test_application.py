# tests/scm/config/objects/test_application.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import Application
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import ApplicationResponseModel
from tests.factories import (
    ApplicationCreateApiFactory,
    ApplicationResponseFactory,
    ApplicationUpdateApiFactory,
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
        self.client = Application(self.mock_scm, max_limit=5000)  # noqa
        yield
        # Reset mock methods after each test
        self.mock_scm.get.reset_mock()
        self.mock_scm.post.reset_mock()
        self.mock_scm.put.reset_mock()
        self.mock_scm.delete.reset_mock()


# -------------------- Unit Tests --------------------


@pytest.mark.unit
class TestApplicationMaxLimit(TestApplicationBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = Application(self.mock_scm)  # noqa
        assert client.max_limit == Application.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = Application(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = Application(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Application(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Application(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Application(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


# -------------------- Integration Tests --------------------


@pytest.mark.integration
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
        existing_objects = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "limit": 5000,
                "folder": "Texas",
                "offset": 0,
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
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
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

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="NonexistentFolder")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Listing failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Operation Impossible"

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

        result = self.client.list(folder="Texas", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "limit": 5000,
                "folder": "Texas",
                "offset": 0,
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
            folder="Texas",
            category=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            subcategory=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            technology=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
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
        assert isinstance(exc_info.value, InvalidObjectError)

        # Test with string instead of list for subcategory
        invalid_filters = {"subcategory": "subcategory1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_applications, invalid_filters)
        assert isinstance(exc_info.value, InvalidObjectError)

        # Test with string instead of list for technology
        invalid_filters = {"technology": "technology1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_applications, invalid_filters)
        assert isinstance(exc_info.value, InvalidObjectError)

        # Test with integer instead of list for risk
        invalid_filters = {"risk": 5}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_applications, invalid_filters)
        assert isinstance(exc_info.value, InvalidObjectError)

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when API returns response with missing data field."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when API returns non-list data field."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

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
            self.client.list(folder="Texas")

    # -------------------- New Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """
        Test that exact_match=True returns only applications that match the container exactly.
        """
        mock_response = {
            "data": [
                ApplicationResponseFactory(
                    name="app_in_texas",
                    folder="Texas",
                    category="general-internet",
                ).model_dump(),
                ApplicationResponseFactory(
                    name="app_in_all",
                    folder="All",
                    category="general-internet",
                ).model_dump(),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exact_match=True)
        # exact_match should exclude the one from "All"
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"
        assert filtered[0].name == "app_in_texas"

    def test_list_exclude_folders(self):
        """
        Test that exclude_folders removes applications from those folders.
        """
        mock_response = {
            "data": [
                ApplicationResponseFactory(
                    name="app_in_texas",
                    folder="Texas",
                    category="general-internet",
                ).model_dump(),
                ApplicationResponseFactory(
                    name="app_in_all",
                    folder="All",
                    category="general-internet",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exclude_snippets(self):
        """
        Test that exclude_snippets removes applications from those snippets.
        Assume snippet is supported by ApplicationResponseModel and ApplicationResponseFactory.
        """
        mock_response = {
            "data": [
                ApplicationResponseFactory(
                    name="app_default_snippet",
                    folder="Texas",
                    snippet="default",
                    category="general-internet",
                ).model_dump(),
                ApplicationResponseFactory(
                    name="app_special_snippet",
                    folder="Texas",
                    snippet="special",
                    category="general-internet",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """
        Test combining exact_match with exclusions.
        Assume snippet and device are supported by ApplicationResponseModel.
        """
        mock_response = {
            "data": [
                ApplicationResponseFactory(
                    name="app_texas_default_deviceA",
                    folder="Texas",
                    snippet="default",
                    device="DeviceA",
                    category="general-internet",
                ).model_dump(),
                ApplicationResponseFactory(
                    name="app_texas_special_deviceB",
                    folder="Texas",
                    snippet="special",
                    device="DeviceB",
                    category="general-internet",
                ).model_dump(),
                ApplicationResponseFactory(
                    name="app_all_default_deviceA",
                    folder="All",
                    snippet="default",
                    device="DeviceA",
                    category="general-internet",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(
            folder="Texas",
            exact_match=True,
            exclude_folders=["All"],
            exclude_snippets=["default"],
            exclude_devices=["DeviceA"],
        )

        # Only app_texas_special_deviceB should remain after all filters
        assert len(filtered) == 1
        obj = filtered[0]
        assert obj.folder == "Texas"
        assert obj.snippet != "default"

    def test_list_pagination_multiple_pages(self):
        """
        Test that the list method correctly aggregates data from multiple pages.
        Using a custom client with max_limit=2500 to test pagination.
        """
        client = Application(self.mock_scm, max_limit=2500)  # noqa

        # Create test data for three pages
        first_page = [
            ApplicationResponseFactory(
                name=f"p2p-app-page1-{i}",
                folder="Texas",
                category="general-internet",
                subcategory="file-sharing",
                technology="peer-to-peer",
                risk=5,
                evasive=True,
                pervasive=True,
                ports=["tcp/3468,6346,11300"],
            ).model_dump()
            for i in range(2500)
        ]

        second_page = [
            ApplicationResponseFactory(
                name=f"business-app-page2-{i}",
                folder="Texas",
                category="business-systems",
                subcategory="ics-protocols",
                technology="client-server",
                risk=2,
                ports=["tcp/2404"],
            ).model_dump()
            for i in range(2500)
        ]

        third_page = [
            ApplicationResponseFactory(
                name=f"web-app-page3-{i}",
                folder="Texas",
                category="web-applications",
                subcategory="social-networking",
                technology="browser-based",
                risk=3,
                ports=["tcp/443,80"],
            ).model_dump()
            for i in range(2500)
        ]

        # Mock API responses for pagination
        mock_responses = [
            {"data": first_page},
            {"data": second_page},
            {"data": third_page},
            {"data": []},  # Empty response to end pagination
        ]
        self.mock_scm.get.side_effect = mock_responses  # noqa

        # Get results
        results = client.list(folder="Texas")

        # Verify results
        assert len(results) == 7500  # Total objects across all pages
        assert isinstance(results[0], ApplicationResponseModel)
        assert all(isinstance(obj, ApplicationResponseModel) for obj in results)

        # Verify API calls
        assert self.mock_scm.get.call_count == 4  # noqa # Three pages + one final check

        # Verify API calls were made with correct offset values
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/applications",
            params={"folder": "Texas", "limit": 2500, "offset": 0},
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/applications",
            params={"folder": "Texas", "limit": 2500, "offset": 2500},
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/applications",
            params={"folder": "Texas", "limit": 2500, "offset": 5000},
        )

        # Verify content ordering and application-specific attributes
        # First page - P2P applications
        assert results[0].name == "p2p-app-page1-0"
        assert results[0].category == "general-internet"
        assert results[0].subcategory == "file-sharing"
        assert results[0].technology == "peer-to-peer"
        assert results[0].risk == 5
        assert results[0].evasive is True
        assert results[0].pervasive is True

        # Second page - Business applications
        assert results[2500].name == "business-app-page2-0"
        assert results[2500].category == "business-systems"
        assert results[2500].subcategory == "ics-protocols"
        assert results[2500].technology == "client-server"
        assert results[2500].risk == 2

        # Third page - Web applications
        assert results[5000].name == "web-app-page3-0"
        assert results[5000].category == "web-applications"
        assert results[5000].subcategory == "social-networking"
        assert results[5000].technology == "browser-based"
        assert results[5000].risk == 3


@pytest.mark.integration
class TestApplicationCreate(TestApplicationBase):
    """Tests for creating Application objects."""

    def test_create_valid_object(self):
        """Test creating an object."""
        test_object = ApplicationCreateApiFactory()
        mock_response = ApplicationResponseFactory(**test_object.model_dump())

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert isinstance(created_object, ApplicationResponseModel)
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.folder == test_object.folder


@pytest.mark.integration
class TestApplicationGet(TestApplicationBase):
    """Tests for retrieving a specific Application object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = ApplicationResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-app",
            folder="Texas",
            category="general-internet",
            subcategory="file-sharing",
            technology="peer-to-peer",
            risk=5,
        )

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        object_id = mock_response.id

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{object_id}"
        )
        assert isinstance(retrieved_object, ApplicationResponseModel)
        assert retrieved_object.id == mock_response.id
        assert retrieved_object.name == mock_response.name
        assert retrieved_object.folder == mock_response.folder


@pytest.mark.integration
class TestApplicationUpdate(TestApplicationBase):
    """Tests for updating Application objects."""

    def test_update_valid_object(self):
        """Test updating an application with valid data."""
        update_data = ApplicationUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-app",
            description="Updated description",
            category="networking",
            subcategory="networking",
            technology="client-server",
            risk=2,
        )

        mock_response = ApplicationResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa
        call_args = self.mock_scm.put.call_args  # noqa
        assert call_args[0][0] == f"/config/objects/v1/applications/{update_data.id}"

        payload = call_args[1]["json"]
        assert payload["name"] == "updated-app"
        assert payload["description"] == "Updated description"
        assert payload["category"] == "networking"
        assert payload["subcategory"] == "networking"
        assert payload["technology"] == "client-server"
        assert payload["risk"] == 2

        assert isinstance(updated_object, ApplicationResponseModel)
        assert str(updated_object.id) == str(mock_response.id)
        assert updated_object.name == mock_response.name
        assert updated_object.description == mock_response.description
        assert updated_object.category == mock_response.category
        assert updated_object.subcategory == mock_response.subcategory
        assert updated_object.technology == mock_response.technology
        assert updated_object.risk == mock_response.risk


@pytest.mark.integration
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


@pytest.mark.integration
class TestApplicationFetch(TestApplicationBase):
    """Tests for fetching Application objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an application by its name."""
        mock_response_model = ApplicationResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-app",
            folder="Texas",
            category="general-internet",
            subcategory="file-sharing",
            technology="peer-to-peer",
            risk=5,
            description="Test application",
        )
        mock_response_data = mock_response_model.model_dump()

        self.mock_scm.get.return_value = mock_response_data  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        # Validate the returned object
        assert isinstance(fetched_object, ApplicationResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.folder == mock_response_model.folder
        assert fetched_object.category == mock_response_model.category
        assert fetched_object.subcategory == mock_response_model.subcategory
        assert fetched_object.technology == mock_response_model.technology
        assert fetched_object.risk == mock_response_model.risk
        assert fetched_object.description == mock_response_model.description

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Texas")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'name', 'error': '\"name\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_fetch_empty_folder_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test-app", folder="")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-app",
            "folder": "Texas",
            "category": "general-internet",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-app", folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)


# -------------------- Mock Tests --------------------


@pytest.mark.mock
class TestApplicationCreateErrorHandling(TestApplicationBase):
    """Mock tests for error handling in create operations."""

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
        """Test that ErrorHandler.raise_for_error is called with appropriate arguments."""
        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="API_I00013",
            message="Error occurred",
            error_type="Malformed Command",
        )

        test_data = {
            "name": "test-app",
            "category": "general-internet",
            "folder": "test",
            "technology": "peer-to-peer",
            "risk": 5,
            "subcategory": "file-sharing",
        }

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"


@pytest.mark.mock
class TestApplicationGetErrorHandling(TestApplicationBase):
    """Mock tests for error handling in get operations."""

    def test_get_object_not_present_error(self):
        """Test error handling when the application is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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


@pytest.mark.mock
class TestApplicationUpdateErrorHandling(TestApplicationBase):
    """Mock tests for error handling in update operations."""

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = ApplicationUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-app",
            description="Updated description",
            category="networking",
            subcategory="networking",
            technology="client-server",
            risk=2,
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Update failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = ApplicationUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            category="general-internet",
            subcategory="file-sharing",
            technology="peer-to-peer",
            risk=2,
        )

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)


@pytest.mark.mock
class TestApplicationDeleteErrorHandling(TestApplicationBase):
    """Mock tests for error handling in delete operations."""

    def test_delete_object_not_present_error(self):
        """Test error handling when the application to delete is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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


@pytest.mark.mock
class TestApplicationFetchErrorHandling(TestApplicationBase):
    """Mock tests for error handling in fetch operations."""

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-app", folder="Texas")

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-app", folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

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
                folder="Texas",
                snippet="TestSnippet",
            )

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_error_handler(self):
        """Test error handler behavior in fetch method with properly formatted error response."""
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

        mock_http_error = HTTPError(response=mock_error_response)
        mock_http_error.response = mock_error_response

        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test-app", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"


# -------------------- Parametrized Tests --------------------


@pytest.mark.parametrized
class TestApplicationParametrized(TestApplicationBase):
    """Parametrized tests for Application functionality."""

    @pytest.mark.parametrize(
        "category,subcategory,technology,risk",
        [
            ("general-internet", "file-sharing", "peer-to-peer", 5),
            ("business-systems", "ics-protocols", "client-server", 2),
            ("web-applications", "social-networking", "browser-based", 3),
        ],
    )
    def test_create_application_types(self, category, subcategory, technology, risk):
        """Test creating applications with different types."""
        test_object = ApplicationCreateApiFactory(
            category=category, subcategory=subcategory, technology=technology, risk=risk
        )

        mock_response = ApplicationResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        # Verify the application attributes match the expected values
        assert created_object.category == category
        assert created_object.subcategory == subcategory
        assert created_object.technology == technology
        assert created_object.risk == risk


# -------------------- Functional Tests --------------------


@pytest.mark.functional
def test_application_lifecycle(mock_scm):
    """Functional test for complete application object lifecycle (CRUD)."""
    # Setup
    mock_scm.get = MagicMock()
    mock_scm.post = MagicMock()
    mock_scm.put = MagicMock()
    mock_scm.delete = MagicMock()
    client = Application(mock_scm, max_limit=5000)

    # 1. Create application
    create_data = {
        "name": "test-app-lifecycle",
        "folder": "Texas",
        "category": "web-applications",
        "subcategory": "social-networking",
        "technology": "browser-based",
        "risk": 3,
        "description": "Lifecycle test application",
        "ports": ["tcp/443,80"],
    }

    app_id = "123e4567-e89b-12d3-a456-426655440000"
    mock_create_response = {
        "id": app_id,
        "name": "test-app-lifecycle",
        "folder": "Texas",
        "category": "web-applications",
        "subcategory": "social-networking",
        "technology": "browser-based",
        "risk": 3,
        "description": "Lifecycle test application",
        "ports": ["tcp/443,80"],
    }
    mock_scm.post.return_value = mock_create_response

    created = client.create(create_data)
    assert str(created.id) == app_id
    assert created.name == "test-app-lifecycle"

    # 2. List applications
    mock_list_response = {"data": [mock_create_response], "offset": 0, "total": 1, "limit": 100}
    mock_scm.get.return_value = mock_list_response

    apps = client.list(folder="Texas")
    assert len(apps) == 1
    assert str(apps[0].id) == app_id

    # 3. Get specific application
    mock_scm.get.return_value = mock_create_response

    retrieved = client.get(app_id)
    assert str(retrieved.id) == app_id

    # 4. Update application
    update_data = ApplicationUpdateApiFactory(
        id=app_id,
        name="test-app-lifecycle",
        folder="Texas",
        category="web-applications",
        subcategory="social-networking",
        technology="browser-based",
        risk=3,
        description="Updated lifecycle test application",
        ports=["tcp/443,80,8080"],
    )

    mock_update_response = {
        "id": app_id,
        "name": "test-app-lifecycle",
        "folder": "Texas",
        "category": "web-applications",
        "subcategory": "social-networking",
        "technology": "browser-based",
        "risk": 3,
        "description": "Updated lifecycle test application",
        "ports": ["tcp/443,80,8080"],
    }
    mock_scm.put.return_value = mock_update_response

    updated = client.update(update_data)
    assert updated.description == "Updated lifecycle test application"
    assert updated.ports == ["tcp/443,80,8080"]

    # 5. Delete application
    mock_scm.delete.return_value = None

    # Should not raise any exceptions
    client.delete(app_id)
    mock_scm.delete.assert_called_once_with(f"/config/objects/v1/applications/{app_id}")


# -------------------- End of Test Classes --------------------
