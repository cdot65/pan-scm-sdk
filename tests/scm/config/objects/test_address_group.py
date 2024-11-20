# tests/scm/config/objects/test_address_group.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import AddressGroup
from scm.exceptions import (
    APIError,
    BadRequestError,
    InvalidObjectError,
    MalformedCommandError,
    MissingQueryParameterError,
    ObjectNotPresentError,
    ReferenceNotZeroError,
)
from scm.models.objects import AddressGroupResponseModel
from tests.factories import (
    AddressGroupCreateApiFactory,
    AddressGroupResponseFactory,
    AddressGroupUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestAddressGroupBase:
    """Base class for Address Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AddressGroup(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestAddressGroupList(TestAddressGroupBase):
    """Tests for listing Address Group objects."""

    def test_list_valid(self):
        """Test listing all address groups successfully."""
        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static(
                    id="123e4567-e89b-12d3-a456-426655440000",
                    name="static_group",
                    folder="Shared",
                    static=["address1", "address2"],
                    description="Static address group",
                ).model_dump(),
                AddressGroupResponseFactory.with_dynamic(
                    id="223e4567-e89b-12d3-a456-426655440000",
                    name="dynamic_group",
                    folder="Shared",
                    dynamic={"filter": "'tag1 and tag2'"},
                    description="Dynamic address group",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], AddressGroupResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "static_group"

    def test_list_folder_empty_error(self):
        """Test that an empty 'folder' parameter raises an error."""
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
            '"folder" is not allowed to be empty' in error_msg
            and "HTTP error: 400" in error_msg
            and "API error: E003" in error_msg
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
            "{'errorType': 'Operation Impossible'}" in error_msg
            and "HTTP error: 404" in error_msg
            and "API error: API_I00013" in error_msg
        )

    def test_list_container_missing_error(self):
        """Test that missing container parameter raises an error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list()

        error_msg = str(exc_info.value)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in error_msg
            and "HTTP error: 400" in error_msg
            and "API error: E003" in error_msg
        )

    def test_list_container_multiple_error(self):
        """Test that multiple container parameters raise an error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Multiple container types provided",
            error_type="Invalid Query Parameter",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")

        error_msg = str(exc_info.value)
        assert (
            "Multiple container types provided" in error_msg
            and "HTTP error: 400" in error_msg
            and "API error: E003" in error_msg
        )

    def test_list_filters_valid(self):
        """Test that valid filters are processed correctly."""
        filters = {
            "types": ["static"],
            "values": ["address1"],
            "tags": ["tag1"],
        }

        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static(
                    id="123e4567-e89b-12d3-a456-426655440000",
                    name="static_group",
                    folder="Shared",
                    static=["address1", "address2"],
                    description="Static address group",
                    tag=["tag1"],
                ).model_dump(),
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert len(result) == 1
        assert result[0].name == "static_group"

    def test_list_filters_invalid_types(self):
        """Test that invalid filter types raise BadRequestError."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'types' filter must be a list",
            error_type="Invalid Query Parameter",
        )

        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types="static")
        error_msg = str(exc_info.value)
        assert (
            "'types' filter must be a list" in error_msg
            and "HTTP error: 400" in error_msg
            and "API error: E003" in error_msg
        )

    def test_list_response_invalid_format(self):
        """Test that an invalid response format raises InvalidObjectError."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            "Invalid response format" in error_msg
            and "HTTP error: 500" in error_msg
            and "API error: E003" in error_msg
        )

    def test_list_server_error(self):
        """Test handling of server errors during list operation."""
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
            "An internal error occurred" in error_msg
            and "HTTP error: 500" in error_msg
            and "API error: E003" in error_msg
        )

    def test_list_http_error_no_response_content(self):
        """Test that an HTTPError without response content re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None  # Simulate no content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")


class TestAddressGroupCreate(TestAddressGroupBase):
    """Tests for creating Address Group objects."""

    def test_create_valid_type_static(self):
        """Test creating an address group with static type."""
        test_object = AddressGroupCreateApiFactory.with_static()
        mock_response = AddressGroupResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.static == test_object.static
        assert created_object.folder == test_object.folder

    def test_create_valid_type_dynamic(self):
        """Test creating an address group with dynamic type."""
        test_object = AddressGroupCreateApiFactory.with_dynamic()
        mock_response = AddressGroupResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.dynamic == test_object.dynamic
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
                {"name": "test", "static": ["address1", "address2"], "folder": "test"}
            )

    def test_create_http_error_with_response(self):
        """Test handling of HTTPError with response content."""
        test_data = {
            "name": "test-address-group",
            "folder": "Shared",
            "static": ["address1", "address2"],
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Create failed",
            error_type="Malformed Command",
        )

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.create(test_data)

        error_msg = str(exc_info.value)
        assert (
            "Create failed" in error_msg
            and "HTTP error: 400" in error_msg
            and "API error: API_I00013" in error_msg
        )

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(
                {"name": "test", "static": ["address1", "address2"], "folder": "test"}
            )
        assert str(exc_info.value) == "Generic error"


class TestAddressGroupGet(TestAddressGroupBase):
    """Tests for retrieving a specific Address Group object."""

    def test_get_valid_object(self):
        """Test retrieving a specific address group."""
        mock_response = AddressGroupResponseFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-group",
            folder="Shared",
            static=["address1", "address2"],
        ).model_dump()

        self.mock_scm.get.return_value = mock_response  # noqa
        object_id = mock_response["id"]

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{object_id}"
        )
        assert isinstance(retrieved_object, AddressGroupResponseModel)
        assert retrieved_object.id == mock_response["id"]
        assert retrieved_object.name == mock_response["name"]
        assert retrieved_object.static == mock_response["static"]
        assert retrieved_object.folder == mock_response["folder"]

    def test_get_object_not_present_error(self):
        """Test error handling when the address group is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.get(object_id)

        error_msg = str(exc_info.value)
        assert (
            "Object not found" in error_msg
            and "HTTP error: 404" in error_msg
            and "API error: API_I00013" in error_msg
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


class TestAddressGroupUpdate(TestAddressGroupBase):
    """Tests for updating Address Group objects."""

    def test_update_valid_object(self):
        """Test updating an address group with valid data."""
        update_data = AddressGroupUpdateApiFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-group",
            static=["address3", "address4"],
            description="Updated description",
            folder="Shared",
        )
        input_data = update_data.model_dump()

        mock_response = AddressGroupResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(input_data)

        expected_payload = input_data.copy()
        expected_payload.pop("id")

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{update_data.id}",
            json=expected_payload,
        )

        assert isinstance(updated_object, AddressGroupResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name
        assert updated_object.static == mock_response.static
        assert updated_object.description == mock_response.description
        assert updated_object.folder == mock_response.folder

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = AddressGroupUpdateApiFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-group",
            folder="Shared",
            static=["address1", "address2"],
        )
        input_data = update_data.model_dump()

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.update(input_data)

        error_msg = str(exc_info.value)
        assert (
            "Update failed" in error_msg
            and "HTTP error: 400" in error_msg
            and "API error: API_I00013" in error_msg
        )

    def test_update_object_not_present_error(self):
        """Test error handling when the address group to update is not present."""
        update_data = AddressGroupUpdateApiFactory.with_static(
            id="nonexistent-id",
            name="test-group",
            folder="Shared",
            static=["address1", "address2"],
        )
        input_data = update_data.model_dump()

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.update(input_data)

        error_msg = str(exc_info.value)
        assert (
            "Object not found" in error_msg
            and "HTTP error: 404" in error_msg
            and "API error: API_I00013" in error_msg
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
                {"id": "test-id", "name": "test", "static": ["address1", "address2"]}
            )

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(
                {"id": "test-id", "name": "test", "static": ["address1", "address2"]}
            )
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = AddressGroupUpdateApiFactory.with_static(
            id="test-id",
            name="test-group",
            folder="Shared",
            static=["address1", "address2"],
        )
        input_data = update_data.model_dump()

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.update(input_data)

        error_msg = str(exc_info.value)
        assert (
            "An internal error occurred" in error_msg
            and "HTTP error: 500" in error_msg
            and "API error: E003" in error_msg
        )


class TestAddressGroupDelete(TestAddressGroupBase):
    """Tests for deleting Address Group objects."""

    def test_delete_referenced_object(self):
        """Test deleting an address group that is referenced elsewhere."""
        object_id = "abcdefg"
        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=409,
            error_code="E009",
            message="Your configuration is not valid.",
            error_type="Reference Not Zero",
        )

        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(object_id)

        error_message = str(exc_info.value)
        assert (
            "Your configuration is not valid." in error_message
            and "HTTP error: 409" in error_message
            and "API error: E009" in error_message
        )

    def test_delete_object_not_present_error(self):
        """Test error handling when the address group to delete is not present."""
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
        assert (
            "Object not found" in error_message
            and "HTTP error: 404" in error_message
            and "API error: API_I00013" in error_message
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

        with pytest.raises(APIError) as exc_info:
            self.client.delete(object_id)

        error_message = str(exc_info.value)
        assert (
            "An internal error occurred" in error_message
            and "HTTP error: 500" in error_message
            and "API error: E003" in error_message
        )

    def test_delete_success(self):
        """Test successful deletion of an address group."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{object_id}"
        )


class TestAddressGroupFetch(TestAddressGroupBase):
    """Tests for fetching Address Group objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an address group by its name."""
        mock_response = AddressGroupResponseFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-group",
            folder="Shared",
            static=["address1", "address2"],
            description="Test address group",
        ).model_dump()

        self.mock_scm.get.return_value = mock_response  # noqa

        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        assert isinstance(fetched_object, dict)
        assert fetched_object["id"] == mock_response["id"]
        assert fetched_object["name"] == mock_response["name"]
        assert fetched_object["static"] == mock_response["static"]

    def test_fetch_object_not_present_error(self):
        """Test fetching an address group that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            "Object not found" in error_msg
            and "HTTP error: 404" in error_msg
            and "API error: API_I00013" in error_msg
        )

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty 'name' parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"name" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            '"name" is not allowed to be empty' in error_msg
            and "HTTP error: 400" in error_msg
            and "API error: E003" in error_msg
        )

    def test_fetch_empty_folder_error(self):
        """Test fetching with an empty 'folder' parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test-group", folder="")

        error_msg = str(exc_info.value)
        assert (
            '"folder" is not allowed to be empty' in error_msg
            and "HTTP error: 400" in error_msg
            and "API error: E003" in error_msg
        )

    def test_fetch_invalid_response_format_error(self):
        """Test fetching when the API returns an unexpected format."""
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-group", folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            "Invalid response format" in error_msg
            and "HTTP error: 500" in error_msg
            and "API error: E003" in error_msg
        )

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test-group", folder="Shared")

        assert str(exc_info.value) == "Generic error"

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-group", folder="Shared")


# -------------------- End of Test Classes --------------------
