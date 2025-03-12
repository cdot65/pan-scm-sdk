# tests/scm/config/objects/test_syslog_server_profiles.py

import pytest
from unittest.mock import MagicMock, patch
import uuid
import requests

from scm.client import Scm
from scm.config.objects import SyslogServerProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import (
    SyslogServerProfileUpdateModel,
    SyslogServerProfileResponseModel,
)


# -------------------- Helper functions --------------------


def create_sample_syslog_server_profile_response():
    """Create a sample syslog server profile response dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-syslog-profile",
        "servers": {
            "server1": {
                "name": "server1",
                "server": "192.168.1.100",
                "transport": "UDP",
                "port": 514,
                "format": "BSD",
                "facility": "LOG_USER",
            }
        },
        "format": {
            "traffic": "traffic-format",
            "threat": "threat-format",
        },
        "folder": "Security Profiles",
    }


def create_valid_syslog_server_profile_data():
    """Create a valid syslog server profile data dictionary for testing."""
    return {
        "name": "test-syslog-profile",
        "servers": {
            "server1": {
                "name": "server1",
                "server": "192.168.1.100",
                "transport": "UDP",
                "port": 514,
                "format": "BSD",
                "facility": "LOG_USER",
            }
        },
        "folder": "Security Profiles",
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
        assert response.name == "test-syslog-profile"
        assert "server1" in response.servers
        assert response.servers["server1"]["transport"] == "UDP"
        assert response.folder == "Security Profiles"

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
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        response = syslog_server_profile.get(object_id)

        # Verify the result
        assert response.name == "test-syslog-profile"
        assert "server1" in response.servers
        assert response.servers["server1"]["transport"] == "UDP"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == f"/config/objects/v1/syslog-server-profiles/{object_id}"

    def test_update(self):
        """Test updating a syslog server profile."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_syslog_server_profile_response()
        api_client.put.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)

        # Create a valid update model
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-profile",
            "servers": {
                "server1": {
                    "name": "server1",
                    "server": "192.168.1.200",
                    "transport": "TCP",
                    "port": 1514,
                    "format": "IETF",
                    "facility": "LOG_LOCAL0",
                }
            },
        }
        update_model = SyslogServerProfileUpdateModel(**update_data)

        response = syslog_server_profile.update(update_model)

        # Verify the result is correct
        assert response.name == "test-syslog-profile"  # From our mocked response
        assert "server1" in response.servers

        # Verify API call
        api_client.put.assert_called_once()
        args, kwargs = api_client.put.call_args
        assert args[0] == f"/config/objects/v1/syslog-server-profiles/{update_data['id']}"
        assert "json" in kwargs
        assert "id" not in kwargs["json"]  # ID should be removed from the payload

    def test_delete(self):
        """Test deleting a syslog server profile."""
        api_client = MagicMock(spec=Scm)
        api_client.delete.return_value = None

        syslog_server_profile = SyslogServerProfile(api_client)
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        syslog_server_profile.delete(object_id)

        # Verify API call
        api_client.delete.assert_called_once_with(
            f"/config/objects/v1/syslog-server-profiles/{object_id}"
        )


# -------------------- SyslogServerProfile list and fetch tests --------------------


class TestSyslogServerProfileListAndFetch:
    """Tests for SyslogServerProfile list and fetch operations."""

    def test_list_with_folder(self):
        """Test listing syslog server profiles in a folder."""
        api_client = MagicMock(spec=Scm)
        profile1 = create_sample_syslog_server_profile_response()
        profile2 = create_sample_syslog_server_profile_response()
        profile2["name"] = "another-profile"
        mock_response = {
            "data": [profile1, profile2],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profiles = syslog_server_profile.list(folder="Security Profiles")

        # Verify the result
        assert len(profiles) == 2
        assert profiles[0].folder == "Security Profiles"
        assert profiles[1].name == "another-profile"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["folder"] == "Security Profiles"

    def test_list_with_snippet(self):
        """Test listing syslog server profiles in a snippet."""
        api_client = MagicMock(spec=Scm)
        profile1 = create_sample_syslog_server_profile_response()
        profile1["folder"] = None
        profile1["snippet"] = "TestSnippet"
        mock_response = {
            "data": [profile1],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profiles = syslog_server_profile.list(snippet="TestSnippet")

        # Verify the result
        assert len(profiles) == 1
        assert profiles[0].snippet == "TestSnippet"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["snippet"] == "TestSnippet"

    def test_list_with_device(self):
        """Test listing syslog server profiles in a device."""
        api_client = MagicMock(spec=Scm)
        profile1 = create_sample_syslog_server_profile_response()
        profile1["folder"] = None
        profile1["device"] = "TestDevice"
        mock_response = {
            "data": [profile1],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profiles = syslog_server_profile.list(device="TestDevice")

        # Verify the result
        assert len(profiles) == 1
        assert profiles[0].device == "TestDevice"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["device"] == "TestDevice"

    def test_list_empty_folder(self):
        """Test listing syslog server profiles with empty folder string."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            syslog_server_profile.list(folder="")
        assert "folder" in str(exc_info.value.details.get("field"))

    def test_list_no_container(self):
        """Test listing syslog server profiles without a container."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list()
        assert "Invalid container parameters" in str(exc_info.value.details.get("error"))

    def test_list_with_filtering(self):
        """Test listing syslog server profiles with filtering."""
        api_client = MagicMock(spec=Scm)
        profile1 = create_sample_syslog_server_profile_response()
        profile1["servers"]["server1"]["transport"] = "UDP"
        profile2 = create_sample_syslog_server_profile_response()
        profile2["name"] = "another-profile"
        profile2["servers"]["server1"]["transport"] = "TCP"

        mock_response = {
            "data": [profile1, profile2],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profiles = syslog_server_profile.list(folder="Security Profiles", transport=["UDP"])

        # Verify the result
        assert len(profiles) == 1
        assert profiles[0].servers["server1"]["transport"] == "UDP"
        assert profiles[0].name == "test-syslog-profile"

    def test_list_with_multiple_filters(self):
        """Test listing syslog server profiles with multiple filters."""
        api_client = MagicMock(spec=Scm)

        # Profile 1: UDP with BSD format
        profile1 = create_sample_syslog_server_profile_response()
        profile1["servers"]["server1"]["transport"] = "UDP"
        profile1["servers"]["server1"]["format"] = "BSD"

        # Profile 2: TCP with BSD format
        profile2 = create_sample_syslog_server_profile_response()
        profile2["name"] = "profile2"
        profile2["servers"]["server1"]["transport"] = "TCP"
        profile2["servers"]["server1"]["format"] = "BSD"

        # Profile 3: UDP with IETF format
        profile3 = create_sample_syslog_server_profile_response()
        profile3["name"] = "profile3"
        profile3["servers"]["server1"]["transport"] = "UDP"
        profile3["servers"]["server1"]["format"] = "IETF"

        # Profile 4: TCP with IETF format
        profile4 = create_sample_syslog_server_profile_response()
        profile4["name"] = "profile4"
        profile4["servers"]["server1"]["transport"] = "TCP"
        profile4["servers"]["server1"]["format"] = "IETF"

        mock_response = {
            "data": [profile1, profile2, profile3, profile4],
            "limit": 200,
            "offset": 0,
            "total": 4,
        }
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)

        # Filter by transport and format (should return only profile3)
        profiles = syslog_server_profile.list(
            folder="Security Profiles", transport=["UDP"], format=["IETF"]
        )

        # Verify the result - should be just one profile with both criteria
        assert len(profiles) == 1
        assert profiles[0].servers["server1"]["transport"] == "UDP"
        assert profiles[0].servers["server1"]["format"] == "IETF"
        assert profiles[0].name == "profile3"

    def test_list_with_invalid_transport_filter(self):
        """Test listing syslog server profiles with invalid transport filter."""
        api_client = MagicMock(spec=Scm)
        # Need to return a valid response for the first API call
        api_client.get.return_value = {
            "data": [create_sample_syslog_server_profile_response()],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }

        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Security Profiles", transport="UDP")
        assert "errorType" in str(exc_info.value.details)

    def test_list_with_transport_filter(self):
        """Test listing syslog server profiles with transport filter."""
        api_client = MagicMock(spec=Scm)

        # Profile with UDP server
        profile1 = create_sample_syslog_server_profile_response()
        profile1["servers"]["server1"]["transport"] = "UDP"

        # Profile with TCP server
        profile2 = create_sample_syslog_server_profile_response()
        profile2["name"] = "tcp-profile"
        profile2["servers"]["server1"]["transport"] = "TCP"

        mock_response = {
            "data": [profile1, profile2],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profiles = syslog_server_profile.list(folder="Security Profiles", transport=["TCP"])

        # Verify the result
        assert len(profiles) == 1
        assert profiles[0].name == "tcp-profile"
        assert profiles[0].servers["server1"]["transport"] == "TCP"

    def test_list_with_invalid_format_filter(self):
        """Test listing syslog server profiles with invalid format filter."""
        api_client = MagicMock(spec=Scm)
        # Need to return a valid response for the first API call
        api_client.get.return_value = {
            "data": [create_sample_syslog_server_profile_response()],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }

        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Security Profiles", format="BSD")
        assert "errorType" in str(exc_info.value.details)

    def test_apply_filters_directly(self):
        """Test _apply_filters method directly to improve code coverage."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        # Create sample profiles
        profile1 = SyslogServerProfileResponseModel(
            **create_sample_syslog_server_profile_response()
        )
        profile1.servers["server1"]["transport"] = "UDP"

        profile2 = SyslogServerProfileResponseModel(
            **create_sample_syslog_server_profile_response()
        )
        profile2.name = "profile2"
        profile2.servers["server1"]["transport"] = "TCP"

        # Test transport filter
        filtered = syslog_server_profile._apply_filters(
            [profile1, profile2], {"transport": ["UDP"]}
        )
        assert len(filtered) == 1
        assert filtered[0].servers["server1"]["transport"] == "UDP"

        # Test format filter
        profile1.servers["server1"]["format"] = "BSD"
        profile2.servers["server1"]["format"] = "IETF"

        filtered = syslog_server_profile._apply_filters([profile1, profile2], {"format": ["IETF"]})
        assert len(filtered) == 1
        assert filtered[0].servers["server1"]["format"] == "IETF"

        # Test multiple filters (should result in empty list with our test data)
        filtered = syslog_server_profile._apply_filters(
            [profile1, profile2], {"transport": ["TCP"], "format": ["BSD"]}
        )
        assert len(filtered) == 0

        # Test with empty profiles list
        filtered = syslog_server_profile._apply_filters([], {"transport": ["UDP"]})
        assert len(filtered) == 0

        # Test with empty filters dictionary
        filtered = syslog_server_profile._apply_filters([profile1, profile2], {})
        assert len(filtered) == 2

    def test_fetch(self):
        """Test fetching a single syslog server profile by name."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_syslog_server_profile_response()
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profile = syslog_server_profile.fetch(
            name="test-syslog-profile", folder="Security Profiles"
        )

        # Verify the result
        assert profile.name == "test-syslog-profile"
        assert profile.folder == "Security Profiles"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["name"] == "test-syslog-profile"
        assert kwargs["params"]["folder"] == "Security Profiles"

    def test_fetch_with_snippet(self):
        """Test fetching a syslog server profile in a snippet container."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_syslog_server_profile_response()
        mock_response["folder"] = None
        mock_response["snippet"] = "TestSnippet"
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profile = syslog_server_profile.fetch(name="test-syslog-profile", snippet="TestSnippet")

        # Verify the result
        assert profile.name == "test-syslog-profile"
        assert profile.snippet == "TestSnippet"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["name"] == "test-syslog-profile"
        assert kwargs["params"]["snippet"] == "TestSnippet"

    def test_fetch_with_device(self):
        """Test fetching a syslog server profile in a device container."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_syslog_server_profile_response()
        mock_response["folder"] = None
        mock_response["device"] = "TestDevice"
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)
        profile = syslog_server_profile.fetch(name="test-syslog-profile", device="TestDevice")

        # Verify the result
        assert profile.name == "test-syslog-profile"
        assert profile.device == "TestDevice"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/syslog-server-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["name"] == "test-syslog-profile"
        assert kwargs["params"]["device"] == "TestDevice"

    def test_fetch_empty_name(self):
        """Test fetching with empty name."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            syslog_server_profile.fetch(name="", folder="Security Profiles")
        assert "name" in str(exc_info.value.details.get("field"))

    def test_fetch_empty_folder(self):
        """Test fetching with empty folder string."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            syslog_server_profile.fetch(name="test-profile", folder="")
        assert "folder" in str(exc_info.value.details.get("field"))

    def test_fetch_no_container(self):
        """Test fetching without a container."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.fetch(name="test-profile")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_fetch_invalid_response_format(self):
        """Test fetching with an invalid response format."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = "not a dictionary"  # Invalid response

        syslog_server_profile = SyslogServerProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.fetch(name="test-profile", folder="Security Profiles")
        assert "Invalid response format: expected dictionary" in exc_info.value.message

    def test_fetch_missing_id_field(self):
        """Test fetching with response missing ID field."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {"name": "test-profile"}  # Missing ID

        syslog_server_profile = SyslogServerProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.fetch(name="test-profile", folder="Security Profiles")
        assert "Invalid response format: missing 'id' field" in exc_info.value.message

    def test_list_response_not_dict(self):
        """Test list with response that's not a dictionary."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = "not a dictionary"  # Invalid response

        syslog_server_profile = SyslogServerProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Security Profiles")
        assert "Invalid response format: expected dictionary" in exc_info.value.message

    def test_list_response_missing_data(self):
        """Test list with response missing data field."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {"total": 0}  # Missing data field

        syslog_server_profile = SyslogServerProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Security Profiles")
        assert "Invalid response format: missing 'data' field" in exc_info.value.message

    def test_list_response_data_not_list(self):
        """Test list with data field that's not a list."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {"data": "not a list"}  # Data not a list

        syslog_server_profile = SyslogServerProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            syslog_server_profile.list(folder="Security Profiles")
        assert "Invalid response format: 'data' field must be a list" in exc_info.value.message

    def test_list_with_pagination(self):
        """Test list with pagination through multiple requests."""
        api_client = MagicMock(spec=Scm)

        # First response with 2 items (limit=2)
        profile1 = create_sample_syslog_server_profile_response()
        profile1["name"] = "profile1"
        profile2 = create_sample_syslog_server_profile_response()
        profile2["name"] = "profile2"

        first_response = {
            "data": [profile1, profile2],
            "limit": 2,
            "offset": 0,
            "total": 3,
        }

        # Second response with 1 item
        profile3 = create_sample_syslog_server_profile_response()
        profile3["name"] = "profile3"

        second_response = {
            "data": [profile3],
            "limit": 2,
            "offset": 2,
            "total": 3,
        }

        # Configure the mock to return different responses based on the offset parameter
        def get_side_effect(*args, **kwargs):
            if kwargs.get("params", {}).get("offset") == 0:
                return first_response
            else:
                return second_response

        api_client.get.side_effect = get_side_effect

        # Call list with max_limit=2 to trigger pagination
        syslog_server_profile = SyslogServerProfile(api_client, max_limit=2)
        profiles = syslog_server_profile.list(folder="Security Profiles")

        # Verify we got all 3 profiles from both API calls
        assert len(profiles) == 3
        assert profiles[0].name == "profile1"
        assert profiles[1].name == "profile2"
        assert profiles[2].name == "profile3"

        # Verify API was called twice with different offset values
        assert api_client.get.call_count == 2
        # First call should have offset=0
        assert api_client.get.call_args_list[0][1]["params"]["offset"] == 0
        # Second call should have offset=2
        assert api_client.get.call_args_list[1][1]["params"]["offset"] == 2

    def test_list_with_exclude_filters(self):
        """Test list with exclude filters."""
        api_client = MagicMock(spec=Scm)

        # Create test profiles
        profile1 = create_sample_syslog_server_profile_response()
        profile1["name"] = "profile1"
        profile1["folder"] = "Folder1"

        profile2 = create_sample_syslog_server_profile_response()
        profile2["name"] = "profile2"
        profile2["folder"] = "Folder2"

        profile3 = create_sample_syslog_server_profile_response()
        profile3["name"] = "profile3"
        profile3["snippet"] = "Snippet1"

        profile4 = create_sample_syslog_server_profile_response()
        profile4["name"] = "profile4"
        profile4["device"] = "Device1"

        mock_response = {
            "data": [profile1, profile2, profile3, profile4],
            "limit": 200,
            "offset": 0,
            "total": 4,
        }
        api_client.get.return_value = mock_response

        # Test excluding folders
        syslog_server_profile = SyslogServerProfile(api_client)
        profiles = syslog_server_profile.list(
            folder="Security Profiles", exclude_folders=["Folder2"]
        )

        # Should exclude profile2 with Folder2
        assert len(profiles) == 3
        assert "profile2" not in [p.name for p in profiles]

        # Test excluding snippets
        profiles = syslog_server_profile.list(
            folder="Security Profiles", exclude_snippets=["Snippet1"]
        )

        # Should exclude profile3 with Snippet1
        assert len(profiles) == 3
        assert "profile3" not in [p.name for p in profiles]

        # Test excluding devices
        profiles = syslog_server_profile.list(
            folder="Security Profiles", exclude_devices=["Device1"]
        )

        # Should exclude profile4 with Device1
        assert len(profiles) == 3
        assert "profile4" not in [p.name for p in profiles]

    def test_list_with_multiple_excludes(self):
        """Test list with multiple exclude filters."""
        api_client = MagicMock(spec=Scm)

        # Create test profiles
        profile1 = create_sample_syslog_server_profile_response()
        profile1["name"] = "profile1"
        profile1["folder"] = "Folder1"

        profile2 = create_sample_syslog_server_profile_response()
        profile2["name"] = "profile2"
        profile2["folder"] = "Folder2"

        profile3 = create_sample_syslog_server_profile_response()
        profile3["name"] = "profile3"
        profile3["snippet"] = "Snippet1"

        profile4 = create_sample_syslog_server_profile_response()
        profile4["name"] = "profile4"
        profile4["device"] = "Device1"

        mock_response = {
            "data": [profile1, profile2, profile3, profile4],
            "limit": 200,
            "offset": 0,
            "total": 4,
        }
        api_client.get.return_value = mock_response

        # Test excluding multiple items
        syslog_server_profile = SyslogServerProfile(api_client)
        profiles = syslog_server_profile.list(
            folder="Security Profiles",
            exclude_folders=["Folder2"],
            exclude_snippets=["Snippet1"],
            exclude_devices=["Device1"],
        )

        # Should only keep profile1
        assert len(profiles) == 1
        assert profiles[0].name == "profile1"

    def test_list_with_invalid_exclude_types(self):
        """Test list with invalid exclude filter types."""
        api_client = MagicMock(spec=Scm)
        # Need valid response for initial get
        api_client.get.return_value = {
            "data": [create_sample_syslog_server_profile_response()],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }

        syslog_server_profile = SyslogServerProfile(api_client)

        # Testing with non-list exclude_folders (should still work but ignore the filter)
        profiles = syslog_server_profile.list(
            folder="Security Profiles",
            exclude_folders="Folder2",  # String instead of list
        )

        # Should not apply the invalid filter
        assert len(profiles) == 1

    def test_list_with_exact_match(self):
        """Test list with exact_match parameter."""
        api_client = MagicMock(spec=Scm)

        # Create test profiles with different folder values
        profile1 = create_sample_syslog_server_profile_response()
        profile1["name"] = "profile1"
        profile1["folder"] = "Security Profiles"  # Exact match

        profile2 = create_sample_syslog_server_profile_response()
        profile2["name"] = "profile2"
        profile2["folder"] = "Other Folder"  # Different folder

        mock_response = {
            "data": [profile1, profile2],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        api_client.get.return_value = mock_response

        syslog_server_profile = SyslogServerProfile(api_client)

        # Without exact_match, should return both profiles
        profiles = syslog_server_profile.list(folder="Security Profiles", exact_match=False)
        assert len(profiles) == 2

        # With exact_match, should return only the exact match profile
        profiles = syslog_server_profile.list(folder="Security Profiles", exact_match=True)
        assert len(profiles) == 1
        assert profiles[0].name == "profile1"
        assert profiles[0].folder == "Security Profiles"

    def test_build_container_params(self):
        """Test the _build_container_params method directly for code coverage."""
        api_client = MagicMock(spec=Scm)
        syslog_server_profile = SyslogServerProfile(api_client)

        # Test with all None values
        params = syslog_server_profile._build_container_params(None, None, None)
        assert params == {}

        # Test with only folder
        params = syslog_server_profile._build_container_params("FolderA", None, None)
        assert params == {"folder": "FolderA"}

        # Test with only snippet
        params = syslog_server_profile._build_container_params(None, "SnippetB", None)
        assert params == {"snippet": "SnippetB"}

        # Test with only device
        params = syslog_server_profile._build_container_params(None, None, "DeviceC")
        assert params == {"device": "DeviceC"}

        # Test with multiple values (this would lead to an error in actual usage)
        params = syslog_server_profile._build_container_params("FolderA", "SnippetB", "DeviceC")
        assert len(params) == 3
        assert params["folder"] == "FolderA"
        assert params["snippet"] == "SnippetB"
        assert params["device"] == "DeviceC"
