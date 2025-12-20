"""Live API tests for Security models.

These tests validate that Pydantic models correctly parse real API responses.
They are excluded from CI and only run locally with valid credentials.

Run with: pytest -m api tests/scm/api/test_security_api.py -v
"""

import pytest

from scm.models.security import (
    AntiSpywareProfileResponseModel,
    DecryptionProfileResponseModel,
    DNSSecurityProfileResponseModel,
    SecurityRuleResponseModel,
    URLCategoriesResponseModel,
    VulnerabilityProfileResponseModel,
    WildfireAvProfileResponseModel,
)


@pytest.mark.api
class TestAntiSpywareProfileAPI:
    """Live API tests for AntiSpywareProfile objects."""

    def test_list_anti_spyware_profiles(self, live_client, folder):
        """Verify AntiSpywareProfile list responses parse correctly."""
        profiles = live_client.anti_spyware_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, AntiSpywareProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestDecryptionProfileAPI:
    """Live API tests for DecryptionProfile objects."""

    def test_list_decryption_profiles(self, live_client, folder):
        """Verify DecryptionProfile list responses parse correctly."""
        profiles = live_client.decryption_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, DecryptionProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestDNSSecurityProfileAPI:
    """Live API tests for DNSSecurityProfile objects."""

    def test_list_dns_security_profiles(self, live_client, folder):
        """Verify DNSSecurityProfile list responses parse correctly."""
        profiles = live_client.dns_security_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, DNSSecurityProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestSecurityRuleAPI:
    """Live API tests for SecurityRule objects."""

    def test_list_security_rules(self, live_client, folder):
        """Verify SecurityRule list responses parse correctly."""
        rules = live_client.security_rule.list(folder=folder, limit=10)
        assert isinstance(rules, list)
        for rule in rules:
            assert isinstance(rule, SecurityRuleResponseModel)
            assert rule.id is not None
            assert rule.name is not None

    def test_security_rule_has_valid_action(self, live_client, folder):
        """Verify SecurityRule action field is valid."""
        rules = live_client.security_rule.list(folder=folder, limit=5)
        valid_actions = {"allow", "deny", "drop", "reset-client", "reset-server", "reset-both"}
        for rule in rules:
            if rule.action is not None:
                assert rule.action in valid_actions, f"Invalid action: {rule.action}"


@pytest.mark.api
class TestURLCategoriesAPI:
    """Live API tests for URLCategories objects."""

    def test_list_url_categories(self, live_client, folder):
        """Verify URLCategories list responses parse correctly."""
        categories = live_client.url_category.list(folder=folder, limit=10)
        assert isinstance(categories, list)
        for category in categories:
            assert isinstance(category, URLCategoriesResponseModel)
            assert category.id is not None
            assert category.name is not None


@pytest.mark.api
class TestVulnerabilityProtectionProfileAPI:
    """Live API tests for VulnerabilityProtectionProfile objects."""

    def test_list_vulnerability_protection_profiles(self, live_client, folder):
        """Verify VulnerabilityProtectionProfile list responses parse correctly."""
        profiles = live_client.vulnerability_protection_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, VulnerabilityProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestWildfireAntivirusProfileAPI:
    """Live API tests for WildfireAntivirusProfile objects."""

    def test_list_wildfire_antivirus_profiles(self, live_client, folder):
        """Verify WildfireAntivirusProfile list responses parse correctly."""
        profiles = live_client.wildfire_antivirus_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, WildfireAvProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None
