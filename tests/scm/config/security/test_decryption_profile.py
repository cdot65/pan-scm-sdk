# tests/scm/config/security/test_decryption_profile.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.security import DecryptionProfile
from scm.exceptions import (
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
    ReferenceNotZeroError,
    APIError,
)
from scm.models.security.decryption_profiles import (
    DecryptionProfileResponseModel,
    SSLVersion,
)
from tests.factories import (
    DecryptionProfileCreateApiFactory,
    DecryptionProfileUpdateApiFactory,
    DecryptionProfileResponseFactory,
    SSLProtocolSettingsFactory,
    SSLForwardProxyFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestDecryptionProfileBase:
    """Base class for Decryption Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = DecryptionProfile(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestDecryptionProfileList(TestDecryptionProfileBase):
    """Tests for listing Decryption Profile objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                DecryptionProfileResponseFactory(
                    name="profile1",
                    folder="Shared",
                    ssl_protocol_settings=SSLProtocolSettingsFactory(),
                ).model_dump(),
                DecryptionProfileResponseFactory(
                    name="profile2",
                    folder="Shared",
                    ssl_forward_proxy=SSLForwardProxyFactory(),
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], DecryptionProfileResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "profile1"

    def test_list_folder_empty_error(self):
        """Test that an empty folder raises appropriate error."""
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
            "types": ["forward", "inbound", "no"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                DecryptionProfileResponseFactory(
                    name="profile1",
                    folder="Shared",
                    ssl_protocol_settings=SSLProtocolSettingsFactory(),
                ).model_dump()
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered_objects = self.client.list(
            folder="Shared",
            types=[],
        )
        assert len(filtered_objects) == 0

    def test_list_filters_types_validation(self):
        """Test validation of 'types' filter specifically."""
        mock_profiles = []

        # Test with string instead of list
        invalid_filters = {"types": "type1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_profiles, invalid_filters)

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

    def test_list_http_error_no_content(self):
        """Test handling of HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")


class TestDecryptionProfileCreate(TestDecryptionProfileBase):
    """Tests for creating Decryption Profile objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = DecryptionProfileCreateApiFactory.build()
        mock_response = DecryptionProfileResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()
        created_object = self.client.create(test_object.model_dump())

        self.mock_scm.post.assert_called_once_with(
            "/config/security/v1/decryption-profiles",
            json=test_object.model_dump(),
        )
        assert isinstance(created_object, DecryptionProfileResponseModel)
        assert created_object.name == test_object.name

    def test_create_http_error_no_content(self):
        """Test creation with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.create(
                {
                    "name": "test",
                    "folder": "Shared",
                    "ssl_protocol_settings": {
                        "min_version": "tls1-0",
                        "max_version": "tls1-2",
                    },
                }
            )

    def test_create_with_ssl_settings(self):
        """Test creating profile with SSL protocol settings."""
        test_object = DecryptionProfileCreateApiFactory.with_custom_ssl_settings(
            min_ver=SSLVersion.tls1_1,
            max_ver=SSLVersion.tls1_3,
        )

        mock_response = DecryptionProfileResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()

        created_object = self.client.create(test_object.model_dump())

        assert isinstance(created_object, DecryptionProfileResponseModel)
        assert created_object.ssl_protocol_settings.min_version == SSLVersion.tls1_1
        assert created_object.ssl_protocol_settings.max_version == SSLVersion.tls1_3

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-profile",
            "folder": "Shared",
            "ssl_protocol_settings": {
                "min_version": "tls1-0",
                "max_version": "tls1-2",
            },
        }

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
                    "name": "test-profile",
                    "folder": "Shared",
                    "ssl_protocol_settings": {
                        "min_version": "tls1-0",
                        "max_version": "tls1-2",
                    },
                }
            )
        assert str(exc_info.value) == "Generic error"


class TestDecryptionProfileGet(TestDecryptionProfileBase):
    """Tests for retrieving a specific Decryption Profile object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = DecryptionProfileResponseFactory.build()

        self.mock_scm.get.return_value = mock_response.model_dump()
        retrieved_object = self.client.get(str(mock_response.id))

        self.mock_scm.get.assert_called_once_with(
            f"/config/security/v1/decryption-profiles/{mock_response.id}"
        )
        assert isinstance(retrieved_object, DecryptionProfileResponseModel)
        assert retrieved_object.name == mock_response.name

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.get(object_id)

        assert "Object Not Present" in str(exc_info.value)

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

        with pytest.raises(APIError) as exc_info:
            self.client.get(object_id)

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Internal Error'} - HTTP error: 500 - API error: E003"
            in error_msg
        )


class TestDecryptionProfileUpdate(TestDecryptionProfileBase):
    """Tests for updating Decryption Profile objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = DecryptionProfileUpdateApiFactory.with_updated_ssl_settings(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-profile",
        )
        input_data = update_data.model_dump()

        # Create mock response
        mock_response = DecryptionProfileResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        # Perform update
        updated_object = self.client.update(input_data)

        # Assert the put method was called with correct parameters
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/security/v1/decryption-profiles/{update_data.id}",
            json=input_data,
        )

        assert isinstance(updated_object, DecryptionProfileResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = DecryptionProfileUpdateApiFactory.with_updated_ssl_settings(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
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

        assert (
            "{'errorType': 'Malformed Command'} - HTTP error: 400 - API error: API_I00013"
            in str(exc_info.value)
        )

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = DecryptionProfileUpdateApiFactory.with_updated_ssl_settings(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
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

        assert (
            "{'errorType': 'Object Not Present'} - HTTP error: 404 - API error: API_I00013"
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
                    "name": "test-profile",
                    "ssl_protocol_settings": {
                        "min_version": "tls1-0",
                        "max_version": "tls1-2",
                    },
                }
            )

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-profile",
                    "ssl_protocol_settings": {
                        "min_version": "tls1-0",
                        "max_version": "tls1-2",
                    },
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = DecryptionProfileUpdateApiFactory.with_updated_ssl_settings(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
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

        assert (
            "{'errorType': 'Internal Error'} - HTTP error: 500 - API error: E003"
            in str(exc_info.value)
        )


class TestDecryptionProfileDelete(TestDecryptionProfileBase):
    """Tests for deleting Decryption Profile objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(
            f"/config/security/v1/decryption-profiles/{object_id}"
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=409,
            error_code="E009",
            message="Reference not zero",
            error_type="Reference Not Zero",
        )

        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(object_id)

        assert "Reference Not Zero" in str(exc_info.value)

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
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
        assert "{'errorType': 'Internal Error'}" in error_message
        assert "HTTP error: 500" in error_message
        assert "API error: E003" in error_message


class TestDecryptionProfileFetch(TestDecryptionProfileBase):
    """Tests for fetching Decryption Profile objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = DecryptionProfileResponseFactory.build()
        mock_response_data = mock_response_model.model_dump()

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        assert isinstance(fetched_object, dict)
        assert fetched_object["id"] == mock_response_model.id
        assert fetched_object["name"] == mock_response_model.name

    def test_fetch_object_not_present_error(self):
        """Test fetching an object that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Shared")

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Object Not Present'}" in error_msg
        assert "HTTP error: 404" in error_msg
        assert "API error: API_I00013" in error_msg

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")

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
            self.client.fetch(name="test-profile", folder="Shared")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Internal Error'}" in error_msg
        assert "HTTP error: 500" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-profile",
            "folder": "Shared",
            "ssl_protocol_settings": {
                "min_version": "tls1-0",
                "max_version": "tls1-2",
            },
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile", folder="Shared")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Shared")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500


# -------------------- End of Test Classes --------------------
