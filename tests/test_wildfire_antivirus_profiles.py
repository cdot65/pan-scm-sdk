# tests/test_wildfire_antivirus_profiles.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.wildfire_antivirus_profile import WildfireAntivirusProfile
from scm.exceptions import ValidationError
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAntivirusProfileRequestModel,
    WildfireAntivirusProfileResponseModel,
    RuleRequest,
    Analysis,
    Direction,
)


def test_list_wildfire_antivirus_profiles(load_env, mock_scm):
    """
    Test listing wildfire antivirus profiles.
    """
    # Mock response from the API client
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
                "description": "Best practice antivirus and wildfire analysis security profile",
            },
        ],
        "offset": 0,
        "total": 2,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of WildfireAntivirusProfile with the mocked Scm
    wf_av_profile_client = WildfireAntivirusProfile(mock_scm)

    # Call the list method
    profiles = wf_av_profile_client.list(folder="All")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/wildfire-anti-virus-profiles", params={"folder": "All"}
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 2
    assert isinstance(profiles[0], WildfireAntivirusProfileResponseModel)
    assert profiles[0].name == "web-security-default"
    assert profiles[0].rules[0].name == "default-fawkes"
    assert profiles[0].rules[0].direction == Direction.both
    assert profiles[0].rules[0].file_type == ["any"]
    assert profiles[0].rules[0].application == ["any"]
    assert profiles[1].description == (
        "Best practice antivirus and wildfire analysis security profile"
    )


def test_create_wildfire_antivirus_profile(load_env, mock_scm):
    """
    Test creating a wildfire antivirus profile.
    """
    # Prepare test data
    test_profile_data = {
        "name": "NewWFProfile",
        "folder": "All",
        "description": "A new test wildfire antivirus profile",
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

    # Expected payload after model processing
    expected_payload = test_profile_data.copy()

    # Mock response from the API client
    mock_response = expected_payload.copy()
    mock_response["id"] = "333e4567-e89b-12d3-a456-426655440002"  # Mocked ID

    # Mock the API client's post method
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of WildfireAntivirusProfile with the mocked Scm
    wf_av_profile_client = WildfireAntivirusProfile(mock_scm)

    # Call the create method
    created_profile = wf_av_profile_client.create(test_profile_data)

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/security/v1/wildfire-anti-virus-profiles",
        json=expected_payload,
    )
    assert isinstance(created_profile, WildfireAntivirusProfileResponseModel)
    assert created_profile.id == "333e4567-e89b-12d3-a456-426655440002"
    assert created_profile.name == "NewWFProfile"
    assert created_profile.rules[0].name == "NewRule"
    assert created_profile.rules[0].analysis == Analysis.public_cloud
    assert created_profile.rules[0].direction == Direction.both
    assert created_profile.mlav_exception[0].name == "Exception1"
    assert created_profile.threat_exception[0].name == "ThreatException1"


def test_get_wildfire_antivirus_profile(load_env, mock_scm):
    """
    Test retrieving a wildfire antivirus profile by ID.
    """
    # Mock response from the API client
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    mock_response = {
        "id": profile_id,
        "name": "TestProfile",
        "folder": "All",
        "description": "A test wildfire antivirus profile",
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

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of WildfireAntivirusProfile with the mocked Scm
    wf_av_profile_client = WildfireAntivirusProfile(mock_scm)

    # Call the get method
    profile = wf_av_profile_client.get(profile_id)

    # Assertions
    mock_scm.get.assert_called_once_with(
        f"/config/security/v1/wildfire-anti-virus-profiles/{profile_id}"
    )
    assert isinstance(profile, WildfireAntivirusProfileResponseModel)
    assert profile.id == profile_id
    assert profile.name == "TestProfile"
    assert profile.description == "A test wildfire antivirus profile"
    assert profile.rules[0].name == "TestRule"
    assert profile.rules[0].direction == Direction.download
    assert profile.rules[0].analysis == Analysis.private_cloud


def test_update_wildfire_antivirus_profile(load_env, mock_scm):
    """
    Test updating a wildfire antivirus profile.
    """
    # Prepare test data
    profile_id = "123e4567-e89b-12d3-a456-426655440000"
    update_data = {
        "name": "UpdatedProfile",
        "folder": "All",
        "description": "An updated wildfire antivirus profile",
        "rules": [
            {
                "name": "UpdatedRule",
                "direction": "upload",
                "application": ["app3"],
                "file_type": ["docx"],
            }
        ],
        "packet_capture": False,
    }

    # Expected payload after model processing
    expected_payload = update_data.copy()

    # Mock response from the API client
    mock_response = expected_payload.copy()
    mock_response["id"] = profile_id

    # Mock the API client's put method
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of WildfireAntivirusProfile with the mocked Scm
    wf_av_profile_client = WildfireAntivirusProfile(mock_scm)

    # Call the update method
    updated_profile = wf_av_profile_client.update(profile_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/security/v1/wildfire-anti-virus-profiles/{profile_id}",
        json=expected_payload,
    )
    assert isinstance(updated_profile, WildfireAntivirusProfileResponseModel)
    assert updated_profile.id == profile_id
    assert updated_profile.name == "UpdatedProfile"
    assert updated_profile.description == "An updated wildfire antivirus profile"
    assert updated_profile.rules[0].name == "UpdatedRule"
    assert updated_profile.rules[0].direction == Direction.upload


def test_delete_wildfire_antivirus_profile(load_env, mock_scm):
    """
    Test deleting a wildfire antivirus profile.
    """
    # Prepare test data
    profile_id = "123e4567-e89b-12d3-a456-426655440000"

    # Mock the API client's delete method
    mock_scm.delete = MagicMock(return_value=None)

    # Create an instance of WildfireAntivirusProfile with the mocked Scm
    wf_av_profile_client = WildfireAntivirusProfile(mock_scm)

    # Call the delete method
    wf_av_profile_client.delete(profile_id)

    # Assertions
    mock_scm.delete.assert_called_once_with(
        f"/config/security/v1/wildfire-anti-virus-profiles/{profile_id}"
    )


def test_wildfire_antivirus_profile_request_model_validation_errors():
    """
    Test validation errors in WildfireAntivirusProfileRequestModel.
    """
    # No container provided
    data_no_container = {
        "name": "InvalidProfile",
        "rules": [
            {
                "name": "Rule1",
                "direction": "both",
            }
        ],
    }
    with pytest.raises(ValueError) as exc_info:
        WildfireAntivirusProfileRequestModel(**data_no_container)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Multiple containers provided
    data_multiple_containers = {
        "name": "InvalidProfile",
        "folder": "Shared",
        "device": "Device1",
        "rules": [
            {
                "name": "Rule1",
                "direction": "both",
            }
        ],
    }
    with pytest.raises(ValueError) as exc_info:
        WildfireAntivirusProfileRequestModel(**data_multiple_containers)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Invalid direction in RuleRequest
    data_invalid_direction = {
        "name": "InvalidProfile",
        "folder": "Shared",
        "rules": [
            {
                "name": "InvalidRule",
                "direction": "sideways",  # Invalid direction
            }
        ],
    }
    with pytest.raises(ValueError) as exc_info:
        WildfireAntivirusProfileRequestModel(**data_invalid_direction)
    assert "1 validation error for WildfireAntivirusProfileRequestModel" in str(
        exc_info.value
    )
    assert "Input should be 'download', 'upload' or 'both'" in str(exc_info.value)

    # Invalid UUID in id field (for response model)
    data_invalid_id = {
        "id": "invalid-uuid",
        "name": "TestProfile",
        "folder": "Shared",
        "rules": [
            {
                "name": "Rule1",
                "direction": "both",
            }
        ],
    }
    with pytest.raises(ValueError) as exc_info:
        WildfireAntivirusProfileResponseModel(**data_invalid_id)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_wildfire_antivirus_profile_list_validation_error(load_env, mock_scm):
    """
    Test validation error when listing with multiple containers.
    """
    # Create an instance of WildfireAntivirusProfile with the mocked Scm
    wf_av_profile_client = WildfireAntivirusProfile(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(ValidationError) as exc_info:
        wf_av_profile_client.list(folder="Shared", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_list_wildfire_antivirus_profiles_with_pagination(load_env, mock_scm):
    """
    Test listing wildfire antivirus profiles with pagination parameters.
    """
    # Mock response from the API client
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
                "description": "Best practice antivirus and wildfire analysis security profile",
            },
            {
                "id": "d5994c99-ee2e-4c9c-80a0-20e2eefd3f2d",
                "name": "TEST123",
                "folder": "All",
                "description": "THIS IS A TEST",
                "rules": [
                    {
                        "name": "RULE1",
                        "analysis": "public-cloud",
                        "direction": "download",
                        "application": [
                            "facebook-uploading",
                            "facebook-posting",
                            "facebook-downloading",
                            "facebook-base",
                        ],
                        "file_type": ["flash", "jar"],
                    }
                ],
            },
        ],
        "offset": 1,
        "total": 3,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AntiSpywareProfile with the mocked Scm
    anti_spyware_profile_client = WildfireAntivirusProfile(mock_scm)

    # Call the list method with pagination parameters
    profiles = anti_spyware_profile_client.list(
        folder="Prisma Access",
        offset=1,
        limit=1,
    )

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/wildfire-anti-virus-profiles",
        params={"folder": "Prisma Access", "offset": 1, "limit": 1},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 3
    assert profiles[0].name == "web-security-default"
    assert profiles[0].id == "dd0f80ce-9345-4cf1-9979-bce99da27888"


def test_wildfire_antivirus_profile_list_with_invalid_pagination(load_env, mock_scm):
    """
    Test validation error when invalid pagination parameters are provided.
    """
    # Create an instance of WildfireAntivirusProfile with the mocked Scm
    wf_av_profile_client = WildfireAntivirusProfile(mock_scm)

    # Attempt to call the list method with invalid pagination parameters
    with pytest.raises(ValueError) as exc_info:
        wf_av_profile_client.list(folder="All", offset=-1, limit=0)

    # Assertions
    assert "Offset must be a non-negative integer" in str(exc_info.value)
    assert "Limit must be a positive integer" in str(exc_info.value)


def test_rule_request_model_validation():
    """
    Test validation in RuleRequest model.
    """
    # Invalid analysis
    data_invalid_analysis = {
        "name": "TestRule",
        "direction": "both",
        "analysis": "invalid-cloud",
    }
    with pytest.raises(ValueError) as exc_info:
        RuleRequest(**data_invalid_analysis)
    assert "1 validation error for RuleRequest" in str(exc_info.value)
    assert " Input should be 'public-cloud' or 'private-cloud'" in str(exc_info.value)

    # Missing required fields
    data_missing_fields = {
        "analysis": "public-cloud",
        "direction": "both",
    }
    with pytest.raises(ValueError) as exc_info:
        RuleRequest(**data_missing_fields)
    assert "1 validation error for RuleRequest" in str(exc_info.value)
    assert "name\n  Field required" in str(exc_info.value)


def test_list_wildfire_antivirus_profiles_with_name_filter(load_env, mock_scm):
    """
    Test listing wildfire antivirus profiles with name filter.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "e2a5dfc4-d8c8-489a-9661-092032796e09",
                "name": "SpecificProfile",
                "folder": "All",
                "rules": [
                    {
                        "name": "default",
                        "application": ["any"],
                        "file_type": ["any"],
                        "direction": "both",
                        "analysis": "public-cloud",
                    }
                ],
            }
        ],
        "offset": 0,
        "total": 1,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of WildfireAntivirusProfile with the mocked Scm
    wf_av_profile_client = WildfireAntivirusProfile(mock_scm)

    # Call the list method with name filter
    profiles = wf_av_profile_client.list(folder="All", name="SpecificProfile")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/wildfire-anti-virus-profiles",
        params={"folder": "All", "name": "SpecificProfile"},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 1
    assert profiles[0].name == "SpecificProfile"
    assert profiles[0].id == "e2a5dfc4-d8c8-489a-9661-092032796e09"
