# tests/test_dns_security_profiles.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.dns_security_profile import DNSSecurityProfile
from scm.exceptions import ValidationError
from scm.models.security.dns_security_profiles import (
    DNSSecurityProfileRequestModel,
    DNSSecurityProfileResponseModel,
    ActionEnum,
    ListActionRequest,
    ListActionResponse,
)

from tests.factories import (
    DNSSecurityProfileRequestFactory,
    DNSSecurityProfileResponseFactory,
)


@pytest.mark.usefixtures("load_env")
class TestDNSSecurityProfileBase:
    """Base class for DNS Security Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        # Create new MagicMock instances for each HTTP method
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = DNSSecurityProfile(self.mock_scm)


class TestDNSSecurityProfileAPI(TestDNSSecurityProfileBase):
    """Tests for DNS Security Profile API operations."""

    def test_list_dns_security_profiles(self):
        """Test listing DNS security profiles."""
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

        self.mock_scm.get.return_value = mock_response
        profiles = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(
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
        assert (
            profiles[1].botnet_domains.lists[0].action.get_action_name() == "sinkhole"
        )

    def test_create_dns_security_profile(self):
        """Test creating a DNS security profile."""
        profile_request = DNSSecurityProfileRequestFactory()
        mock_response = DNSSecurityProfileResponseFactory.from_request(
            profile_request, id="333e4567-e89b-12d3-a456-426655440002"
        )

        self.mock_scm.post.return_value = mock_response.model_dump()

        # Create a clean request payload without None values
        request_payload = profile_request.model_dump(exclude_none=True)
        created_profile = self.client.create(request_payload)

        self.mock_scm.post.assert_called_once_with(
            "/config/security/v1/dns-security-profiles",
            json=request_payload,
        )

        assert isinstance(created_profile, DNSSecurityProfileResponseModel)
        assert created_profile.id == "333e4567-e89b-12d3-a456-426655440002"
        assert created_profile.name == profile_request.name
        assert created_profile.description == profile_request.description

    def test_get_dns_security_profile(self):
        """Test retrieving a DNS security profile by ID."""
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

        self.mock_scm.get.return_value = mock_response
        profile = self.client.get(profile_id)

        self.mock_scm.get.assert_called_once_with(
            f"/config/security/v1/dns-security-profiles/{profile_id}"
        )
        assert isinstance(profile, DNSSecurityProfileResponseModel)
        assert profile.id == profile_id
        assert profile.name == "TestDNSProfile"
        assert profile.description == "A test DNS security profile"
        assert (
            profile.botnet_domains.dns_security_categories[0].name
            == "pan-dns-sec-malware"
        )
        assert (
            profile.botnet_domains.dns_security_categories[0].action == ActionEnum.block
        )

    def test_update_dns_security_profile(self):
        """Test updating a DNS security profile."""
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

        mock_response = update_data.copy()
        mock_response["id"] = profile_id

        self.mock_scm.put.return_value = mock_response
        updated_profile = self.client.update(profile_id, update_data)

        self.mock_scm.put.assert_called_once_with(
            f"/config/security/v1/dns-security-profiles/{profile_id}",
            json=update_data,
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

    def test_delete_dns_security_profile(self):
        """Test deleting a DNS security profile."""
        profile_id = "e4af4e61-29aa-4454-86f7-269a6e6c5868"

        self.mock_scm.delete.return_value = None
        self.client.delete(profile_id)

        self.mock_scm.delete.assert_called_once_with(
            f"/config/security/v1/dns-security-profiles/{profile_id}"
        )


class TestDNSSecurityProfileValidation(TestDNSSecurityProfileBase):
    """Tests for DNS Security Profile validation."""

    def test_dns_security_profile_request_model_validation_errors(self):
        """Test validation errors in DNSSecurityProfileRequestModel."""
        # No container provided
        with pytest.raises(ValueError) as exc_info:
            DNSSecurityProfileRequestModel(
                name="InvalidDNSProfile",
                botnet_domains={},
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Multiple containers provided
        with pytest.raises(ValueError) as exc_info:
            DNSSecurityProfileRequestModel(
                name="InvalidDNSProfile",
                folder="Shared",
                device="Device1",
                botnet_domains={},
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Invalid action in dns_security_categories
        with pytest.raises(ValueError) as exc_info:
            DNSSecurityProfileRequestModel(
                name="InvalidDNSProfile",
                folder="Shared",
                botnet_domains={
                    "dns_security_categories": [
                        {
                            "name": "pan-dns-sec-malware",
                            "action": "invalid_action",
                        }
                    ]
                },
            )
        assert "1 validation error for DNSSecurityProfileRequestModel" in str(
            exc_info.value
        )

        # Invalid action in lists
        with pytest.raises(ValueError) as exc_info:
            DNSSecurityProfileRequestModel(
                name="InvalidDNSProfile",
                folder="Shared",
                botnet_domains={
                    "lists": [
                        {
                            "name": "CustomDNSList",
                            "action": {"invalid_action": {}},
                        }
                    ]
                },
            )
        assert "Exactly one action must be provided in 'action' field." in str(
            exc_info.value
        )

    def test_dns_security_profile_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_dns_security_profile_list_with_invalid_pagination(self):
        """Test validation error when invalid pagination parameters are provided."""
        with pytest.raises(ValueError) as exc_info:
            self.client.list(
                folder="All",
                offset=-1,
                limit=0,
            )

        assert "Offset must be a non-negative integer" in str(exc_info.value)
        assert "Limit must be a positive integer" in str(exc_info.value)


class TestListActionValidation:
    """Tests for List Action validation."""

    def test_list_action_request_validation(self):
        """Test validation in ListActionRequest."""
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

    def test_list_action_response_validation(self):
        """Test validation in ListActionResponse."""
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

    def test_list_action_get_action_name(self):
        """Test get_action_name method in ListActionRequest and ListActionResponse."""
        action_req = ListActionRequest("sinkhole")
        assert action_req.get_action_name() == "sinkhole"

        action_res = ListActionResponse({"block": {}})
        assert action_res.get_action_name() == "block"

        action_res_empty = ListActionResponse({})
        assert action_res_empty.get_action_name() == "unknown"

    def test_list_action_response_invalid_non_empty_dict(self):
        """Test validation in ListActionResponse for invalid non-empty dict."""
        # Test invalid non-empty dict with invalid format
        with pytest.raises(ValueError, match="Invalid action format."):
            ListActionResponse({"invalid_key": "invalid_value"})

        # Test invalid non-empty dict with wrong structure
        with pytest.raises(ValueError, match="Invalid action format."):
            ListActionResponse({"action": "invalid"})

        # Test that empty dict is accepted
        empty_action = ListActionResponse({})
        assert empty_action.root == {}

        # Test valid non-empty dict
        valid_action = ListActionResponse({"sinkhole": {}})
        assert valid_action.root == {"sinkhole": {}}


class TestModelValidation:
    """Tests for model-specific validations."""

    def test_dns_security_profile_response_id_validation(self):
        """Test UUID validation in DNSSecurityProfileResponseModel."""
        # Test valid UUID
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        valid_data = {
            "id": valid_uuid,
            "name": "TestProfile",
            "folder": "All",
            "botnet_domains": {},
        }
        profile = DNSSecurityProfileResponseModel(**valid_data)
        assert profile.id == valid_uuid

        # Test invalid UUID format
        invalid_uuids = [
            "not-a-uuid",
            "123",
            "550e8400-e29b-41d4-a716",  # Incomplete UUID
            "550e8400-e29b-41d4-a716-44665544000Z",  # Invalid character
            "",  # Empty string
        ]

        for invalid_uuid in invalid_uuids:
            invalid_data = valid_data.copy()
            invalid_data["id"] = invalid_uuid
            with pytest.raises(ValueError, match="Invalid UUID format for 'id'"):
                DNSSecurityProfileResponseModel(**invalid_data)

        # Test that the validator handles None (though it shouldn't occur due to field requirements)
        invalid_data = valid_data.copy()
        invalid_data["id"] = None
        with pytest.raises(ValueError):
            DNSSecurityProfileResponseModel(**invalid_data)


class TestDNSSecurityProfilePagination(TestDNSSecurityProfileBase):
    """Tests for DNS Security Profile pagination."""

    def test_list_dns_security_profiles_with_pagination(self):
        """Test listing DNS security profiles with pagination parameters."""
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

        self.mock_scm.get.return_value = mock_response
        profiles = self.client.list(
            folder="All",
            offset=1,
            limit=1,
        )

        self.mock_scm.get.assert_called_once_with(
            "/config/security/v1/dns-security-profiles",
            params={
                "folder": "All",
                "offset": 1,
                "limit": 1,
            },
        )
        assert isinstance(profiles, list)
        assert len(profiles) == 1
        assert profiles[0].name == "best-practice"
        assert profiles[0].id == "d3d1d8bf-d7e3-44ae-a3be-37396c365572"

    def test_list_dns_security_profiles_with_name_filter(self):
        """Test listing DNS security profiles with name filter."""
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

        self.mock_scm.get.return_value = mock_response
        profiles = self.client.list(folder="All", name="SpecificProfile")

        self.mock_scm.get.assert_called_once_with(
            "/config/security/v1/dns-security-profiles",
            params={"folder": "All", "name": "SpecificProfile"},
        )
        assert isinstance(profiles, list)
        assert len(profiles) == 1
        assert profiles[0].name == "SpecificProfile"
        assert profiles[0].id == "e4af4e61-29aa-4454-86f7-269a6e6c5868"


class TestSuite(
    TestDNSSecurityProfileAPI,
    TestDNSSecurityProfileValidation,
    TestListActionValidation,
    TestDNSSecurityProfilePagination,
    TestModelValidation,
):
    """Main test suite that combines all test classes."""

    pass
