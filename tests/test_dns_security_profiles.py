# tests/test_dns_security_profiles.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.dns_security_profile import DNSSecurityProfile
from scm.exceptions import ValidationError
from scm.models.security.dns_security_profiles import (
    DNSSecurityProfileRequestModel,
    DNSSecurityProfileResponseModel,
    DNSSecurityCategoryEntry,
    ListEntryRequest,
    ListEntryResponse,
    SinkholeSettings,
    WhitelistEntry,
    BotnetDomainsRequest,
    BotnetDomainsResponse,
    ActionEnum,
    LogLevelEnum,
    PacketCaptureEnum,
    IPv4AddressEnum,
    IPv6AddressEnum,
    ListActionRequest,
    ListActionResponse,
)
from typing import List
import uuid


def test_list_dns_security_profiles(load_env, mock_scm):
    """
    Test listing DNS security profiles.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "e4af4e61-29aa-4454-86f7-269a6e6c5868",
                "name": "web-security-default",
                "folder": "All",
                "snippet": "Web-Security-Default",
                "botnet_domains": {
                    "sinkhole": {
                        "ipv4_address": "pan-sinkhole-default-ip",
                        "ipv6_address": "::1",
                    },
                    "dns_security_categories": [
                        {"name": "pan-dns-sec-grayware", "action": "default"},
                        {"name": "pan-dns-sec-recent", "action": "default"},
                        {"name": "pan-dns-sec-parked", "action": "default"},
                        {"name": "pan-dns-sec-proxy", "action": "default"},
                        {"name": "pan-dns-sec-cc", "action": "default"},
                        {"name": "pan-dns-sec-ddns", "action": "default"},
                        {"name": "pan-dns-sec-phishing", "action": "default"},
                        {"name": "pan-dns-sec-malware", "action": "default"},
                    ],
                },
            },
            {
                "id": "d3d1d8bf-d7e3-44ae-a3be-37396c365572",
                "name": "best-practice",
                "folder": "All",
                "snippet": "predefined-snippet",
                "botnet_domains": {
                    "dns_security_categories": [
                        {
                            "name": "pan-dns-sec-grayware",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "pan-dns-sec-adtracking",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "pan-dns-sec-recent",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "pan-dns-sec-parked",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "pan-dns-sec-proxy",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "pan-dns-sec-cc",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "extended-capture",
                        },
                        {
                            "name": "pan-dns-sec-ddns",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "pan-dns-sec-phishing",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "pan-dns-sec-malware",
                            "log_level": "default",
                            "action": "sinkhole",
                            "packet_capture": "disable",
                        },
                    ],
                    "lists": [
                        {
                            "name": "default-paloalto-dns",
                            "packet_capture": "single-packet",
                            "action": {"sinkhole": {}},
                        }
                    ],
                    "sinkhole": {
                        "ipv4_address": "pan-sinkhole-default-ip",
                        "ipv6_address": "::1",
                    },
                },
                "description": "Best practice dns security profile",
            },
        ],
        "offset": 0,
        "total": 2,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Call the list method
    profiles = dns_security_profile_client.list(folder="All")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/dns-security-profiles",
        params={"folder": "All"},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 2
    assert isinstance(profiles[0], DNSSecurityProfileResponseModel)
    assert profiles[0].name == "web-security-default"
    assert profiles[0].folder == "All"
    assert profiles[0].snippet == "Web-Security-Default"
    assert profiles[0].botnet_domains is not None
    assert len(profiles[0].botnet_domains.dns_security_categories) == 8
    assert (
        profiles[0].botnet_domains.dns_security_categories[0].name
        == "pan-dns-sec-grayware"
    )
    assert (
        profiles[0].botnet_domains.dns_security_categories[0].action
        == ActionEnum.default
    )

    assert profiles[1].description == "Best practice dns security profile"
    assert profiles[1].botnet_domains.lists[0].name == "default-paloalto-dns"
    assert profiles[1].botnet_domains.lists[0].action.get_action_name() == "sinkhole"


def test_create_dns_security_profile(load_env, mock_scm):
    """
    Test creating a DNS security profile.
    """
    # Prepare test data
    test_profile_data = {
        "name": "NewDNSProfile",
        "folder": "All",
        "description": "A new test DNS security profile",
        "botnet_domains": {
            "dns_security_categories": [
                {
                    "name": "pan-dns-sec-malware",
                    "action": "block",
                    "log_level": "high",
                    "packet_capture": "single-packet",
                }
            ],
            "lists": [
                {
                    "name": "CustomDNSList",
                    "action": {"sinkhole": {}},
                    "packet_capture": "extended-capture",
                }
            ],
            "sinkhole": {
                "ipv4_address": "pan-sinkhole-default-ip",
                "ipv6_address": "::1",
            },
            "whitelist": [
                {
                    "name": "trusted.com",
                    "description": "Trusted domain",
                }
            ],
        },
    }

    # Expected payload after model processing
    expected_payload = test_profile_data.copy()

    # Mock response from the API client
    mock_response = expected_payload.copy()
    mock_response["id"] = "333e4567-e89b-12d3-a456-426655440002"  # Mocked ID

    # Mock the API client's post method
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Call the create method
    created_profile = dns_security_profile_client.create(test_profile_data)

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/security/v1/dns-security-profiles",
        json=expected_payload,
    )
    assert isinstance(created_profile, DNSSecurityProfileResponseModel)
    assert created_profile.id == "333e4567-e89b-12d3-a456-426655440002"
    assert created_profile.name == "NewDNSProfile"
    assert created_profile.description == "A new test DNS security profile"
    assert (
        created_profile.botnet_domains.dns_security_categories[0].name
        == "pan-dns-sec-malware"
    )
    assert (
        created_profile.botnet_domains.dns_security_categories[0].action
        == ActionEnum.block
    )
    assert created_profile.botnet_domains.lists[0].name == "CustomDNSList"
    assert (
        created_profile.botnet_domains.lists[0].action.get_action_name() == "sinkhole"
    )
    assert created_profile.botnet_domains.whitelist[0].name == "trusted.com"


def test_get_dns_security_profile(load_env, mock_scm):
    """
    Test retrieving a DNS security profile by ID.
    """
    # Mock response from the API client
    profile_id = "e4af4e61-29aa-4454-86f7-269a6e6c5868"
    mock_response = {
        "id": profile_id,
        "name": "TestDNSProfile",
        "folder": "All",
        "description": "A test DNS security profile",
        "botnet_domains": {
            "sinkhole": {
                "ipv4_address": "pan-sinkhole-default-ip",
                "ipv6_address": "::1",
            },
            "dns_security_categories": [
                {
                    "name": "pan-dns-sec-malware",
                    "action": "block",
                    "log_level": "high",
                    "packet_capture": "single-packet",
                }
            ],
        },
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Call the get method
    profile = dns_security_profile_client.get(profile_id)

    # Assertions
    mock_scm.get.assert_called_once_with(
        f"/config/security/v1/dns-security-profiles/{profile_id}"
    )
    assert isinstance(profile, DNSSecurityProfileResponseModel)
    assert profile.id == profile_id
    assert profile.name == "TestDNSProfile"
    assert profile.description == "A test DNS security profile"
    assert (
        profile.botnet_domains.dns_security_categories[0].name == "pan-dns-sec-malware"
    )
    assert profile.botnet_domains.dns_security_categories[0].action == ActionEnum.block


def test_update_dns_security_profile(load_env, mock_scm):
    """
    Test updating a DNS security profile.
    """
    # Prepare test data
    profile_id = "e4af4e61-29aa-4454-86f7-269a6e6c5868"
    update_data = {
        "name": "UpdatedDNSProfile",
        "folder": "All",
        "description": "An updated DNS security profile",
        "botnet_domains": {
            "dns_security_categories": [
                {
                    "name": "pan-dns-sec-phishing",
                    "action": "sinkhole",
                    "log_level": "medium",
                    "packet_capture": "extended-capture",
                }
            ],
            "whitelist": [
                {
                    "name": "safe.com",
                    "description": "Safe domain",
                }
            ],
        },
    }

    # Expected payload after model processing
    expected_payload = update_data.copy()

    # Mock response from the API client
    mock_response = expected_payload.copy()
    mock_response["id"] = profile_id

    # Mock the API client's put method
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Call the update method
    updated_profile = dns_security_profile_client.update(profile_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/security/v1/dns-security-profiles/{profile_id}",
        json=expected_payload,
    )
    assert isinstance(updated_profile, DNSSecurityProfileResponseModel)
    assert updated_profile.id == profile_id
    assert updated_profile.name == "UpdatedDNSProfile"
    assert updated_profile.description == "An updated DNS security profile"
    assert (
        updated_profile.botnet_domains.dns_security_categories[0].name
        == "pan-dns-sec-phishing"
    )
    assert (
        updated_profile.botnet_domains.dns_security_categories[0].action
        == ActionEnum.sinkhole
    )
    assert updated_profile.botnet_domains.whitelist[0].name == "safe.com"


def test_delete_dns_security_profile(load_env, mock_scm):
    """
    Test deleting a DNS security profile.
    """
    # Prepare test data
    profile_id = "e4af4e61-29aa-4454-86f7-269a6e6c5868"

    # Mock the API client's delete method
    mock_scm.delete = MagicMock(return_value=None)

    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Call the delete method
    dns_security_profile_client.delete(profile_id)

    # Assertions
    mock_scm.delete.assert_called_once_with(
        f"/config/security/v1/dns-security-profiles/{profile_id}"
    )


def test_dns_security_profile_request_model_validation_errors():
    """
    Test validation errors in DNSSecurityProfileRequestModel.
    """
    # No container provided
    data_no_container = {
        "name": "InvalidDNSProfile",
        "botnet_domains": {},
    }
    with pytest.raises(ValueError) as exc_info:
        DNSSecurityProfileRequestModel(**data_no_container)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Multiple containers provided
    data_multiple_containers = {
        "name": "InvalidDNSProfile",
        "folder": "Shared",
        "device": "Device1",
        "botnet_domains": {},
    }
    with pytest.raises(ValueError) as exc_info:
        DNSSecurityProfileRequestModel(**data_multiple_containers)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Invalid action in dns_security_categories
    data_invalid_action = {
        "name": "InvalidDNSProfile",
        "folder": "Shared",
        "botnet_domains": {
            "dns_security_categories": [
                {
                    "name": "pan-dns-sec-malware",
                    "action": "invalid_action",
                }
            ]
        },
    }
    with pytest.raises(ValueError) as exc_info:
        DNSSecurityProfileRequestModel(**data_invalid_action)
    assert "1 validation error for DNSSecurityProfileRequestModel" in str(
        exc_info.value
    )
    assert "1 validation error for DNSSecurityProfileRequestModel" in str(
        exc_info.value
    )

    # Invalid action in lists
    data_invalid_list_action = {
        "name": "InvalidDNSProfile",
        "folder": "Shared",
        "botnet_domains": {
            "lists": [
                {
                    "name": "CustomDNSList",
                    "action": {"invalid_action": {}},
                }
            ]
        },
    }
    with pytest.raises(ValueError) as exc_info:
        DNSSecurityProfileRequestModel(**data_invalid_list_action)
    assert "Exactly one action must be provided in 'action' field." in str(
        exc_info.value
    )

    # Invalid UUID in id field (for response model)
    data_invalid_id = {
        "id": "invalid-uuid",
        "name": "TestDNSProfile",
        "folder": "Shared",
        "botnet_domains": {},
    }
    with pytest.raises(ValueError) as exc_info:
        DNSSecurityProfileResponseModel(**data_invalid_id)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_dns_security_profile_list_validation_error(load_env, mock_scm):
    """
    Test validation error when listing with multiple containers.
    """
    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(ValidationError) as exc_info:
        dns_security_profile_client.list(folder="Shared", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_list_dns_security_profiles_with_pagination(load_env, mock_scm):
    """
    Test listing DNS security profiles with pagination parameters.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "d3d1d8bf-d7e3-44ae-a3be-37396c365572",
                "name": "best-practice",
                "folder": "All",
                "snippet": "predefined-snippet",
                "botnet_domains": {},
                "description": "Best practice dns security profile",
            }
        ],
        "offset": 1,
        "total": 2,
        "limit": 1,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Call the list method with pagination parameters
    profiles = dns_security_profile_client.list(folder="All", offset=1, limit=1)

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/dns-security-profiles",
        params={"folder": "All", "offset": 1, "limit": 1},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 1
    assert profiles[0].name == "best-practice"
    assert profiles[0].id == "d3d1d8bf-d7e3-44ae-a3be-37396c365572"


def test_dns_security_profile_list_with_invalid_pagination(load_env, mock_scm):
    """
    Test validation error when invalid pagination parameters are provided.
    """
    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Attempt to call the list method with invalid pagination parameters
    with pytest.raises(ValueError) as exc_info:
        dns_security_profile_client.list(
            folder="All",
            offset=-1,
            limit=0,
        )

    # Assertions
    assert "Offset must be a non-negative integer" in str(exc_info.value)
    assert "Limit must be a positive integer" in str(exc_info.value)


def test_list_action_request_validation():
    """
    Test validation in ListActionRequest.
    """
    # Valid action
    valid_action = ListActionRequest("sinkhole")
    assert valid_action.root == {"sinkhole": {}}

    # Invalid action format
    with pytest.raises(
        ValueError, match="Invalid action format; must be a string or dict."
    ):
        ListActionRequest(123)

    # Multiple actions
    with pytest.raises(
        ValueError, match="Exactly one action must be provided in 'action' field."
    ):
        ListActionRequest({"sinkhole": {}, "block": {}})

    # Invalid action name
    with pytest.raises(
        ValueError, match="Exactly one action must be provided in 'action' field."
    ):
        ListActionRequest({"invalid_action": {}})

    # Non-empty parameters
    with pytest.raises(
        ValueError, match="Action 'sinkhole' does not take any parameters."
    ):
        ListActionRequest({"sinkhole": {"param": "value"}})


def test_list_action_response_validation():
    """
    Test validation in ListActionResponse.
    """
    # Valid action
    valid_action = ListActionResponse("sinkhole")
    assert valid_action.root == {"sinkhole": {}}

    # Empty dict (no action specified)
    empty_action = ListActionResponse({})
    assert empty_action.root == {}

    # Invalid action format
    with pytest.raises(
        ValueError, match="Invalid action format; must be a string or dict."
    ):
        ListActionResponse(123)

    # Multiple actions
    with pytest.raises(
        ValueError, match="At most one action must be provided in 'action' field."
    ):
        ListActionResponse({"sinkhole": {}, "block": {}})

    # Non-empty parameters
    with pytest.raises(
        ValueError, match="Action 'sinkhole' does not take any parameters."
    ):
        ListActionResponse({"sinkhole": {"param": "value"}})


def test_list_action_get_action_name():
    """
    Test get_action_name method in ListActionRequest and ListActionResponse.
    """
    action_req = ListActionRequest("sinkhole")
    assert action_req.get_action_name() == "sinkhole"

    action_res = ListActionResponse({"block": {}})
    assert action_res.get_action_name() == "block"

    action_res_empty = ListActionResponse({})
    assert action_res_empty.get_action_name() == "unknown"


def test_list_dns_security_profiles_with_name_filter(load_env, mock_scm):
    """
    Test listing DNS security profiles with name filter.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "e4af4e61-29aa-4454-86f7-269a6e6c5868",
                "name": "SpecificProfile",
                "folder": "All",
                "botnet_domains": {},
            },
        ],
        "offset": 0,
        "total": 1,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of DNSSecurityProfile with the mocked Scm
    dns_security_profile_client = DNSSecurityProfile(mock_scm)

    # Call the list method with name filter
    profiles = dns_security_profile_client.list(folder="All", name="SpecificProfile")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/dns-security-profiles",
        params={"folder": "All", "name": "SpecificProfile"},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 1
    assert profiles[0].name == "SpecificProfile"
    assert profiles[0].id == "e4af4e61-29aa-4454-86f7-269a6e6c5868"


def test_list_action_response_invalid_non_empty_dict():
    """
    Test validation in ListActionResponse for invalid non-empty dict.
    """
    # Test invalid non-empty dict
    with pytest.raises(ValueError, match="Invalid action format."):
        ListActionResponse({"invalid_action": "value"})

    # Test empty dict (should be valid)
    valid_empty = ListActionResponse({})
    assert valid_empty.root == {}

    # Test valid non-empty dict
    valid_action = ListActionResponse({"sinkhole": {}})
    assert valid_action.root == {"sinkhole": {}}
