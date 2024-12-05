# tests/scm/config/objects/test_application_filters.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import ApplicationFilters
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.objects import ApplicationFiltersResponseModel
from tests.factories import (
    ApplicationFiltersResponseFactory,
    ApplicationFiltersCreateApiFactory,
    ApplicationFiltersUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestApplicationsFilterBase:
    """Base class for Application filter tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = ApplicationFilters(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestApplicationsFiltersList(TestApplicationsFilterBase):
    """Tests for listing Application filter objects."""

    def test_list_valid(self):
        """Test listing all application filters successfully."""
        mock_response = {
            "data": [
                ApplicationFiltersResponseFactory(
                    name="All Web Applications",
                    category=None,
                    sub_category=None,
                    technology=None,
                    evasive=False,
                    used_by_malware=False,
                    transfers_files=False,
                    has_known_vulnerabilities=False,
                    tunnels_other_apps=False,
                    prone_to_misuse=False,
                    pervasive=False,
                    is_saas=False,
                    new_appid=False,
                    risk=None,
                    saas_certifications=None,
                    saas_risk=None,
                    folder="All",
                ).model_dump(),
                ApplicationFiltersResponseFactory(
                    name="New Web Applications",
                    category=None,
                    sub_category=None,
                    technology=None,
                    evasive=False,
                    used_by_malware=False,
                    transfers_files=False,
                    has_known_vulnerabilities=False,
                    tunnels_other_apps=False,
                    prone_to_misuse=False,
                    pervasive=False,
                    is_saas=False,
                    new_appid=True,
                    risk=None,
                    saas_certifications=None,
                    saas_risk=None,
                    folder="All",
                ).model_dump(),
                ApplicationFiltersResponseFactory(
                    name="High Risk Applications",
                    category=None,
                    sub_category=None,
                    technology=None,
                    evasive=False,
                    used_by_malware=False,
                    transfers_files=False,
                    has_known_vulnerabilities=False,
                    tunnels_other_apps=False,
                    prone_to_misuse=False,
                    pervasive=False,
                    is_saas=False,
                    new_appid=False,
                    risk=[5],
                    saas_certifications=None,
                    saas_risk=None,
                    folder="All",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/application-filters",
            params={
                "limit": 10000,
                "folder": "Texas",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], ApplicationFiltersResponseModel)
        assert len(existing_objects) == 3

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
        assert (
            error_response["_errors"][0]["details"]["errorType"]
            == "Operation Impossible"
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
                ApplicationFiltersResponseFactory(
                    id="123e4567-e89b-12d3-a456-426655440000",
                    name="test123",
                    folder="All",
                    category=["general-internet"],
                    sub_category=["file-sharing"],  # Fixed attribute name
                    technology=["peer-to-peer"],
                    risk=[5],
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
            "/config/objects/v1/application-filters",
            params={
                "limit": 10000,
                "folder": "Texas",
            },
        )
        assert len(result) == 1
        assert result[0].name == "test123"

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                ApplicationFiltersResponseFactory(
                    name="test-app",
                    folder="All",
                    category=["general-internet"],
                    subcategory=["file-sharing"],
                    technology=["peer-to-peer"],
                    risk=[5],
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


class TestApplicationsFiltersCreate(TestApplicationsFilterBase):
    """Tests for creating Application filter objects."""

    def test_create_valid_object(self):
        """Test creating an object with ip_netmask."""
        test_object = ApplicationFiltersCreateApiFactory.with_folder()
        mock_response = ApplicationFiltersResponseFactory(**test_object.model_dump())

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/application-filters",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert isinstance(created_object, ApplicationFiltersResponseModel)
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.folder == test_object.folder

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
                    "category": ["general-internet"],
                    "folder": "test",
                    "technology": ["peer-to-peer"],
                    "risk": [5],
                    "subcategory": ["file-sharing"],
                }
            )

    def test_create_error_handler(self):
        """Test that ErrorHandler.raise_for_error is called with appropriate arguments."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="API_I00013",
            message="Error occurred",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test-group", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Error occurred"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"
        )


class TestApplicationsFiltersGet(TestApplicationsFilterBase):
    """Tests for retrieving a specific Application filter object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = ApplicationFiltersResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-app",
            folder="Texas",
            category=["general-internet"],
            subcategory=["file-sharing"],
            technology=["peer-to-peer"],
            risk=[5],
        )

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        object_id = mock_response.id

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/application-filters/{object_id}"
        )
        assert isinstance(retrieved_object, ApplicationFiltersResponseModel)
        assert retrieved_object.id == mock_response.id
        assert retrieved_object.name == mock_response.name
        assert retrieved_object.folder == mock_response.folder

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
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
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


class TestApplicationsFiltersUpdate(TestApplicationsFilterBase):
    """Tests for updating Application filter objects."""

    def test_update_valid_object(self):
        """Test updating an application with valid data."""
        # Create update data using factory
        update_data = ApplicationFiltersUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-app-filter",
            category=["networking"],
            sub_category=["networking"],
            technology=["client-server"],
            risk=[2],
        )

        # Create mock response
        mock_response = ApplicationFiltersResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        # Perform update with Pydantic model directly
        updated_object = self.client.update(update_data)

        # Verify call was made once
        self.mock_scm.put.assert_called_once()  # noqa

        # Get the actual call arguments
        call_args = self.mock_scm.put.call_args  # noqa

        # Check endpoint
        assert (
            call_args[0][0]
            == f"/config/objects/v1/application-filters/{update_data.id}"
        )

        # Check important payload fields
        payload = call_args[1]["json"]
        assert payload["name"] == "updated-app-filter"
        assert payload["category"] == ["networking"]
        assert payload["sub_category"] == ["networking"]
        assert payload["technology"] == ["client-server"]
        assert payload["risk"] == [2]

        # Assert the updated object matches the mock response
        assert isinstance(updated_object, ApplicationFiltersResponseModel)
        assert str(updated_object.id) == str(mock_response.id)
        assert updated_object.name == mock_response.name
        assert updated_object.category == mock_response.category
        assert updated_object.sub_category == mock_response.sub_category
        assert updated_object.technology == mock_response.technology
        assert updated_object.risk == mock_response.risk

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        # Create update data using factory
        update_data = ApplicationFiltersUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-app-filter",
            category=["networking"],
            subcategory=["networking"],
            technology=["client-server"],
            risk=[2],
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
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"
        )

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        # Create test data using factory
        update_data = ApplicationFiltersUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            category=["general-internet"],
            subcategory=["file-sharing"],
            technology=["peer-to-peer"],
            risk=[2],
        )

        # Create mock response without content
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        # Create HTTPError with mock response
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        # Test with Pydantic model
        with pytest.raises(HTTPError):
            self.client.update(update_data)


class TestApplicationsFiltersDelete(TestApplicationsFilterBase):
    """Tests for deleting Application filter objects."""

    def test_delete_success(self):
        """Test successful deletion of an application."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/application-filters/{object_id}"
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

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

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


class TestApplicationsFiltersFetch(TestApplicationsFilterBase):
    """Tests for fetching Application filter objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an application by its name."""
        mock_response_model = ApplicationFiltersResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-app-filter",
            folder="Texas",
            category=["general-internet"],
            subcategory=["file-sharing"],
            technology=["peer-to-peer"],
            risk=[5],
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
            "/config/objects/v1/application-filters",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        # Validate the returned object
        assert isinstance(fetched_object, ApplicationFiltersResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.folder == mock_response_model.folder
        assert fetched_object.category == mock_response_model.category
        assert fetched_object.sub_category == mock_response_model.sub_category
        assert fetched_object.technology == mock_response_model.technology
        assert fetched_object.risk == mock_response_model.risk

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

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
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


# -------------------- End of Test Classes --------------------
