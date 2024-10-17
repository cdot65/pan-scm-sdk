# tests/test_anti_spyware_profiles.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.anti_spyware_profiles import AntiSpywareProfile
from scm.exceptions import ValidationError
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareProfileRequestModel,
    AntiSpywareProfileResponseModel,
    RuleRequest,
    RuleResponse,
    ThreatExceptionRequest,
    ThreatExceptionResponse,
    Severity,
    Category,
    PacketCapture,
    ActionRequest,
    ActionResponse,
)
from typing import List


def test_list_anti_spyware_profiles(load_env, mock_scm):
    """
    Test listing anti-spyware profiles.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "123e4567-e89b-12d3-a456-426655440000",
                "name": "TestProfile1",
                "folder": "Prisma Access",
                "description": "A test anti-spyware profile",
                "rules": [
                    {
                        "name": "TestRule1",
                        "severity": ["critical", "high"],
                        "category": "spyware",
                        "threat_name": "any",
                        "packet_capture": "disable",
                        "action": {"alert": {}},
                    }
                ],
                "threat_exception": [
                    {
                        "name": "TestException1",
                        "action": {"allow": {}},
                        "packet_capture": "single-packet",
                        "exempt_ip": [{"name": "192.168.1.1"}],
                        "notes": "Test note",
                    }
                ],
            },
            {
                "id": "223e4567-e89b-12d3-a456-426655440001",
                "name": "TestProfile2",
                "folder": "Prisma Access",
                "rules": [],
                "threat_exception": [],
            },
        ],
        "offset": 0,
        "total": 2,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Call the list method
    profiles = anti_spyware_profile_client.list(folder="Prisma Access")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/anti-spyware-profiles", params={"folder": "Prisma Access"}
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 2
    assert isinstance(profiles[0], AntiSpywareProfileResponseModel)
    assert profiles[0].name == "TestProfile1"
    assert profiles[0].description == "A test anti-spyware profile"
    assert profiles[0].rules[0].name == "TestRule1"
    assert profiles[0].rules[0].severity == [Severity.critical, Severity.high]
    assert profiles[0].rules[0].category == Category.spyware
    assert profiles[0].rules[0].action.get_action_name() == "alert"
    assert profiles[0].threat_exception[0].name == "TestException1"
    assert profiles[0].threat_exception[0].action.get_action_name() == "allow"
    assert profiles[0].threat_exception[0].exempt_ip[0].name == "192.168.1.1"


def test_create_anti_spyware_profile(load_env, mock_scm):
    """
    Test creating an anti-spyware profile.
    """
    # Prepare test data
    test_profile_data = {
        "name": "NewTestProfile",
        "folder": "Prisma Access",
        "description": "A new test anti-spyware profile",
        "rules": [
            {
                "name": "NewRule",
                "severity": ["medium", "low"],
                "category": "adware",
                "packet_capture": "single-packet",
                "action": "alert",
            }
        ],
        "threat_exception": [
            {
                "name": "NewException",
                "action": "allow",
                "packet_capture": "disable",
                "exempt_ip": [{"name": "10.0.0.1"}],
                "notes": "Exception note",
            }
        ],
    }

    # Expected payload after model processing
    expected_payload = {
        "name": "NewTestProfile",
        "folder": "Prisma Access",
        "description": "A new test anti-spyware profile",
        "rules": [
            {
                "name": "NewRule",
                "severity": ["medium", "low"],
                "category": "adware",
                "packet_capture": "single-packet",
                "action": {"alert": {}},
            }
        ],
        "threat_exception": [
            {
                "name": "NewException",
                "action": {"allow": {}},
                "packet_capture": "disable",
                "exempt_ip": [{"name": "10.0.0.1"}],
                "notes": "Exception note",
            }
        ],
    }

    # Mock response from the API client
    mock_response = expected_payload.copy()
    mock_response["id"] = "333e4567-e89b-12d3-a456-426655440002"  # Mocked ID

    # Mock the API client's post method
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Call the create method
    created_profile = anti_spyware_profile_client.create(test_profile_data)

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/security/v1/anti-spyware-profiles",
        json=expected_payload,
    )
    assert isinstance(created_profile, AntiSpywareProfileResponseModel)
    assert created_profile.id == "333e4567-e89b-12d3-a456-426655440002"
    assert created_profile.name == "NewTestProfile"
    assert created_profile.rules[0].name == "NewRule"
    assert created_profile.rules[0].action.get_action_name() == "alert"
    assert created_profile.threat_exception[0].name == "NewException"


def test_get_anti_spyware_profile(load_env, mock_scm):
    """
    Test retrieving an anti-spyware profile by ID.
    """
    # Mock response from the API client
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    mock_response = {
        "id": profile_id,
        "name": "TestProfile",
        "folder": "Prisma Access",
        "description": "A test anti-spyware profile",
        "rules": [],
        "threat_exception": [],
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Call the get method
    profile = anti_spyware_profile_client.get(profile_id)

    # Assertions
    mock_scm.get.assert_called_once_with(
        f"/config/security/v1/anti-spyware-profiles/{profile_id}"
    )
    assert isinstance(profile, AntiSpywareProfileResponseModel)
    assert profile.id == profile_id
    assert profile.name == "TestProfile"
    assert profile.description == "A test anti-spyware profile"


def test_update_anti_spyware_profile(load_env, mock_scm):
    """
    Test updating an anti-spyware profile.
    """
    # Prepare test data
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    update_data = {
        "name": "UpdatedProfile",
        "folder": "Prisma Access",
        "description": "An updated anti-spyware profile",
        "rules": [
            {
                "name": "UpdatedRule",
                "severity": ["high"],
                "category": "botnet",
                "packet_capture": "extended-capture",
                "action": {"block_ip": {"track_by": "source", "duration": 3600}},
            }
        ],
        "threat_exception": [],
    }

    # Expected payload after model processing
    expected_payload = {
        "name": "UpdatedProfile",
        "folder": "Prisma Access",
        "description": "An updated anti-spyware profile",
        "rules": [
            {
                "name": "UpdatedRule",
                "severity": ["high"],
                "category": "botnet",
                "packet_capture": "extended-capture",
                "action": {"block_ip": {"track_by": "source", "duration": 3600}},
            }
        ],
        "threat_exception": [],
    }

    # Mock response from the API client
    mock_response = expected_payload.copy()
    mock_response["id"] = profile_id

    # Mock the API client's put method
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Call the update method
    updated_profile = anti_spyware_profile_client.update(profile_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/security/v1/anti-spyware-profiles/{profile_id}",
        json=expected_payload,
    )
    assert isinstance(updated_profile, AntiSpywareProfileResponseModel)
    assert updated_profile.id == profile_id
    assert updated_profile.name == "UpdatedProfile"
    assert updated_profile.description == "An updated anti-spyware profile"
    assert updated_profile.rules[0].action.get_action_name() == "block_ip"


def test_delete_anti_spyware_profile(load_env, mock_scm):
    """
    Test deleting an anti-spyware profile.
    """
    # Prepare test data
    profile_id = "123e4567-e89b-12d3-a456-426655440000"

    # Mock the API client's delete method
    mock_scm.delete = MagicMock(return_value=None)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Call the delete method
    anti_spyware_profile_client.delete(profile_id)

    # Assertions
    mock_scm.delete.assert_called_once_with(
        f"/config/security/v1/anti-spyware-profiles/{profile_id}"
    )


def test_anti_spyware_profile_list_validation_error(load_env, mock_scm):
    """
    Test validation error when listing with multiple containers.
    """
    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(ValidationError) as exc_info:
        anti_spyware_profile_client.list(folder="Shared", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_anti_spyware_profile_request_model_validation_errors():
    """
    Test validation errors in AntiSpywareProfileRequestModel.
    """
    # No container provided
    data_no_container = {
        "name": "InvalidProfile",
        "rules": [],
    }
    with pytest.raises(ValueError) as exc_info:
        AntiSpywareProfileRequestModel(**data_no_container)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Multiple containers provided
    data_multiple_containers = {
        "name": "InvalidProfile",
        "folder": "Shared",
        "device": "Device1",
        "rules": [],
    }
    with pytest.raises(ValueError) as exc_info:
        AntiSpywareProfileRequestModel(**data_multiple_containers)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Invalid action in RuleRequest
    data_invalid_action = {
        "name": "InvalidProfile",
        "folder": "Shared",
        "rules": [
            {
                "name": "InvalidRule",
                "severity": ["high"],
                "category": "botnet",
                "action": {},  # Empty action dictionary
            }
        ],
    }
    with pytest.raises(ValueError) as exc_info:
        AntiSpywareProfileRequestModel(**data_invalid_action)
    assert "Exactly one action must be provided in 'action' field." in str(
        exc_info.value
    )

    # Invalid UUID in id field (for response model)
    data_invalid_id = {
        "id": "invalid-uuid",
        "name": "TestProfile",
        "folder": "Shared",
        "rules": [],
    }
    with pytest.raises(ValueError) as exc_info:
        AntiSpywareProfileResponseModel(**data_invalid_id)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_rule_request_model_validation():
    """
    Test validation in RuleRequest model.
    """
    # Invalid severity
    data_invalid_severity = {
        "name": "TestRule",
        "severity": ["nonexistent_severity"],
        "category": "spyware",
        "action": "alert",
    }
    with pytest.raises(ValueError) as exc_info:
        RuleRequest(**data_invalid_severity)
    assert "1 validation error for RuleRequest" in str(exc_info.value)

    # Missing action
    data_missing_action = {
        "name": "TestRule",
        "severity": ["critical"],
        "category": "spyware",
    }
    rule = RuleRequest(**data_missing_action)
    assert rule.action is None


def test_threat_exception_request_model_validation():
    """
    Test validation in ThreatExceptionRequest model.
    """
    # Invalid packet_capture
    data_invalid_packet_capture = {
        "name": "TestException",
        "action": "alert",
        "packet_capture": "invalid_option",
    }
    with pytest.raises(ValueError) as exc_info:
        ThreatExceptionRequest(**data_invalid_packet_capture)
    assert "1 validation error for ThreatExceptionRequest" in str(exc_info.value)

    # Missing action
    data_missing_action = {
        "name": "TestException",
        "packet_capture": "disable",
    }
    with pytest.raises(Exception) as exc_info:
        ThreatExceptionRequest(**data_missing_action)
    # assert isinstance(exc_info.value, ValidationError)
    assert "1 validation error for ThreatExceptionRequest" in str(exc_info.value)
    assert "action\n  Field required" in str(exc_info.value)


def test_list_anti_spyware_profiles_with_pagination(load_env, mock_scm):
    """
    Test listing anti-spyware profiles with pagination parameters.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "223e4567-e89b-12d3-a456-426655440001",
                "name": "TestProfile2",
                "folder": "Prisma Access",
                "rules": [],
                "threat_exception": [],
            },
        ],
        "offset": 1,
        "total": 2,
        "limit": 1,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Call the list method with pagination parameters
    profiles = anti_spyware_profile_client.list(
        folder="Prisma Access", offset=1, limit=1
    )

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/anti-spyware-profiles",
        params={"folder": "Prisma Access", "offset": 1, "limit": 1},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 1
    assert profiles[0].name == "TestProfile2"
    assert profiles[0].id == "223e4567-e89b-12d3-a456-426655440001"


def test_list_anti_spyware_profiles_with_name_filter(load_env, mock_scm):
    """
    Test listing anti-spyware profiles with name filter.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "223e4567-e89b-12d3-a456-426655440001",
                "name": "SpecificProfile",
                "folder": "Prisma Access",
                "rules": [],
                "threat_exception": [],
            },
        ],
        "offset": 0,
        "total": 1,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Call the list method with name filter
    profiles = anti_spyware_profile_client.list(
        folder="Prisma Access", name="SpecificProfile"
    )

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/anti-spyware-profiles",
        params={"folder": "Prisma Access", "name": "SpecificProfile"},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 1
    assert profiles[0].name == "SpecificProfile"
    assert profiles[0].id == "223e4567-e89b-12d3-a456-426655440001"


def test_list_anti_spyware_profiles_with_all_parameters(load_env, mock_scm):
    """
    Test listing anti-spyware profiles with all optional parameters.
    """
    # Mock response from the API client
    mock_response = {
        "data": [],
        "offset": 10,
        "total": 2,
        "limit": 5,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Call the list method with all optional parameters
    profiles = anti_spyware_profile_client.list(
        folder="Prisma Access", name="TestProfile", offset=10, limit=5
    )

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/anti-spyware-profiles",
        params={
            "folder": "Prisma Access",
            "name": "TestProfile",
            "offset": 10,
            "limit": 5,
        },
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 0  # As per the mocked response data


def test_anti_spyware_profile_list_with_invalid_pagination(load_env, mock_scm):
    """
    Test validation error when invalid pagination parameters are provided.
    """
    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = AntiSpywareProfile(mock_scm)

    # Attempt to call the list method with invalid pagination parameters
    with pytest.raises(ValueError) as exc_info:
        anti_spyware_profile_client.list(
            folder="Prisma Access",
            offset=-1,
            limit=0,
        )

    # Assertions
    assert "Offset must be a non-negative integer" in str(exc_info.value)
    assert "Limit must be a positive integer" in str(exc_info.value)


def test_action_request_check_and_transform_action():
    # Test string input
    action = ActionRequest("alert")
    assert action.root == {"alert": {}}

    # Test dict input
    action = ActionRequest({"drop": {}})
    assert action.root == {"drop": {}}

    # Test invalid input type
    with pytest.raises(
        ValueError, match="Invalid action format; must be a string or dict."
    ):
        ActionRequest(123)

    # Test multiple actions
    with pytest.raises(
        ValueError, match="Exactly one action must be provided in 'action' field."
    ):
        ActionRequest({"alert": {}, "drop": {}})

    # Test empty dict
    with pytest.raises(
        ValueError, match="Exactly one action must be provided in 'action' field."
    ):
        ActionRequest({})


def test_action_request_get_action_name():
    action = ActionRequest("alert")
    assert action.get_action_name() == "alert"

    action = ActionRequest({"drop": {}})
    assert action.get_action_name() == "drop"


def test_action_response_check_action():
    # Test string input
    action = ActionResponse("alert")
    assert action.root == {"alert": {}}

    # Test dict input
    action = ActionResponse({"drop": {}})
    assert action.root == {"drop": {}}

    # Test invalid input type
    with pytest.raises(
        ValueError, match="Invalid action format; must be a string or dict."
    ):
        ActionResponse(123)

    # Test multiple actions
    with pytest.raises(
        ValueError, match="At most one action must be provided in 'action' field."
    ):
        ActionResponse({"alert": {}, "drop": {}})

    # Test empty dict (should be allowed for ActionResponse)
    action = ActionResponse({})
    assert action.root == {}


def test_action_response_get_action_name():
    action = ActionResponse("alert")
    assert action.get_action_name() == "alert"

    action = ActionResponse({"drop": {}})
    assert action.get_action_name() == "drop"

    action = ActionResponse({})
    assert action.get_action_name() == "unknown"
