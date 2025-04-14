# tests/scm/config/security/test_security_rules.py

# Standard library imports
from unittest.mock import MagicMock
import uuid

from pydantic import ValidationError

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.security import SecurityRule
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.security.security_rules import (
    SecurityRuleAction,
    SecurityRuleCreateModel,
    SecurityRuleMoveDestination,
    SecurityRuleMoveModel,
    SecurityRuleProfileSetting,
    SecurityRuleResponseModel,
    SecurityRuleRulebase,
)
from tests.test_factories.security import (
    SecurityRuleCreateApiFactory,
    SecurityRuleMoveApiFactory,
    SecurityRuleProfileSettingFactory,
    SecurityRuleResponseFactory,
    SecurityRuleUpdateApiFactory,
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
        self.client = SecurityRule(self.mock_scm, max_limit=5000)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestSecurityRuleMaxLimit(TestSecurityRuleBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = SecurityRule(self.mock_scm)  # noqa
        assert client.max_limit == SecurityRule.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = SecurityRule(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = SecurityRule(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            SecurityRule(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            SecurityRule(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            SecurityRule(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestSecurityRuleList(TestSecurityRuleBase):
    """Tests for listing Security Rule objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    action=SecurityRuleAction.allow,
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    action=SecurityRuleAction.deny,
                ).model_dump(by_alias=True),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={
                "folder": "Texas",
                "limit": 5000,
                "offset": 0,
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
        """Test that valid filters are properly applied."""
        # Create mock rules with different attributes
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    action=SecurityRuleAction.allow,
                    source=["10.0.0.0/24"],
                    destination=["any"],
                    from_=["trust"],
                    to_=["untrust"],
                    tag=["tag1"],
                    profile_setting=SecurityRuleProfileSettingFactory(group=["best-practice"]),
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
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

        filtered_objects = self.client.list(folder="Texas", **filters)

        # Verify the filtering
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"
        assert filtered_objects[0].action == SecurityRuleAction.allow

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                SecurityRuleResponseFactory(
                    name="rule1", folder="Texas", action=SecurityRuleAction.allow
                ).model_dump(by_alias=True)
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Texas",
            action=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            category=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            service=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            disabled=False,
        )
        assert len(filtered_objects) == 1

        filtered_objects = self.client.list(
            folder="Texas",
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
            folder="Texas",
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
                    folder="Texas",
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    disabled=False,
                    folder="Texas",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test filtering disabled rules
        filtered_objects = self.client.list(folder="Texas", disabled=True)
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"
        assert filtered_objects[0].disabled is True

        # Test filtering enabled rules
        filtered_objects = self.client.list(folder="Texas", disabled=False)
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
                    folder="Texas",
                ).model_dump(by_alias=True),
                SecurityRuleResponseFactory(
                    name="rule2",
                    log_setting="custom-logging",
                    folder="Texas",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test filtering by log setting
        filtered_objects = self.client.list(folder="Texas", log_setting=["default-logging"])
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"
        assert filtered_objects[0].log_setting == "default-logging"

        # Test filtering by multiple log settings
        filtered_objects = self.client.list(
            folder="Texas", log_setting=["default-logging", "custom-logging"]
        )
        assert len(filtered_objects) == 2

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

    def test_list_invalid_action_filter(self):
        """Test that list method raises InvalidObjectError when 'action' filter is not a list."""
        folder = "Texas"
        filters = {"action": "allow"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder=folder, **filters)
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_invalid_disabled_filter(self):
        """Test that list method raises InvalidObjectError when 'disabled' filter is not a bool."""
        folder = "Texas"
        filters = {"disabled": "True"}  # Should be a bool, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder=folder, **filters)
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_invalid_source_filter(self):
        """Test that list method raises InvalidObjectError when 'source' filter is not a list."""
        folder = "Texas"
        filters = {"source": "192.168.1.1"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder=folder, **filters)
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_invalid_profile_setting_filter(self):
        """Test that list method raises InvalidObjectError when 'profile_setting' filter is not a list."""
        folder = "Texas"
        filters = {"profile_setting": "default"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder=folder, **filters)
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_invalid_rulebase(self):
        """Test that list method raises InvalidObjectError when rulebase is invalid."""
        folder = "Texas"
        invalid_rulebase = "invalid"

        with pytest.raises(InvalidObjectError):
            self.client.list(folder=folder, rulebase=invalid_rulebase)

    @pytest.mark.parametrize(
        "rulebase",
        [
            "pre",
            "post",
        ],
    )
    def test_list_rulebase(self, rulebase):
        """Test that list method is called with correct rulebase value."""
        folder = "Texas"

        mock_response = {
            "data": [
                SecurityRuleResponseFactory().model_dump(by_alias=True),
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
            "rulebase": rulebase,
        }

        self.mock_scm.get.return_value = mock_response
        self.client.list(folder=folder, rulebase=rulebase)

        self.mock_scm.get.assert_called_once_with(
            "/config/security/v1/security-rules",
            params={
                "folder": folder,
                "limit": 5000,
                "offset": 0,
                "position": rulebase,
            },
        )

    # -------------------- New Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """
        Test that exact_match=True returns only objects that match the container exactly.
        """
        mock_response = {
            "data": [
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345678",
                    name="addr_in_texas",
                    folder="Texas",
                ).model_dump(),
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345671",
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
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345678",
                    name="addr_in_texas",
                    folder="Texas",
                ).model_dump(),
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345671",
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
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345678",
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(),
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345671",
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
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345678",
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                    device="DeviceA",
                ).model_dump(),
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345671",
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
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345678",
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(),
                SecurityRuleResponseModel(
                    id="12345678-1234-5678-1234-567812345671",
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
        """
        Test that the list method correctly aggregates data from multiple pages.
        Using a custom client with max_limit=2500 to test pagination.
        """
        client = SecurityRule(self.mock_scm, max_limit=2500)  # noqa

        # Create test data for three pages
        first_page = [
            SecurityRuleResponseFactory(
                name=f"allow-rule-page1-{i}",
                folder="Texas",
                action=SecurityRuleAction.allow,
                source=["10.0.0.0/24"],
                destination=["any"],
                from_=["trust"],
                to_=["untrust"],
            ).model_dump(by_alias=True)
            for i in range(2500)
        ]

        second_page = [
            SecurityRuleResponseFactory(
                name=f"deny-rule-page2-{i}",
                folder="Texas",
                action=SecurityRuleAction.deny,
                source=["any"],
                destination=["10.1.0.0/24"],
                from_=["untrust"],
                to_=["trust"],
            ).model_dump(by_alias=True)
            for i in range(2500)
        ]

        third_page = [
            SecurityRuleResponseFactory(
                name=f"drop-rule-page3-{i}",
                folder="Texas",
                action=SecurityRuleAction.drop,
                source=["192.168.1.0/24"],
                destination=["any"],
                from_=["dmz"],
                to_=["trust"],
            ).model_dump(by_alias=True)
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
        assert isinstance(results[0], SecurityRuleResponseModel)
        assert all(isinstance(obj, SecurityRuleResponseModel) for obj in results)

        # Verify API calls
        assert self.mock_scm.get.call_count == 4  # noqa # Three pages + one final check

        # Verify API calls were made with correct offset values
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/security-rules",
            params={"folder": "Texas", "limit": 2500, "offset": 0, "position": "pre"},
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/security-rules",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 2500,
                "position": "pre",
            },
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/security-rules",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 5000,
                "position": "pre",
            },
        )

        # Verify content ordering and rule-specific attributes
        assert results[0].name == "allow-rule-page1-0"
        assert results[0].action == SecurityRuleAction.allow
        assert results[0].source == ["10.0.0.0/24"]
        assert results[0].from_ == ["trust"]

        assert results[2500].name == "deny-rule-page2-0"
        assert results[2500].action == SecurityRuleAction.deny
        assert results[2500].destination == ["10.1.0.0/24"]
        assert results[2500].to_ == ["trust"]

        assert results[5000].name == "drop-rule-page3-0"
        assert results[5000].action == SecurityRuleAction.drop
        assert results[5000].source == ["192.168.1.0/24"]
        assert results[5000].from_ == ["dmz"]


class TestSecurityRuleCreate(TestSecurityRuleBase):
    """Tests for creating Security Rule objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = SecurityRuleCreateApiFactory.build()
        mock_response = SecurityRuleResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump(  # noqa
            by_alias=True
        )  # noqa
        created_object = self.client.create(test_object.model_dump(by_alias=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={"position": "pre"},
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
                    "folder": "Texas",
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
        self.mock_scm.post.return_value = mock_response.model_dump(  # noqa
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
            "folder": "Texas",
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

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Create failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(
                {
                    "name": "test-rule",
                    "folder": "Texas",
                    "action": "allow",
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_create_invalid_rulebase(self):
        """Test that create method raises InvalidObjectError when rulebase is invalid."""
        data = {
            "name": "test-rule",
            "folder": "Texas",
            "source": ["any"],
            "destination": ["any"],
            "action": "allow",
        }
        invalid_rulebase = "invalid"  # Not 'pre' or 'post'

        with pytest.raises(InvalidObjectError):
            self.client.create(data, rulebase=invalid_rulebase)

    @pytest.mark.parametrize(
        "rulebase",
        [
            "pre",
            "post",
        ],
    )
    def test_create_rulebase(self, rulebase):
        """Test that create method is called with correct rulebase value."""
        test_object = SecurityRuleCreateApiFactory.build()
        mock_response = SecurityRuleResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump(by_alias=True)
        self.client.create(test_object.model_dump(by_alias=True), rulebase=rulebase)

        self.mock_scm.post.assert_called_once_with(
            "/config/security/v1/security-rules",
            params={"position": rulebase},
            json=test_object.model_dump(by_alias=True),
        )


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
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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

        # Create mock response
        mock_response = SecurityRuleResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump(by_alias=True)  # noqa

        # Perform update with Pydantic model directly
        updated_object = self.client.update(update_data)

        # Verify call was made once
        self.mock_scm.put.assert_called_once()  # noqa

        # Get the actual call arguments
        call_args = self.mock_scm.put.call_args  # noqa

        # Check endpoint
        assert call_args[0][0] == f"/config/security/v1/security-rules/{update_data.id}"

        # Check important payload fields
        payload = call_args[1]["json"]
        assert payload["name"] == "updated-rule"

        assert isinstance(updated_object, SecurityRuleResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name
        assert updated_object.action == SecurityRuleAction.deny

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        # Create update data using factory
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

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

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

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
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        # Create test data using factory
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
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
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = SecurityRuleUpdateApiFactory.with_action_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

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

    def test_update_invalid_rulebase(self):
        """Test that update method raises InvalidObjectError when rulebase is invalid."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-rule",
            "action": "deny",
        }
        invalid_rulebase = "invalid"

        with pytest.raises(InvalidObjectError):
            self.client.update(
                data,  # noqa
                rulebase=invalid_rulebase,
            )


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

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Reference not zero"
        assert error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"

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
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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

        # Set the mock to return the response data directly
        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
                "position": "pre",  # Include the default position parameter
            },
        )

        # Validate the returned object is a Pydantic model
        assert isinstance(fetched_object, SecurityRuleResponseModel)

        # Validate the object attributes match the mock response
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.action == mock_response_model.action
        assert fetched_object.folder == mock_response_model.folder

    def test_fetch_valid_object_with_position(self):
        """Test retrieving an object by its name using the `fetch` method with explicit position."""
        mock_response_model = SecurityRuleResponseFactory.build()
        mock_response_data = mock_response_model.model_dump(by_alias=True)

        # Set the mock to return the response data directly
        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
            rulebase="post",  # Explicitly set position
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
                "position": "post",
            },
        )

        # Validate the returned object is a Pydantic model
        assert isinstance(fetched_object, SecurityRuleResponseModel)

        # Validate the object attributes match the mock response
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.action == mock_response_model.action
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
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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
            self.client.fetch(name="test-rule")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-rule",
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
            self.client.fetch(name="test-rule", folder="Texas")

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
            "name": "test-rule",
            "folder": "Texas",
            "action": "allow",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-rule", folder="Texas")

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

    def test_fetch_invalid_rulebase(self):
        """Test that fetch method raises InvalidObjectError when rulebase is invalid."""
        name = "test-rule"
        folder = "Texas"
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
        move_config = SecurityRuleMoveApiFactory.before_rule(
            dest_rule=dest_rule_id,
            rulebase=SecurityRuleRulebase.PRE,
        )

        # Get the data as a dictionary
        move_data = move_config.model_dump(exclude_none=True)

        # Expected data - with destination_rule as string
        expected_data = move_data.copy()
        if "destination_rule" in expected_data:
            expected_data["destination_rule"] = str(expected_data["destination_rule"])

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)  # noqa

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{source_rule}:move",
            json=expected_data,
        )

    def test_move_after_rule(self):
        """Test moving a rule after another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_config = SecurityRuleMoveApiFactory.after_rule(
            dest_rule=dest_rule_id,
            rulebase=SecurityRuleRulebase.PRE,
        )

        # Get the data as a dictionary
        move_data = move_config.model_dump(exclude_none=True)

        # Expected data - with destination_rule as string
        expected_data = move_data.copy()
        if "destination_rule" in expected_data:
            expected_data["destination_rule"] = str(expected_data["destination_rule"])

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)  # noqa

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{source_rule}:move",
            json=expected_data,
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

        assert "destination_rule is required when destination is 'before'" in str(exc_info.value)

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

        with pytest.raises(HTTPError) as exc_info:
            self.client.move(rule_id, move_data)  # noqa
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Rule not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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

        with pytest.raises(HTTPError) as exc_info:
            self.client.move(rule_id, move_data)  # noqa
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestSecurityRuleModelMisc(TestSecurityRuleBase):
    def test_security_rule_profile_setting_group_unique(self):
        """Test that duplicate items in 'group' raise a ValueError."""
        with pytest.raises(ValueError, match="List items in 'group' must be unique"):
            SecurityRuleProfileSetting(group=["group1", "group1"])

    def test_ensure_list_of_strings_single_string(self):
        """Test that a single string is converted to a list containing that string."""
        model = SecurityRuleCreateModel(
            name="test-rule",
            source="192.168.1.1",
            folder="Texas",  # noqa
        )
        assert model.source == ["192.168.1.1"]

    def test_ensure_list_of_strings_invalid_type(self):
        """Test that a non-string, non-list value raises a ValueError."""
        with pytest.raises(ValueError, match="Value must be a list of strings"):
            SecurityRuleCreateModel(
                name="test-rule",
                source=123,  # noqa
                folder="Texas",
            )  # noqa

    def test_ensure_list_of_strings_non_string_items(self):
        """Test that a list containing non-string items raises a ValueError."""
        with pytest.raises(ValueError, match="All items must be strings"):
            SecurityRuleCreateModel(name="test-rule", source=["192.168.1.1", 123], folder="Texas")

    def test_ensure_unique_items_duplicates(self):
        """Test that duplicate items in lists raise a ValueError."""
        with pytest.raises(ValueError, match="List items must be unique"):
            SecurityRuleCreateModel(
                name="test-rule", source=["192.168.1.1", "192.168.1.1"], folder="Texas"
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
            SecurityRuleCreateModel(name="test-rule", folder="Texas", snippet="MySnippet")

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
