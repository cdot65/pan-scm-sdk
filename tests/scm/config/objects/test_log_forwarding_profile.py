# tests/scm/config/objects/test_log_forwarding_profile.py

import uuid
from unittest.mock import MagicMock, patch

import pytest
import requests

from scm.client import Scm
from scm.config.objects import LogForwardingProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import (
    LogForwardingProfileResponseModel,
    LogForwardingProfileUpdateModel,
    MatchListItem,
)
from tests.factories import LogForwardingProfileCreateModelFactory

# -------------------- Helper functions --------------------


def create_sample_log_forwarding_profile_response():
    """Create a sample log forwarding profile response dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-log-profile",
        "description": "Test log forwarding profile",
        "match_list": [
            {
                "name": "traffic-match",
                "log_type": "traffic",
                "filter": "addr.src in 192.168.0.0/24",
                "send_http": ["http-profile-1"],
            }
        ],
        "folder": "Shared",
    }


# -------------------- LogForwardingProfile validation tests --------------------


class TestLogForwardingProfileValidation:
    """Tests for LogForwardingProfile validation."""

    def test_max_limit_validation_default(self):
        """Test default max_limit validation."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)
        assert log_forwarding_profile.max_limit == LogForwardingProfile.DEFAULT_MAX_LIMIT

    def test_max_limit_validation_custom(self):
        """Test custom max_limit validation."""
        api_client = MagicMock(spec=Scm)
        custom_limit = 1000
        log_forwarding_profile = LogForwardingProfile(api_client, max_limit=custom_limit)
        assert log_forwarding_profile.max_limit == custom_limit

    def test_max_limit_validation_invalid_type(self):
        """Test max_limit validation with invalid type."""
        api_client = MagicMock(spec=Scm)
        with pytest.raises(InvalidObjectError) as exc_info:
            LogForwardingProfile(api_client, max_limit="invalid")
        assert "Invalid max_limit type" in str(exc_info.value.details)

    def test_max_limit_validation_too_small(self):
        """Test max_limit validation with value that's too small."""
        api_client = MagicMock(spec=Scm)
        with pytest.raises(InvalidObjectError) as exc_info:
            LogForwardingProfile(api_client, max_limit=0)
        assert "Invalid max_limit value" in str(exc_info.value.details)

    def test_max_limit_validation_too_large(self):
        """Test max_limit validation with value that's too large."""
        api_client = MagicMock(spec=Scm)
        with pytest.raises(InvalidObjectError) as exc_info:
            LogForwardingProfile(api_client, max_limit=10000)
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value.details)

    def test_max_limit_setter(self):
        """Test max_limit setter."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)
        log_forwarding_profile.max_limit = 1000
        assert log_forwarding_profile.max_limit == 1000


# -------------------- LogForwardingProfile CRUD operation tests --------------------


class TestLogForwardingProfileOperations:
    """Tests for LogForwardingProfile CRUD operations."""

    def test_create(self):
        """Test creating a new log forwarding profile."""
        api_client = MagicMock(spec=Scm)
        api_client.post.return_value = create_sample_log_forwarding_profile_response()

        log_forwarding_profile = LogForwardingProfile(api_client)
        data = LogForwardingProfileCreateModelFactory.build_valid()
        response = log_forwarding_profile.create(data)

        # Verify the result
        assert response.name == "test-log-profile"
        assert len(response.match_list) == 1
        assert response.match_list[0].log_type == "traffic"
        assert response.folder == "Shared"

        # Verify API call
        api_client.post.assert_called_once()
        args, kwargs = api_client.post.call_args
        assert args[0] == "/config/objects/v1/log-forwarding-profiles"
        assert "json" in kwargs

    def test_create_with_api_error(self):
        """Test error handling when API returns an error during creation."""
        api_client = MagicMock(spec=Scm)
        api_client.post.side_effect = requests.exceptions.HTTPError(
            "API Error", response=MagicMock(status_code=500)
        )

        log_forwarding_profile = LogForwardingProfile(api_client)
        data = LogForwardingProfileCreateModelFactory.build_valid()

        with pytest.raises(Exception) as exc_info:
            log_forwarding_profile.create(data)
        assert "API Error" in str(exc_info.value)

    def test_create_with_generic_exception(self):
        """Test handling of generic exceptions in the create method."""
        api_client = MagicMock(spec=Scm)
        api_client.post.side_effect = Exception("Generic error")

        log_forwarding_profile = LogForwardingProfile(api_client)
        data = LogForwardingProfileCreateModelFactory.build_valid()

        with pytest.raises(Exception) as exc_info:
            log_forwarding_profile.create(data)
        assert "Generic error" in str(exc_info.value)

    def test_create_error_logging(self):
        """Test that errors are properly logged during create operations."""
        api_client = MagicMock(spec=Scm)
        api_client.post.side_effect = Exception("Test error")

        with patch("logging.Logger.error") as mock_log:
            log_forwarding_profile = LogForwardingProfile(api_client)
            data = LogForwardingProfileCreateModelFactory.build_valid()

            with pytest.raises(Exception):
                log_forwarding_profile.create(data)

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

        log_forwarding_profile = LogForwardingProfile(api_client)
        data = LogForwardingProfileCreateModelFactory.build_valid()

        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            log_forwarding_profile.create(data)
        assert "500 Server Error" in str(exc_info.value)

    def test_get(self):
        """Test getting a log forwarding profile by ID."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_log_forwarding_profile_response()
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        response = log_forwarding_profile.get(object_id)

        # Verify the result
        assert response.name == "test-log-profile"
        assert len(response.match_list) == 1
        assert response.match_list[0].log_type == "traffic"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == f"/config/objects/v1/log-forwarding-profiles/{object_id}"

    def test_update(self):
        """Test updating a log forwarding profile."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_log_forwarding_profile_response()
        api_client.put.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)

        # Create a valid update model
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-profile",
            "match_list": [
                {
                    "name": "updated-match",
                    "log_type": "threat",
                    "filter": "severity eq critical",
                    "send_syslog": ["syslog-profile-1"],
                }
            ],
        }
        update_model = LogForwardingProfileUpdateModel(**update_data)

        response = log_forwarding_profile.update(update_model)

        # Verify the result is correct
        assert response.name == "test-log-profile"  # From our mocked response
        assert len(response.match_list) == 1

        # Verify API call
        api_client.put.assert_called_once()
        args, kwargs = api_client.put.call_args
        assert args[0] == f"/config/objects/v1/log-forwarding-profiles/{update_data['id']}"
        assert "json" in kwargs
        assert "id" not in kwargs["json"]  # ID should be removed from the payload

    def test_delete(self):
        """Test deleting a log forwarding profile."""
        api_client = MagicMock(spec=Scm)
        api_client.delete.return_value = None

        log_forwarding_profile = LogForwardingProfile(api_client)
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        log_forwarding_profile.delete(object_id)

        # Verify API call
        api_client.delete.assert_called_once_with(
            f"/config/objects/v1/log-forwarding-profiles/{object_id}"
        )


# -------------------- LogForwardingProfile list and fetch tests --------------------


class TestLogForwardingProfileListAndFetch:
    """Tests for LogForwardingProfile list and fetch operations."""

    def test_list_with_folder(self):
        """Test listing log forwarding profiles in a folder."""
        api_client = MagicMock(spec=Scm)
        profile1 = create_sample_log_forwarding_profile_response()
        profile2 = create_sample_log_forwarding_profile_response()
        profile2["name"] = "another-profile"
        mock_response = {
            "data": [profile1, profile2],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)
        profiles = log_forwarding_profile.list(folder="Shared")

        # Verify the result
        assert len(profiles) == 2
        assert profiles[0].folder == "Shared"
        assert profiles[1].name == "another-profile"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/log-forwarding-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["folder"] == "Shared"

    def test_list_with_snippet(self):
        """Test listing log forwarding profiles in a snippet."""
        api_client = MagicMock(spec=Scm)
        profile1 = create_sample_log_forwarding_profile_response()
        profile1["folder"] = None
        profile1["snippet"] = "TestSnippet"
        mock_response = {
            "data": [profile1],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)
        profiles = log_forwarding_profile.list(snippet="TestSnippet")

        # Verify the result
        assert len(profiles) == 1
        assert profiles[0].snippet == "TestSnippet"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/log-forwarding-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["snippet"] == "TestSnippet"

    def test_list_with_device(self):
        """Test listing log forwarding profiles in a device."""
        api_client = MagicMock(spec=Scm)
        profile1 = create_sample_log_forwarding_profile_response()
        profile1["folder"] = None
        profile1["device"] = "TestDevice"
        mock_response = {
            "data": [profile1],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)
        profiles = log_forwarding_profile.list(device="TestDevice")

        # Verify the result
        assert len(profiles) == 1
        assert profiles[0].device == "TestDevice"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/log-forwarding-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["device"] == "TestDevice"

    def test_list_empty_folder(self):
        """Test listing log forwarding profiles with empty folder string."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            log_forwarding_profile.list(folder="")
        assert "folder" in str(exc_info.value.details.get("field"))

    def test_list_no_container(self):
        """Test listing log forwarding profiles without a container."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile.list()
        assert "Invalid container parameters" in str(exc_info.value.details.get("error"))

    def test_list_with_filtering(self):
        """Test listing log forwarding profiles with filtering."""
        api_client = MagicMock(spec=Scm)

        # Profile with traffic log type
        profile1 = create_sample_log_forwarding_profile_response()
        profile1["match_list"][0]["log_type"] = "traffic"

        # Profile with threat log type
        profile2 = create_sample_log_forwarding_profile_response()
        profile2["name"] = "another-profile"
        profile2["match_list"][0]["log_type"] = "threat"

        mock_response = {
            "data": [profile1, profile2],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)
        profiles = log_forwarding_profile.list(folder="Shared", log_type="traffic")

        # Verify the result - should only include profile with traffic log type
        assert len(profiles) == 1
        assert profiles[0].match_list[0].log_type == "traffic"
        assert profiles[0].name == "test-log-profile"

    def test_list_with_multiple_log_types(self):
        """Test listing log forwarding profiles with multiple log types."""
        api_client = MagicMock(spec=Scm)

        # Profile with traffic log type
        profile1 = create_sample_log_forwarding_profile_response()
        profile1["match_list"][0]["log_type"] = "traffic"

        # Profile with threat log type
        profile2 = create_sample_log_forwarding_profile_response()
        profile2["name"] = "profile2"
        profile2["match_list"][0]["log_type"] = "threat"

        # Profile with URL log type
        profile3 = create_sample_log_forwarding_profile_response()
        profile3["name"] = "profile3"
        profile3["match_list"][0]["log_type"] = "url"

        mock_response = {
            "data": [profile1, profile2, profile3],
            "limit": 200,
            "offset": 0,
            "total": 3,
        }
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)

        # Filter for traffic and threat log types
        profiles = log_forwarding_profile.list(folder="Shared", log_type=["traffic", "threat"])

        # Verify result - should include profiles 1 and 2
        assert len(profiles) == 2
        assert "profile3" not in [p.name for p in profiles]

    def test_list_with_invalid_log_type_filter(self):
        """Test listing log forwarding profiles with invalid log_type filter."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {
            "data": [create_sample_log_forwarding_profile_response()],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }

        log_forwarding_profile = LogForwardingProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile.list(folder="Shared", log_type=123)  # Invalid type
        assert "errorType" in str(exc_info.value.details)

    def test_apply_filters_directly(self):
        """Test _apply_filters method directly to improve code coverage."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)

        # Create sample profiles
        profile1 = LogForwardingProfileResponseModel(
            **create_sample_log_forwarding_profile_response()
        )
        profile1.match_list[0].log_type = "traffic"

        profile2 = LogForwardingProfileResponseModel(
            **create_sample_log_forwarding_profile_response()
        )
        profile2.match_list[0].log_type = "threat"

        # Create profile3 with url log type
        profile3 = LogForwardingProfileResponseModel(
            **create_sample_log_forwarding_profile_response()
        )
        profile3.match_list[0].log_type = "url"

        # Test log_type filter
        filtered = log_forwarding_profile._apply_filters(
            [profile1, profile2], {"log_type": ["traffic"]}
        )
        assert len(filtered) == 1
        assert filtered[0].match_list[0].log_type == "traffic"

        # Test with empty profiles list
        filtered = log_forwarding_profile._apply_filters([], {"log_type": ["traffic"]})
        assert len(filtered) == 0

        # Test with empty filters dictionary
        filtered = log_forwarding_profile._apply_filters([profile1, profile2], {})
        assert len(filtered) == 2

        # Test with log_types (plural) filter
        filtered = log_forwarding_profile._apply_filters(
            [profile1, profile2, profile3], {"log_types": ["traffic", "url"]}
        )
        assert len(filtered) == 2
        assert set([p.match_list[0].log_type for p in filtered]) == set(["traffic", "url"])

        # Test with invalid log_types value
        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile._apply_filters(
                [profile1, profile2], {"log_types": "invalid-not-a-list"}
            )
        assert "filter must be a list" in str(exc_info.value.message)

        # For testing tags, we need to use a different approach since Pydantic models
        # don't allow setting arbitrary attributes

        # Create a test class with a tag property for testing
        class TestObject:
            def __init__(self, has_tag=False, match_list=None):
                self._has_tag = has_tag
                self._match_list = match_list

            @property
            def tag(self):
                if self._has_tag:
                    return ["test-tag", "production"]
                return None

            @property
            def match_list(self):
                return self._match_list

        # Create test profiles with the test class
        test_profile1 = TestObject(has_tag=False)
        test_profile2 = TestObject(has_tag=False)
        test_profile3 = TestObject(has_tag=True)

        # Test with tags filter using our test objects
        filtered = log_forwarding_profile._apply_filters(
            [test_profile1, test_profile2, test_profile3], {"tags": ["test-tag"]}
        )
        # Only test_profile3 should match
        assert len(filtered) == 1
        assert filtered[0] == test_profile3

        # Test with invalid tags value
        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile._apply_filters(
                [profile1, profile2, profile3], {"tags": "invalid-not-a-list"}
            )
        assert "filter must be a list" in str(exc_info.value.message)

    def test_fetch(self):
        """Test fetching a single log forwarding profile by name."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_log_forwarding_profile_response()
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)
        profile = log_forwarding_profile.fetch(name="test-log-profile", folder="Shared")

        # Verify the result
        assert profile.name == "test-log-profile"
        assert profile.folder == "Shared"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/log-forwarding-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["name"] == "test-log-profile"
        assert kwargs["params"]["folder"] == "Shared"

    def test_fetch_with_snippet(self):
        """Test fetching a log forwarding profile in a snippet container."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_log_forwarding_profile_response()
        mock_response["folder"] = None
        mock_response["snippet"] = "TestSnippet"
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)
        profile = log_forwarding_profile.fetch(name="test-log-profile", snippet="TestSnippet")

        # Verify the result
        assert profile.name == "test-log-profile"
        assert profile.snippet == "TestSnippet"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/log-forwarding-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["name"] == "test-log-profile"
        assert kwargs["params"]["snippet"] == "TestSnippet"

    def test_fetch_with_device(self):
        """Test fetching a log forwarding profile in a device container."""
        api_client = MagicMock(spec=Scm)
        mock_response = create_sample_log_forwarding_profile_response()
        mock_response["folder"] = None
        mock_response["device"] = "TestDevice"
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)
        profile = log_forwarding_profile.fetch(name="test-log-profile", device="TestDevice")

        # Verify the result
        assert profile.name == "test-log-profile"
        assert profile.device == "TestDevice"

        # Verify API call
        api_client.get.assert_called_once()
        args, kwargs = api_client.get.call_args
        assert args[0] == "/config/objects/v1/log-forwarding-profiles"
        assert "params" in kwargs
        assert kwargs["params"]["name"] == "test-log-profile"
        assert kwargs["params"]["device"] == "TestDevice"

    def test_fetch_empty_name(self):
        """Test fetching with empty name."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            log_forwarding_profile.fetch(name="", folder="Shared")
        assert "name" in str(exc_info.value.details.get("field"))

    def test_fetch_empty_folder(self):
        """Test fetching with empty folder string."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)

        with pytest.raises(MissingQueryParameterError) as exc_info:
            log_forwarding_profile.fetch(name="test-profile", folder="")
        assert "folder" in str(exc_info.value.details.get("field"))

    def test_fetch_no_container(self):
        """Test fetching without a container."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)

        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile.fetch(name="test-profile")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_fetch_invalid_response_format(self):
        """Test fetching with an invalid response format."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = "not a dictionary"  # Invalid response

        log_forwarding_profile = LogForwardingProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile.fetch(name="test-profile", folder="Shared")
        assert "Invalid response format: expected dictionary" in exc_info.value.message

    def test_fetch_missing_id_field(self):
        """Test fetching with response missing ID field."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {"name": "test-profile"}  # Missing ID

        log_forwarding_profile = LogForwardingProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile.fetch(name="test-profile", folder="Shared")
        assert "Invalid response format: missing 'id' field" in exc_info.value.message

    def test_list_response_not_dict(self):
        """Test list with response that's not a dictionary."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = "not a dictionary"  # Invalid response

        log_forwarding_profile = LogForwardingProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in exc_info.value.message

    def test_list_response_missing_data(self):
        """Test list with response missing data field."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {"total": 0}  # Missing data field

        log_forwarding_profile = LogForwardingProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile.list(folder="Shared")
        assert "Invalid response format: missing 'data' field" in exc_info.value.message

    def test_list_response_data_not_list(self):
        """Test list with data field that's not a list."""
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {"data": "not a list"}  # Data not a list

        log_forwarding_profile = LogForwardingProfile(api_client)
        with pytest.raises(InvalidObjectError) as exc_info:
            log_forwarding_profile.list(folder="Shared")
        assert "Invalid response format: 'data' field must be a list" in exc_info.value.message

    def test_list_with_pagination(self):
        """Test list with pagination through multiple requests."""
        api_client = MagicMock(spec=Scm)

        # First response with 2 items (limit=2)
        profile1 = create_sample_log_forwarding_profile_response()
        profile1["name"] = "profile1"
        profile2 = create_sample_log_forwarding_profile_response()
        profile2["name"] = "profile2"

        first_response = {
            "data": [profile1, profile2],
            "limit": 2,
            "offset": 0,
            "total": 3,
        }

        # Second response with 1 item
        profile3 = create_sample_log_forwarding_profile_response()
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
        log_forwarding_profile = LogForwardingProfile(api_client, max_limit=2)
        profiles = log_forwarding_profile.list(folder="Shared")

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
        profile1 = create_sample_log_forwarding_profile_response()
        profile1["name"] = "profile1"
        profile1["folder"] = "Folder1"

        profile2 = create_sample_log_forwarding_profile_response()
        profile2["name"] = "profile2"
        profile2["folder"] = "Folder2"

        profile3 = create_sample_log_forwarding_profile_response()
        profile3["name"] = "profile3"
        profile3["snippet"] = "Snippet1"

        profile4 = create_sample_log_forwarding_profile_response()
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
        log_forwarding_profile = LogForwardingProfile(api_client)
        profiles = log_forwarding_profile.list(folder="Shared", exclude_folders=["Folder2"])

        # Should exclude profile2 with Folder2
        assert len(profiles) == 3
        assert "profile2" not in [p.name for p in profiles]

        # Test excluding snippets
        profiles = log_forwarding_profile.list(folder="Shared", exclude_snippets=["Snippet1"])

        # Should exclude profile3 with Snippet1
        assert len(profiles) == 3
        assert "profile3" not in [p.name for p in profiles]

        # Test excluding devices
        profiles = log_forwarding_profile.list(folder="Shared", exclude_devices=["Device1"])

        # Should exclude profile4 with Device1
        assert len(profiles) == 3
        assert "profile4" not in [p.name for p in profiles]

    def test_list_with_exact_match(self):
        """Test list with exact_match parameter."""
        api_client = MagicMock(spec=Scm)

        # Create test profiles with different folder values
        profile1 = create_sample_log_forwarding_profile_response()
        profile1["name"] = "profile1"
        profile1["folder"] = "Shared"  # Exact match

        profile2 = create_sample_log_forwarding_profile_response()
        profile2["name"] = "profile2"
        profile2["folder"] = "Other Folder"  # Different folder

        mock_response = {
            "data": [profile1, profile2],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        api_client.get.return_value = mock_response

        log_forwarding_profile = LogForwardingProfile(api_client)

        # Without exact_match, should return both profiles
        profiles = log_forwarding_profile.list(folder="Shared", exact_match=False)
        assert len(profiles) == 2

        # With exact_match, should return only the exact match profile
        profiles = log_forwarding_profile.list(folder="Shared", exact_match=True)
        assert len(profiles) == 1
        assert profiles[0].name == "profile1"
        assert profiles[0].folder == "Shared"

    def test_build_container_params(self):
        """Test the _build_container_params method directly for code coverage."""
        api_client = MagicMock(spec=Scm)
        log_forwarding_profile = LogForwardingProfile(api_client)

        # Test with all None values
        params = log_forwarding_profile._build_container_params(None, None, None)
        assert params == {}

        # Test with only folder
        params = log_forwarding_profile._build_container_params("FolderA", None, None)
        assert params == {"folder": "FolderA"}

        # Test with only snippet
        params = log_forwarding_profile._build_container_params(None, "SnippetB", None)
        assert params == {"snippet": "SnippetB"}

        # Test with only device
        params = log_forwarding_profile._build_container_params(None, None, "DeviceC")
        assert params == {"device": "DeviceC"}

        # Test with multiple values (this would lead to an error in actual usage)
        params = log_forwarding_profile._build_container_params("FolderA", "SnippetB", "DeviceC")
        assert len(params) == 3
        assert params["folder"] == "FolderA"
        assert params["snippet"] == "SnippetB"
        assert params["device"] == "DeviceC"


# -------------------- Tests for MatchListItem --------------------


class TestMatchListItem:
    """Tests for MatchListItem model."""

    def test_basic_match_list_item(self):
        """Test creating a basic MatchListItem."""
        match = MatchListItem(
            name="test-match",
            log_type="traffic",
            filter="addr.src in 192.168.0.0/24",
            send_http=["http-profile-1"],
        )

        assert match.name == "test-match"
        assert match.log_type == "traffic"
        assert match.filter == "addr.src in 192.168.0.0/24"
        assert match.send_http == ["http-profile-1"]
        assert match.send_syslog is None
        assert match.action_desc is None

    def test_match_list_item_with_syslog(self):
        """Test creating a MatchListItem with syslog profiles."""
        match = MatchListItem(
            name="syslog-match",
            log_type="threat",
            filter="severity eq critical",
            send_syslog=["syslog-profile-1"],
        )

        assert match.name == "syslog-match"
        assert match.log_type == "threat"
        assert match.filter == "severity eq critical"
        assert match.send_syslog == ["syslog-profile-1"]
        assert match.send_http is None

    def test_match_list_item_with_description(self):
        """Test creating a MatchListItem with a description."""
        match = MatchListItem(
            name="desc-match",
            log_type="url",
            action_desc="Match for URL category logging",
            filter="category eq social-networking",
            send_http=["http-profile-1"],
            send_syslog=["syslog-profile-1"],
        )

        assert match.name == "desc-match"
        assert match.log_type == "url"
        assert match.action_desc == "Match for URL category logging"
        assert match.filter == "category eq social-networking"
        assert match.send_http == ["http-profile-1"]
        assert match.send_syslog == ["syslog-profile-1"]
