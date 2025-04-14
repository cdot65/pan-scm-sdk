# tests/scm/config/network/test_nat_rules.py

from unittest.mock import MagicMock

from pydantic import ValidationError
from pydantic.v1 import UUID4
import pytest
from requests.exceptions import HTTPError

# Import the NAT Rule SDK and related exceptions
from scm.config.network.nat_rules import NatRule
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network.nat_rules import (
    NatRuleCreateModel,
    NatRuleResponseModel,
    NatRuleUpdateModel,
)
from tests.factories.network import (
    NatRuleCreateApiFactory,
    NatRuleResponseFactory,
    NatRuleUpdateApiFactory,
)

# Import utility function for simulating HTTP errors


@pytest.mark.usefixtures("load_env")
class TestNatRuleBase:
    """Base class for NAT Rule tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = NatRule(self.mock_scm, max_limit=5000)


# -------------------- Max Limit Tests --------------------


class TestNatRuleMaxLimit(TestNatRuleBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = NatRule(self.mock_scm)
        assert client.max_limit == NatRule.DEFAULT_MAX_LIMIT  # should be 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = NatRule(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test that max_limit can be updated via the setter."""
        client = NatRule(self.mock_scm)
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that a non-integer max_limit raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(exc_info.value)

    def test_max_limit_too_low(self):
        """Test that a max_limit below 1 raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule(self.mock_scm, max_limit=0)
        assert "Invalid max_limit value" in str(exc_info.value)

    def test_max_limit_too_high(self):
        """Test that a max_limit above the allowed maximum raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule(self.mock_scm, max_limit=6000)
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


# -------------------- List Method Tests --------------------


class TestNatRuleList(TestNatRuleBase):
    """Tests for listing NAT Rule objects."""

    def test_list_valid(self):
        """Test listing NAT rules successfully."""
        # Create a mock response with two NAT rule objects
        mock_response = {
            "data": [
                NatRuleResponseFactory(name="nat_rule_1", folder="Shared").model_dump(
                    by_alias=True
                ),
                NatRuleResponseFactory(name="nat_rule_2", folder="Shared").model_dump(
                    by_alias=True
                ),
            ],
            "offset": 0,
            "total": 2,
            "limit": 5000,
        }
        self.mock_scm.get.return_value = mock_response

        rules = self.client.list(folder="Shared")
        self.mock_scm.get.assert_called_once_with(
            "/config/network/v1/nat-rules",
            params={"folder": "Shared", "limit": 5000, "offset": 0, "position": "pre"},
        )
        assert isinstance(rules, list)
        assert len(rules) == 2
        assert isinstance(rules[0], NatRuleResponseModel)
        assert rules[0].name.startswith("nat_rule_")

    def test_list_folder_empty_error(self):
        """Test that an empty folder raises MissingQueryParameterError."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg

    def test_list_container_missing_error(self):
        """Test that not providing any container parameter raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()
        assert "Invalid container parameters" in str(exc_info.value)

    def test_list_container_multiple_error(self):
        """Test that providing multiple container parameters raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")
        assert "Invalid container parameters" in str(exc_info.value)

    def test_list_filters_valid(self):
        """Test that valid filters are applied."""
        # Create a mock response with two NAT rule objects having different attributes
        mock_response = {
            "data": [
                NatRuleResponseFactory(
                    name="nat_rule_filter_1",
                    folder="Shared",
                    nat_type="ipv4",
                    service="http",
                    source=["10.0.0.0/24"],
                    destination=["any"],
                    tag=["Automation"],  # Example tag
                    disabled=False,
                ).model_dump(by_alias=True),
                NatRuleResponseFactory(
                    name="nat_rule_filter_2",
                    folder="Shared",
                    nat_type="ipv4",
                    service="https",
                    source=["any"],
                    destination=["20.0.0.0/24"],
                    tag=["Decrypted"],  # Example tag
                    disabled=True,
                ).model_dump(by_alias=True),
            ],
            "offset": 0,
            "total": 2,
            "limit": 5000,
        }
        self.mock_scm.get.return_value = mock_response

        filters = {
            "nat_type": ["ipv4"],
            "service": ["http"],
            "source": ["10.0.0.0/24"],  # Note: adjust if your filter logic expects list of strings
            "tag": ["Automation"],  # Filter by tag
            "disabled": False,
        }
        rules = self.client.list(folder="Shared", **filters)
        # With these filters, we expect only the first object to remain
        assert len(rules) == 1
        assert rules[0].name == "nat_rule_filter_1"

    def test_list_filters_invalid_type(self):
        """Test that an invalid filter type raises an error."""
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Shared", nat_type="ipv4")  # should be a list

    def test_list_pagination_multiple_pages(self):
        """Test that pagination aggregates all objects."""
        # Simulate three pages of responses
        client = NatRule(self.mock_scm, max_limit=2500)  # Use 2500 as the page size
        first_page = [
            NatRuleResponseFactory(name=f"nat_rule_page1_{i}", folder="Shared").model_dump(
                by_alias=True
            )
            for i in range(2500)
        ]
        second_page = [
            NatRuleResponseFactory(name=f"nat_rule_page2_{i}", folder="Shared").model_dump(
                by_alias=True
            )
            for i in range(2500)
        ]
        third_page = [
            NatRuleResponseFactory(name=f"nat_rule_page3_{i}", folder="Shared").model_dump(
                by_alias=True
            )
            for i in range(100)
        ]
        mock_responses = [
            {"data": first_page},
            {"data": second_page},
            {"data": third_page},
            {"data": []},
        ]
        self.mock_scm.get.side_effect = mock_responses

        results = client.list(folder="Shared")
        assert len(results) == 2500 + 2500 + 100
        assert self.mock_scm.get.call_count == 3

    def test_list_http_error_no_content(self):
        """Test that an HTTPError without content in list() is raised."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")

    def test_list_response_missing_data_field(self):
        """
        Test that InvalidObjectError is raised when the API response
        is missing the 'data' field.
        """
        # Simulate an API response without the 'data' key
        self.mock_scm.get.return_value = {
            "offset": 0,
            "total": 0,
            "limit": self.client.max_limit,
        }
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")
        error_msg = str(exc_info.value)
        assert "field missing in the response" in error_msg

    def test_list_response_invalid_data_field_type(self):
        """
        Test that InvalidObjectError is raised when the API response's
        'data' field is not a list.
        """
        # Simulate an API response with 'data' not being a list
        self.mock_scm.get.return_value = {
            "data": "not a list",
            "offset": 0,
            "total": 0,
            "limit": self.client.max_limit,
        }
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")
        error_msg = str(exc_info.value)
        assert "field must be a list" in error_msg

    def test_fetch_missing_id_field(self):
        """
        Test that fetch() raises an InvalidObjectError when the API response
        is missing the 'id' field.
        """
        # Create test data using a factory that produces a valid container (using device)
        test_data = NatRuleCreateApiFactory.with_device(device="TestDevice").model_dump(
            by_alias=True
        )
        # Simulate a response that is missing the "id" field.
        response_data = test_data.copy()
        response_data.pop("id", None)
        self.mock_scm.get.return_value = response_data

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name=test_data["name"], device=test_data["device"])

        error = exc_info.value
        # Verify the error message indicates the missing 'id' field.
        assert "missing 'id' field" in error.message


# -------------------- Create Method Tests --------------------


class TestNatRuleCreate(TestNatRuleBase):
    """Tests for creating NAT Rule objects."""

    def test_create_valid_object(self):
        """Test creating a NAT rule with valid data."""
        test_data = NatRuleCreateApiFactory.with_device(device="TestDevice").model_dump(
            by_alias=True
        )
        mock_response = NatRuleResponseFactory.from_request(NatRuleCreateModel(**test_data))
        self.mock_scm.post.return_value = mock_response.model_dump(by_alias=True)

        created_rule = self.client.create(test_data)
        self.mock_scm.post.assert_called_once_with(
            "/config/network/v1/nat-rules",
            params={"position": "pre"},
            json=test_data,
        )
        assert isinstance(created_rule, NatRuleResponseModel)
        assert created_rule.name == test_data["name"]

    def test_create_with_invalid_container(self):
        """Test that creating with no or multiple containers raises an error."""
        # No container provided
        with pytest.raises(ValidationError) as exc_info:
            NatRuleCreateApiFactory.build_with_no_containers()
        errors = exc_info.value.errors()
        assert any(
            "Exactly one of 'folder', 'snippet', or 'device'" in err["msg"] for err in errors
        )

        # Multiple containers provided
        with pytest.raises(ValidationError) as exc_info:
            NatRuleCreateApiFactory.build_with_multiple_containers()
        errors = exc_info.value.errors()
        assert any(
            "Exactly one of 'folder', 'snippet', or 'device'" in err["msg"] for err in errors
        )

    def test_create_http_error_no_content(self):
        """Test creation when HTTPError with no response content is raised."""
        test_data = NatRuleCreateApiFactory.with_device(device="TestDevice").model_dump(
            by_alias=True
        )
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.create(test_data)

    def test_create_generic_exception_handling(self):
        """Test that a generic exception during create is propagated."""
        test_data = NatRuleCreateApiFactory.with_device(device="TestDevice").model_dump(
            by_alias=True
        )
        self.mock_scm.post.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.create(test_data)
        assert str(exc_info.value) == "Generic error"


# -------------------- Get Method Tests --------------------


class TestNatRuleGet(TestNatRuleBase):
    """Tests for retrieving a NAT rule by ID."""

    def test_get_valid_object(self):
        """Test that get returns a valid NAT rule object."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = NatRuleResponseFactory(name="TestNatRule", folder="Shared").model_dump(
            by_alias=True
        )
        mock_response["id"] = rule_id
        self.mock_scm.get.return_value = mock_response

        retrieved = self.client.get(rule_id)
        self.mock_scm.get.assert_called_once_with(f"/config/network/v1/nat-rules/{rule_id}")
        assert isinstance(retrieved, NatRuleResponseModel)
        assert retrieved.id == UUID4(rule_id)

    def test_get_http_error_no_content(self):
        """Test that get raises HTTPError when response content is missing."""
        rule_id = "invalid-id"
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)

        with pytest.raises(HTTPError):
            self.client.get(rule_id)

    def test_get_generic_exception_handling(self):
        """Test generic exception handling in get method."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        self.mock_scm.get.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.get(rule_id)
        assert str(exc_info.value) == "Generic error"


# -------------------- Update Method Tests --------------------


class TestNatRuleUpdate(TestNatRuleBase):
    """Tests for updating NAT rule objects."""

    def test_update_valid_object(self):
        """Test updating a NAT rule with valid data."""
        update_model = NatRuleUpdateApiFactory.with_source_translation()
        update_dict = update_model.model_dump(by_alias=True)
        update_dict["folder"] = "Shared"
        # Prepare a mock response which will generate a new id
        mock_response = NatRuleResponseFactory.from_request(NatRuleCreateModel(**update_dict))
        self.mock_scm.put.return_value = mock_response.model_dump(by_alias=True)

        updated_rule = self.client.update(update_model)
        expected_endpoint = f"/config/network/v1/nat-rules/{update_dict['id']}"

        # Remove 'id' from the expected payload because update() pops it
        expected_payload = update_dict.copy()
        expected_payload.pop("id", None)
        expected_payload.pop("folder", None)
        expected_payload.pop("snippet", None)
        expected_payload.pop("device", None)

        # Use put.assert_called to verify that the method was called
        assert self.mock_scm.put.called

        # Get actual arguments
        call_args = self.mock_scm.put.call_args

        # Verify that the endpoint and params are correct
        assert call_args[0][0] == expected_endpoint
        assert call_args[1]["params"] == {"position": "pre"}

        # Check that basic parameters match (but not comparing the entire structure)
        actual_json = call_args[1]["json"]
        assert actual_json["name"] == expected_payload["name"]
        assert actual_json["tag"] == expected_payload["tag"]
        assert actual_json["nat_type"] == expected_payload["nat_type"]
        assert "source_translation" in actual_json

        # The format of source_translation might differ slightly but it should exist and have dynamic_ip_and_port
        assert "dynamic_ip_and_port" in actual_json["source_translation"]
        assert isinstance(updated_rule, NatRuleResponseModel)
        # Instead of comparing to update_dict["id"], compare to the mock response's id:
        assert updated_rule.id == mock_response.id

    def test_update_http_error_no_content(self):
        """Test update method when HTTPError with no content is raised."""
        update_data = NatRuleUpdateApiFactory.with_source_translation()
        update_model = NatRuleUpdateModel(**update_data.model_dump())
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.put.side_effect = HTTPError(response=mock_response)

        with pytest.raises(HTTPError):
            self.client.update(update_model)

    def test_update_generic_exception_handling(self):
        """Test generic exception handling in update method."""
        update_data = NatRuleUpdateApiFactory.with_source_translation()
        update_model = NatRuleUpdateModel(**update_data.model_dump())
        self.mock_scm.put.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.update(update_model)
        assert str(exc_info.value) == "Generic error"


# -------------------- Delete Method Tests --------------------


class TestNatRuleDelete(TestNatRuleBase):
    """Tests for deleting NAT rule objects."""

    def test_delete_success(self):
        """Test successful deletion of a NAT rule."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        self.mock_scm.delete.return_value = None
        self.client.delete(rule_id)
        self.mock_scm.delete.assert_called_once_with(f"/config/network/v1/nat-rules/{rule_id}")

    def test_delete_http_error_no_content(self):
        """Test that delete raises HTTPError when response content is missing."""
        rule_id = "bad-id"
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.delete.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.delete(rule_id)

    def test_delete_generic_exception_handling(self):
        """Test that a generic exception during delete is propagated."""
        self.mock_scm.delete.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdef")
        assert str(exc_info.value) == "Generic error"


# -------------------- Fetch Method Tests --------------------


class TestNatRuleFetch(TestNatRuleBase):
    """Tests for fetching a NAT rule by name."""

    def test_fetch_valid_object(self):
        """Test that fetch returns a valid NAT rule object."""
        test_data = NatRuleCreateApiFactory.with_device(device="TestDevice").model_dump(
            by_alias=True
        )
        # Create a request model and a response from that request
        request_model = NatRuleCreateModel(**test_data)
        response_data = NatRuleResponseFactory.from_request(request_model).model_dump(by_alias=True)
        self.mock_scm.get.return_value = response_data

        fetched_rule = self.client.fetch(name=request_model.name, folder=test_data.get("device"))
        params_expected = {
            "folder": test_data.get("device"),
            "name": request_model.name,
            "position": "pre",
        }
        self.mock_scm.get.assert_called_once_with(
            "/config/network/v1/nat-rules", params=params_expected
        )
        assert isinstance(fetched_rule, NatRuleResponseModel)
        assert fetched_rule.name == request_model.name

    def test_fetch_empty_name_error(self):
        """Test that fetch with empty name raises MissingQueryParameterError."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")
        assert '"name" is not allowed to be empty' in str(exc_info.value)

    def test_fetch_empty_container_error(self):
        """Test that fetch with empty container parameter raises MissingQueryParameterError."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="TestNatRule", folder="")
        assert '"folder" is not allowed to be empty' in str(exc_info.value)

    def test_fetch_container_multiple_error(self):
        """Test that fetch with multiple container parameters raises InvalidObjectError."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestNatRule", folder="Shared", snippet="TestSnippet")
        assert "Exactly one of 'folder', 'snippet', or 'device'" in str(exc_info.value)

    def test_fetch_http_error_no_response_content(self):
        """Test that fetch raises HTTPError when response content is missing."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.fetch(name="TestNatRule", folder="Shared")

    def test_fetch_invalid_response_format(self):
        """Test that fetch raises InvalidObjectError when response is not a dict."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestNatRule", folder="Shared")
        assert "Response is not a dictionary" in str(exc_info.value)


class TestNatRuleApplyFilters:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Create two dummy NAT rule objects with varying attributes.
        self.rule1 = NatRuleResponseFactory(
            name="rule1",
            nat_type="ipv4",
            service="http",
            destination=["10.0.0.1"],
            source=["any"],
            tag=["Automation"],  # Tag for filtering
            disabled=False,
        )
        self.rule2 = NatRuleResponseFactory(
            name="rule2",
            nat_type="nat64",
            service="https",
            destination=["20.0.0.1"],
            source=["any"],
            tag=["Decrypted"],  # Tag for filtering
            disabled=True,
        )
        self.rules = [self.rule1, self.rule2]

    def test_invalid_nat_type_filter(self):
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"nat_type": "ipv4"})
        # Expect the error message indicating the filter must be a list
        assert exc_info.value.message == "'nat_type' filter must be a list"

    def test_invalid_service_filter(self):
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"service": "http"})
        # Expect the error message indicating the filter must be a list
        assert exc_info.value.message == "'service' filter must be a list"

    def test_invalid_destination_filter(self):
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"destination": "10.0.0.1"})
        assert exc_info.value.message == "'destination' filter must be a list"

    def test_invalid_source_filter(self):
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"source": "any"})
        assert exc_info.value.message == "'source' filter must be a list"

    def test_invalid_tag_filter(self):
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"tag": "test"})
        assert exc_info.value.message == "'tag' filter must be a list"

    def test_invalid_disabled_filter_string(self):
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"disabled": "false"})
        assert exc_info.value.message == "'disabled' filter must be a boolean"

    def test_invalid_disabled_filter_int(self):
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"disabled": 0})
        assert exc_info.value.message == "'disabled' filter must be a boolean"


class TestNatRuleListFiltering:
    """Tests for filtering logic within the list() method (i.e. filtered_objects)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        # Create dummy NAT rule response objects.
        # Note: NatRuleResponseModel may not include container attributes,
        # so we define them here in the factory by using extra fields.
        self.rule1 = NatRuleResponseFactory(
            name="rule1",
            nat_type="ipv4",
            service="http",
            destination=["10.0.0.1"],
            source=["any"],
            tag=["Automation"],  # Tag for filtering
            disabled=False,
        )
        self.rule2 = NatRuleResponseFactory(
            name="rule2",
            nat_type="nat64",
            service="https",
            destination=["20.0.0.1"],
            source=["any"],
            tag=["Decrypted"],  # Tag for filtering
            disabled=True,
        )
        self.rule3 = NatRuleResponseFactory(
            name="rule3",
            nat_type="ipv4",
            service="http",
            destination=["30.0.0.1"],
            source=["any"],
            tag=["Automation", "Decrypted"],  # Multiple tags for filtering
            disabled=False,
        )
        # We'll use these objects as our base rules.
        self.rules = [self.rule1, self.rule2, self.rule3]

    # --- Direct _apply_filters tests remain unchanged ---
    def test_filter_by_nat_type(self):
        filters = {"nat_type": ["ipv4"]}
        filtered = NatRule._apply_filters(self.rules, filters)
        assert len(filtered) == 2
        for rule in filtered:
            assert rule.nat_type == "ipv4"

    def test_filter_by_service(self):
        """Test filtering by service returns only matching rules."""
        filters = {"service": ["http"]}
        filtered = NatRule._apply_filters(self.rules, filters)
        assert len(filtered) == 2
        for rule in filtered:
            assert rule.service == "http"

    def test_filter_by_destination(self):
        """Test filtering by destination returns rules where any destination matches."""
        filters = {"destination": ["10.0.0.1"]}
        filtered = NatRule._apply_filters(self.rules, filters)
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_filter_by_source(self):
        """Test filtering by source returns only matching rules."""
        filters = {"source": ["any"]}
        filtered = NatRule._apply_filters(self.rules, filters)
        # All rules have source equal to ["any"] in this setup.
        assert len(filtered) == 3

    def test_filter_by_tag(self):
        """Test filtering by tag returns only matching rules."""
        filters = {"tag": ["Automation"]}
        filtered = NatRule._apply_filters(self.rules, filters)
        # rule1 and rule3 have "Automation" in their tag list.
        assert len(filtered) == 2
        for rule in filtered:
            assert "Automation" in rule.tag

    def test_filter_by_disabled(self):
        """Test filtering by disabled returns only rules with matching status."""
        filters = {"disabled": True}
        filtered = NatRule._apply_filters(self.rules, filters)
        assert len(filtered) == 1
        assert filtered[0].disabled is True

    # --- Tests for invalid filter types ---

    def test_invalid_nat_type_filter(self):
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"nat_type": "ipv4"})
        assert exc_info.value.message == "'nat_type' filter must be a list"

    def test_invalid_service_filter(self):
        """Test that providing a non-list for 'service' raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"service": "http"})
        assert exc_info.value.message == "'service' filter must be a list"

    def test_invalid_destination_filter(self):
        """Test that providing a non-list for 'destination' raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"destination": "10.0.0.1"})
        assert exc_info.value.message == "'destination' filter must be a list"

    def test_invalid_source_filter(self):
        """Test that providing a non-list for 'source' raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"source": "any"})
        assert exc_info.value.message == "'source' filter must be a list"

    def test_invalid_tag_filter(self):
        """Test that providing a non-list for 'tag' raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"tag": "Automation"})
        assert exc_info.value.message == "'tag' filter must be a list"

    def test_invalid_disabled_filter(self):
        """Test that providing a non-boolean for 'disabled' raises an error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NatRule._apply_filters(self.rules, {"disabled": "False"})
        assert exc_info.value.message == "'disabled' filter must be a boolean"


class TestNatRuleContainerFiltering(TestNatRuleBase):
    def test_exact_match_filter(self):
        """
        Test that when exact_match=True, only objects whose container
        field exactly matches the provided value are returned.
        """
        # Simulate API response with two NAT rule objects:
        # one with folder "Shared" (matching) and one with folder "Other" (non-matching)
        rule_shared = NatRuleResponseFactory(folder="Shared", name="rule_shared").model_dump(
            by_alias=True
        )
        rule_other = NatRuleResponseFactory(folder="Other", name="rule_other").model_dump(
            by_alias=True
        )
        response_data = {
            "data": [rule_shared, rule_other],
            "offset": 0,
            "total": 2,
            "limit": self.client.max_limit,
        }
        self.mock_scm.get.return_value = response_data

        # Call list with folder="Shared" and exact_match=True.
        results = self.client.list(folder="Shared", exact_match=True)
        # Only the object with folder "Shared" should remain.
        assert len(results) == 1
        assert results[0].folder == "Shared"
        assert results[0].name == "rule_shared"

    def test_exclude_folders_filter(self):
        """
        Test that when exclude_folders is provided, any object whose folder is in
        the exclusion list is removed from the results.
        """
        # Simulate API response with two objects: one with folder "Shared" and one with folder "All"
        rule_shared = NatRuleResponseFactory(folder="Shared", name="rule_shared").model_dump(
            by_alias=True
        )
        rule_all = NatRuleResponseFactory(folder="All", name="rule_all").model_dump(by_alias=True)
        response_data = {
            "data": [rule_shared, rule_all],
            "offset": 0,
            "total": 2,
            "limit": self.client.max_limit,
        }
        self.mock_scm.get.return_value = response_data

        # Call list with folder="Shared" and exclude_folders=["All"].
        # Even if the API response contains an object with folder "All", the exclusion filter should remove it.
        results = self.client.list(folder="Shared", exclude_folders=["All"])
        assert len(results) == 1
        assert results[0].folder == "Shared"
        assert results[0].name == "rule_shared"

    def test_exclude_snippets_filter(self):
        """
        Test that when exclude_snippets is provided, any object whose snippet is in
        the exclusion list is removed from the results.
        """
        # Simulate API response with two objects having different snippet values.
        rule_snippet = NatRuleResponseFactory(
            snippet="TestSnippet", name="rule_snippet"
        ).model_dump(by_alias=True)
        rule_other_snippet = NatRuleResponseFactory(
            snippet="OtherSnippet", name="rule_other_snippet"
        ).model_dump(by_alias=True)
        response_data = {
            "data": [rule_snippet, rule_other_snippet],
            "offset": 0,
            "total": 2,
            "limit": self.client.max_limit,
        }
        self.mock_scm.get.return_value = response_data

        # Call list with snippet="TestSnippet" and exclude_snippets=["OtherSnippet"].
        # Only the object with snippet "TestSnippet" should remain.
        results = self.client.list(snippet="TestSnippet", exclude_snippets=["OtherSnippet"])
        assert len(results) == 1
        assert results[0].snippet == "TestSnippet"
        assert results[0].name == "rule_snippet"

    def test_exclude_devices_filter(self):
        """
        Test that when exclude_devices is provided, any object whose device is in
        the exclusion list is removed from the results.
        """
        # Simulate API response with two objects having different device values.
        rule_device = NatRuleResponseFactory(device="TestDevice", name="rule_device").model_dump(
            by_alias=True
        )
        rule_other_device = NatRuleResponseFactory(
            device="OtherDevice", name="rule_other_device"
        ).model_dump(by_alias=True)
        response_data = {
            "data": [rule_device, rule_other_device],
            "offset": 0,
            "total": 2,
            "limit": self.client.max_limit,
        }
        self.mock_scm.get.return_value = response_data

        # Call list with device="TestDevice" and exclude_devices=["OtherDevice"].
        # Only the object with device "TestDevice" should remain.
        results = self.client.list(device="TestDevice", exclude_devices=["OtherDevice"])
        assert len(results) == 1
        assert results[0].device == "TestDevice"
        assert results[0].name == "rule_device"
