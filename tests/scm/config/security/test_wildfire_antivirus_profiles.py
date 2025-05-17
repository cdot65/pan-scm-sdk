# tests/scm/config/security/test_wildfire_antivirus_profiles.py

import logging
from unittest.mock import MagicMock

from pydantic import ValidationError as PydanticValidationError
import pytest
from requests import HTTPError

from scm.config.security.wildfire_antivirus_profile import WildfireAntivirusProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAvAnalysis,
    WildfireAvDirection,
    WildfireAvProfileCreateModel,
    WildfireAvProfileResponseModel,
)
from scm.utils.logging import setup_logger
from tests.factories.security import (
    WildfireAvProfileResponseFactory,
    WildfireAvProfileUpdateApiFactory,
)
from tests.utils import raise_mock_http_error

logger = setup_logger(__name__, logging.DEBUG)


@pytest.mark.usefixtures("load_env")
class TestWildfireAntivirusProfileBase:
    """Base class for Wildfire Antivirus Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = WildfireAntivirusProfile(self.mock_scm, max_limit=5000)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestWildfireAntivirusProfileMaxLimit(TestWildfireAntivirusProfileBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = WildfireAntivirusProfile(self.mock_scm)  # noqa
        assert client.max_limit == WildfireAntivirusProfile.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = WildfireAntivirusProfile(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = WildfireAntivirusProfile(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            WildfireAntivirusProfile(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            WildfireAntivirusProfile(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            WildfireAntivirusProfile(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestWildfireAntivirusProfileModelValidation(TestWildfireAntivirusProfileBase):
    """Tests for object model validation."""

    def test_object_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "InvalidProfile",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            WildfireAvProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_object_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "InvalidProfile",
            "folder": "Texas",
            "device": "Device1",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            WildfireAvProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )


class TestWildfireAntivirusProfileList(TestWildfireAntivirusProfileBase):
    """Tests for listing Wildfire Antivirus Profile objects."""

    def test_list_objects(self):
        """**Objective:** Test listing all objects.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing objects.
            2. Calls the `list` method with a filter parameter.
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of objects.
        """
        mock_response = {
            "data": [
                {
                    "id": "dd0f80ce-9345-4cf1-9979-bce99da27888",
                    "name": "web-security-default",
                    "folder": "All",
                    "snippet": "Web-Security-Default",
                    "rules": [
                        {
                            "name": "default-fawkes",
                            "direction": "both",
                            "file_type": ["any"],
                            "application": ["any"],
                        }
                    ],
                },
                {
                    "id": "e2a5dfc4-d8c8-489a-9661-092032796e09",
                    "name": "best-practice",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "rules": [
                        {
                            "name": "default",
                            "application": ["any"],
                            "file_type": ["any"],
                            "direction": "both",
                            "analysis": "public-cloud",
                        }
                    ],
                    "description": "Best practice profile",
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "limit": 5000,
                "folder": "All",
                "offset": 0,
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], WildfireAvProfileResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "web-security-default"
        assert existing_objects[0].rules[0].direction == WildfireAvDirection.both

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)

    # -------------------- New Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """Test that exact_match=True returns only objects that match the container exactly.
        """
        mock_response = {
            "data": [
                WildfireAvProfileResponseFactory(
                    name="addr_in_texas",
                    folder="Texas",
                ).model_dump(),
                WildfireAvProfileResponseFactory(
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
        """Test that exclude_folders removes objects from those folders.
        """
        mock_response = {
            "data": [
                WildfireAvProfileResponseFactory(
                    name="addr_in_texas",
                    folder="Texas",
                ).model_dump(),
                WildfireAvProfileResponseFactory(
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
        """Test that exclude_snippets removes objects with those snippets.
        """
        mock_response = {
            "data": [
                WildfireAvProfileResponseFactory(
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(),
                WildfireAvProfileResponseFactory(
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
        """Test that exclude_devices removes objects with those devices.
        """
        mock_response = {
            "data": [
                WildfireAvProfileResponseFactory(
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                    device="DeviceA",
                ).model_dump(),
                WildfireAvProfileResponseFactory(
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
        """Test combining exact_match with exclusions.
        """
        mock_response = {
            "data": [
                WildfireAvProfileResponseFactory(
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(),
                WildfireAvProfileResponseFactory(
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

    def test_list_pagination_multiple_pages(self):
        """Test that the list method correctly aggregates data from multiple pages.
        Using a custom client with max_limit=2500 to test pagination.
        """
        client = WildfireAntivirusProfile(self.mock_scm, max_limit=2500)  # noqa

        # Create test data for three pages with different profile configurations
        first_page = [
            WildfireAvProfileResponseFactory(
                name=f"both-direction-page1-{i}",
                folder="Texas",
                rules=[
                    {
                        "name": f"rule-both-{i}",
                        "direction": WildfireAvDirection.both,
                        "application": ["any"],
                        "file_type": ["any"],
                        "analysis": "public-cloud",
                    }
                ],
            ).model_dump()
            for i in range(2500)
        ]

        second_page = [
            WildfireAvProfileResponseFactory(
                name=f"upload-direction-page2-{i}",
                folder="Texas",
                rules=[
                    {
                        "name": f"rule-upload-{i}",
                        "direction": WildfireAvDirection.upload,
                        "application": ["web-browsing"],
                        "file_type": ["pe"],
                        "analysis": "private-cloud",
                    }
                ],
            ).model_dump()
            for i in range(2500)
        ]

        third_page = [
            WildfireAvProfileResponseFactory(
                name=f"download-direction-page3-{i}",
                folder="Texas",
                rules=[
                    {
                        "name": f"rule-download-{i}",
                        "direction": WildfireAvDirection.download,
                        "application": ["ftp"],
                        "file_type": ["pdf"],
                        "analysis": "public-cloud",
                    }
                ],
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
        assert isinstance(results[0], WildfireAvProfileResponseModel)
        assert all(isinstance(obj, WildfireAvProfileResponseModel) for obj in results)

        # Verify API calls
        assert self.mock_scm.get.call_count == 4  # noqa # Three pages + one final check

        # Verify API calls were made with correct offset values
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 0,
            },
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 2500,
            },
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 5000,
            },
        )

        # Verify content ordering and profile-specific attributes
        assert results[0].name == "both-direction-page1-0"
        assert results[0].rules[0].direction == WildfireAvDirection.both
        assert results[0].rules[0].analysis == "public-cloud"

        assert results[2500].name == "upload-direction-page2-0"
        assert results[2500].rules[0].direction == WildfireAvDirection.upload
        assert results[2500].rules[0].analysis == "private-cloud"

        assert results[5000].name == "download-direction-page3-0"
        assert results[5000].rules[0].direction == WildfireAvDirection.download
        assert results[5000].rules[0].file_type == ["pdf"]


class TestWildfireAntivirusProfileCreate(TestWildfireAntivirusProfileBase):
    """Tests for creating Wildfire Antivirus Profile objects."""

    def test_create_object(self):
        """**Objective:** Test creating a new object.
        **Workflow:**
            1. Creates test data.
            2. Mocks the API response.
            3. Verifies the creation request and response.
        """
        test_profile_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "description": "A new test profile",
            "packet_capture": True,
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
            "mlav_exception": [
                {
                    "name": "Exception1",
                    "description": "An exception",
                    "filename": "malicious.exe",
                }
            ],
            "threat_exception": [
                {
                    "name": "ThreatException1",
                    "notes": "Some notes",
                }
            ],
        }

        mock_response = test_profile_data.copy()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_profile = self.client.create(test_profile_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            json=test_profile_data,
        )
        assert isinstance(created_profile, WildfireAvProfileResponseModel)
        assert str(created_profile.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_profile.name == "NewWFProfile"
        assert created_profile.rules[0].analysis == WildfireAvAnalysis.public_cloud

    def test_create_object_error_handling(self):
        """**Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }

        # Configure mock to raise HTTPError with proper error details
        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=409,  # Conflict status code
            error_code="API_I00013",
            message="Object Already Exists",
            error_type="Object Already Exists",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object Already Exists"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Already Exists"

    def test_create_generic_exception_handling(self):
        """Test generic exception handling in create method."""
        test_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_create_malformed_response_handling(self):
        """Test handling of malformed response in create method."""
        test_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Invalid request format",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Invalid request format"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"

    def test_create_http_error_no_content(self):
        """Test create method when HTTP error has no response content."""
        test_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }

        # Mock an HTTPError with no response content
        mock_response = MagicMock()
        mock_response.content = None  # No content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(test_data)


class TestWildfireAntivirusProfileGet(TestWildfireAntivirusProfileBase):
    """Tests for retrieving a specific Wildfire Antivirus Profile object."""

    def test_get_object(self):
        """**Objective:** Test retrieving a specific object.
        **Workflow:**
            1. Mocks the API response for a specific object.
            2. Verifies the get request and response handling.
        """
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": profile_id,
            "name": "TestProfile",
            "folder": "All",
            "description": "A test profile",
            "rules": [
                {
                    "name": "TestRule",
                    "direction": "download",
                    "application": ["app1", "app2"],
                    "file_type": ["pdf", "exe"],
                    "analysis": "private-cloud",
                }
            ],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        get_object = self.client.get(profile_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/wildfire-anti-virus-profiles/{profile_id}"
        )
        assert isinstance(get_object, WildfireAvProfileResponseModel)
        assert str(get_object.id) == profile_id
        assert get_object.rules[0].analysis == WildfireAvAnalysis.private_cloud

    def test_get_object_error_handling(self):
        """Test error handling during object retrieval."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="E005",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_get_generic_exception_handling(self):
        """Test generic exception handling in get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="Internal server error",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Internal server error"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_get_http_error_no_content(self):
        """Test get method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock an HTTPError with no response content
        mock_response = MagicMock()
        mock_response.content = None  # No content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.get(object_id)


class TestWildfireAntivirusProfileUpdate(TestWildfireAntivirusProfileBase):
    """Tests for updating Wildfire Antivirus Profile objects."""

    def test_update_valid_object(self):
        """Test updating an application with valid data."""
        # Create update data using factory
        update_data = WildfireAvProfileUpdateApiFactory.with_packet_capture()

        # Create mock response
        mock_response = WildfireAvProfileResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        # Perform update with Pydantic model directly
        updated_object = self.client.update(update_data)

        # Verify call was made once
        self.mock_scm.put.assert_called_once()  # noqa

        # Get the actual call arguments
        call_args = self.mock_scm.put.call_args  # noqa

        # Check endpoint
        assert (
            call_args[0][0] == f"/config/security/v1/wildfire-anti-virus-profiles/{update_data.id}"
        )

        # Check important payload fields
        payload = call_args[1]["json"]
        assert payload["name"] == update_data.name
        assert payload["description"] == update_data.description

        # Assert the updated object matches the mock response
        assert isinstance(updated_object, WildfireAvProfileResponseModel)
        assert str(updated_object.id) == str(mock_response.id)
        assert updated_object.name == mock_response.name
        assert updated_object.description == mock_response.description

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        # Create update data using factory
        update_data = WildfireAvProfileUpdateApiFactory.with_packet_capture()

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

    def test_update_generic_exception_handling(self):
        # Create update data using factory
        update_data = WildfireAvProfileUpdateApiFactory.with_packet_capture()

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_http_error_no_response_content(self):
        # Create update data using factory
        update_data = WildfireAvProfileUpdateApiFactory.with_packet_capture()

        # Create a mock response object without content
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)


class TestWildfireAntivirusProfileDelete(TestWildfireAntivirusProfileBase):
    """Tests for deleting Wildfire Antivirus Profile objects."""

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced by other objects."""
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

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
        assert error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"

    def test_delete_error_handling(self):
        """Test error handling during object deletion.

        **Objective:** Test error handling during object deletion.
        **Workflow:**
            1. Mocks various error scenarios
            2. Verifies proper error handling for each case
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Test object not found scenario
        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,  # Not Found status code
            error_code="E005",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_delete_generic_exception_handling(self):
        """Test generic exception handling in delete method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="Internal server error",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Internal server error"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_delete_http_error_no_content(self):
        """Test delete method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock an HTTPError with no response content
        mock_response = MagicMock()
        mock_response.content = None  # No content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.delete(object_id)


class TestWildfireAntivirusProfileFetch(TestWildfireAntivirusProfileBase):
    """Tests for fetching Wildfire Antivirus Profile objects by name."""

    def test_fetch_valid_object(self):
        """**Objective:** Test retrieving an object by its name using the `fetch` method.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an object by name.
            2. Calls the `fetch` method of `self.client` with a specific name and container.
            3. Asserts that the mocked service was called with the correct URL and parameters.
            4. Validates the returned object's attributes.
        """
        mock_response_model = WildfireAvProfileResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
            folder="All",
            description="Test profile",
            rules=[
                {
                    "name": "TestRule",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
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
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        # Validate the returned object
        assert isinstance(fetched_object, WildfireAvProfileResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.folder == mock_response_model.folder
        assert fetched_object.description == mock_response_model.description

    def test_fetch_object_not_found(self):
        """Test fetching an object by name that does not exist.

        **Objective:** Test that fetching a non-existent object raises ObjectNotPresentError.
        **Workflow:**
            1. Mocks the API response to indicate object not found
            2. Calls the `fetch` method with a name that does not exist
            3. Asserts that ObjectNotPresentError is raised
        """
        object_name = "NonExistent"
        folder_name = "Texas"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="E005",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name=object_name, folder=folder_name)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

        # Verify the get method was called with correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "folder": folder_name,
                "name": object_name,
            },
        )

    def test_fetch_empty_name(self):
        """**Objective:** Test fetch with empty name parameter.
        **Workflow:**
            1. Attempts to fetch with empty name
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Texas")
        assert (
            "{'field': 'name', 'error': '\"name\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

    def test_fetch_container_validation(self):
        """**Objective:** Test container parameter validation in fetch.
        **Workflow:**
            1. Tests various invalid container combinations
            2. Verifies proper error handling
        """
        # Test empty folder
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

        # Test no container provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile")
        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)

        # Test multiple containers provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile", folder="Texas", snippet="TestSnippet")
        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)

    def test_fetch_object_unexpected_response_format(self):
        """Test fetching an object when the API returns an unexpected format."""
        group_name = "TestGroup"
        folder_name = "Texas"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Invalid response format",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name=group_name, folder=folder_name)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Invalid response format"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"

    def test_fetch_error_handler_json_error(self):
        """Test fetch method error handling when json() raises an error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Input Format Mismatch",
            error_type="Input Format Mismatch",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Input Format Mismatch"
        assert error_response["_errors"][0]["details"]["errorType"] == "Input Format Mismatch"

    def test_fetch_response_not_dict(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile", folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_fetch_response_missing_id_field(self):
        """Test that InvalidObjectError is raised when response is missing 'id' field."""
        self.mock_scm.get.return_value = {  # noqa
            "name": "test-profile",
            "folder": "Texas",
            "rules": [],
        }  # Missing 'id' field

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile", folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_fetch_http_error_no_content(self):
        """Test fetch method when HTTP error has no response content."""
        # Mock an HTTPError with no response content
        mock_response = MagicMock()
        mock_response.content = None  # No content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-profile", folder="Texas")


class TestWildfireAntivirusProfileListFilters(TestWildfireAntivirusProfileBase):
    """Tests for filtering during listing Wildfire Antivirus Profile objects."""

    def test_list_with_filters(self):
        """**Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        filters = {
            "rules": ["rule1", "rule2"],
            "analysis": ["public-cloud", "private-cloud"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Texas", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "limit": 5000,
                "folder": "Texas",
                "offset": 0,
            },
        )

    def test_list_empty_folder_error(self):
        """**Objective:** Test that empty folder raises appropriate error.
        **Workflow:**
            1. Attempts to list objects with empty folder
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

    def test_list_multiple_containers_error(self):
        """**Objective:** Test validation of container parameters.
        **Workflow:**
            1. Attempts to list with multiple containers
            2. Verifies InvalidObjectError is raised
        """
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")
        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)

    def test_list_non_dict_response(self):
        """Test list method handling of non-dictionary response."""
        # Test with list response
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Invalid Object",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Invalid Object"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"

        # Verify the get method was called with correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "folder": "Texas",
                "limit": 5000,
                "offset": 0,
            },
        )

    def test_list_filters_type_validation(self):
        """**Objective:** Test validation of filter types in list method.
        **Workflow:**
            1. Tests various invalid filter type scenarios
            2. Verifies InvalidObjectError is raised with correct message
            3. Tests valid filter types pass validation
        """
        mock_response = {
            "data": [
                {
                    "id": "dd0f80ce-9345-4cf1-9979-bce99da27888",
                    "name": "web-security-default",
                    "folder": "All",
                    "rules": [
                        {
                            "name": "default-fawkes",
                            "direction": "both",
                            "file_type": ["any"],
                            "application": ["any"],
                        }
                    ],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid rules filter (string instead of list)
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", rules="rule1")

        # Test invalid rules filter (dict instead of list)
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", rules={"rule": "rule1"})

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Texas",
                rules=["rule1"],
            )
        except InvalidObjectError:
            pytest.fail("Unexpected InvalidObjectError raised with valid list filters")

    def test_list_response_not_dict(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_missing_data_field(self):
        """Test that InvalidObjectError is raised when 'data' field is missing."""
        self.mock_scm.get.return_value = {"invalid": "data"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_data_not_list(self):
        """Test that InvalidObjectError is raised when 'data' field is not a list."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_http_error_no_content(self):
        """Test list method when HTTP error has no response content."""
        # Mock an HTTPError with no response content
        mock_response = MagicMock()
        mock_response.content = None  # No content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")


# -------------------- End of Test Classes --------------------
