# tests/scm/config/security/test_security_rules.py

# Standard library imports
import uuid
from unittest.mock import MagicMock

# External libraries
import pytest
from pydantic import ValidationError
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.security import SecurityRule
from scm.exceptions import (
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
    ReferenceNotZeroError,
    APIError,
)
from scm.models.security.security_rules import (
    SecurityRuleResponseModel,
    SecurityRuleAction,
    SecurityRuleRulebase,
    SecurityRuleProfileSetting,
    SecurityRuleCreateModel,
    SecurityRuleMoveModel,
    SecurityRuleMoveDestination,
)
from tests.factories import (
    SecurityRuleCreateApiFactory,
    SecurityRuleUpdateApiFactory,
    SecurityRuleResponseFactory,
    SecurityRuleProfileSettingFactory,
    SecurityRuleMoveApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestSecurityRuleBase:
    """Base class for Security Rule tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = SecurityRule(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestSecurityRuleList(TestSecurityRuleBase):
    """Tests for listing Security Rule objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1",
                    folder="Shared",
                    action=SecurityRuleAction.allow,
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    folder="Shared",
                    action=SecurityRuleAction.deny,
                ).model_dump(by_alias=True),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={
                "limit": 10000,
                "folder": "Shared",
                "position": "pre",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], SecurityRuleResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "rule1"

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
        """Test that valid filters are properly applied."""
        # Create mock rules with different attributes
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1",
                    folder="Shared",
                    action=SecurityRuleAction.allow,
                    source=["10.0.0.0/24"],
                    destination=["any"],
                    from_=["trust"],
                    to_=["untrust"],
                    tag=["tag1"],
                    profile_setting=SecurityRuleProfileSettingFactory(
                        group=["best-practice"]
                    ),
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    folder="Shared",
                    action=SecurityRuleAction.deny,
                    source=["any"],
                    destination=["10.1.0.0/24"],
                    from_=["untrust"],
                    to_=["trust"],
                    tag=["tag2"],
                    profile_setting=SecurityRuleProfileSettingFactory(group=["strict"]),
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test each type of filter
        filters = {
            "action": [SecurityRuleAction.allow],
            "category": ["any"],
            "service": ["any"],
            "application": ["any"],
            "destination": ["any"],
            "to_": ["untrust"],
            "source": ["10.0.0.0/24"],
            "from_": ["trust"],
            "tag": ["tag1"],
            "profile_setting": ["best-practice"],
        }

        filtered_objects = self.client.list(folder="Shared", **filters)

        # Verify the filtering
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"
        assert filtered_objects[0].action == SecurityRuleAction.allow

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1", folder="Shared", action=SecurityRuleAction.allow
                ).model_dump(by_alias=True)
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Shared",
            action=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            category=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            service=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            disabled=False,
        )
        assert len(filtered_objects) == 1

        filtered_objects = self.client.list(
            folder="Shared",
            log_setting=[],
        )
        assert len(filtered_objects) == 0

    def test_list_filters_types_validation(self):
        """Test validation of filter types specifically."""
        mock_rules = []
        test_cases = [
            ("action", "allow"),
            ("category", "category1"),
            ("service", "service1"),
            ("application", "app1"),
            ("destination", "10.0.0.0/24"),
            ("to_", "trust"),
            ("source", "any"),
            ("from_", "untrust"),
            ("tag", "tag1"),
            ("profile_setting", "group1"),
        ]

        # Test each filter type
        for filter_name, filter_value in test_cases:
            invalid_filters = {filter_name: filter_value}  # String instead of list
            with pytest.raises(InvalidObjectError):
                self.client._apply_filters(mock_rules, invalid_filters)

    def test_list_complex_filtering(self):
        """Test multiple filters combined."""
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1",
                    action=SecurityRuleAction.allow,
                    source=["10.0.0.0/24"],
                    destination=["any"],
                    tag=["tag1", "tag2"],
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    action=SecurityRuleAction.allow,
                    source=["10.0.0.0/24"],
                    destination=["any"],
                    tag=["tag2"],
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test multiple combined filters
        filtered_objects = self.client.list(
            folder="Shared",
            action=[SecurityRuleAction.allow],
            source=["10.0.0.0/24"],
            tag=["tag1"],
        )

        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"

    def test_list_filters_disabled_validation(self):
        """Test validation of 'disabled' filter specifically."""
        mock_rules = []

        # Test with string instead of boolean
        invalid_filters = {"disabled": "true"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

        # Test with integer instead of boolean
        invalid_filters = {"disabled": 1}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

        # Test with list instead of boolean
        invalid_filters = {"disabled": [True]}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

    def test_list_filters_log_setting_validation(self):
        """Test validation of 'log_setting' filter specifically."""
        mock_rules = []

        # Test with string instead of list
        invalid_filters = {"log_setting": "default-logging"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

        # Test with integer instead of list
        invalid_filters = {"log_setting": 1}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

        # Test with dict instead of list
        invalid_filters = {"log_setting": {"setting": "default-logging"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

    def test_list_filters_disabled_functionality(self):
        """Test that disabled filter works correctly when valid."""
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1",
                    disabled=True,
                    folder="Shared",
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    disabled=False,
                    folder="Shared",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test filtering disabled rules
        filtered_objects = self.client.list(folder="Shared", disabled=True)
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"
        assert filtered_objects[0].disabled is True

        # Test filtering enabled rules
        filtered_objects = self.client.list(folder="Shared", disabled=False)
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule2"
        assert filtered_objects[0].disabled is False

    def test_list_filters_log_setting_functionality(self):
        """Test that log_setting filter works correctly when valid."""
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1",
                    log_setting="default-logging",
                    folder="Shared",
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    log_setting="custom-logging",
                    folder="Shared",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test filtering by log setting
        filtered_objects = self.client.list(
            folder="Shared", log_setting=["default-logging"]
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"
        assert filtered_objects[0].log_setting == "default-logging"

        # Test filtering by multiple log settings
        filtered_objects = self.client.list(
            folder="Shared", log_setting=["default-logging", "custom-logging"]
        )
        assert len(filtered_objects) == 2

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
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")

    def test_list_invalid_action_filter(self):
        """Test that list method raises InvalidObjectError when 'action' filter is not a list."""
        folder = "Shared"
        filters = {"action": "allow"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder=folder, **filters)
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_invalid_disabled_filter(self):
        """Test that list method raises InvalidObjectError when 'disabled' filter is not a bool."""
        folder = "Shared"
        filters = {"disabled": "True"}  # Should be a bool, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder=folder, **filters)
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_invalid_source_filter(self):
        """Test that list method raises InvalidObjectError when 'source' filter is not a list."""
        folder = "Shared"
        filters = {"source": "192.168.1.1"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder=folder, **filters)
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_invalid_profile_setting_filter(self):
        """Test that list method raises InvalidObjectError when 'profile_setting' filter is not a list."""
        folder = "Shared"
        filters = {"profile_setting": "default"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder=folder, **filters)
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_invalid_rulebase(self):
        """Test that list method raises InvalidObjectError when rulebase is invalid."""
        folder = "Shared"
        invalid_rulebase = "invalid"

        with pytest.raises(InvalidObjectError):
            self.client.list(folder=folder, rulebase=invalid_rulebase)


class TestSecurityRuleCreate(TestSecurityRuleBase):
    """Tests for creating Security Rule objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = SecurityRuleCreateApiFactory.build()
        mock_response = SecurityRuleResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump(
            by_alias=True
        )  # noqa
        created_object = self.client.create(test_object.model_dump(by_alias=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            json=test_object.model_dump(by_alias=True),
        )
        assert isinstance(created_object, SecurityRuleResponseModel)
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
                {
                    "name": "test",
                    "folder": "Shared",
                    "action": "allow",
                }
            )

    def test_create_with_profile_setting(self):
        """Test creating rule with profile settings."""
        test_object = SecurityRuleCreateApiFactory.build(
            profile_setting=SecurityRuleProfileSettingFactory(
                group=["best-practice", "strict"],
            )
        )

        mock_response = SecurityRuleResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump(
            by_alias=True
        )  # noqa

        created_object = self.client.create(test_object.model_dump(by_alias=True))

        assert isinstance(created_object, SecurityRuleResponseModel)
        assert len(created_object.profile_setting.group) == 2
        assert "best-practice" in created_object.profile_setting.group

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-rule",
            "folder": "Shared",
            "action": "allow",
            "from": ["any"],
            "to": ["any"],
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
                    "name": "test-rule",
                    "folder": "Shared",
                    "action": "allow",
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_create_invalid_rulebase(self):
        """Test that create method raises InvalidObjectError when rulebase is invalid."""
        data = {
            "name": "test-rule",
            "folder": "Shared",
            "source": ["any"],
            "destination": ["any"],
            "action": "allow",
        }
        invalid_rulebase = "invalid"  # Not 'pre' or 'post'

        with pytest.raises(InvalidObjectError):
            self.client.create(data, rulebase=invalid_rulebase)


class TestSecurityRuleGet(TestSecurityRuleBase):
    """Tests for retrieving a specific Security Rule object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = SecurityRuleResponseFactory.build()

        self.mock_scm.get.return_value = mock_response.model_dump(by_alias=True)  # noqa
        retrieved_object = self.client.get(str(mock_response.id))

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{mock_response.id}"
        )
        assert isinstance(retrieved_object, SecurityRuleResponseModel)
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

    def test_get_invalid_rulebase(self):
        """Test that get method raises InvalidObjectError when rulebase is invalid."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        invalid_rulebase = "invalid"

        with pytest.raises(InvalidObjectError):
            self.client.get(object_id, rulebase=invalid_rulebase)


class TestSecurityRuleUpdate(TestSecurityRuleBase):
    """Tests for updating Security Rule objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rule",
            action=SecurityRuleAction.deny,
        )
        input_data = update_data.model_dump(exclude_none=True, by_alias=True)

        # Create mock response
        mock_response = SecurityRuleResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump(by_alias=True)  # noqa

        # Perform update
        updated_object = self.client.update(input_data)

        # Assert the put method was called with correct parameters
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{update_data.id}",
            params={"position": "pre"},
            json=input_data,
        )

        assert isinstance(updated_object, SecurityRuleResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name
        assert updated_object.action == SecurityRuleAction.deny

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )
        input_data = update_data.model_dump(exclude_none=True, by_alias=True)

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
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )
        input_data = update_data.model_dump(exclude_none=True, by_alias=True)

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
                    "name": "test-rule",
                    "action": "allow",
                }
            )

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-rule",
                    "action": "allow",
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )
        input_data = update_data.model_dump(exclude_none=True, by_alias=True)

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

    def test_update_invalid_rulebase(self):
        """Test that update method raises InvalidObjectError when rulebase is invalid."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-rule",
            "action": "deny",
        }
        invalid_rulebase = "invalid"

        with pytest.raises(InvalidObjectError):
            self.client.update(data, rulebase=invalid_rulebase)


class TestSecurityRuleDelete(TestSecurityRuleBase):
    """Tests for deleting Security Rule objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{object_id}",
            params={"position": "pre"},
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

    def test_delete_invalid_rulebase(self):
        """Test that delete method raises InvalidObjectError when rulebase is invalid."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        invalid_rulebase = "invalid"

        with pytest.raises(InvalidObjectError):
            self.client.delete(object_id, rulebase=invalid_rulebase)


class TestSecurityRuleFetch(TestSecurityRuleBase):
    """Tests for fetching Security Rule objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = SecurityRuleResponseFactory.build()
        mock_response_data = mock_response_model.model_dump(by_alias=True)

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
                "position": "pre",
            },
        )

        assert isinstance(fetched_object, dict)
        assert fetched_object["id"] == mock_response_model.id
        assert fetched_object["name"] == mock_response_model.name
        assert fetched_object["action"] == mock_response_model.action

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
            self.client.fetch(name="test-rule")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-rule",
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
            self.client.fetch(name="test-rule", folder="Shared")

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
            "name": "test-rule",
            "folder": "Shared",
            "action": "allow",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-rule", folder="Shared")

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

    def test_fetch_invalid_rulebase(self):
        """Test that fetch method raises InvalidObjectError when rulebase is invalid."""
        name = "test-rule"
        folder = "Shared"
        invalid_rulebase = "invalid"

        with pytest.raises(InvalidObjectError):
            self.client.fetch(name, folder=folder, rulebase=invalid_rulebase)


class TestSecurityRuleMove(TestSecurityRuleBase):
    """Tests for moving Security Rule objects."""

    def test_move_valid(self):
        """Test moving a rule successfully to the top."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)  # noqa

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{source_rule}:move",
            json=move_data,
        )

    def test_move_before_rule(self):
        """Test moving a rule before another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_data = SecurityRuleMoveApiFactory.before_rule(
            dest_rule=dest_rule_id,
            rulebase=SecurityRuleRulebase.PRE,
        ).model_dump(exclude_none=True)

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)  # noqa

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{source_rule}:move",
            json=move_data,
        )

    def test_move_after_rule(self):
        """Test moving a rule after another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_data = SecurityRuleMoveApiFactory.after_rule(
            dest_rule=dest_rule_id,
            rulebase=SecurityRuleRulebase.PRE,
        ).model_dump(exclude_none=True)

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)  # noqa

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{source_rule}:move",
            json=move_data,
        )

    def test_move_invalid_destination_error(self):
        """Test error handling when move destination is invalid."""
        source_rule = str(uuid.uuid4())
        move_data = {
            "destination": "invalid",
            "destination_rule": str(uuid.uuid4()),
            "rulebase": "pre",
        }

        with pytest.raises(ValidationError) as exc_info:
            self.client.move(source_rule, move_data)  # noqa

        assert (
            "1 validation error for SecurityRuleMoveModel\ndestination\n  Input should be 'top', 'bottom', 'before' or 'after'"
            in str(exc_info.value)
        )

    def test_move_missing_destination_rule_error(self):
        """Test error handling when destination_rule is missing for before/after moves."""
        source_rule = str(uuid.uuid4())
        move_data = {
            "destination": "before",
            "rulebase": "pre",
        }

        with pytest.raises(ValidationError) as exc_info:
            self.client.move(source_rule, move_data)  # noqa

        assert "destination_rule is required when destination is 'before'" in str(
            exc_info.value
        )

    def test_move_rule_not_found_error(self):
        """Test error handling when source or destination rule is not found."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Rule not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.move(rule_id, move_data)  # noqa

        assert (
            "{'errorType': 'Object Not Present'} - HTTP error: 404 - API error: API_I00013"
            in str(exc_info.value)
        )

    def test_move_http_error_no_response_content(self):
        """Test move method when HTTP error has no response content."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.move(rule_id, move_data)  # noqa

    def test_move_generic_exception_handling(self):
        """Test handling of a generic exception during move."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.move(rule_id, move_data)  # noqa

        assert str(exc_info.value) == "Generic error"

    def test_move_server_error(self):
        """Test handling of server errors during move."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.move(rule_id, move_data)  # noqa

        error_message = str(exc_info.value)
        assert "{'errorType': 'Internal Error'}" in error_message
        assert "HTTP error: 500" in error_message
        assert "API error: E003" in error_message


class TestSecurityRuleModelMisc(TestSecurityRuleBase):

    def test_security_rule_profile_setting_group_unique(self):
        """Test that duplicate items in 'group' raise a ValueError."""
        with pytest.raises(ValueError, match="List items in 'group' must be unique"):
            SecurityRuleProfileSetting(group=["group1", "group1"])

    def test_ensure_list_of_strings_single_string(self):
        """Test that a single string is converted to a list containing that string."""
        model = SecurityRuleCreateModel(
            name="test-rule", source="192.168.1.1", folder="Shared"  # noqa
        )
        assert model.source == ["192.168.1.1"]

    def test_ensure_list_of_strings_invalid_type(self):
        """Test that a non-string, non-list value raises a ValueError."""
        with pytest.raises(ValueError, match="Value must be a list of strings"):
            SecurityRuleCreateModel(
                name="test-rule", source=123, folder="Shared"
            )  # noqa

    def test_ensure_list_of_strings_non_string_items(self):
        """Test that a list containing non-string items raises a ValueError."""
        with pytest.raises(ValueError, match="All items must be strings"):
            SecurityRuleCreateModel(
                name="test-rule", source=["192.168.1.1", 123], folder="Shared"
            )

    def test_ensure_unique_items_duplicates(self):
        """Test that duplicate items in lists raise a ValueError."""
        with pytest.raises(ValueError, match="List items must be unique"):
            SecurityRuleCreateModel(
                name="test-rule", source=["192.168.1.1", "192.168.1.1"], folder="Shared"
            )

    def test_security_rule_create_no_container(self):
        """Test that not providing any container raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
        ):
            SecurityRuleCreateModel(name="test-rule")

    def test_security_rule_create_multiple_containers(self):
        """Test that providing multiple containers raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
        ):
            SecurityRuleCreateModel(
                name="test-rule", folder="Shared", snippet="MySnippet"
            )

    def test_move_model_unexpected_destination_rule_top(self):
        """Test that providing destination_rule with 'top' raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'top'",
        ):
            SecurityRuleMoveModel(
                destination=SecurityRuleMoveDestination.TOP,
                rulebase=SecurityRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )

    def test_move_model_unexpected_destination_rule_bottom(self):
        """Test that providing destination_rule with 'bottom' raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'bottom'",
        ):
            SecurityRuleMoveModel(
                destination=SecurityRuleMoveDestination.BOTTOM,
                rulebase=SecurityRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )


# -------------------- End of Test Classes --------------------
