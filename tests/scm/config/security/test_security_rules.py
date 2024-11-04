# tests/test_security_rules.py
import uuid
from unittest.mock import MagicMock, patch, Mock

import pytest
from pydantic import ValidationError as PydanticValidationError
from scm.exceptions import ValidationError
from scm.models.security.security_rules import (
    SecurityRuleRequestModel,
    SecurityRuleResponseModel,
    ProfileSetting,
    string_validator,
    RuleMoveDestination,
    Rulebase,
    SecurityRuleMoveModel,
)
from scm.config.security import SecurityRule
from tests.factories import SecurityRuleRequestFactory, SecurityRuleResponseFactory


class TestSecurityRuleBasicOperations:
    """Test basic CRUD operations for security rules."""

    @pytest.fixture
    def security_rule_client(self, mock_scm):
        return SecurityRule(mock_scm)

    def test_create_security_rule(
        self,
        security_rule_client,
        mock_scm,
    ):
        """Test creating a security rule with default rulebase."""
        test_rule = SecurityRuleRequestFactory()
        mock_response = SecurityRuleResponseFactory(**test_rule.model_dump())

        # Ensure mock_scm.post is a MagicMock object
        mock_scm.post = MagicMock()
        mock_scm.post.return_value = mock_response.model_dump(by_alias=True)

        created_rule = security_rule_client.create(
            test_rule.model_dump(
                exclude_none=True,
                by_alias=True,
            )
        )

        mock_scm.post.assert_called_once_with(
            "/config/security/v1/security-rules",
            params={"position": "pre"},
            json=test_rule.model_dump(
                exclude_none=True,
                by_alias=True,
            ),
        )
        assert isinstance(created_rule, SecurityRuleResponseModel)

    def test_create_with_explicit_rulebase(
        self,
        security_rule_client,
        mock_scm,
    ):
        """Test creating a security rule with explicit rulebase."""
        test_rule = SecurityRuleRequestFactory()
        mock_response = SecurityRuleResponseFactory(**test_rule.model_dump())

        # Ensure mock_scm.post is a MagicMock object
        mock_scm.post = MagicMock()
        mock_scm.post.return_value = mock_response.model_dump(by_alias=True)

        security_rule_client.create(
            test_rule.model_dump(
                exclude_none=True,
                by_alias=True,
            ),
            rulebase="post",
        )

        mock_scm.post.assert_called_once_with(
            "/config/security/v1/security-rules",
            params={"position": "post"},
            json=test_rule.model_dump(
                exclude_none=True,
                by_alias=True,
            ),
        )


class TestSecurityRuleAPI:
    """Test suite for SecurityRule SDK API methods."""

    @pytest.fixture
    def security_rules_client(self, mock_scm):
        return SecurityRule(mock_scm)

    def test_list_security_rules(
        self,
        load_env,
        mock_scm,
    ):
        # Mock the API client's get method if you don't want to make real API calls
        mock_response = {
            "data": [
                {
                    "id": "721c065c-0966-4aab-84ae-d70f55e9c5a7",
                    "name": "default",
                    "folder": "All",
                    "log_setting": "Cortex Data Lake",
                    "log_end": True,
                },
                {
                    "id": "980a0e95-9c14-4383-bf19-dd8f03c41943",
                    "name": "Web-Security-Default",
                    "folder": "All",
                    "log_setting": "Cortex Data Lake",
                    "log_end": True,
                },
                {
                    "id": "2cfc7c35-ac36-4cd2-9ce9-33dd1b99ea87",
                    "name": "hip-default",
                    "folder": "All",
                },
                {
                    "id": "404cc766-539b-4245-a2ae-822f2770846f",
                    "name": "optional-default",
                    "folder": "Shared",
                    "log_setting": "Cortex Data Lake",
                    "log_end": True,
                },
                {
                    "id": "b80505fa-217f-4626-8dde-35545e3df611",
                    "name": "office365",
                    "folder": "Shared",
                    "log_setting": "Cortex Data Lake",
                    "log_end": True,
                },
                {
                    "id": "70b9f4f2-b3e5-422f-8726-8cc41ef39078",
                    "name": "deny FTP",
                    "folder": "Shared",
                    "disabled": False,
                    "from": ["trust"],
                    "source": ["any"],
                    "source_user": ["any"],
                    "source_hip": ["any"],
                    "to": ["untrust"],
                    "destination": ["any"],
                    "destination_hip": ["any"],
                    "application": ["ftp"],
                    "service": ["any"],
                    "category": ["any"],
                    "action": "deny",
                    "log_start": False,
                    "log_end": True,
                    "log_setting": "Cortex Data Lake",
                },
                {
                    "id": "dc5cffdb-fc21-4882-b5c5-ccbcc134e004",
                    "name": "rbi",
                    "folder": "Shared",
                    "log_setting": "Cortex Data Lake",
                    "log_end": True,
                },
                {
                    "id": "b9a5af08-151f-4761-aced-98d6e5e2dc7a",
                    "name": "saas-tenant-restrictions",
                    "folder": "Shared",
                    "log_setting": "Cortex Data Lake",
                    "log_end": True,
                },
                {
                    "id": "504fb7f5-b63d-45e4-a599-7dcc80974f42",
                    "name": "VPN clients to Corporate",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["any"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Permit any clients to access corporate network",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "8a5cb583-85bd-45d9-be7e-2a6f79888f4c",
                    "name": "Monitor WAN to GlobalProtect",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["panos-global-protect", "ssl", "web-browsing"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Monitor GlobalProtect requests",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "91cc19e4-c154-4a8b-959d-13be61303c11",
                    "name": "Auto-Rule-1",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["dns"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 1",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "385d9ff9-3370-40b9-b4f7-5a822da39d5c",
                    "name": "Auto-Rule-3",
                    "folder": "Shared",
                    "action": "deny",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["smtp"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 3",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "0e23d466-cc28-4037-ba5a-28d4ec907f3b",
                    "name": "Auto-Rule-6",
                    "folder": "Shared",
                    "action": "deny",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["ssh"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 6",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "37d82545-4084-43d4-8b55-0089290b85d4",
                    "name": "Auto-Rule-9",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["web-browsing"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 9",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "4efb42ba-dd4a-4a47-a5c0-4b4ec8b8c41e",
                    "name": "Auto-Rule-12",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["ssh"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 12",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "1ca04f5f-f03b-44de-a872-183d0818fe21",
                    "name": "Auto-Rule-15",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["smtp"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 15",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "9a5fd2c9-efb0-46f6-802b-40d6ef8f6dad",
                    "name": "Auto-Rule-18",
                    "folder": "Shared",
                    "action": "deny",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["dns"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 18",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "1c59570f-1632-4a93-9f7c-a8d0146683b5",
                    "name": "Auto-Rule-19",
                    "folder": "Shared",
                    "action": "deny",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["dns"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 19",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "0d2637d9-33fa-4e5b-b3f1-94f21e3bc6e2",
                    "name": "Auto-Rule-20",
                    "folder": "Shared",
                    "action": "deny",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["smtp"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 20",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "864b7614-8377-4e2c-a0b2-c2ef12179c9f",
                    "name": "Auto-Rule-32",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["smtp"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 32",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "58c93101-2fb5-438b-a397-7e927f77be25",
                    "name": "Auto-Rule-33",
                    "folder": "Shared",
                    "action": "deny",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["smtp"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 33",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "6aae06a8-9044-4db3-a3c9-516c1c74e36c",
                    "name": "Auto-Rule-34",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["smtp"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 34",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "5f26df62-228a-4671-827e-4b03fea06c96",
                    "name": "Auto-Rule-35",
                    "folder": "Shared",
                    "action": "deny",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["dns"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 35",
                    "log_end": True,
                    "disabled": True,
                },
                {
                    "id": "6ed52d68-bb27-4abc-9346-4eac2652a4b9",
                    "name": "Auto-Rule-37",
                    "folder": "Shared",
                    "action": "allow",
                    "from": ["any"],
                    "to": ["any"],
                    "source": ["any"],
                    "destination": ["any"],
                    "source_user": ["any"],
                    "category": ["any"],
                    "application": ["dns"],
                    "service": ["any"],
                    "log_setting": "Cortex Data Lake",
                    "description": "Randomly generated security rule 37",
                    "log_end": True,
                    "disabled": True,
                },
            ],
            "offset": 0,
            "total": 24,
            "limit": 200,
        }

        mock_scm.get = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)
        security_rules = security_rules_client.list(folder="All")

        # Updated assertion to include position parameter
        mock_scm.get.assert_called_once_with(
            "/config/security/v1/security-rules",
            params={"folder": "All", "position": "pre"},  # pre is default
        )
        assert isinstance(security_rules, list)
        assert isinstance(security_rules[0], SecurityRuleResponseModel)
        assert len(security_rules) == 24

    def test_create_security_rule(
        self,
        load_env,
        mock_scm,
    ):
        """Test creating a security rule with default rulebase."""
        test_security_rule = SecurityRuleRequestFactory()
        mock_response = test_security_rule.model_dump(
            exclude_none=True,
            by_alias=True,
        )
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        mock_scm.post = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)

        created_rule = security_rules_client.create(
            test_security_rule.model_dump(
                exclude_none=True,
                by_alias=True,
            )
        )

        # Updated assertion to include position parameter
        mock_scm.post.assert_called_once_with(
            "/config/security/v1/security-rules",
            params={"position": "pre"},  # pre is default
            json=test_security_rule.model_dump(
                exclude_none=True,
                by_alias=True,
            ),
        )
        assert created_rule.id == "123e4567-e89b-12d3-a456-426655440000"

    def test_create_security_rule_with_explicit_rulebase(
        self,
        load_env,
        mock_scm,
    ):
        """Test creating a security rule with explicit rulebase."""
        test_security_rule = SecurityRuleRequestFactory()
        mock_response = test_security_rule.model_dump(
            exclude_none=True,
            by_alias=True,
        )
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        mock_scm.post = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)

        security_rules_client.create(
            test_security_rule.model_dump(
                exclude_none=True,
                by_alias=True,
            ),
            rulebase="post",
        )

        mock_scm.post.assert_called_once_with(
            "/config/security/v1/security-rules",
            params={"position": "post"},
            json=test_security_rule.model_dump(
                exclude_none=True,
                by_alias=True,
            ),
        )

    def test_update_security_rule(
        self,
        load_env,
        mock_scm,
    ):
        """Test updating a security rule with default rulebase."""
        test_security_rule = SecurityRuleRequestFactory(name="UpdatedSecurityRule")
        mock_response = test_security_rule.model_dump(
            exclude_unset=True,
            by_alias=True,
        )
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response["id"] = rule_id

        mock_scm.put = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)

        update_data = test_security_rule.model_dump(
            exclude_unset=True,
            by_alias=True,
        )
        update_data["id"] = (
            rule_id  # Include the 'id' in update_data for endpoint construction
        )

        updated_rule = security_rules_client.update(update_data)

        # Create a copy of update_data without 'id' for the expected JSON payload
        expected_json = update_data.copy()
        expected_json.pop("id")

        mock_scm.put.assert_called_once_with(
            f"/config/security/v1/security-rules/{rule_id}",
            params={"position": "pre"},  # pre is default
            json=expected_json,
        )
        assert updated_rule.id == rule_id

    def test_get_security_rule(
        self,
        load_env,
        mock_scm,
    ):
        # Mock the API client's get method
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "folder": "Shared",
            "description": "A test security rule",
            "action": "allow",
            "from": ["any"],
            "to": ["any"],
            "source": ["any"],
            "destination": ["any"],
            "application": ["any"],
            "service": ["any"],
        }
        mock_scm.get = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)

        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        security_rule = security_rules_client.get(rule_id)

        # Updated assertion to include position parameter
        mock_scm.get.assert_called_once_with(
            f"/config/security/v1/security-rules/{rule_id}",
            params={"position": "pre"},  # pre is default
        )

        assert isinstance(security_rule, SecurityRuleResponseModel)
        assert security_rule.id == rule_id

    def test_delete_security_rule(
        self,
        load_env,
        mock_scm,
    ):
        """Test deleting a security rule with default rulebase."""
        mock_scm.delete = MagicMock(return_value=None)
        security_rules_client = SecurityRule(mock_scm)

        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        security_rules_client.delete(rule_id)

        # Updated assertion to include position parameter
        mock_scm.delete.assert_called_once_with(
            f"/config/security/v1/security-rules/{rule_id}",
            params={"position": "pre"},  # pre is default
        )

    def test_security_rule_list_with_invalid_offset_limit(
        self,
        load_env,
        mock_scm,
    ):
        """
        Test that invalid offset and limit values raise ValueError.
        """
        # Create an instance of SecurityRule with the mocked Scm
        security_rules_client = SecurityRule(mock_scm)

        # Invalid offset
        with pytest.raises(ValueError) as exc_info:
            security_rules_client.list(
                folder="Shared",
                offset=-1,
            )
        assert "Offset must be a non-negative integer" in str(exc_info.value)

        # Invalid limit
        with pytest.raises(ValueError) as exc_info:
            security_rules_client.list(
                folder="Shared",
                limit=0,
            )
        assert "Limit must be a positive integer" in str(exc_info.value)

        # Both invalid
        with pytest.raises(ValueError) as exc_info:
            security_rules_client.list(
                folder="Shared",
                offset=-1,
                limit=-10,
            )
        assert (
            "Offset must be a non-negative integer. Limit must be a positive integer"
            in str(exc_info.value)
        )

    def test_security_rule_list_no_container_provided(
        self,
        load_env,
        mock_scm,
    ):
        """
        Test that providing no container raises ValidationError.
        """
        # Create an instance of SecurityRule with the mocked Scm
        security_rules_client = SecurityRule(mock_scm)

        # Call the list method without any container
        with pytest.raises(ValidationError) as exc_info:
            security_rules_client.list()

        # Assertions
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_security_rule_list_multiple_containers_provided(
        self,
        load_env,
        mock_scm,
    ):
        """
        Test that providing multiple containers raises ValidationError.
        """
        # Create an instance of SecurityRule with the mocked Scm
        security_rules_client = SecurityRule(mock_scm)

        # Call the list method with multiple containers
        with pytest.raises(ValidationError) as exc_info:
            security_rules_client.list(
                folder="Shared",
                snippet="TestSnippet",
            )

        # Assertions
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_security_rule_list_with_name_filter(
        self,
        load_env,
        mock_scm,
    ):
        """Test listing security rules with name filter and default rulebase."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "Allow_HTTP",
                    "folder": "Shared",
                    "action": "allow",
                }
            ],
            "offset": 0,
            "total": 1,
            "limit": 100,
        }
        mock_scm.get = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)

        security_rules_client.list(folder="Shared", name="Allow_HTTP")

        # Updated assertion to include position parameter
        expected_params = {
            "folder": "Shared",
            "name": "Allow_HTTP",
            "position": "pre",  # pre is default
        }
        mock_scm.get.assert_called_once_with(
            "/config/security/v1/security-rules",
            params=expected_params,
        )

    def test_security_rule_list_with_additional_filters(
        self,
        load_env,
        mock_scm,
    ):
        """Test listing security rules with additional filters and default rulebase."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "Allow_HTTP",
                    "folder": "Shared",
                    "action": "allow",
                    "source": ["10.0.0.0/24"],
                }
            ],
            "offset": 0,
            "total": 1,
            "limit": 100,
        }
        mock_scm.get = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)

        filters = {
            "folder": "Shared",
            "action": "allow",
            "source": "10.0.0.0/24",
        }
        security_rules = security_rules_client.list(**filters)

        # Updated assertion to include position parameter
        expected_params = {
            "folder": "Shared",
            "action": "allow",
            "source": "10.0.0.0/24",
            "position": "pre",  # pre is default
        }
        mock_scm.get.assert_called_once_with(
            "/config/security/v1/security-rules",
            params=expected_params,
        )

        assert len(security_rules) == 1
        assert security_rules[0].source == ["10.0.0.0/24"]

    def test_security_rule_list_with_offset_limit(
        self,
        load_env,
        mock_scm,
    ):
        """Test listing security rules with offset, limit, and default rulebase."""
        mock_response = {
            "data": [],
            "offset": 10,
            "total": 100,
            "limit": 20,
        }
        mock_scm.get = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)

        security_rules = security_rules_client.list(
            folder="Shared",
            offset=10,
            limit=20,
        )

        # Updated assertion to include position parameter
        expected_params = {
            "folder": "Shared",
            "offset": 10,
            "limit": 20,
            "position": "pre",  # pre is default
        }
        mock_scm.get.assert_called_once_with(
            "/config/security/v1/security-rules",
            params=expected_params,
        )

        # Since the data is empty, security_rules should be an empty list
        assert len(security_rules) == 0

    def test_invalid_rulebase_value(
        self,
        load_env,
        mock_scm,
    ):
        """Test that invalid rulebase values raise ValueError."""
        security_rules_client = SecurityRule(mock_scm)

        with pytest.raises(
            ValueError,
            match="rulebase must be either 'pre' or 'post'",
        ):
            security_rules_client.create(
                {
                    "name": "test",
                    "folder": "Shared",
                },
                rulebase="invalid",
            )

        with pytest.raises(
            ValueError,
            match="rulebase must be either 'pre' or 'post'",
        ):
            security_rules_client.list(
                folder="Shared",
                rulebase="invalid",
            )

    def test_update_security_rule_with_invalid_rulebase(
        self,
        load_env,
        mock_scm,
        security_rules_client,
    ):
        """Test that update() raises ValueError with invalid rulebase."""
        test_security_rule = SecurityRuleRequestFactory(name="UpdatedSecurityRule")
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = test_security_rule.model_dump(
            exclude_unset=True,
            by_alias=True,
        )
        update_data["id"] = rule_id  # Include 'id' in update_data

        # Ensure mock_scm.put is a MagicMock object
        mock_scm.put = MagicMock()

        with pytest.raises(ValueError, match="rulebase must be either 'pre' or 'post'"):
            security_rules_client.update(
                update_data,
                rulebase="invalid_value",
            )

        # Verify no API call was made
        mock_scm.put.assert_not_called()

    def test_update_security_rule_with_alternate_case(
        self,
        load_env,
        mock_scm,
    ):
        """Test that update() handles case-insensitive rulebase values."""
        test_security_rule = SecurityRuleRequestFactory(name="UpdatedSecurityRule")
        mock_response = test_security_rule.model_dump(
            exclude_unset=True,
            by_alias=True,
        )
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response["id"] = rule_id

        mock_scm.put = MagicMock(return_value=mock_response)
        security_rules_client = SecurityRule(mock_scm)
        update_data = test_security_rule.model_dump(
            exclude_unset=True,
            by_alias=True,
        )
        update_data["id"] = rule_id  # Include 'id' in update_data

        # Test with uppercase value
        updated_rule = security_rules_client.update(
            update_data,
            rulebase="PRE",
        )

        # Create a copy of update_data without 'id' for the expected JSON payload
        expected_json = update_data.copy()
        expected_json.pop("id")

        mock_scm.put.assert_called_once_with(
            f"/config/security/v1/security-rules/{rule_id}",
            params={"position": "pre"},
            json=expected_json,
        )
        assert updated_rule.id == rule_id

    def test_delete_security_rule_with_invalid_rulebase(
        self,
        load_env,
        mock_scm,
        security_rules_client,
    ):
        """Test that delete() raises ValueError with invalid rulebase."""

        # Ensure mock_scm.delete is a MagicMock object
        mock_scm.delete = MagicMock()

        rule_id = "123e4567-e89b-12d3-a456-426655440000"

        with pytest.raises(ValueError, match="rulebase must be either 'pre' or 'post'"):
            security_rules_client.delete(rule_id, rulebase="invalid_value")

        # Verify no API call was made
        mock_scm.delete.assert_not_called()

    def test_delete_security_rule_with_alternate_case(
        self,
        load_env,
        mock_scm,
    ):
        """Test that delete() handles case-insensitive rulebase values."""
        mock_scm.delete = MagicMock(return_value=None)
        security_rules_client = SecurityRule(mock_scm)
        rule_id = "123e4567-e89b-12d3-a456-426655440000"

        # Test with uppercase value
        security_rules_client.delete(rule_id, rulebase="POST")

        mock_scm.delete.assert_called_once_with(
            f"/config/security/v1/security-rules/{rule_id}",
            params={"position": "post"},
        )

    def test_get_security_rule_with_invalid_rulebase(
        self,
        load_env,
        mock_scm,
        security_rules_client,
    ):
        """Test that get() raises ValueError with invalid rulebase."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"

        # Ensure mock_scm.get is a MagicMock object
        mock_scm.get = MagicMock()

        with pytest.raises(ValueError, match="rulebase must be either 'pre' or 'post'"):
            security_rules_client.get(rule_id, rulebase="invalid_value")

        # Verify no API call was made
        mock_scm.get.assert_not_called()

    def test_get_security_rule_with_alternate_case(
        self,
        load_env,
        mock_scm,
        security_rules_client,
    ):
        """Test that get() handles case-insensitive rulebase values."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": rule_id,
            "name": "TestRule",
            "folder": "Shared",
            "action": "allow",
            "from": ["any"],
            "to": ["any"],
            "source": ["any"],
            "destination": ["any"],
            "application": ["any"],
            "service": ["any"],
        }

        # Ensure mock_scm.get is a MagicMock object
        mock_scm.get = MagicMock(return_value=mock_response)

        # Test with uppercase value
        security_rule = security_rules_client.get(rule_id, rulebase="POST")

        mock_scm.get.assert_called_once_with(
            f"/config/security/v1/security-rules/{rule_id}",
            params={"position": "post"},
        )

        assert isinstance(security_rule, SecurityRuleResponseModel)
        assert security_rule.id == rule_id


class TestSecurityRuleModels:
    """Test suite for SecurityRule model validations."""

    def test_create_security_rule_with_invalid_names(self):
        """
        Test creating security rules with invalid names that do not match the regex pattern.
        """
        # List of invalid names that include characters not allowed by the regex
        invalid_names = [
            "Invalid@Name",
            "Name!",
            "Name#",
            "Name$",
            "Name%",
            "Name^",
            "Name&",
            "Name*",
            "Name(",
            "Name)",
            "Name+",
            "Name=",
            "Name{",
            "Name}",
            "Name[",
            "Name]",
            "Name|",
            "Name\\",
            "Name/",
            "Name<",
            "Name>",
            "Name?",
            "Name~",
            "Name`",
            'Name"',
            "Name'",
            "Name:",
            "Name;",
        ]

        for name in invalid_names:
            # We also need to provide at least one container field to pass the model validation
            with pytest.raises(PydanticValidationError) as exc_info:
                SecurityRuleRequestModel(
                    name=name,
                    folder="test-folder",  # Added this to satisfy the container validation
                )

            errors = exc_info.value.errors()
            assert len(errors) >= 1, f"No validation errors found for name: {name}"

            name_errors = [error for error in errors if error["loc"] == ("name",)]
            assert (
                name_errors
            ), f"No validation error for 'name' field with value: {name}"

            error = name_errors[0]
            assert (
                error["type"] == "string_pattern_mismatch"
            ), f"Unexpected error type: {error['type']}"
            assert (
                "should match pattern" in error["msg"]
            ), f"Unexpected error message: {error['msg']}"

    def test_security_rule_response_model_invalid_uuid(self):
        """
        Test that providing an invalid UUID raises a validation error.
        """
        invalid_data = {
            "id": "invalid-uuid",
            "name": "TestRule",
            "folder": "Shared",
            "action": "allow",
            "from": ["zone1"],
            "to": ["zone2"],
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleResponseModel(**invalid_data)
        assert "Invalid UUID format for 'id'" in str(exc_info.value)

    def test_security_rule_request_model_no_container_provided(self):
        """
        Test that providing no container raises validation error.
        """
        data = {
            "name": "TestRule",
            "action": "allow",
            # No 'folder', 'snippet', or 'device' provided
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleRequestModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_security_rule_request_model_multiple_containers_provided(self):
        """
        Test that providing multiple containers raises validation error.
        """
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "snippet": "TestSnippet",
            # Multiple containers provided
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleRequestModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_ensure_list_of_strings_single_string(self):
        """
        Test that a single string is converted to a list containing that string.
        """
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "from": "zone1",  # single string
            "to": "zone2",  # single string
        }
        model = SecurityRuleRequestModel(**data)
        assert model.from_ == ["zone1"]
        assert model.to_ == ["zone2"]

    def test_ensure_list_of_strings_invalid_type(self):
        """
        Test that a non-string, non-list input raises ValueError.
        """
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "from": 123,  # invalid type
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleRequestModel(**data)
        assert "Value must be a list of strings" in str(exc_info.value)

    def test_ensure_list_of_strings_non_string_items(self):
        """
        Test that a list containing non-string items raises ValueError.
        """
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "from": ["zone1", 123],  # list with non-string item
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleRequestModel(**data)
        assert "All items must be strings" in str(exc_info.value)

    def test_ensure_unique_items(self):
        """
        Test that duplicate items in lists raise ValueError.
        """
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "from": ["zone1", "zone1"],  # duplicate item
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleRequestModel(**data)
        assert "List items must be unique" in str(exc_info.value)


class TestStringValidator:
    """Test suite for string_validator function."""

    def test_string_validator(self):
        """
        Test that string_validator raises ValueError for non-string inputs.
        """
        # Valid input
        assert string_validator("test") == "test"

        # Invalid input: integer
        with pytest.raises(ValueError) as exc_info:
            string_validator(123)
        assert "Must be a string" in str(exc_info.value)

        # Invalid input: None
        with pytest.raises(ValueError) as exc_info:
            string_validator(None)
        assert "Must be a string" in str(exc_info.value)


class TestProfileSetting:
    """Test suite for ProfileSetting validations."""

    def test_profile_setting_validate_unique_items(self):
        """
        Test that ProfileSetting raises ValueError when 'group' has duplicate items.
        """
        # Valid input
        ps = ProfileSetting(group=["group1", "group2"])
        assert ps.group == ["group1", "group2"]

        # Duplicate items in 'group'
        with pytest.raises(ValueError) as exc_info:
            ProfileSetting(group=["group1", "group1"])
        assert "List items in 'group' must be unique" in str(exc_info.value)


class TestSecurityRuleMoveModel:
    """Test suite for SecurityRuleMoveModel validation."""

    def test_validate_uuid_fields_none_value(self):
        """Test that None values are allowed and returned as-is."""
        model = SecurityRuleMoveModel(
            source_rule="123e4567-e89b-12d3-a456-426655440000",
            destination=RuleMoveDestination.TOP,
            rulebase=Rulebase.PRE,
            destination_rule=None,
        )
        assert model.destination_rule is None

    def test_validate_uuid_fields_valid_uuid(self):
        """Test that valid UUIDs are accepted."""
        valid_uuid = str(uuid.uuid4())
        model = SecurityRuleMoveModel(
            source_rule=valid_uuid,
            destination=RuleMoveDestination.TOP,
            rulebase=Rulebase.PRE,
        )
        assert model.source_rule == valid_uuid

    def test_validate_uuid_fields_invalid_uuid(self):
        """Test that invalid UUIDs raise ValueError."""
        with pytest.raises(ValueError, match="Field must be a valid UUID"):
            SecurityRuleMoveModel(
                source_rule="not-a-uuid",
                destination=RuleMoveDestination.TOP,
                rulebase=Rulebase.PRE,
            )

    def test_validate_uuid_fields_both_fields(self):
        """Test UUID validation on both source_rule and destination_rule fields."""
        valid_uuid1 = str(uuid.uuid4())
        valid_uuid2 = str(uuid.uuid4())
        model = SecurityRuleMoveModel(
            source_rule=valid_uuid1,
            destination=RuleMoveDestination.BEFORE,
            rulebase=Rulebase.PRE,
            destination_rule=valid_uuid2,
        )
        assert model.source_rule == valid_uuid1
        assert model.destination_rule == valid_uuid2

    def test_validate_move_configuration_before_with_destination_rule(self):
        """Test valid move configuration with BEFORE and destination_rule."""
        model = SecurityRuleMoveModel(
            source_rule=str(uuid.uuid4()),
            destination=RuleMoveDestination.BEFORE,
            rulebase=Rulebase.PRE,
            destination_rule=str(uuid.uuid4()),
        )
        assert model is not None  # Validates successful return of self

    def test_validate_move_configuration_after_with_destination_rule(self):
        """Test valid move configuration with AFTER and destination_rule."""
        model = SecurityRuleMoveModel(
            source_rule=str(uuid.uuid4()),
            destination=RuleMoveDestination.AFTER,
            rulebase=Rulebase.PRE,
            destination_rule=str(uuid.uuid4()),
        )
        assert model is not None  # Validates successful return of self

    def test_validate_move_configuration_before_without_destination_rule(self):
        """Test that BEFORE without destination_rule raises ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule is required when destination is 'before'",
        ):
            SecurityRuleMoveModel(
                source_rule=str(uuid.uuid4()),
                destination=RuleMoveDestination.BEFORE,
                rulebase=Rulebase.PRE,
            )

    def test_validate_move_configuration_after_without_destination_rule(self):
        """Test that AFTER without destination_rule raises ValueError."""
        with pytest.raises(
            ValueError, match="destination_rule is required when destination is 'after'"
        ):
            SecurityRuleMoveModel(
                source_rule=str(uuid.uuid4()),
                destination=RuleMoveDestination.AFTER,
                rulebase=Rulebase.PRE,
            )

    def test_validate_move_configuration_top_with_destination_rule(self):
        """Test that TOP with destination_rule raises ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'top'",
        ):
            SecurityRuleMoveModel(
                source_rule=str(uuid.uuid4()),
                destination=RuleMoveDestination.TOP,
                rulebase=Rulebase.PRE,
                destination_rule=str(uuid.uuid4()),
            )

    def test_validate_move_configuration_bottom_with_destination_rule(self):
        """Test that BOTTOM with destination_rule raises ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'bottom'",
        ):
            SecurityRuleMoveModel(
                source_rule=str(uuid.uuid4()),
                destination=RuleMoveDestination.BOTTOM,
                rulebase=Rulebase.PRE,
                destination_rule=str(uuid.uuid4()),
            )

    def test_validate_move_configuration_successful_return(self):
        """Test that validation returns self for valid configurations."""
        model_data = {
            "source_rule": str(uuid.uuid4()),
            "destination": RuleMoveDestination.TOP,
            "rulebase": Rulebase.PRE,
        }
        model = SecurityRuleMoveModel(**model_data)
        validated_model = model.validate_move_configuration()  # noqa
        assert validated_model == model


class TestSecurityRule:
    """Test suite for SecurityRule SDK."""

    @pytest.fixture
    def security_rule(self, mock_scm):
        """Create a SecurityRule instance with mock API client."""
        return SecurityRule(mock_scm)

    def test_move_model_instantiation(self, security_rule):
        """Test that move() correctly instantiates SecurityRuleMoveModel."""
        rule_id = str(uuid.uuid4())
        move_data = {
            "destination": "before",
            "rulebase": "pre",
            "destination_rule": str(uuid.uuid4()),
        }

        security_rule.move(rule_id, move_data)

        # Verify the model was created with correct data
        expected_model_data = {
            "source_rule": rule_id,
            **move_data,
        }
        actual_model = SecurityRuleMoveModel(**expected_model_data)
        assert actual_model.source_rule == rule_id
        assert actual_model.destination == RuleMoveDestination.BEFORE
        assert actual_model.rulebase == Rulebase.PRE
        assert actual_model.destination_rule == move_data["destination_rule"]

    def test_move_payload_generation(self, security_rule):
        """Test that move() generates correct payload from model."""
        rule_id = str(uuid.uuid4())
        dest_rule_id = str(uuid.uuid4())
        move_data = {
            "destination": "before",
            "rulebase": "pre",
            "destination_rule": dest_rule_id,
        }

        # Patch post method to capture payload
        with patch.object(security_rule.api_client, "post") as mock_post:
            security_rule.move(rule_id, move_data)

            # Verify payload structure
            expected_payload = {
                "source_rule": rule_id,
                "destination": "before",
                "rulebase": "pre",
                "destination_rule": dest_rule_id,
            }
            mock_post.assert_called_once()
            actual_payload = mock_post.call_args[1]["json"]
            assert actual_payload == expected_payload

    def test_move_endpoint_construction(self, security_rule):
        """Test that move() constructs correct endpoint URL."""
        rule_id = str(uuid.uuid4())
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        # Patch post method to capture endpoint
        with patch.object(security_rule.api_client, "post") as mock_post:
            security_rule.move(rule_id, move_data)

            # Verify endpoint construction
            expected_endpoint = f"{security_rule.ENDPOINT}/{rule_id}:move"
            mock_post.assert_called_once()
            actual_endpoint = mock_post.call_args[0][0]
            assert actual_endpoint == expected_endpoint

    def test_move_api_call(self, security_rule):
        """Test that move() makes correct API call."""
        rule_id = str(uuid.uuid4())
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        # Test API call
        with patch.object(security_rule.api_client, "post") as mock_post:
            security_rule.move(rule_id, move_data)

            # Verify API call was made with correct arguments
            mock_post.assert_called_once()
            assert mock_post.call_args[1]["json"]["source_rule"] == rule_id
            assert mock_post.call_args[1]["json"]["destination"] == "top"
            assert mock_post.call_args[1]["json"]["rulebase"] == "pre"


class TestSecurityRuleFetch:
    """Tests for the fetch method of SecurityRule."""

    @pytest.fixture(autouse=True)
    def setup_method(self, load_env, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        # Create new MagicMock instances for each HTTP method
        self.mock_scm.get = MagicMock()
        self.security_rules_client = SecurityRule(self.mock_scm)

    def test_fetch_security_rule_success(self):
        """
        Test successful fetch of a security rule.

        **Objective:** Test fetching a security rule with all fields populated.
        """
        mock_response = {
            "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
            "name": "Allow_HTTP",
            "folder": "Shared",
            "action": "allow",
            "from": ["zone1"],
            "to": ["zone2"],
            "source": ["10.0.0.0/24"],
            "destination": ["0.0.0.0/0"],
            "application": ["web-browsing"],
            "service": ["application-default"],
            "log_setting": "Cortex Data Lake",
            "description": "Allow HTTP traffic",
        }
        self.mock_scm.get.return_value = mock_response

        result = self.security_rules_client.fetch(name="Allow_HTTP", folder="Shared")

        self.mock_scm.get.assert_called_once_with(
            "/config/security/v1/security-rules",
            params={"folder": "Shared", "name": "Allow_HTTP"},
        )
        assert isinstance(result, dict)
        assert result["name"] == "Allow_HTTP"
        assert result["action"] == "allow"
        assert result["from_"] == ["zone1"]
        assert result["to_"] == ["zone2"]

    def test_fetch_security_rule_validations(self):
        """
        Test fetch method parameter validations.

        **Objective:** Test all validation scenarios for fetch parameters.
        """
        # Test empty name
        with pytest.raises(ValidationError) as exc_info:
            self.security_rules_client.fetch(name="", folder="Shared")
        assert "Parameter 'name' must be provided for fetch method." in str(
            exc_info.value
        )

        # Test no container provided
        with pytest.raises(ValidationError) as exc_info:
            self.security_rules_client.fetch(name="Allow_HTTP")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(ValidationError) as exc_info:
            self.security_rules_client.fetch(
                name="Allow_HTTP", folder="Shared", snippet="TestSnippet"
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_fetch_security_rule_with_different_containers(self):
        """
        Test fetch with different container types.

        **Objective:** Test fetch using different container parameters.
        """
        mock_response = {
            "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
            "name": "Allow_HTTP",
            "action": "allow",
        }
        self.mock_scm.get.return_value = mock_response

        # Test with folder
        self.security_rules_client.fetch(name="Allow_HTTP", folder="Shared")
        self.mock_scm.get.assert_called_with(
            "/config/security/v1/security-rules",
            params={"folder": "Shared", "name": "Allow_HTTP"},
        )

        # Test with snippet
        self.security_rules_client.fetch(name="Allow_HTTP", snippet="TestSnippet")
        self.mock_scm.get.assert_called_with(
            "/config/security/v1/security-rules",
            params={"snippet": "TestSnippet", "name": "Allow_HTTP"},
        )

        # Test with device
        self.security_rules_client.fetch(name="Allow_HTTP", device="TestDevice")
        self.mock_scm.get.assert_called_with(
            "/config/security/v1/security-rules",
            params={"device": "TestDevice", "name": "Allow_HTTP"},
        )

    def test_fetch_security_rule_with_filters(self):
        """
        Test fetch with additional filters.

        **Objective:** Test handling of additional filter parameters.
        """
        mock_response = {
            "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
            "name": "Allow_HTTP",
            "action": "allow",
        }
        self.mock_scm.get.return_value = mock_response

        # Test with allowed and excluded filters
        result = self.security_rules_client.fetch(
            name="Allow_HTTP",
            folder="Shared",
            custom_filter="value",
            types=["excluded"],
            values=["excluded"],
            names=["excluded"],
            tags=["excluded"],
        )

        # Verify only allowed filters are included
        self.mock_scm.get.assert_called_with(
            "/config/security/v1/security-rules",
            params={"folder": "Shared", "name": "Allow_HTTP", "custom_filter": "value"},
        )
        assert isinstance(result, dict)
        assert result["name"] == "Allow_HTTP"

    def test_fetch_security_rule_response_handling(self):
        """
        Test fetch response handling.

        **Objective:** Test handling of different response scenarios.
        """
        # Test with all fields present
        complete_response = {
            "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
            "name": "Allow_HTTP",
            "folder": "Shared",
            "description": "Allow HTTP traffic",
            "action": "allow",
            "from": ["zone1"],
            "to": ["zone2"],
            "source": ["any"],
            "destination": ["any"],
            "application": ["web-browsing"],
            "service": ["application-default"],
        }
        self.mock_scm.get.return_value = complete_response
        result = self.security_rules_client.fetch(name="Allow_HTTP", folder="Shared")
        assert result["description"] == "Allow HTTP traffic"
        assert result["application"] == ["web-browsing"]

        # Test with minimal fields
        minimal_response = {
            "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
            "name": "Allow_HTTP",
            "folder": "Shared",
            "action": "allow",
        }
        self.mock_scm.get.return_value = minimal_response
        result = self.security_rules_client.fetch(name="Allow_HTTP", folder="Shared")
        assert "description" not in result
        assert "application" not in result

    def test_fetch_security_rule_not_found(self):
        """
        Test fetch when the security rule is not found.

        **Objective:** Test handling when the API returns an error or empty response.
        """
        # Simulate a NotFoundError from the API client
        from scm.exceptions import NotFoundError

        self.mock_scm.get.side_effect = NotFoundError("Security rule not found")

        with pytest.raises(NotFoundError) as exc_info:
            self.security_rules_client.fetch(name="NonExistentRule", folder="Shared")

        assert "Security rule not found" in str(exc_info.value)

    def test_fetch_security_rule_api_error(self):
        """
        Test fetch when the API client raises an unexpected error.

        **Objective:** Ensure that unexpected API errors are propagated.
        """
        from scm.exceptions import APIError

        self.mock_scm.get.side_effect = APIError("API is unavailable")

        with pytest.raises(APIError) as exc_info:
            self.security_rules_client.fetch(name="Allow_HTTP", folder="Shared")

        assert "API is unavailable" in str(exc_info.value)
