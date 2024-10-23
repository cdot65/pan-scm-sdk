# tests/test_security_rules.py
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError as PydanticValidationError
from scm.exceptions import ValidationError
from scm.models.security.security_rules import (
    SecurityRuleRequestModel,
    SecurityRuleResponseModel,
    ProfileSetting,
    string_validator,
)
from scm.config.security import SecurityRule
from tests.factories import SecurityRuleFactory


def test_list_security_rules(load_env, mock_scm):
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

    # Mock the get method on the Scm instance
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Call the list method
    security_rules = security_rules_client.list(folder="All")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/security-rules", params={"folder": "All"}
    )
    assert isinstance(security_rules, list)
    assert isinstance(security_rules[0], SecurityRuleResponseModel)
    assert len(security_rules) == 24

    assert security_rules[0].name == "default"
    assert security_rules[0].id == "721c065c-0966-4aab-84ae-d70f55e9c5a7"


def test_create_security_rule(load_env, mock_scm):
    """
    Test creating a security rule.
    """
    # Create a test SecurityRuleRequestModel instance using Factory Boy
    test_security_rule = SecurityRuleFactory()

    # Define the mock response for the post method
    mock_response = test_security_rule.model_dump(
        exclude_none=True,  # Use exclude_none instead of exclude_unset
        by_alias=True,
    )
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID

    # Mock the post method on the Scm instance
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Call the create method
    created_rule = security_rules_client.create(
        test_security_rule.model_dump(
            exclude_none=True,  # Use exclude_none here as well
            by_alias=True,
        )
    )

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/security/v1/security-rules",
        json=test_security_rule.model_dump(
            exclude_none=True,  # Ensure consistency in model_dump calls
            by_alias=True,
        ),
    )
    assert created_rule.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_rule.name == test_security_rule.name
    assert created_rule.description == test_security_rule.description
    assert created_rule.folder == test_security_rule.folder


def test_create_security_rule_with_invalid_names(load_env, mock_scm):
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
        assert name_errors, f"No validation error for 'name' field with value: {name}"

        error = name_errors[0]
        assert (
            error["type"] == "string_pattern_mismatch"
        ), f"Unexpected error type: {error['type']}"
        assert (
            "should match pattern" in error["msg"]
        ), f"Unexpected error message: {error['msg']}"


def test_update_security_rule(load_env, mock_scm):
    """
    Test updating a security rule.
    """
    # Create a test SecurityRuleRequestModel instance using Factory Boy
    test_security_rule = SecurityRuleFactory(name="UpdatedSecurityRule")

    # Define the mock response for the put method
    mock_response = test_security_rule.model_dump(
        exclude_unset=True,
        by_alias=True,
    )
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID

    # Mock the put method on the Scm instance
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Prepare data for update
    rule_id = "123e4567-e89b-12d3-a456-426655440000"
    update_data = test_security_rule.model_dump(
        exclude_unset=True,
        by_alias=True,
    )

    # Call the update method
    updated_rule = security_rules_client.update(rule_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/security/v1/security-rules/{rule_id}",
        json=update_data,
    )
    assert updated_rule.id == rule_id
    assert updated_rule.name == test_security_rule.name
    assert updated_rule.description == test_security_rule.description
    assert updated_rule.folder == test_security_rule.folder
    # Add other assertions as needed


def test_get_security_rule(load_env, mock_scm):
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

    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Call the get method
    rule_id = "123e4567-e89b-12d3-a456-426655440000"
    security_rule = security_rules_client.get(rule_id)

    # Assertions
    mock_scm.get.assert_called_once_with(
        f"/config/security/v1/security-rules/{rule_id}"
    )
    assert isinstance(security_rule, SecurityRuleResponseModel)
    assert security_rule.id == rule_id
    assert security_rule.name == "TestRule"
    assert security_rule.description == "A test security rule"
    assert security_rule.action == "allow"
    assert security_rule.from_ == ["any"]
    assert security_rule.to_ == ["any"]
    # Add other assertions as needed


def test_delete_security_rule(load_env, mock_scm):
    """
    Test deleting a security rule.
    """
    # Mock the delete method on the Scm instance
    mock_scm.delete = MagicMock(return_value=None)

    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Call the delete method
    rule_id = "123e4567-e89b-12d3-a456-426655440000"
    security_rules_client.delete(rule_id)

    # Assertions
    mock_scm.delete.assert_called_once_with(
        f"/config/security/v1/security-rules/{rule_id}"
    )


def test_security_rule_list_with_invalid_offset_limit(load_env, mock_scm):
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


def test_security_rule_list_no_container_provided(load_env, mock_scm):
    """
    Test that providing no container raises ValidationError.
    """
    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Call the list method without any container
    with pytest.raises(ValidationError) as exc_info:
        security_rules_client.list()

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_security_rule_list_multiple_containers_provided(load_env, mock_scm):
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
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_security_rule_response_model_invalid_uuid():
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


def test_security_rule_request_model_no_container_provided():
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
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_security_rule_request_model_multiple_containers_provided():
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
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_security_rule_list_with_name_filter(load_env, mock_scm):
    """
    Test listing security rules with a name filter.
    """
    # Mock the API client's get method
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

    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Call the list method with name filter
    security_rules = security_rules_client.list(folder="Shared", name="Allow_HTTP")

    # Assertions
    expected_params = {
        "folder": "Shared",
        "name": "Allow_HTTP",
    }
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/security-rules",
        params=expected_params,
    )
    assert len(security_rules) == 1
    assert security_rules[0].name == "Allow_HTTP"


def test_security_rule_list_with_additional_filters(load_env, mock_scm):
    """
    Test listing security rules with additional filters.
    """
    # Mock the API client's get method
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

    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Call the list method with additional filters
    filters = {
        "folder": "Shared",
        "action": "allow",
        "source": "10.0.0.0/24",
    }
    security_rules = security_rules_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "action": "allow",
        "source": "10.0.0.0/24",
    }
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/security-rules",
        params=expected_params,
    )
    assert len(security_rules) == 1
    assert security_rules[0].source == ["10.0.0.0/24"]


def test_security_rule_list_with_offset_limit(load_env, mock_scm):
    """
    Test listing security rules with offset and limit parameters.
    """
    # Mock the API client's get method
    mock_response = {
        "data": [],
        "offset": 10,
        "total": 100,
        "limit": 20,
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of SecurityRule with the mocked Scm
    security_rules_client = SecurityRule(mock_scm)

    # Call the list method with offset and limit
    security_rules = security_rules_client.list(folder="Shared", offset=10, limit=20)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "offset": 10,
        "limit": 20,
    }
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/security-rules",
        params=expected_params,
    )
    # Since the data is empty, security_rules should be an empty list
    assert len(security_rules) == 0


def test_string_validator():
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


def test_profile_setting_validate_unique_items():
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


def test_ensure_list_of_strings_single_string():
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


def test_ensure_list_of_strings_invalid_type():
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


def test_ensure_list_of_strings_non_string_items():
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


def test_ensure_unique_items():
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
