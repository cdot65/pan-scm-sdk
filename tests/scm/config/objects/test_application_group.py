# tests/scm/config/objects/test_application_group.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import ApplicationGroup
from scm.exceptions import (
    InvalidObjectError,
    ObjectNotPresentError,
    MissingQueryParameterError,
    BadRequestError,
    APIError,
    MalformedCommandError,
)
from scm.models.objects import ApplicationGroupResponseModel
from tests.factories import (
    ApplicationGroupCreateApiFactory,
    ApplicationGroupUpdateApiFactory,
    ApplicationGroupResponseFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestApplicationGroupBase:
    """Base class for Application Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = ApplicationGroup(self.mock_scm)


class TestApplicationGroupList(TestApplicationGroupBase):
    """Tests for listing Application Group objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                ApplicationGroupResponseFactory(
                    name="Microsoft 365 Access",
                    folder="Shared",
                    members=[
                        "office365-consumer-access",
                        "office365-enterprise-access",
                    ],
                ).model_dump(),
                ApplicationGroupResponseFactory(
                    name="Microsoft 365 Services",
                    folder="Shared",
                    members=["ms-office365", "ms-onedrive"],
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/application-groups",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], ApplicationGroupResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "Microsoft 365 Access"

    def test_list_folder_empty_error(self):
        """Test that empty folder raises appropriate error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)

        assert (
            "['\"folder\" is not allowed to be empty'] - HTTP error: 400 - API error: E003"
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

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.list(folder="NonexistentFolder")

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Operation Impossible'} - HTTP error: 404 - API error: API_I00013"
            in error_msg
        )

    def test_list_container_missing_error(self):
        """
        Test that InvalidObjectError is raised when no container parameter is provided.
        """
        # Use the utility function to create the mock HTTP error
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()
        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_container_multiple_error(self):
        """Test validation of container parameters."""
        # Use the utility function to create the mock HTTP error
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Multiple container types provided",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_filters_valid(self):
        """Test that filters are properly added to parameters."""
        filters = {
            "members": ["type1", "type2"],
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

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                {
                    "id": "24613eca-f875-4ebc-b4c3-045711dfe283",
                    "name": "web-apps",
                    "folder": "Texas",
                    "members": ["ssl"],
                }
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Shared",
            members=[],
        )
        assert len(filtered_objects) == 0

    def test_list_filters_types(self):
        """Test validation of filter types in list method."""
        # Mock response for successful case
        mock_response = {
            "data": [
                {
                    "id": "24613eca-f875-4ebc-b4c3-045711dfe283",
                    "name": "web-apps",
                    "folder": "Texas",
                    "members": ["ssl"],
                }
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }

        # Test invalid types filter (string instead of list)
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'members' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types="netmask")
        assert (
            "{'errorType': 'Invalid Query Parameter'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

        # Reset side effect for successful case
        self.mock_scm.get.side_effect = None  # noqa
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                members=["ssl"],
            )
        except BadRequestError:
            pytest.fail("Unexpected BadRequestError raised with valid list filters")

    def test_list_filters_members_validation(self):
        """Test validation of 'members' filter specifically."""
        mock_application_groups = []

        # Test with string instead of list
        invalid_filters = {"members": "tag1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_application_groups, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        # assert error.error_code == "E003"
        # assert "{'errorType': 'Invalid Object'}" in str(error)

        # Test with dict instead of list
        invalid_filters = {"members": {"tag": "tag1"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_application_groups, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        # assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_response_invalid_format(self):
        """
        Test that InvalidObjectError is raised when the response is not a dictionary.
        """
        # Mock the API client to return a non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """
        Test that InvalidObjectError is raised when API returns response with missing data field.

        This tests the case where the API response is a dictionary but missing the required 'data' field,
        expecting an InvalidObjectError with specific error details.
        """
        # Mock the API to return a dictionary without 'data' field
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_list_response_invalid_data_field_type(self):
        """
        Test that InvalidObjectError is raised when API returns non-list data field.

        This tests the case where the API response's 'data' field is not a list,
        expecting an InvalidObjectError with specific error details.
        """
        # Mock the API to return a response where 'data' is not a list
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500

    def test_list_response_no_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None  # Simulate no content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")

    def test_list_server_error(self):
        """Test generic exception handling in list method."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Internal Error'} - HTTP error: 500 - API error: E003"
            in error_msg
        )


class TestApplicationGroupCreate(TestApplicationGroupBase):
    """Tests for creating Application Group objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = ApplicationGroupCreateApiFactory()
        mock_response = ApplicationGroupResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/application-groups",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.members == test_object.members
        assert created_object.folder == test_object.folder

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        # Create a mock response object without content
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)

        # Set the side effect of the post method to raise the HTTPError
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {"name": "test", "members": ["app1"], "folder": "test"},
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-address",
            "folder": "Shared",
            "members": [
                "office365-consumer-access",
                "office365-enterprise-access",
            ],
        }

        # Use the utility function to create the mock HTTP error
        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Create failed",
            error_type="Malformed Command",
        )

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.create(test_data)

        assert (
            "{'errorType': 'Malformed Command'} - HTTP error: 400 - API error: API_I00013"
            in str(exc_info.value)
        )

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(
                {
                    "name": "test-address",
                    "folder": "Shared",
                    "members": [
                        "office365-consumer-access",
                        "office365-enterprise-access",
                    ],
                }
            )
        assert str(exc_info.value) == "Generic error"


class TestApplicationGroupGet(TestApplicationGroupBase):
    """Tests for retrieving a specific Application Group object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = ApplicationGroupResponseFactory(
            name="TestGroup",
            members=["app1", "app2"],
            folder="Shared",
        )

        self.mock_scm.get.return_value = mock_response.model_dump()
        object_id = mock_response.id

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(
            f"/config/objects/v1/application-groups/{object_id}"
        )
        assert isinstance(retrieved_object, ApplicationGroupResponseModel)
        assert retrieved_object.id == mock_response.id
        assert retrieved_object.name == mock_response.name
        assert retrieved_object.members == mock_response.members

    def test_get_object_not_present_error(self):
        """Test error handling when object doesn't exist."""
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
        mock_response.content = None  # Simulate no content
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

        with pytest.raises(APIError) as exc_info:
            self.client.get(object_id)

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Internal Error'} - HTTP error: 500 - API error: E003"
            in error_msg
        )


class TestApplicationGroupUpdate(TestApplicationGroupBase):
    """Tests for updating Application Group objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = ApplicationGroupUpdateApiFactory.with_members(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestApplicationGroup",
            members=["tag1", "tag2"],
            folder="Shared",
        )
        input_data = update_data.model_dump()

        # Create mock response
        mock_response = ApplicationGroupResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        # Perform update
        updated_object = self.client.update(input_data)

        # Assert the put method was called with correct parameters
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/application-groups/{update_data.id}",
            json=input_data,
        )

        # Assert the updated object matches the mock response
        assert isinstance(updated_object, ApplicationGroupResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name
        assert updated_object.members == mock_response.members

    def test_update_object_not_present_error(self):
        """Test error handling when object to update doesn't exist."""
        update_data = ApplicationGroupUpdateApiFactory().model_dump()

        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.update(update_data)


class TestApplicationGroupDelete(TestApplicationGroupBase):
    """Tests for deleting Application Group objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(
            f"/config/objects/v1/application-groups/{object_id}"
        )

    def test_delete_object_not_present_error(self):
        """Test error handling when object to delete doesn't exist."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.delete(object_id)

        assert "Object Not Present" in str(exc_info.value)


class TestApplicationGroupFetch(TestApplicationGroupBase):
    """Tests for fetching Application Group objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by name."""
        mock_response = ApplicationGroupResponseFactory(
            name="TestGroup",
            members=["app1", "app2"],
            folder="Shared",
        ).model_dump()

        self.mock_scm.get.return_value = mock_response

        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/application-groups",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )
        assert fetched_object["id"] == mock_response["id"]
        assert fetched_object["name"] == mock_response["name"]

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="", folder="Shared")

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="test", folder="")
