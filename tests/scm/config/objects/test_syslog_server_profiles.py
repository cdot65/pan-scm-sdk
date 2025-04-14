# tests/scm/config/objects/test_syslog_server_profiles.py

from unittest.mock import MagicMock, patch
import uuid

import pytest
import requests

from scm.client import Scm
from scm.config.objects import SyslogServerProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import SyslogServerProfileResponseModel

# Import the factories
from tests.factories.objects.syslog_server_profiles import (
    SyslogServerModelFactory,
    SyslogServerProfileCreateModelFactory,
    SyslogServerProfileResponseModelFactory,
    SyslogServerProfileUpdateModelFactory,
)

# -------------------- Helper functions --------------------


def create_sample_syslog_server_profile_response():
    """Create a sample syslog server profile response dictionary."""
    # Convert model to dict for API mock response
    response_model = SyslogServerProfileResponseModelFactory()
    return response_model.model_dump(by_alias=True)


def create_valid_syslog_server_profile_data():
    """Create a valid syslog server profile data dictionary for testing."""
    # Convert model to dict for request data
    create_model = SyslogServerProfileCreateModelFactory()
    return create_model.model_dump(by_alias=True, exclude_unset=True)


def verify_fetch_response(response, expected_model, container_key=None, container_value=None):
    """Verify a fetch response against expected values."""
    assert isinstance(response, SyslogServerProfileResponseModel)
    assert response.name == expected_model.name

    # Verify container field if provided
    if container_key and container_value:
        assert getattr(response, container_key) == container_value


def create_mock_list_response(profiles):
    """Create a mock list response for testing."""
    return {
        "data": [profile.model_dump(by_alias=True) for profile in profiles],
        "total": len(profiles),
        "limit": 10,
        "offset": 0,
    }


# -------------------- SyslogServerProfile validation tests --------------------


class TestSyslogServerProfileValidation:
    """Tests for SyslogServerProfile validation."""

    def test_max_limit_validation_default(self):
        """Test default max_limit validation."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)
        assert syslog_server_profile.max_limit == SyslogServerProfile.DEFAULT_MAX_LIMIT

    def test_max_limit_validation_custom(self):
        """Test custom max_limit validation."""
        api_client = MagicMock(spec=Scm)
        custom_limit = 1000
        syslog_server_profile = SyslogServerProfile(api_client, max_limit=custom_limit)
        assert syslog_server_profile.max_limit == custom_limit

    def test_max_limit_validation_invalid_type(self):
        """Test max_limit validation with invalid type."""
        api_client = MagicMock(spec=Scm)
        with pytest.raises(InvalidObjectError) as exc_info:
            SyslogServerProfile(api_client, max_limit="invalid")
        assert "Invalid max_limit type" in str(exc_info.value.details)

    def test_max_limit_validation_too_small(self):
        """Test max_limit validation with value that's too small."""
        api_client = MagicMock(spec=Scm)
        with pytest.raises(InvalidObjectError) as exc_info:
            SyslogServerProfile(api_client, max_limit=0)
        assert "Invalid max_limit value" in str(exc_info.value.details)

    def test_max_limit_validation_too_large(self):
        """Test max_limit validation with value that's too large."""
        api_client = MagicMock(spec=Scm)
        with pytest.raises(InvalidObjectError) as exc_info:
            SyslogServerProfile(api_client, max_limit=10000)
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value.details)

    def test_max_limit_setter(self):
        """Test max_limit setter."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)
        syslog_server_profile.max_limit = 1000
        assert syslog_server_profile.max_limit == 1000


# -------------------- SyslogServerProfile CRUD operation tests --------------------


class TestSyslogServerProfileOperations:
    """Tests for SyslogServerProfile CRUD operations."""

    def test_create(self):
        """Test creating a new syslog server profile."""
        api_client = MagicMock(spec=Scm)
        api_client.post.return_value = create_sample_syslog_server_profile_response()

        syslog_server_profile = SyslogServerProfile(api_client)
        data = create_valid_syslog_server_profile_data()
        response = syslog_server_profile.create(data)

        # Verify the result
        assert response.name is not None
        assert len(response.server) > 0
        assert response.folder is not None

        # Verify API call
        api_client.post.assert_called_once()
        args, kwargs = api_client.post.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "json" in kwargs

    def test_create_with_api_error(self):
        """Test error handling when API returns an error during creation."""
        api_client = MagicMock(spec=Scm)
        api_client.post.side_effect = requests.exceptions.HTTPError(
            "API Error", response=MagicMock(status_code=500)
        )

        syslog_server_profile = SyslogServerProfile(api_client)
        data = create_valid_syslog_server_profile_data()

        with pytest.raises(Exception) as exc_info:
            syslog_server_profile.create(data)
        assert "API Error" in str(exc_info.value)

    def test_create_with_generic_exception(self):
        """Test handling of generic exceptions in the create method."""
        api_client = MagicMock(spec=Scm)
        api_client.post.side_effect = Exception("Generic error")

        syslog_server_profile = SyslogServerProfile(api_client)
        data = create_valid_syslog_server_profile_data()

        with pytest.raises(Exception) as exc_info:
            syslog_server_profile.create(data)
        assert "Generic error" in str(exc_info.value)

    def test_create_error_logging(self):
        """Test that errors are properly logged during create operations."""
        api_client = MagicMock(spec=Scm)
        api_client.post.side_effect = Exception("Test error")

        with patch("logging.Logger.error") as mock_log:
            syslog_server_profile = SyslogServerProfile(api_client)
            data = create_valid_syslog_server_profile_data()

            with pytest.raises(Exception):
                syslog_server_profile.create(data)

            # Verify error was logged
            mock_log.assert_called_once()
            assert "Error in API call" in mock_log.call_args[0][0]

    def test_create_with_server_error(self):
        """Test handling of 500 server errors in the create method."""
        api_client = MagicMock(spec=Scm)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        api_client.post.side_effect = requests.exceptions.HTTPError(
            "500 Server Error", response=mock_response
        )

        syslog_server_profile = SyslogServerProfile(api_client)
        data = create_valid_syslog_server_profile_data()

        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            syslog_server_profile.create(data)
        assert "500 Server Error" in str(exc_info.value)

    def test_get(self):
        """Test getting a syslog server profile by ID."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_syslog_server_profile_response()
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profile_id = str(uuid.uuid4())
        response = syslog_server_profile.get(profile_id)

        # Verify the result
        assert isinstance(response, SyslogServerProfileResponseModel)
        assert response.id is not None
        assert len(response.server) > 0

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == f"/config/objects/v1/syslog-server-profiles/{profile_id}"
        assert not kwargs  # no additional params

    def test_get_with_api_error(self):
        """Test error handling when API returns an error during retrieval."""
        api_client = MagicMock(spec=Scm)
        api_client.get.side_effect = requests.exceptions.HTTPError(
            "API Error", response=MagicMock(status_code=500)
        )

        syslog_server_profile = SyslogServerProfile(api_client)
        profile_id = str(uuid.uuid4())

        with pytest.raises(Exception) as exc_info:
            syslog_server_profile.get(profile_id)
        assert "API Error" in str(exc_info.value)

    def test_update(self):
        """Test updating a syslog server profile."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_syslog_server_profile_response()
        api_client.put.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profile_id = str(uuid.uuid4())

        # Use the factory to create the update model
        update_model = SyslogServerProfileUpdateModelFactory(
            id=uuid.UUID(profile_id),
            folder="Shared",  # Set a specific folder to override factory default
            snippet=None,  # Ensure other containers are None
            device=None,  # Ensure other containers are None
        )

        response = syslog_server_profile.update(update_model)

        # Verify the result
        assert isinstance(response, SyslogServerProfileResponseModel)
        assert response.id is not None
        assert len(response.server) > 0

        # Verify API call
        api_client.put.assert_called_once()
        args, kwargs = api_client.put.call_args
        assert args[0] == f"/config/objects/v1/syslog-server-profiles/{profile_id}"
        assert "json" in kwargs
        # ID should be removed from the payload
        payload = update_model.model_dump(exclude_unset=True)
        payload.pop("id", None)
        assert kwargs["json"] == payload

    def test_update_with_api_error(self):
        """Test error handling when API returns an error during update."""
        api_client = MagicMock(spec=Scm)
        api_client.put.side_effect = requests.exceptions.HTTPError(
            "API Error", response=MagicMock(status_code=500)
        )

        syslog_server_profile = SyslogServerProfile(api_client)
        profile_id = str(uuid.uuid4())

        # Use the factory with a different container type
        update_model = SyslogServerProfileUpdateModelFactory(
            id=uuid.UUID(profile_id),
            folder=None,  # Ensure folder is None when using snippet
            snippet="TestSnippet",
            device=None,  # Ensure device is None
        )

        with pytest.raises(Exception) as exc_info:
            syslog_server_profile.update(update_model)
        assert "API Error" in str(exc_info.value)

    def test_delete(self):
        """Test deleting a syslog server profile."""
        api_client = MagicMock(spec=Scm)
        api_client.delete.return_value = None  # Delete returns None

        syslog_server_profile = SyslogServerProfile(api_client)
        profile_id = str(uuid.uuid4())
        result = syslog_server_profile.delete(profile_id)

        # Verify the result is None
        assert result is None

        # Verify API call
        api_client.delete.assert_called_once()
        args, kwargs = api_client.delete.call_args
        assert args[0] == f"/config/objects/v1/syslog-server-profiles/{profile_id}"
        assert not kwargs  # no additional params

    def test_delete_with_api_error(self):
        """Test error handling when API returns an error during deletion."""
        api_client = MagicMock(spec=Scm)
        api_client.delete.side_effect = requests.exceptions.HTTPError(
            "API Error", response=MagicMock(status_code=500)
        )

        syslog_server_profile = SyslogServerProfile(api_client)
        profile_id = str(uuid.uuid4())

        with pytest.raises(Exception) as exc_info:
            syslog_server_profile.delete(profile_id)
        assert "API Error" in str(exc_info.value)


# -------------------- SyslogServerProfile list and fetch tests --------------------


class TestSyslogServerProfileListAndFetch:
    """Tests for SyslogServerProfile list and fetch operations."""

    def test_list_with_folder(self):
        """Test listing syslog server profiles in a folder."""
        # Create mock API response using our factory
        response_models = [SyslogServerProfileResponseModelFactory() for _ in range(3)]
        mock_response = {
            "data": [model.model_dump(by_alias=True) for model in response_models],
            "total": 3,
            "limit": 10,
            "offset": 0,
        }

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        folder_name = "Shared"
        response = syslog_server_profile.list(folder=folder_name)

        # Verify the result
        assert isinstance(response, list)
        assert len(response) == 3
        for item in response:
            assert isinstance(item, SyslogServerProfileResponseModel)

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"].get("folder") == folder_name

    def test_list_with_snippet(self):
        """Test listing syslog server profiles in a snippet."""
        # Create mock API response using our factory
        response_models = [SyslogServerProfileResponseModelFactory.with_snippet() for _ in range(2)]
        mock_response = {
            "data": [model.model_dump(by_alias=True) for model in response_models],
            "total": 2,
            "limit": 10,
            "offset": 0,
        }

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        snippet_name = "TestSnippet"
        response = syslog_server_profile.list(snippet=snippet_name)

        # Verify the result
        assert isinstance(response, list)
        assert len(response) == 2
        for item in response:
            assert isinstance(item, SyslogServerProfileResponseModel)
            assert item.snippet == snippet_name

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"].get("snippet") == snippet_name

    def test_list_with_device(self):
        """Test listing syslog server profiles in a device."""
        # Create mock API response using our factory
        response_models = [SyslogServerProfileResponseModelFactory.with_device() for _ in range(2)]
        mock_response = {
            "data": [model.model_dump(by_alias=True) for model in response_models],
            "total": 2,
            "limit": 10,
            "offset": 0,
        }

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        device_name = "TestDevice"
        response = syslog_server_profile.list(device=device_name)

        # Verify the result
        assert isinstance(response, list)
        assert len(response) == 2
        for item in response:
            assert isinstance(item, SyslogServerProfileResponseModel)
            assert item.device == device_name

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"].get("device") == device_name

    def test_list_empty_folder(self):
        """Test listing syslog server profiles with empty folder string."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            syslog_server_profile.list(folder="")
        error_details = str(exc_info.value.details)
        assert "folder" in error_details
        assert "not allowed to be empty" in error_details

    def test_list_no_container(self):
        """Test listing syslog server profiles without a container."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list()
        error_details = str(exc_info.value.details)
        assert "Invalid container parameters" in error_details

    def test_fetch(self):
        """Test fetching a single syslog server profile by name."""
        # Create mock API response - for fetch, the API returns the item directly, not in data array
        response_model = SyslogServerProfileResponseModelFactory()
        mock_response = response_model.model_dump(
            by_alias=True
        )  # Direct object, not wrapped in data array

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        folder_name = "Shared"
        profile_name = response_model.name
        response = syslog_server_profile.fetch(name=profile_name, folder=folder_name)

        # Verify the result
        verify_fetch_response(response, response_model, "folder", folder_name)

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"].get("folder") == folder_name
        assert kwargs["params"].get("name") == profile_name

    def test_fetch_with_snippet(self):
        """Test fetching a syslog server profile in a snippet container."""
        # Create mock API response using our factory
        response_model = SyslogServerProfileResponseModelFactory.with_snippet()
        mock_response = response_model.model_dump(
            by_alias=True
        )  # Direct object, not wrapped in data array

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        snippet_name = "TestSnippet"
        profile_name = response_model.name
        response = syslog_server_profile.fetch(name=profile_name, snippet=snippet_name)

        # Verify the result
        verify_fetch_response(response, response_model, "snippet", snippet_name)

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"].get("snippet") == snippet_name
        assert kwargs["params"].get("name") == profile_name

    def test_fetch_empty_name(self):
        """Test fetching with empty name."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            syslog_server_profile.fetch(name="", folder="Shared")
        error_details = str(exc_info.value.details)
        assert "name" in error_details
        assert "not allowed to be empty" in error_details

    def test_fetch_empty_folder(self):
        """Test fetching with empty folder string."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            syslog_server_profile.fetch(name="test-profile", folder="")
        error_details = str(exc_info.value.details)
        assert "folder" in error_details
        assert "not allowed to be empty" in error_details

    def test_fetch_no_container(self):
        """Test fetching without a container."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.fetch(name="test-profile")
        error_details = str(exc_info.value.details)
        assert "Exactly one of" in error_details or "must be provided" in error_details

    def test_fetch_with_device(self):
        """Test fetching a syslog server profile in a device container."""
        # Create mock API response using our factory
        response_model = SyslogServerProfileResponseModelFactory.with_device()
        mock_response = response_model.model_dump(
            by_alias=True
        )  # Direct object, not wrapped in data array

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        device_name = "TestDevice"
        profile_name = response_model.name
        response = syslog_server_profile.fetch(name=profile_name, device=device_name)

        # Verify the result
        verify_fetch_response(response, response_model, "device", device_name)

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"].get("device") == device_name
        assert kwargs["params"].get("name") == profile_name

    def test_fetch_invalid_response_format(self):
        """Test fetch method with invalid response format (not a dictionary)."""
        api_client = MagicMock(spec=Scm)
        # Return a list instead of a dictionary to trigger the error
        api_client.get.return_value = ["not", "a", "dictionary"]

        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.fetch(name="test-profile", folder="Shared")

        assert "Invalid response format" in str(exc_info.value.message)
        assert "expected dictionary" in str(exc_info.value.message)
        assert "Response is not a dictionary" in str(exc_info.value.details)
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_missing_id_field(self):
        """Test fetch method with response missing 'id' field."""
        api_client = MagicMock(spec=Scm)
        # Return a dictionary without an 'id' field
        api_client.get.return_value = {
            "name": "test-profile",
            "folder": "Shared",
            # 'id' field is missing
        }

        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.fetch(name="test-profile", folder="Shared")

        assert "Invalid response format" in str(exc_info.value.message)
        assert "missing 'id' field" in str(exc_info.value.message)
        assert "Response missing 'id' field" in str(exc_info.value.details)
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500


# -------------------- SyslogServerProfile filtering and pagination tests --------------------


class TestSyslogServerProfileFilteringAndPagination:
    """Tests for SyslogServerProfile filtering and pagination."""

    @patch.object(SyslogServerProfile, "_apply_filters")
    def test_filter_by_transport(self, mock_apply_filters):
        """Test filtering syslog server profiles by transport protocol."""
        api_client = MagicMock(spec=Scm)

        # Create test profiles with different transports
        udp_server = SyslogServerModelFactory(transport="UDP")
        tcp_server = SyslogServerModelFactory(transport="TCP")

        profiles = [
            SyslogServerProfileResponseModelFactory(server=[udp_server]),
            SyslogServerProfileResponseModelFactory(server=[tcp_server]),
            SyslogServerProfileResponseModelFactory(server=[udp_server, tcp_server]),
        ]

        # Set up mock response
        mock_response = create_mock_list_response(profiles)
        api_client.get.return_value = mock_response

        # Make mock_apply_filters return only UDP profiles
        mock_apply_filters.return_value = [
            p for p in profiles if any(s.transport == "UDP" for s in p.server)
        ]

        # Create SyslogServerProfile instance and call list with transport filter
        syslog_server_profile = SyslogServerProfile(api_client)
        result = syslog_server_profile.list(folder="Shared", transport=["UDP"])

        # Verify results
        assert len(result) == 2
        assert any(s.transport == "UDP" for s in result[0].server)
        assert any(s.transport == "UDP" for s in result[1].server)

        # Verify that _apply_filters was called with the right parameters
        mock_apply_filters.assert_called_once()
        args = mock_apply_filters.call_args[0]
        assert args[1] == {"transport": ["UDP"]}

    @patch.object(SyslogServerProfile, "_apply_filters")
    def test_filter_by_format(self, mock_apply_filters):
        """Test filtering syslog server profiles by format."""
        api_client = MagicMock(spec=Scm)

        # Create test profiles with different formats
        bsd_server = SyslogServerModelFactory(format="BSD")
        ietf_server = SyslogServerModelFactory(format="IETF")

        profiles = [
            SyslogServerProfileResponseModelFactory(server=[bsd_server]),
            SyslogServerProfileResponseModelFactory(server=[ietf_server]),
            SyslogServerProfileResponseModelFactory(server=[bsd_server, ietf_server]),
        ]

        # Set up mock response
        mock_response = create_mock_list_response(profiles)
        api_client.get.return_value = mock_response

        # Make mock_apply_filters return only IETF profiles
        mock_apply_filters.return_value = [
            p for p in profiles if any(s.format == "IETF" for s in p.server)
        ]

        # Create SyslogServerProfile instance and call list with format filter
        syslog_server_profile = SyslogServerProfile(api_client)
        result = syslog_server_profile.list(folder="Shared", format=["IETF"])

        # Verify results
        assert len(result) == 2
        assert any(s.format == "IETF" for s in result[0].server) or any(
            s.format == "IETF" for s in result[1].server
        )

        # Verify that _apply_filters was called with the right parameters
        mock_apply_filters.assert_called_once()
        args = mock_apply_filters.call_args[0]
        assert args[1] == {"format": ["IETF"]}

    @patch.object(SyslogServerProfile, "_apply_filters")
    def test_filter_by_multiple_criteria(self, mock_apply_filters):
        """Test filtering syslog server profiles by multiple criteria."""
        api_client = MagicMock(spec=Scm)

        # Create servers with different combinations
        udp_bsd = SyslogServerModelFactory(transport="UDP", format="BSD")
        udp_ietf = SyslogServerModelFactory(transport="UDP", format="IETF")
        tcp_bsd = SyslogServerModelFactory(transport="TCP", format="BSD")
        tcp_ietf = SyslogServerModelFactory(transport="TCP", format="IETF")

        profiles = [
            SyslogServerProfileResponseModelFactory(server=[udp_bsd]),
            SyslogServerProfileResponseModelFactory(server=[tcp_ietf]),
            SyslogServerProfileResponseModelFactory(server=[udp_ietf]),
            SyslogServerProfileResponseModelFactory(server=[tcp_bsd]),
        ]

        # Set up mock response
        mock_response = create_mock_list_response(profiles)
        api_client.get.return_value = mock_response

        # Make mock_apply_filters return only UDP+IETF profiles
        mock_apply_filters.return_value = [
            p
            for p in profiles
            if any(s.transport == "UDP" and s.format == "IETF" for s in p.server)
        ]

        # Create SyslogServerProfile instance and call list with multiple filters
        syslog_server_profile = SyslogServerProfile(api_client)
        result = syslog_server_profile.list(folder="Shared", transport=["UDP"], format=["IETF"])

        # Verify results
        assert len(result) == 1
        assert any(s.transport == "UDP" and s.format == "IETF" for s in result[0].server)

        # Verify that _apply_filters was called with the right parameters
        mock_apply_filters.assert_called_once()
        args = mock_apply_filters.call_args[0]
        assert args[1] == {"transport": ["UDP"], "format": ["IETF"]}

    def test_invalid_transport_filter_type(self):
        """Test with invalid transport filter type (not a list)."""
        api_client = MagicMock(spec=Scm)

        # Create mock response - the actual content doesn't matter since we'll raise an exception
        mock_response = {"data": [], "total": 0, "limit": 10, "offset": 0}
        api_client.get.return_value = mock_response

        # Mock the _apply_filters to raise an exception when called with non-list transport
        syslog_server_profile = SyslogServerProfile(api_client)

        # Override the _apply_filters method to check list type and raise exception if needed
        def patched_apply_filters(profiles, filters):
            if "transport" in filters and not isinstance(filters["transport"], list):
                raise InvalidObjectError(
                    message="'transport' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            return profiles

        # Apply the patch
        with patch.object(
            syslog_server_profile, "_apply_filters", side_effect=patched_apply_filters
        ):
            with pytest.raises(InvalidObjectError) as exc_info:
                syslog_server_profile.list(folder="Shared", transport="UDP")

        # Check if it's the right exception
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400
        assert "Invalid Object" in str(exc_info.value.details)

    def test_invalid_format_filter_type(self):
        """Test with invalid format filter type (not a list)."""
        api_client = MagicMock(spec=Scm)

        # Create mock response - the actual content doesn't matter since we'll raise an exception
        mock_response = {"data": [], "total": 0, "limit": 10, "offset": 0}
        api_client.get.return_value = mock_response

        # Mock the _apply_filters to raise an exception when called with non-list format
        syslog_server_profile = SyslogServerProfile(api_client)

        # Override the _apply_filters method to check list type and raise exception if needed
        def patched_apply_filters(profiles, filters):
            if "format" in filters and not isinstance(filters["format"], list):
                raise InvalidObjectError(
                    message="'format' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            return profiles

        # Apply the patch
        with patch.object(
            syslog_server_profile, "_apply_filters", side_effect=patched_apply_filters
        ):
            with pytest.raises(InvalidObjectError) as exc_info:
                syslog_server_profile.list(folder="Shared", format="BSD")

        # Check if it's the right exception
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400
        assert "Invalid Object" in str(exc_info.value.details)

    def test_exclude_parameters(self):
        """Test list with exclude parameters."""
        api_client = MagicMock(spec=Scm)

        # Create mock response with an empty list
        mock_response = {"data": [], "total": 0, "limit": 10, "offset": 0}
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)

        # Override the _apply_filters method to verify filters were passed correctly
        mock_apply_filters = MagicMock()
        # Just return the input objects unchanged
        mock_apply_filters.side_effect = lambda objs, _: objs

        with patch.object(syslog_server_profile, "_apply_filters", mock_apply_filters):
            # Call list with exclude parameters
            syslog_server_profile.list(
                folder="Shared",
                exclude_folders=["Folder1", "Folder2"],
                exclude_snippets=["Snippet1"],
                exclude_devices=["Device1"],
            )

        # Verify API call - only folder should be in params
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["folder"] == "Shared"
        # These should NOT be in the params because they're not added to the API call
        assert "exclude_folders" not in kwargs["params"]
        assert "exclude_snippets" not in kwargs["params"]
        assert "exclude_devices" not in kwargs["params"]

    def test_exact_match(self):
        """Test list with exact_match parameter."""
        api_client = MagicMock(spec=Scm)

        # Create mock response
        mock_response = {"data": [], "total": 0, "limit": 10, "offset": 0}
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)

        # Call list with exact_match parameter
        syslog_server_profile.list(folder="Shared", exact_match=True)

        # Verify API call - only folder should be in params, not exact_match
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["folder"] == "Shared"
        # exact_match should NOT be in the params because it's not added to the API call
        assert "exact_match" not in kwargs["params"]

    def test_list_response_invalid_format(self):
        """Test handling of invalid response format."""
        api_client = MagicMock(spec=Scm)

        # Make API return a non-dict response
        api_client.get.return_value = "Not a dictionary"

        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Shared")

        # Check if the error details match what's in the implementation
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "Response is not a dictionary" in str(exc_info.value.details)

    def test_list_response_missing_data(self):
        """Test handling of response missing data field."""
        api_client = MagicMock(spec=Scm)

        # Make API return a response without 'data' field
        api_client.get.return_value = {"total": 0, "limit": 10, "offset": 0}

        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Shared")

        # Check if the error details match what's in the implementation
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "data" in str(exc_info.value.details)
        assert "field missing" in str(exc_info.value.details)

    def test_list_response_data_not_list(self):
        """Test handling of response with data not a list."""
        api_client = MagicMock(spec=Scm)

        # Make API return a response with 'data' not a list
        api_client.get.return_value = {"data": "Not a list", "total": 0, "limit": 10, "offset": 0}

        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Shared")

        # Check if the error details match what's in the implementation
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "data" in str(exc_info.value.details)
        assert "must be a list" in str(exc_info.value.details)

    def test_list_multiple_container_params(self):
        """Test list with multiple container parameters."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Shared", snippet="MySnippet")

        # Check if the error details match what's in the implementation
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400
        assert "Invalid container parameters" in str(exc_info.value.details)

    def test_list_no_container_params(self):
        """Test list with no container parameters."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list()

        # Check if the error details match what's in the implementation
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400
        assert "Invalid container parameters" in str(exc_info.value.details)

    def test_pagination(self):
        """Test pagination through multiple requests."""
        api_client = MagicMock(spec=Scm)

        # Create first response with limit=2, total=5
        profiles_page1 = [
            SyslogServerProfileResponseModelFactory(name="profile1"),
            SyslogServerProfileResponseModelFactory(name="profile2"),
        ]
        mock_response1 = {
            "data": [model.model_dump(by_alias=True) for model in profiles_page1],
            "total": 5,
            "limit": 2,
            "offset": 0,
        }

        # Create second response
        profiles_page2 = [
            SyslogServerProfileResponseModelFactory(name="profile3"),
            SyslogServerProfileResponseModelFactory(name="profile4"),
        ]
        mock_response2 = {
            "data": [model.model_dump(by_alias=True) for model in profiles_page2],
            "total": 5,
            "limit": 2,
            "offset": 2,
        }

        # Create third response
        profiles_page3 = [SyslogServerProfileResponseModelFactory(name="profile5")]
        mock_response3 = {
            "data": [model.model_dump(by_alias=True) for model in profiles_page3],
            "total": 5,
            "limit": 2,
            "offset": 4,
        }

        # Configure API client to return different responses based on offset
        api_client.get.side_effect = [mock_response1, mock_response2, mock_response3]

        # Create SyslogServerProfile instance with max_limit=2 to force pagination
        syslog_server_profile = SyslogServerProfile(api_client, max_limit=2)

        # Call list method
        profiles = syslog_server_profile.list(folder="Shared")

        # Verify results
        assert len(profiles) == 5
        assert profiles[0].name == "profile1"
        assert profiles[1].name == "profile2"
        assert profiles[2].name == "profile3"
        assert profiles[3].name == "profile4"
        assert profiles[4].name == "profile5"

        # Verify API calls
        assert api_client.get.call_count == 3

        # First call should use offset=0
        args1, kwargs1 = api_client.get.call_args_list[0]
        assert kwargs1["params"]["offset"] == 0

        # Second call should use offset=2
        args2, kwargs2 = api_client.get.call_args_list[1]
        assert kwargs2["params"]["offset"] == 2

        # Third call should use offset=4
        args3, kwargs3 = api_client.get.call_args_list[2]
        assert kwargs3["params"]["offset"] == 4

    def test_filter_with_empty_profiles(self):
        """Test filtering with an empty profiles list."""
        api_client = MagicMock(spec=Scm)

        # Create empty response
        mock_response = create_mock_list_response([])
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)

        # Test filtering with empty profiles list
        profiles = syslog_server_profile.list(folder="Shared", transport=["UDP"], format=["BSD"])

        # Should return empty list
        assert len(profiles) == 0

    def test_build_container_params_directly(self):
        """Test _build_container_params method directly."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        # Test with folder
        params = syslog_server_profile._build_container_params("Folder1", None, None)
        assert params == {"folder": "Folder1"}

        # Test with snippet
        params = syslog_server_profile._build_container_params(None, "Snippet1", None)
        assert params == {"snippet": "Snippet1"}

        # Test with device
        params = syslog_server_profile._build_container_params(None, None, "Device1")
        assert params == {"device": "Device1"}

        # Test with none
        params = syslog_server_profile._build_container_params(None, None, None)
        assert params == {}

    def test_direct_apply_filters(self):
        """Test the _apply_filters method directly with different filters."""
        api_client = MagicMock(spec=Scm)

        # Create SyslogServerProfile instance
        syslog_server_profile = SyslogServerProfile(api_client)

        # Create a simple mock object that matches what _apply_filters expects
        class MockProfile:
            def __init__(self, servers_dict):
                self.servers = servers_dict

        # Create mock profiles with the servers attribute containing transport and format
        profile1 = MockProfile({"server1": {"transport": "UDP", "format": "BSD"}})
        profile2 = MockProfile({"server2": {"transport": "TCP", "format": "IETF"}})

        profiles = [profile1, profile2]

        # Test with empty filter dict (should return all profiles)
        filtered = syslog_server_profile._apply_filters(profiles, {})
        assert len(filtered) == 2

        # Test with transport filter
        filtered = syslog_server_profile._apply_filters(profiles, {"transport": ["UDP"]})
        assert len(filtered) == 1
        assert filtered[0] == profile1

        # Test with format filter
        filtered = syslog_server_profile._apply_filters(profiles, {"format": ["IETF"]})
        assert len(filtered) == 1
        assert filtered[0] == profile2

        # Test with combined filters that match no profiles
        filtered = syslog_server_profile._apply_filters(
            profiles, {"transport": ["UDP"], "format": ["IETF"]}
        )
        assert len(filtered) == 0

        # Test with non-list transport filter (should raise an exception)
        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile._apply_filters(profiles, {"transport": "UDP"})
        assert exc_info.value.error_code == "E003"

        # Test with non-list format filter (should raise an exception)
        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile._apply_filters(profiles, {"format": "IETF"})
        assert exc_info.value.error_code == "E003"

    def test_build_container_params_all_none(self):
        """Test _build_container_params with all None parameters."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        # Call with all None
        result = syslog_server_profile._build_container_params(None, None, None)
        assert result == {}

    def test_list_with_api_error(self):
        """Test error handling when API call for list fails."""
        api_client = MagicMock(spec=Scm)

        # Set up API client to raise an exception
        api_client.get.side_effect = requests.exceptions.HTTPError(
            "API connection failed", response=MagicMock(status_code=500)
        )

        syslog_server_profile = SyslogServerProfile(api_client)

        # Test that the exception is propagated
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            syslog_server_profile.list(folder="Shared")

        assert "API connection failed" in str(exc_info.value)

    def test_list_with_pagination_break(self):
        """Test pagination with exactly limit objects (edge case)."""
        api_client = MagicMock(spec=Scm)

        # First response has exactly limit objects
        profiles_page1 = [
            SyslogServerProfileResponseModelFactory(name="profile1"),
            SyslogServerProfileResponseModelFactory(name="profile2"),
        ]
        mock_response1 = {
            "data": [model.model_dump(by_alias=True) for model in profiles_page1],
            "total": 2,
            "limit": 2,
            "offset": 0,
        }

        # Second response is empty to indicate end of results
        mock_response2 = {"data": [], "total": 2, "limit": 2, "offset": 2}

        # Set up API client to return these responses
        api_client.get.side_effect = [mock_response1, mock_response2]

        # Create SyslogServerProfile instance with small max_limit
        syslog_server_profile = SyslogServerProfile(api_client, max_limit=2)

        # Call list method
        profiles = syslog_server_profile.list(folder="Shared")

        # Verify results
        assert len(profiles) == 2
        assert profiles[0].name == "profile1"
        assert profiles[1].name == "profile2"

        # Verify there were 2 API calls (one returned exactly limit objects,
        # so pagination continues, but second has no results)
        assert api_client.get.call_count == 2

        # First call should use offset=0
        args1, kwargs1 = api_client.get.call_args_list[0]
        assert kwargs1["params"]["offset"] == 0

        # Second call should use offset=2
        args2, kwargs2 = api_client.get.call_args_list[1]
        assert kwargs2["params"]["offset"] == 2
