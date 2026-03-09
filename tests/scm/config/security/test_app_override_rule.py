# tests/scm/config/security/test_app_override_rule.py

"""Tests for app override rule service."""

from unittest.mock import MagicMock

# Standard library imports
import uuid

from pydantic import ValidationError

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.security.app_override_rule import AppOverrideRule
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.security.app_override_rules import (
    AppOverrideRuleCreateModel,
    AppOverrideRuleMoveDestination,
    AppOverrideRuleMoveModel,
    AppOverrideRuleResponseModel,
    AppOverrideRuleRulebase,
)
from tests.factories.security.app_override_rule import (
    AppOverrideRuleCreateApiFactory,
    AppOverrideRuleMoveApiFactory,
    AppOverrideRuleResponseFactory,
    AppOverrideRuleUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestAppOverrideRuleBase:
    """Base class for App Override Rule tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AppOverrideRule(self.mock_scm)


# -------------------- Test Max Limit --------------------


class TestAppOverrideRuleMaxLimit(TestAppOverrideRuleBase):
    """Tests for max_limit validation in AppOverrideRule."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = AppOverrideRule(self.mock_scm)
        assert client.max_limit == AppOverrideRule.DEFAULT_MAX_LIMIT

    def test_custom_max_limit(self):
        """Test that a custom max_limit is set correctly."""
        client = AppOverrideRule(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test setting max_limit using the setter."""
        client = AppOverrideRule(self.mock_scm)
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_max_limit_too_low(self):
        """Test validation when max_limit is below 1."""
        with pytest.raises(InvalidObjectError):
            AppOverrideRule(self.mock_scm, max_limit=0)

    def test_max_limit_too_high(self):
        """Test validation when max_limit exceeds absolute maximum."""
        with pytest.raises(InvalidObjectError):
            AppOverrideRule(self.mock_scm, max_limit=10000)

    def test_max_limit_invalid_type(self):
        """Test validation when max_limit is not an integer."""
        with pytest.raises(InvalidObjectError):
            AppOverrideRule(self.mock_scm, max_limit="invalid")


# -------------------- Test List --------------------


class TestAppOverrideRuleList(TestAppOverrideRuleBase):
    """Tests for listing App Override Rule objects."""

    def test_list_valid(self):
        """Test listing all objects with valid response."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                ).model_dump(by_alias=True),
            ],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        existing_objects = self.client.list(folder="Texas")
        assert len(existing_objects) == 2
        assert isinstance(existing_objects[0], AppOverrideRuleResponseModel)
        assert existing_objects[0].name == "rule1"

    def test_list_folder_empty_error(self):
        """Test that empty folder raises MissingQueryParameterError."""
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

    def test_list_no_container_error(self):
        """Test that no container raises InvalidObjectError."""
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_multiple_containers_error(self):
        """Test that multiple containers raise InvalidObjectError."""
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", snippet="TestSnippet")

    def test_list_filters_application_functionality(self):
        """Test that application filter works correctly when valid."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    application="web-browsing",
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    application="ssl",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered_objects = self.client.list(folder="Texas", application=["web-browsing"])
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"
        assert filtered_objects[0].application == "web-browsing"

    def test_list_filters_disabled_functionality(self):
        """Test that disabled filter works correctly when valid."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    disabled=True,
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    disabled=False,
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered_objects = self.client.list(folder="Texas", disabled=False)
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule2"
        assert filtered_objects[0].disabled is False

    def test_list_filters_combined(self):
        """Test combining multiple filters."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    application="web-browsing",
                    source=["10.0.0.0/24"],
                    tag=["tag1"],
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    application="ssl",
                    source=["192.168.0.0/16"],
                    tag=["tag2"],
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered_objects = self.client.list(
            folder="Texas",
            application=["web-browsing"],
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

    def test_list_invalid_application_filter(self):
        """Test that _apply_filters raises InvalidObjectError when 'application' filter is not a list."""
        mock_rules = []
        invalid_filters = {"application": "web-browsing"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)
        assert isinstance(exc_info.value, InvalidObjectError)

    def test_list_invalid_disabled_filter(self):
        """Test that _apply_filters raises InvalidObjectError when 'disabled' filter is not a bool."""
        mock_rules = []
        invalid_filters = {"disabled": "True"}  # Should be a bool, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)
        assert isinstance(exc_info.value, InvalidObjectError)

    def test_list_invalid_source_filter(self):
        """Test that _apply_filters raises InvalidObjectError when 'source' filter is not a list."""
        mock_rules = []
        invalid_filters = {"source": "192.168.1.1"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)
        assert isinstance(exc_info.value, InvalidObjectError)

    def test_list_invalid_protocol_filter(self):
        """Test that _apply_filters raises InvalidObjectError when 'protocol' filter is not a list."""
        mock_rules = []
        invalid_filters = {"protocol": "tcp"}  # Should be a list, not a string

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)
        assert isinstance(exc_info.value, InvalidObjectError)

    def test_list_filters_protocol_functionality(self):
        """Test that protocol filter works correctly when valid."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    application="web-browsing",
                    protocol="tcp",
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    application="dns",
                    protocol="udp",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered_objects = self.client.list(folder="Texas", protocol=["tcp"])
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "rule1"

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
                AppOverrideRuleResponseFactory().model_dump(by_alias=True),
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
            "rulebase": rulebase,
        }

        self.mock_scm.get.return_value = mock_response
        self.client.list(folder=folder, rulebase=rulebase)

        self.mock_scm.get.assert_called_once_with(
            "/config/security/v1/app-override-rules",
            params={
                "folder": folder,
                "limit": 2500,
                "offset": 0,
                "position": rulebase,
            },
        )

    # -------------------- Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """Test that exact_match=True returns only objects that match the container exactly."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule_in_texas",
                    folder="Texas",
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule_in_all",
                    folder="All",
                ).model_dump(by_alias=True),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"
        assert filtered[0].name == "rule_in_texas"

    def test_list_exclude_folders(self):
        """Test that exclude_folders removes objects from those folders."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule_in_texas",
                    folder="Texas",
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule_in_all",
                    folder="All",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes objects with those snippets."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule_with_special_snippet",
                    folder="Texas",
                    snippet="special",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes objects with those devices."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule_with_device_a",
                    folder="Texas",
                    snippet="default",
                    device="DeviceA",
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule_with_device_b",
                    folder="Texas",
                    snippet="special",
                    device="DeviceB",
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(a.device != "DeviceA" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """Test combining exact_match with exclusions."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule_with_special_snippet",
                    folder="Texas",
                    snippet="special",
                ).model_dump(by_alias=True),
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
        assert len(filtered) == 1
        obj = filtered[0]
        assert obj.folder == "Texas"
        assert obj.snippet != "default"
        assert obj.device != "DeviceA"

    def test_list_pagination_multiple_pages(self):
        """Test that the list method correctly aggregates data from multiple pages."""
        client = AppOverrideRule(self.mock_scm, max_limit=2500)  # noqa

        first_page = [
            AppOverrideRuleResponseFactory(
                name=f"rule-page1-{i}",
                folder="Texas",
                application="web-browsing",
                source=["10.0.0.0/24"],
                destination=["any"],
                from_=["trust"],
                to_=["untrust"],
            ).model_dump(by_alias=True)
            for i in range(2500)
        ]

        second_page = [
            AppOverrideRuleResponseFactory(
                name=f"rule-page2-{i}",
                folder="Texas",
                application="ssl",
                source=["any"],
                destination=["10.1.0.0/24"],
                from_=["untrust"],
                to_=["trust"],
            ).model_dump(by_alias=True)
            for i in range(2500)
        ]

        third_page = [
            AppOverrideRuleResponseFactory(
                name=f"rule-page3-{i}",
                folder="Texas",
                application="web-browsing",
                source=["192.168.1.0/24"],
                destination=["any"],
                from_=["dmz"],
                to_=["trust"],
            ).model_dump(by_alias=True)
            for i in range(2500)
        ]

        mock_responses = [
            {"data": first_page},
            {"data": second_page},
            {"data": third_page},
            {"data": []},
        ]
        self.mock_scm.get.side_effect = mock_responses  # noqa

        results = client.list(folder="Texas")

        assert len(results) == 7500
        assert isinstance(results[0], AppOverrideRuleResponseModel)
        assert all(isinstance(obj, AppOverrideRuleResponseModel) for obj in results)

        assert self.mock_scm.get.call_count == 4  # noqa

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/app-override-rules",
            params={"folder": "Texas", "limit": 2500, "offset": 0, "position": "pre"},
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/app-override-rules",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 2500,
                "position": "pre",
            },
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/app-override-rules",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 5000,
                "position": "pre",
            },
        )

        assert results[0].name == "rule-page1-0"
        assert results[0].application == "web-browsing"
        assert results[0].source == ["10.0.0.0/24"]
        assert results[0].from_ == ["trust"]

        assert results[2500].name == "rule-page2-0"
        assert results[2500].application == "ssl"
        assert results[2500].destination == ["10.1.0.0/24"]
        assert results[2500].to_ == ["trust"]

        assert results[5000].name == "rule-page3-0"
        assert results[5000].application == "web-browsing"
        assert results[5000].source == ["192.168.1.0/24"]
        assert results[5000].from_ == ["dmz"]

    # -------------------- Filter-specific tests --------------------

    def test_list_filter_by_tag(self):
        """Test filtering by tag."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    tag=["important", "production"],
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    tag=["test"],
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", tag=["important"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_from(self):
        """Test filtering by from_ zones."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    from_=["trust"],
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    from_=["untrust"],
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", from_=["trust"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_to(self):
        """Test filtering by to_ zones."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    to_=["untrust"],
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    to_=["trust"],
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", to_=["untrust"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_source(self):
        """Test filtering by source."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    source=["10.0.0.0/24"],
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    source=["192.168.0.0/16"],
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", source=["10.0.0.0/24"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_destination(self):
        """Test filtering by destination."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(
                    name="rule1",
                    folder="Texas",
                    destination=["10.0.0.0/24"],
                ).model_dump(by_alias=True),
                AppOverrideRuleResponseFactory(
                    name="rule2",
                    folder="Texas",
                    destination=["192.168.1.0/24"],
                ).model_dump(by_alias=True),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", destination=["10.0.0.0/24"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_invalid_tag_filter(self):
        """Test that list method raises InvalidObjectError when 'tag' filter is not a list."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(name="rule1", folder="Texas").model_dump(
                    by_alias=True
                )
            ]
        }
        self.mock_scm.get.return_value = mock_response

        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", tag="my-tag")

    def test_list_invalid_destination_filter(self):
        """Test that list method raises InvalidObjectError when 'destination' filter is not a list."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(name="rule1", folder="Texas").model_dump(
                    by_alias=True
                )
            ]
        }
        self.mock_scm.get.return_value = mock_response

        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", destination="10.0.0.0/24")

    def test_list_invalid_to_filter(self):
        """Test that list method raises InvalidObjectError when 'to_' filter is not a list."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(name="rule1", folder="Texas").model_dump(
                    by_alias=True
                )
            ]
        }
        self.mock_scm.get.return_value = mock_response

        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", to_="untrust")

    def test_list_invalid_from_filter(self):
        """Test that list method raises InvalidObjectError when 'from_' filter is not a list."""
        mock_response = {
            "data": [
                AppOverrideRuleResponseFactory(name="rule1", folder="Texas").model_dump(
                    by_alias=True
                )
            ]
        }
        self.mock_scm.get.return_value = mock_response

        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", from_="trust")


# -------------------- Test Create --------------------


class TestAppOverrideRuleCreate(TestAppOverrideRuleBase):
    """Tests for creating App Override Rule objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = AppOverrideRuleCreateApiFactory.build()
        mock_response = AppOverrideRuleResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump(  # noqa
            by_alias=True
        )
        created_object = self.client.create(test_object.model_dump(by_alias=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/app-override-rules",
            params={"position": "pre"},
            json=test_object.model_dump(by_alias=True),
        )
        assert isinstance(created_object, AppOverrideRuleResponseModel)
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
                    "application": "web-browsing",
                    "port": "80",
                    "protocol": "tcp",
                }
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-rule",
            "folder": "Texas",
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
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
                    "application": "web-browsing",
                    "port": "80",
                    "protocol": "tcp",
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_create_invalid_rulebase(self):
        """Test that create method raises InvalidObjectError when rulebase is invalid."""
        data = {
            "name": "test-rule",
            "folder": "Texas",
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
            "source": ["any"],
            "destination": ["any"],
        }
        invalid_rulebase = "invalid"

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
        test_object = AppOverrideRuleCreateApiFactory.build()
        mock_response = AppOverrideRuleResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump(by_alias=True)
        self.client.create(test_object.model_dump(by_alias=True), rulebase=rulebase)

        self.mock_scm.post.assert_called_once_with(
            "/config/security/v1/app-override-rules",
            params={"position": rulebase},
            json=test_object.model_dump(by_alias=True),
        )


# -------------------- Test Get --------------------


class TestAppOverrideRuleGet(TestAppOverrideRuleBase):
    """Tests for retrieving a specific App Override Rule object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = AppOverrideRuleResponseFactory.build()

        self.mock_scm.get.return_value = mock_response.model_dump(by_alias=True)  # noqa
        retrieved_object = self.client.get(str(mock_response.id))

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/app-override-rules/{mock_response.id}"
        )
        assert isinstance(retrieved_object, AppOverrideRuleResponseModel)
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


# -------------------- Test Update --------------------


class TestAppOverrideRuleUpdate(TestAppOverrideRuleBase):
    """Tests for updating App Override Rule objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = AppOverrideRuleUpdateApiFactory.with_application_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rule",
            application="ssl",
        )

        mock_response = AppOverrideRuleResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump(by_alias=True)  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa

        call_args = self.mock_scm.put.call_args  # noqa

        assert call_args[0][0] == f"/config/security/v1/app-override-rules/{update_data.id}"

        payload = call_args[1]["json"]
        assert payload["name"] == "updated-rule"

        assert isinstance(updated_object, AppOverrideRuleResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = AppOverrideRuleUpdateApiFactory.with_application_update(
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
        update_data = AppOverrideRuleUpdateApiFactory.with_application_update(
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
        update_data = AppOverrideRuleUpdateApiFactory.with_application_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        update_data = AppOverrideRuleUpdateApiFactory.with_application_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = AppOverrideRuleUpdateApiFactory.with_application_update(
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
        update_data = AppOverrideRuleUpdateApiFactory.with_application_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rule",
            application="ssl",
        )
        invalid_rulebase = "invalid"

        with pytest.raises(InvalidObjectError):
            self.client.update(
                update_data,
                rulebase=invalid_rulebase,
            )

    @pytest.mark.parametrize(
        "rulebase",
        [
            "pre",
            "post",
        ],
    )
    def test_update_rulebase(self, rulebase):
        """Test that update method is called with correct rulebase value."""
        update_data = AppOverrideRuleUpdateApiFactory.with_application_update(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rule",
        )

        mock_response = AppOverrideRuleResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump(by_alias=True)

        self.client.update(update_data, rulebase=rulebase)

        call_args = self.mock_scm.put.call_args
        assert call_args[1]["params"] == {"position": rulebase}


# -------------------- Test Delete --------------------


class TestAppOverrideRuleDelete(TestAppOverrideRuleBase):
    """Tests for deleting App Override Rule objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/app-override-rules/{object_id}",
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

    @pytest.mark.parametrize(
        "rulebase",
        [
            "pre",
            "post",
        ],
    )
    def test_delete_rulebase(self, rulebase):
        """Test that delete method is called with correct rulebase value."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None
        self.client.delete(object_id, rulebase=rulebase)

        self.mock_scm.delete.assert_called_once_with(
            f"/config/security/v1/app-override-rules/{object_id}",
            params={"position": rulebase},
        )


# -------------------- Test Fetch --------------------


class TestAppOverrideRuleFetch(TestAppOverrideRuleBase):
    """Tests for fetching App Override Rule objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = AppOverrideRuleResponseFactory.build()
        mock_response_data = mock_response_model.model_dump(by_alias=True)

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/app-override-rules",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
                "position": "pre",
            },
        )

        assert isinstance(fetched_object, AppOverrideRuleResponseModel)

        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.application == mock_response_model.application
        assert fetched_object.folder == mock_response_model.folder

    def test_fetch_valid_object_with_position(self):
        """Test retrieving an object by its name with explicit position."""
        mock_response_model = AppOverrideRuleResponseFactory.build()
        mock_response_data = mock_response_model.model_dump(by_alias=True)

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
            rulebase="post",
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/app-override-rules",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
                "position": "post",
            },
        )

        assert isinstance(fetched_object, AppOverrideRuleResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name

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
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
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


# -------------------- Test Move --------------------


class TestAppOverrideRuleMove(TestAppOverrideRuleBase):
    """Tests for moving App Override Rule objects."""

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
            f"/config/security/v1/app-override-rules/{source_rule}:move",
            json=move_data,
        )

    def test_move_before_rule(self):
        """Test moving a rule before another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_config = AppOverrideRuleMoveApiFactory.before_rule(
            dest_rule=dest_rule_id,
            rulebase=AppOverrideRuleRulebase.PRE,
        )

        move_data = move_config.model_dump(exclude_none=True)

        expected_data = move_data.copy()
        if "destination_rule" in expected_data:
            expected_data["destination_rule"] = str(expected_data["destination_rule"])

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)  # noqa

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/app-override-rules/{source_rule}:move",
            json=expected_data,
        )

    def test_move_after_rule(self):
        """Test moving a rule after another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_config = AppOverrideRuleMoveApiFactory.after_rule(
            dest_rule=dest_rule_id,
            rulebase=AppOverrideRuleRulebase.PRE,
        )

        move_data = move_config.model_dump(exclude_none=True)

        expected_data = move_data.copy()
        if "destination_rule" in expected_data:
            expected_data["destination_rule"] = str(expected_data["destination_rule"])

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)  # noqa

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/app-override-rules/{source_rule}:move",
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
            "1 validation error for AppOverrideRuleMoveModel\ndestination\n  Input should be 'top', 'bottom', 'before' or 'after'"
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

    def test_move_bottom(self):
        """Test moving a rule to the bottom."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "bottom",
            "rulebase": "post",
        }

        self.mock_scm.post.return_value = None
        self.client.move(source_rule, move_data)

        self.mock_scm.post.assert_called_once_with(
            f"/config/security/v1/app-override-rules/{source_rule}:move",
            json=move_data,
        )


# -------------------- Test Misc --------------------


class TestAppOverrideRuleModelMisc(TestAppOverrideRuleBase):
    """Tests for miscellaneous AppOverrideRule model behavior."""

    def test_ensure_list_of_strings_single_string(self):
        """Test that a single string is converted to a list containing that string."""
        model = AppOverrideRuleCreateModel(
            name="test-rule",
            application="web-browsing",
            port="80",
            protocol="tcp",
            source="192.168.1.1",
            folder="Texas",
        )
        assert model.source == ["192.168.1.1"]

    def test_ensure_list_of_strings_invalid_type(self):
        """Test that a non-string, non-list value raises a ValueError."""
        with pytest.raises(ValueError, match="Value must be a list of strings"):
            AppOverrideRuleCreateModel(
                name="test-rule",
                application="web-browsing",
                port="80",
                protocol="tcp",
                source=123,
                folder="Texas",
            )

    def test_ensure_list_of_strings_non_string_items(self):
        """Test that a list containing non-string items raises a ValueError."""
        with pytest.raises(ValueError, match="All items must be strings"):
            AppOverrideRuleCreateModel(
                name="test-rule",
                application="web-browsing",
                port="80",
                protocol="tcp",
                source=["192.168.1.1", 123],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicates(self):
        """Test that duplicate items in lists raise a ValueError."""
        with pytest.raises(ValueError, match="List items must be unique"):
            AppOverrideRuleCreateModel(
                name="test-rule",
                application="web-browsing",
                port="80",
                protocol="tcp",
                source=["192.168.1.1", "192.168.1.1"],
                folder="Texas",
            )

    def test_app_override_rule_create_no_container(self):
        """Test that not providing any container raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
        ):
            AppOverrideRuleCreateModel(
                name="test-rule",
                application="web-browsing",
                port="80",
                protocol="tcp",
            )

    def test_app_override_rule_create_multiple_containers(self):
        """Test that providing multiple containers raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
        ):
            AppOverrideRuleCreateModel(
                name="test-rule",
                application="web-browsing",
                port="80",
                protocol="tcp",
                folder="Texas",
                snippet="MySnippet",
            )

    def test_ensure_list_of_strings_none_value(self):
        """Test that None values pass through ensure_list_of_strings validator unchanged."""
        model = AppOverrideRuleCreateModel(
            name="test-rule",
            application="web-browsing",
            port="80",
            protocol="tcp",
            tag=None,
            folder="Texas",
        )
        assert model.tag is None

    def test_ensure_unique_items_none_value(self):
        """Test that None values pass through ensure_unique_items validator unchanged."""
        # tag=None should pass both validators without error
        model = AppOverrideRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            application="web-browsing",
            port="80",
            protocol="tcp",
            tag=None,
            folder="Texas",
        )
        assert model.tag is None

    def test_move_model_unexpected_destination_rule_top(self):
        """Test that providing destination_rule with 'top' raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'top'",
        ):
            AppOverrideRuleMoveModel(
                destination=AppOverrideRuleMoveDestination.TOP,
                rulebase=AppOverrideRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )

    def test_move_model_unexpected_destination_rule_bottom(self):
        """Test that providing destination_rule with 'bottom' raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'bottom'",
        ):
            AppOverrideRuleMoveModel(
                destination=AppOverrideRuleMoveDestination.BOTTOM,
                rulebase=AppOverrideRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )


# -------------------- End of Test Classes --------------------
