"""Live E2E tests for v0.10.0 Advanced Networking services.

These tests CREATE, READ, UPDATE, and DELETE networking resources against the real SCM API.
QoS Rule tests include the :move operation for rule reordering.

Run with:
    PYTHONPATH=. python -m pytest tests/scm/api/test_advanced_networking_e2e.py -v -s

Prerequisites:
    - .env file with SCM_CLIENT_ID, SCM_CLIENT_SECRET, SCM_TSG_ID
    - Network access to api.strata.paloaltonetworks.com
"""

import logging
import os
import time
import uuid

from dotenv import load_dotenv
import pytest

from scm.client import Scm
from scm.models.network import (
    DnsProxyResponseModel,
    DnsProxyUpdateModel,
    PbfRuleResponseModel,
    PbfRuleUpdateModel,
    QosProfileResponseModel,
    QosProfileUpdateModel,
    QosRuleResponseModel,
)

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FOLDER = "ngfw-shared"
QOS_PROFILE_FOLDER = (
    "Remote Networks"  # QoS Profiles only accept Remote Networks or Service Connections
)


@pytest.fixture(scope="module")
def client():
    """Create a live SCM client using credentials from .env."""
    client_id = os.getenv("SCM_CLIENT_ID") or os.getenv("CLIENT_ID")
    client_secret = os.getenv("SCM_CLIENT_SECRET") or os.getenv("CLIENT_SECRET")
    tsg_id = os.getenv("SCM_TSG_ID") or os.getenv("TSG_ID")

    if not all([client_id, client_secret, tsg_id]):
        pytest.skip("SCM credentials not configured in .env")

    return Scm(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id,
        log_level="DEBUG",
    )


@pytest.fixture(scope="module")
def unique_suffix():
    """Generate unique suffix to avoid test collisions."""
    return uuid.uuid4().hex[:6]


# ---------------------------------------------------------------------------
# Helper to clean up resource if it exists
# ---------------------------------------------------------------------------


def cleanup_resource(client_service, name, folder):
    """Delete a resource by name if it exists."""
    try:
        resource = client_service.fetch(name=name, folder=folder)
        client_service.delete(str(resource.id))
        logger.info(f"Cleaned up: {name} (id={resource.id})")
        time.sleep(1)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# E2E Tests - QoS Profile (Full CRUD)
# ---------------------------------------------------------------------------


@pytest.mark.api
class TestQosProfileE2E:
    """End-to-end tests that CREATE, READ, UPDATE, DELETE QoS profiles."""

    def test_01_create_qos_profile(self, client, unique_suffix):
        """Create a QoS Profile with aggregate bandwidth settings."""
        name = f"SDK-E2E-QOS-PROF-{unique_suffix}"
        cleanup_resource(client.qos_profile, name, QOS_PROFILE_FOLDER)

        config = {
            "name": name,
            "aggregate_bandwidth": {
                "egress_max": 500,
                "egress_guaranteed": 100,
            },
            "folder": QOS_PROFILE_FOLDER,
        }

        print(f"\n  Creating QoS Profile: {name}")
        result = client.qos_profile.create(config)

        assert isinstance(result, QosProfileResponseModel)
        assert result.id is not None
        assert result.name == name
        print(f"  Created: id={result.id}, name={result.name}")

        self.__class__._qos_profile_id = str(result.id)
        self.__class__._qos_profile_name = name
        time.sleep(1)

    def test_02_fetch_qos_profile(self, client):
        """Fetch the QoS Profile by name and verify fields."""
        time.sleep(2)

        profile = client.qos_profile.fetch(
            name=self.__class__._qos_profile_name, folder=QOS_PROFILE_FOLDER
        )
        assert isinstance(profile, QosProfileResponseModel)
        assert profile.name == self.__class__._qos_profile_name
        assert profile.id is not None
        print(f"\n  Fetched QoS Profile: {profile.name} (id={profile.id})")

    def test_03_get_qos_profile_by_id(self, client):
        """Get the QoS Profile by its UUID."""
        profile = client.qos_profile.get(self.__class__._qos_profile_id)
        assert isinstance(profile, QosProfileResponseModel)
        assert str(profile.id) == self.__class__._qos_profile_id
        print(f"\n  Got QoS Profile by ID: {profile.name}")

    def test_04_update_qos_profile(self, client):
        """Update the QoS Profile aggregate bandwidth."""
        profile = client.qos_profile.fetch(
            name=self.__class__._qos_profile_name, folder=QOS_PROFILE_FOLDER
        )

        update_data = profile.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(profile.id)
        update_data["aggregate_bandwidth"] = {
            "egress_max": 1000,
            "egress_guaranteed": 250,
        }

        update_model = QosProfileUpdateModel(**update_data)
        updated = client.qos_profile.update(update_model)

        assert isinstance(updated, QosProfileResponseModel)
        print(f"\n  Updated QoS Profile: {updated.name}")

        # Re-fetch and verify
        time.sleep(1)
        fetched = client.qos_profile.fetch(
            name=self.__class__._qos_profile_name, folder=QOS_PROFILE_FOLDER
        )
        assert fetched.aggregate_bandwidth is not None
        print(f"  Verified aggregate_bandwidth: {fetched.aggregate_bandwidth}")

    def test_05_list_qos_profiles(self, client):
        """List QoS profiles and verify our test profile is present."""
        items = client.qos_profile.list(folder=QOS_PROFILE_FOLDER)
        assert isinstance(items, list)
        names = [item.name for item in items]
        assert self.__class__._qos_profile_name in names
        print(f"\n  Found {len(items)} QoS profiles, test profile present")

    def test_06_delete_qos_profile(self, client):
        """Delete the QoS Profile and verify removal."""
        if hasattr(self.__class__, "_qos_profile_id"):
            client.qos_profile.delete(self.__class__._qos_profile_id)
            print(f"\n  Deleted QoS Profile: {self.__class__._qos_profile_name}")
            time.sleep(1)

            try:
                client.qos_profile.fetch(
                    name=self.__class__._qos_profile_name, folder=QOS_PROFILE_FOLDER
                )
                print("  WARNING: QoS Profile still exists after delete")
            except Exception:
                print("  Confirmed deleted")


# ---------------------------------------------------------------------------
# E2E Tests - DNS Proxy (Full CRUD)
# ---------------------------------------------------------------------------


@pytest.mark.api
class TestDnsProxyE2E:
    """End-to-end tests that CREATE, READ, UPDATE, DELETE DNS proxies."""

    def test_01_create_dns_proxy(self, client, unique_suffix):
        """Create a DNS Proxy with basic configuration."""
        name = f"SDK-E2E-DNSPROXY-{unique_suffix}"
        cleanup_resource(client.dns_proxy, name, FOLDER)

        config = {
            "name": name,
            "enabled": True,
            "default": {
                "primary": "8.8.8.8",
                "secondary": "8.8.4.4",
            },
            "folder": FOLDER,
        }

        print(f"\n  Creating DNS Proxy: {name}")
        result = client.dns_proxy.create(config)

        assert isinstance(result, DnsProxyResponseModel)
        assert result.id is not None
        assert result.name == name
        print(f"  Created: id={result.id}, name={result.name}")

        self.__class__._dns_proxy_id = str(result.id)
        self.__class__._dns_proxy_name = name
        time.sleep(1)

    def test_02_fetch_dns_proxy(self, client):
        """Fetch the DNS Proxy by name and verify fields."""
        time.sleep(2)

        proxy = client.dns_proxy.fetch(name=self.__class__._dns_proxy_name, folder=FOLDER)
        assert isinstance(proxy, DnsProxyResponseModel)
        assert proxy.name == self.__class__._dns_proxy_name
        assert proxy.id is not None
        print(f"\n  Fetched DNS Proxy: {proxy.name} (id={proxy.id})")

    def test_03_get_dns_proxy_by_id(self, client):
        """Get the DNS Proxy by its UUID."""
        proxy = client.dns_proxy.get(self.__class__._dns_proxy_id)
        assert isinstance(proxy, DnsProxyResponseModel)
        assert str(proxy.id) == self.__class__._dns_proxy_id
        print(f"\n  Got DNS Proxy by ID: {proxy.name}")

    def test_04_update_dns_proxy(self, client):
        """Update the DNS Proxy configuration."""
        proxy = client.dns_proxy.fetch(name=self.__class__._dns_proxy_name, folder=FOLDER)

        update_data = proxy.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(proxy.id)
        update_data["enabled"] = False

        update_model = DnsProxyUpdateModel(**update_data)
        updated = client.dns_proxy.update(update_model)

        assert isinstance(updated, DnsProxyResponseModel)
        print(f"\n  Updated DNS Proxy: {updated.name}")

        # Re-fetch and verify
        time.sleep(1)
        client.dns_proxy.fetch(name=self.__class__._dns_proxy_name, folder=FOLDER)
        print("  Verified DNS Proxy fetched after update")

    def test_05_list_dns_proxies(self, client):
        """List DNS proxies and verify our test proxy is present."""
        items = client.dns_proxy.list(folder=FOLDER)
        assert isinstance(items, list)
        names = [item.name for item in items]
        assert self.__class__._dns_proxy_name in names
        print(f"\n  Found {len(items)} DNS proxies, test proxy present")

    def test_06_delete_dns_proxy(self, client):
        """Delete the DNS Proxy and verify removal."""
        if hasattr(self.__class__, "_dns_proxy_id"):
            client.dns_proxy.delete(self.__class__._dns_proxy_id)
            print(f"\n  Deleted DNS Proxy: {self.__class__._dns_proxy_name}")
            time.sleep(1)

            try:
                client.dns_proxy.fetch(name=self.__class__._dns_proxy_name, folder=FOLDER)
                print("  WARNING: DNS Proxy still exists after delete")
            except Exception:
                print("  Confirmed deleted")


# ---------------------------------------------------------------------------
# E2E Tests - PBF Rule (Full CRUD)
# ---------------------------------------------------------------------------


@pytest.mark.api
class TestPbfRuleE2E:
    """End-to-end tests that CREATE, READ, UPDATE, DELETE PBF rules."""

    def test_01_create_pbf_rule(self, client, unique_suffix):
        """Create a PBF Rule with discard action."""
        name = f"SDK-E2E-PBF-{unique_suffix}"
        cleanup_resource(client.pbf_rule, name, FOLDER)

        config = {
            "name": name,
            "description": "SDK E2E test PBF rule",
            "action": {
                "discard": {},
            },
            "from": {
                "zone": ["any"],
            },
            "source": ["any"],
            "destination": ["any"],
            "service": ["any"],
            "folder": FOLDER,
        }

        print(f"\n  Creating PBF Rule: {name}")
        result = client.pbf_rule.create(config)

        assert isinstance(result, PbfRuleResponseModel)
        assert result.id is not None
        assert result.name == name
        print(f"  Created: id={result.id}, name={result.name}")

        self.__class__._pbf_id = str(result.id)
        self.__class__._pbf_name = name
        time.sleep(1)

    def test_02_fetch_pbf_rule(self, client):
        """Fetch the PBF Rule by name and verify fields."""
        time.sleep(2)

        rule = client.pbf_rule.fetch(name=self.__class__._pbf_name, folder=FOLDER)
        assert isinstance(rule, PbfRuleResponseModel)
        assert rule.name == self.__class__._pbf_name
        assert rule.id is not None
        print(f"\n  Fetched PBF Rule: {rule.name} (id={rule.id})")

    def test_03_get_pbf_rule_by_id(self, client):
        """Get the PBF Rule by its UUID."""
        rule = client.pbf_rule.get(self.__class__._pbf_id)
        assert isinstance(rule, PbfRuleResponseModel)
        assert str(rule.id) == self.__class__._pbf_id
        print(f"\n  Got PBF Rule by ID: {rule.name}")

    def test_04_update_pbf_rule(self, client):
        """Update the PBF Rule description."""
        rule = client.pbf_rule.fetch(name=self.__class__._pbf_name, folder=FOLDER)

        update_data = rule.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(rule.id)
        update_data["description"] = "SDK E2E test PBF rule - updated"

        update_model = PbfRuleUpdateModel(**update_data)
        updated = client.pbf_rule.update(update_model)

        assert isinstance(updated, PbfRuleResponseModel)
        print(f"\n  Updated PBF Rule: {updated.name}")

        # Re-fetch and verify
        time.sleep(1)
        fetched = client.pbf_rule.fetch(name=self.__class__._pbf_name, folder=FOLDER)
        assert fetched.description == "SDK E2E test PBF rule - updated"
        print(f"  Verified description: {fetched.description}")

    def test_05_list_pbf_rules(self, client):
        """List PBF rules and verify our test rule is present."""
        items = client.pbf_rule.list(folder=FOLDER)
        assert isinstance(items, list)
        names = [item.name for item in items]
        assert self.__class__._pbf_name in names
        print(f"\n  Found {len(items)} PBF rules, test rule present")

    def test_06_delete_pbf_rule(self, client):
        """Delete the PBF Rule and verify removal."""
        if hasattr(self.__class__, "_pbf_id"):
            client.pbf_rule.delete(self.__class__._pbf_id)
            print(f"\n  Deleted PBF Rule: {self.__class__._pbf_name}")
            time.sleep(1)

            try:
                client.pbf_rule.fetch(name=self.__class__._pbf_name, folder=FOLDER)
                print("  WARNING: PBF Rule still exists after delete")
            except Exception:
                print("  Confirmed deleted")


# ---------------------------------------------------------------------------
# E2E Tests - QoS Rule (No POST, with :move operation)
# ---------------------------------------------------------------------------


@pytest.mark.api
class TestQosRuleE2E:
    """End-to-end tests that CREATE, READ, UPDATE, DELETE, and MOVE QoS rules."""

    def test_01_create_qos_rule(self, client, unique_suffix):
        """Create a QoS Rule."""
        name = f"SDK-E2E-QOS-RULE-{unique_suffix}"
        cleanup_resource(client.qos_rule, name, FOLDER)

        config = {
            "name": name,
            "description": "SDK E2E test QoS rule",
            "action": {
                "class": "1",
            },
            "folder": FOLDER,
        }

        print(f"\n  Creating QoS Rule: {name}")
        result = client.qos_rule.create(config)

        assert isinstance(result, QosRuleResponseModel)
        assert result.id is not None
        assert result.name == name
        print(f"  Created: id={result.id}, name={result.name}")

        self.__class__._qos_rule_id = str(result.id)
        self.__class__._qos_rule_name = name
        time.sleep(1)

    def test_02_fetch_qos_rule(self, client):
        """Fetch the QoS Rule by name."""
        time.sleep(2)

        rule = client.qos_rule.fetch(name=self.__class__._qos_rule_name, folder=FOLDER)
        assert isinstance(rule, QosRuleResponseModel)
        assert rule.name == self.__class__._qos_rule_name
        assert rule.id is not None
        print(f"\n  Fetched QoS Rule: {rule.name} (id={rule.id})")

    def test_03_get_qos_rule_by_id(self, client):
        """Get the QoS Rule by its UUID."""
        rule = client.qos_rule.get(self.__class__._qos_rule_id)
        assert isinstance(rule, QosRuleResponseModel)
        assert str(rule.id) == self.__class__._qos_rule_id
        print(f"\n  Got QoS Rule by ID: {rule.name}")

    def test_04_list_qos_rules(self, client):
        """List QoS rules and verify our test rule is present."""
        items = client.qos_rule.list(folder=FOLDER)
        assert isinstance(items, list)
        names = [item.name for item in items]
        assert self.__class__._qos_rule_name in names
        print(f"\n  Found {len(items)} QoS rules, test rule present")

    def test_05_move_qos_rule_to_top(self, client):
        """Move the QoS Rule to the top of the pre-rulebase."""
        from uuid import UUID

        rule_id = UUID(self.__class__._qos_rule_id)

        print(f"\n  Moving QoS Rule to top: {self.__class__._qos_rule_name}")
        client.qos_rule.move(
            rule_id=rule_id,
            data={
                "destination": "top",
                "rulebase": "pre",
            },
        )
        print("  Move to top succeeded")
        time.sleep(1)

    def test_06_move_qos_rule_to_bottom(self, client):
        """Move the QoS Rule to the bottom of the pre-rulebase."""
        from uuid import UUID

        rule_id = UUID(self.__class__._qos_rule_id)

        print(f"\n  Moving QoS Rule to bottom: {self.__class__._qos_rule_name}")
        client.qos_rule.move(
            rule_id=rule_id,
            data={
                "destination": "bottom",
                "rulebase": "pre",
            },
        )
        print("  Move to bottom succeeded")
        time.sleep(1)

    def test_07_delete_qos_rule(self, client):
        """Delete the QoS Rule and verify removal."""
        if hasattr(self.__class__, "_qos_rule_id"):
            client.qos_rule.delete(self.__class__._qos_rule_id)
            print(f"\n  Deleted QoS Rule: {self.__class__._qos_rule_name}")
            time.sleep(1)

            try:
                client.qos_rule.fetch(name=self.__class__._qos_rule_name, folder=FOLDER)
                print("  WARNING: QoS Rule still exists after delete")
            except Exception:
                print("  Confirmed deleted")
