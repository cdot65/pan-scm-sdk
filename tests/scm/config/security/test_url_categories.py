# tests/scm/config/security/test_url_categories.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.security import URLCategories
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.security.url_categories import (
    URLCategoriesResponseModel,
)
from tests.factories import (
    URLCategoriesCreateApiFactory,
    URLCategoriesUpdateApiFactory,
    URLCategoriesResponseFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestURLCategoriesBase:
    """Base class for DNS Security Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = URLCategories(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestURLCategoriesList(TestURLCategoriesBase):
    """Tests for listing URL Categories."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        test_object = URLCategoriesResponseFactory.build()
        mock_response = {
            "data": [
                test_object.model_dump(),
            ],
            "offset": 0,
            "total": 1,
            "limit": 10000,
        }

        self.mock_scm.get.return_value = mock_response
        existing_objects = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(
            "/config/security/v1/url-categories",
            params={
                "limit": 10000,
                "folder": "Texas",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], URLCategoriesResponseModel)
        assert len(existing_objects) == 1

    def test_list_folder_empty_error(self):
        """Test that an empty folder raises appropriate error."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_list_folder_nonexistent_error(self):
        """Test error handling in list operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

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
        """Test that filters are properly added to parameters."""
        filters = {
            "members": [
                "category1",
                "category2",
            ],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Texas", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/url-categories",
            params={
                "limit": 10000,
                "folder": "Texas",
            },
        )

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                URLCategoriesResponseFactory(
                    name="profile1",
                    folder="Texas",
                    list=[
                        "example.com",
                        "another-example.com",
                    ],
                ).model_dump()
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered_objects = self.client.list(
            folder="Texas",
            members=[],
        )
        assert len(filtered_objects) == 0

    def test_list_filters_types(self):
        """Test validation of filter types in list method."""
        # Mock response for successful case
        mock_response = {
            "data": [
                URLCategoriesResponseFactory(
                    name="profile1",
                    folder="Texas",
                    list=[
                        "example.com",
                        "another-example.com",
                    ],
                ).model_dump()
            ]
        }

        # Test invalid members filter (string instead of list)
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'members' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas", members="Kali")
        error_response = exc_info.value.response.json()
        assert (
            error_response["_errors"][0]["message"] == "'members' filter must be a list"
        )
        assert (
            error_response["_errors"][0]["details"]["errorType"]
            == "Invalid Query Parameter"
        )

        # Reset side effect for successful case
        self.mock_scm.get.side_effect = None  # noqa
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Texas",
                members=["Test1"],
            )
        except HTTPError:
            pytest.fail("Unexpected HTTPError raised with valid list filters")

    def test_list_filters_types_validation(self):
        """Test validation of 'types' filter specifically."""
        mock_dns_sec_profiles = []

        # Test with string instead of list
        invalid_filters = {"members": "type1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_dns_sec_profiles, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        # assert error.error_code == "E003"
        # assert "{'errorType': 'Invalid Object'}" in str(error)

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

    def test_list_http_error_no_content(self):
        """Test handling of HTTPError without content."""
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
        Test that exact_match=True returns only objects that match the container exactly.
        """
        mock_response = {
            "data": [
                URLCategoriesResponseFactory(
                    name="addr_in_texas",
                    folder="Texas",
                ).model_dump(),
                URLCategoriesResponseFactory(
                    name="addr_in_all",
                    folder="All",
                ).model_dump(),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # exact_match should exclude the one from "All"
        filtered = self.client.list(folder="Texas", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"
        assert filtered[0].name == "addr_in_texas"

    def test_list_exclude_folders(self):
        """
        Test that exclude_folders removes objects from those folders.
        """
        mock_response = {
            "data": [
                URLCategoriesResponseFactory(
                    name="addr_in_texas",
                    folder="Texas",
                ).model_dump(),
                URLCategoriesResponseFactory(
                    name="addr_in_all",
                    folder="All",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exclude_snippets(self):
        """
        Test that exclude_snippets removes objects with those snippets.
        """
        mock_response = {
            "data": [
                URLCategoriesResponseFactory(
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(),
                URLCategoriesResponseFactory(
                    name="addr_with_special_snippet",
                    folder="Texas",
                    snippet="special",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exclude_devices(self):
        """
        Test that exclude_devices removes objects with those devices.
        """
        mock_response = {
            "data": [
                URLCategoriesResponseFactory(
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                    device="DeviceA",
                ).model_dump(),
                URLCategoriesResponseFactory(
                    name="addr_with_special_snippet",
                    folder="Texas",
                    snippet="special",
                    device="DeviceB",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(a.device != "DeviceA" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """
        Test combining exact_match with exclusions.
        """
        mock_response = {
            "data": [
                URLCategoriesResponseFactory(
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(),
                URLCategoriesResponseFactory(
                    name="addr_with_special_snippet",
                    folder="Texas",
                    snippet="special",
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
        # Only addr_in_texas_special should remain
        assert len(filtered) == 1
        obj = filtered[0]
        assert obj.folder == "Texas"
        assert obj.snippet != "default"
        assert obj.device != "DeviceA"


class TestURLCategoriesCreate(TestURLCategoriesBase):
    """Tests for creating URL Categories."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = URLCategoriesCreateApiFactory.build()
        mock_response = URLCategoriesResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump())

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/url-categories",
            json=test_object.model_dump(),
        )
        assert isinstance(created_object, URLCategoriesResponseModel)
        assert created_object.name == test_object.name

    def test_create_http_error_no_content(self):
        """Test creation with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {"name": "test", "folder": "Texas", "list": ["example.com"]}
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-profile",
            "folder": "Texas",
            "list": [
                "example.com",
                "another-example.com",
            ],
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Create failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Create failed"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"
        )

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(
                {
                    "name": "test-profile",
                    "folder": "Texas",
                    "list": [
                        "test1",
                        "test2",
                    ],
                }
            )
        assert str(exc_info.value) == "Generic error"


class TestURLCategoriesGet(TestURLCategoriesBase):
    """Tests for retrieving a specific DNS Security Profile object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = URLCategoriesResponseFactory.build()

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        retrieved_object = self.client.get(str(mock_response.id))

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/url-categories/{mock_response.id}"
        )
        assert isinstance(retrieved_object, URLCategoriesResponseModel)
        assert retrieved_object.name == mock_response.name

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_get_generic_exception_handling(self):
        """Test generic exception handling in get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get(object_id)

        assert str(exc_info.value) == "Generic error"

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

    def test_get_server_error(self):
        """Test handling of server errors during get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestURLCategoriesUpdate(TestURLCategoriesBase):
    """Tests for updating URL Categories."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = URLCategoriesUpdateApiFactory.with_updated_list(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-category",
            description="Updated URL category",
        )

        # Create mock response
        mock_response = URLCategoriesResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()

        # Perform update
        updated_object = self.client.update(update_data)

        # Verify call was made once
        self.mock_scm.put.assert_called_once()

        # Get the actual call arguments
        call_args = self.mock_scm.put.call_args

        # Check endpoint
        assert call_args[0][0] == f"/config/security/v1/url-categories/{update_data.id}"

        # Check important payload fields
        payload = call_args[1]["json"]
        assert payload["name"] == "updated-category"
        assert payload["description"] == "Updated URL category"

        # Assert the updated object matches the mock response
        assert isinstance(updated_object, URLCategoriesResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name
        assert updated_object.description == mock_response.description

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = URLCategoriesUpdateApiFactory.build()

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

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = URLCategoriesUpdateApiFactory.build()

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        # Create test data using factory
        update_data = URLCategoriesUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            botnet_domains={},
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

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        # Create test data as Pydantic model
        update_data = URLCategoriesUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            botnet_domains={},
        )

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        # Create test data
        update_data = URLCategoriesUpdateApiFactory.build()

        # Use utility function to simulate server error
        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestURLCategoriesDelete(TestURLCategoriesBase):
    """Tests for deleting URL Categories."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/url-categories/{object_id}"
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=409,
            error_code="E009",
            message="Reference not zero",
            error_type="Reference Not Zero",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Reference not zero"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"
        )

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
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

    def test_delete_generic_exception_handling(self):
        """Test handling of a generic exception during delete."""
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdefg")

        assert str(exc_info.value) == "Generic error"

    def test_delete_server_error(self):
        """Test handling of server errors during delete."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestURLCategoriesFetch(TestURLCategoriesBase):
    """Tests for fetching URL Categories by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = URLCategoriesResponseFactory.build()
        mock_response_data = mock_response_model.model_dump()

        # Set the mock to return the response data directly
        self.mock_scm.get.return_value = mock_response_data  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/url-categories",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )
        # Validate the returned object is a Pydantic model
        assert isinstance(fetched_object, URLCategoriesResponseModel)

        # Validate the object attributes match the mock response
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.folder == mock_response_model.folder

    def test_fetch_object_not_present_error(self):
        """Test fetching an object that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Texas")

        error_msg = str(exc_info.value)
        assert '"name" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")

        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-profile",
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
            self.client.fetch(name="test-profile", folder="Texas")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-profile",
            "folder": "Texas",
            "botnet_domains": {},
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
