# tests/scm/config/security/test_anti_spyware_profile.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.security import AntiSpywareProfile
from scm.exceptions import (
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
    ReferenceNotZeroError,
    BadRequestError,
    APIError,
)
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareProfileResponseModel,
    AntiSpywareSeverity,
    AntiSpywareCategory,
    AntiSpywarePacketCapture,
    AntiSpywareExemptIpEntry,
)
from tests.factories import (
    AntiSpywareProfileCreateApiFactory,
    AntiSpywareProfileUpdateApiFactory,
    AntiSpywareProfileResponseFactory,
    AntiSpywareRuleBaseFactory,
    AntiSpywareThreatExceptionBaseFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestAntiSpywareProfileBase:
    """Base class for Anti-Spyware Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AntiSpywareProfile(self.mock_scm)  # noqa


class TestAntiSpywareProfileList(TestAntiSpywareProfileBase):
    """Tests for listing Anti-Spyware Profile objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                AntiSpywareProfileResponseFactory(
                    name="profile1",
                    folder="Shared",
                    rules=[AntiSpywareRuleBaseFactory()],
                ).model_dump(),
                AntiSpywareProfileResponseFactory(
                    name="profile2",
                    folder="Shared",
                    rules=[AntiSpywareRuleBaseFactory()],
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], AntiSpywareProfileResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "profile1"

    def test_list_folder_empty_error(self):
        """Test that an empty folder raises appropriate error."""
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
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_list_folder_nonexistent_error(self):
        """Test error handling in list operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

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
            "rules": ["test1", "test2"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
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
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "basic-profile",
                    "description": "Basic anti-spyware profile",
                    "folder": "Texas",
                    "rules": [
                        {
                            "name": "block-critical",
                            "severity": ["critical"],
                            "category": "spyware",
                            "action": {
                                "block_ip": {"track_by": "source", "duration": 300}
                            },
                        }
                    ],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Texas",
            rules=[],
        )
        assert len(filtered_objects) == 0

    def test_list_filters_types(self):
        """Test validation of filter types in list method."""
        # Mock response for successful case
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "basic-profile",
                    "description": "Basic anti-spyware profile",
                    "folder": "Texas",
                    "rules": [
                        {
                            "name": "block-critical",
                            "severity": ["critical"],
                            "category": "spyware",
                            "action": {
                                "block_ip": {"track_by": "source", "duration": 300}
                            },
                        }
                    ],
                }
            ]
        }

        # Test invalid types filter (string instead of list)
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'types' filter must be a list",
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
                rules=["test1"],
            )
        except BadRequestError:
            pytest.fail("Unexpected BadRequestError raised with valid list filters")

    def test_list_filters_rules_validation(self):
        """Test validation of filter specific fields."""
        mock_rules = []

        # Test with string instead of list
        invalid_filters = {"rules": "rules"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        # assert error.error_code == "E003"
        # assert error.http_status_code == 500
        # assert "{'errorType': 'Invalid Object'}" in str(error)

        # Test with dict instead of list
        invalid_filters = {"rules": {"value": "rules"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        # assert error.error_code == "E003"
        # assert error.http_status_code == 500
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

    def test_list_http_error_no_content(self):
        """Test handling of HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")


class TestAntiSpywareProfileCreate(TestAntiSpywareProfileBase):
    """Tests for creating Anti-Spyware Profile objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = AntiSpywareProfileCreateApiFactory.build()
        mock_response = AntiSpywareProfileResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump())

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            json=test_object.model_dump(),
        )
        assert isinstance(created_object, AntiSpywareProfileResponseModel)
        assert created_object.name == test_object.name

    def test_create_http_error_no_content(self):
        """Test creation with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create({"name": "test", "folder": "Shared", "rules": []})

    def test_create_with_rules(self):
        """Test creating profile with specific rules configuration."""
        test_object = AntiSpywareProfileCreateApiFactory.build(
            rules=[
                AntiSpywareRuleBaseFactory(
                    severity=[AntiSpywareSeverity.critical],
                    category=AntiSpywareCategory.spyware,
                    packet_capture=AntiSpywarePacketCapture.single_packet,
                )
            ]
        )

        mock_response = AntiSpywareProfileResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa

        created_object = self.client.create(test_object.model_dump())

        assert isinstance(created_object, AntiSpywareProfileResponseModel)
        assert len(created_object.rules) == 1
        assert created_object.rules[0].severity == [AntiSpywareSeverity.critical]
        assert created_object.rules[0].category == AntiSpywareCategory.spyware

    def test_create_with_threat_exceptions(self):
        """Test creating profile with threat exceptions."""
        test_object = AntiSpywareProfileCreateApiFactory.build(
            threat_exception=[
                AntiSpywareThreatExceptionBaseFactory(
                    name="test-exception",
                    packet_capture=AntiSpywarePacketCapture.extended_capture,
                    exempt_ip=[AntiSpywareExemptIpEntry(name="192.168.1.1")],
                )
            ]
        )

        mock_response = AntiSpywareProfileResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa

        created_object = self.client.create(test_object.model_dump())

        assert isinstance(created_object, AntiSpywareProfileResponseModel)
        assert len(created_object.threat_exception) == 1
        assert (
            created_object.threat_exception[0].packet_capture
            == AntiSpywarePacketCapture.extended_capture
        )

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
                {
                    "name": "advanced-profile",
                    "description": "Advanced anti-spyware profile",
                    "folder": "Texas",
                    "cloud_inline_analysis": True,
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "alert",
                        }
                    ],
                    "rules": [
                        {
                            "name": "critical-threats",
                            "severity": ["critical", "high"],
                            "category": "command-and-control",
                            "action": {"reset_both": {}},
                        },
                        {
                            "name": "medium-threats",
                            "severity": ["medium"],
                            "category": "spyware",
                            "action": {"alert": {}},
                        },
                    ],
                }
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "advanced-profile",
            "description": "Advanced anti-spyware profile",
            "folder": "Texas",
            "cloud_inline_analysis": True,
            "mica_engine_spyware_enabled": [
                {
                    "name": "HTTP Command and Control detector",
                    "inline_policy_action": "alert",
                }
            ],
            "rules": [
                {
                    "name": "critical-threats",
                    "severity": ["critical", "high"],
                    "category": "command-and-control",
                    "action": {"reset_both": {}},
                },
                {
                    "name": "medium-threats",
                    "severity": ["medium"],
                    "category": "spyware",
                    "action": {"alert": {}},
                },
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
                    "name": "advanced-profile",
                    "description": "Advanced anti-spyware profile",
                    "folder": "Texas",
                    "cloud_inline_analysis": True,
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "alert",
                        }
                    ],
                    "rules": [
                        {
                            "name": "critical-threats",
                            "severity": ["critical", "high"],
                            "category": "command-and-control",
                            "action": {"reset_both": {}},
                        },
                        {
                            "name": "medium-threats",
                            "severity": ["medium"],
                            "category": "spyware",
                            "action": {"alert": {}},
                        },
                    ],
                }
            )
        assert str(exc_info.value) == "Generic error"


class TestAntiSpywareProfileUpdate(TestAntiSpywareProfileBase):
    """Tests for updating Anti-Spyware Profile objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        # Create update data using factory
        update_data = AntiSpywareProfileUpdateApiFactory.with_cloud_inline_analysis(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="advanced-profile",
            # cloud_inline_analysis=True,
            description="Advanced anti-spyware profile",
            folder="Texas",
            mica_engine_spyware_enabled=[
                {
                    "name": "HTTP Command and Control detector",
                    "inline_policy_action": "alert",
                }
            ],
            rules=[AntiSpywareRuleBaseFactory()],
        )
        input_data = update_data.model_dump()

        # Create mock response
        mock_response = AntiSpywareProfileResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        # Perform update
        updated_object = self.client.update(input_data)

        # Assert the put method was called with correct parameters
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/security/v1/anti-spyware-profiles/{update_data.id}",
            json=input_data,
        )

        # Assert the updated object matches the mock response
        assert isinstance(updated_object, AntiSpywareProfileResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name
        assert updated_object.description == mock_response.description
        assert updated_object.folder == mock_response.folder

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        # Create test data using factory
        update_data = AntiSpywareProfileUpdateApiFactory.with_cloud_inline_analysis(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="advanced-profile",
            # cloud_inline_analysis=True,
            description="Advanced anti-spyware profile",
            folder="Texas",
            mica_engine_spyware_enabled=[
                {
                    "name": "HTTP Command and Control detector",
                    "inline_policy_action": "alert",
                }
            ],
            rules=[AntiSpywareRuleBaseFactory()],
        )
        input_data = update_data.model_dump()

        # Use utility function to create mock HTTP error
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
        # Create test data using factory
        update_data = AntiSpywareProfileUpdateApiFactory.with_cloud_inline_analysis(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="advanced-profile",
            # cloud_inline_analysis=True,
            description="Advanced anti-spyware profile",
            folder="Texas",
            mica_engine_spyware_enabled=[
                {
                    "name": "HTTP Command and Control detector",
                    "inline_policy_action": "alert",
                }
            ],
            rules=[AntiSpywareRuleBaseFactory()],
        )
        input_data = update_data.model_dump()

        # Use utility function to simulate object not present error
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
        # Create a mock response object without content
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "advanced-profile",
                    "description": "Advanced anti-spyware profile",
                    "folder": "Texas",
                    "cloud_inline_analysis": True,
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "alert",
                        }
                    ],
                    "rules": [
                        {
                            "name": "critical-threats",
                            "severity": ["critical", "high"],
                            "category": "command-and-control",
                            "action": {"reset_both": {}},
                        },
                        {
                            "name": "medium-threats",
                            "severity": ["medium"],
                            "category": "spyware",
                            "action": {"alert": {}},
                        },
                    ],
                }
            )

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "advanced-profile",
                    "description": "Advanced anti-spyware profile",
                    "folder": "Texas",
                    "cloud_inline_analysis": True,
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "alert",
                        }
                    ],
                    "rules": [
                        {
                            "name": "critical-threats",
                            "severity": ["critical", "high"],
                            "category": "command-and-control",
                            "action": {"reset_both": {}},
                        },
                        {
                            "name": "medium-threats",
                            "severity": ["medium"],
                            "category": "spyware",
                            "action": {"alert": {}},
                        },
                    ],
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        # Create test data
        update_data = AntiSpywareProfileUpdateApiFactory.with_cloud_inline_analysis(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="advanced-profile",
            # cloud_inline_analysis=True,
            description="Advanced anti-spyware profile",
            folder="Texas",
            mica_engine_spyware_enabled=[
                {
                    "name": "HTTP Command and Control detector",
                    "inline_policy_action": "alert",
                }
            ],
            rules=[AntiSpywareRuleBaseFactory()],
        )

        input_data = update_data.model_dump()

        # Use utility function to simulate server error
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


class TestAntiSpywareProfileDelete(TestAntiSpywareProfileBase):
    """Tests for deleting Anti-Spyware Profile objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/anti-spyware-profiles/{object_id}"
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


class TestAntiSpywareProfileGet(TestAntiSpywareProfileBase):
    """Tests for retrieving a specific Anti-Spyware Profile object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = AntiSpywareProfileResponseFactory.build()

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        retrieved_object = self.client.get(str(mock_response.id))

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/anti-spyware-profiles/{mock_response.id}"
        )
        assert isinstance(retrieved_object, AntiSpywareProfileResponseModel)
        assert retrieved_object.name == mock_response.name

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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


class TestAddressFetch(TestAntiSpywareProfileBase):
    """Tests for fetching Address objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = AntiSpywareProfileResponseFactory.build()
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
            "/config/security/v1/anti-spyware-profiles",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        # Validate the returned object
        assert isinstance(fetched_object, dict)
        assert fetched_object["id"] == mock_response_model.id
        assert fetched_object["name"] == mock_response_model.name
        assert fetched_object["description"] == mock_response_model.description

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
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"name" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")

        error_msg = str(exc_info.value)
        assert '"name" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")

        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_invalid_response_format_error(self):
        """Test fetching an object when the API returns an unexpected format."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="Invalid response format",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Invalid Object'}" in error_msg
        assert "HTTP error: 500" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        assert str(exc_info.value) == "Generic error"

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        # Create a mock response object without content
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)

        # Set the side effect of the get method to raise the HTTPError
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-address", folder="Shared")

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
        # Mock response without 'id' field
        mock_response = {
            "name": "test-address",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-address", folder="Shared")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-address")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-address",
                folder="Shared",
                snippet="TestSnippet",
            )

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        # Mock the API client to return a non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Shared")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
