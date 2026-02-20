"""Live E2E tests for v0.9.0 BGP Routing Profile services.

These tests CREATE, READ, UPDATE, and DELETE routing profile resources against the real SCM API.

Run with:
    PYTHONPATH=. python -m pytest tests/scm/api/test_routing_profiles_e2e.py -v -s

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
    BgpFilteringProfileResponseModel,
    BgpRedistributionProfileResponseModel,
    BgpRouteMapResponseModel,
    BgpRouteMapRedistributionResponseModel,
)

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FOLDER = "ngfw-shared"


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
# E2E Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
class TestRoutingProfilesE2E:
    """End-to-end tests that CREATE, READ, UPDATE, DELETE v0.9.0 routing profiles."""

    # ------------------------------------------------------------------
    # Phase 1: Create all 4 routing profile resources
    # ------------------------------------------------------------------

    def test_01_create_bgp_redistribution_profile(self, client, unique_suffix):
        """Create a BGP Redistribution Profile with static and connected redistribution."""
        name = f"SDK-E2E-BGP-REDIST-{unique_suffix}"
        cleanup_resource(client.bgp_redistribution_profile, name, FOLDER)

        config = {
            "name": name,
            "ipv4": {
                "unicast": {
                    "static": {"enable": True, "metric": 100, "route_map": ""},
                    "connected": {"enable": True, "metric": 50},
                }
            },
            "folder": FOLDER,
        }

        print(f"\n  Creating BGP Redistribution Profile: {name}")
        result = client.bgp_redistribution_profile.create(config)

        assert isinstance(result, BgpRedistributionProfileResponseModel)
        assert result.id is not None
        assert result.name == name
        print(f"  Created: id={result.id}, name={result.name}")

        self.__class__._redist_id = str(result.id)
        self.__class__._redist_name = name
        time.sleep(1)

    def test_02_create_bgp_filtering_profile(self, client, unique_suffix):
        """Create a BGP Filtering Profile with route maps and multicast inherit."""
        name = f"SDK-E2E-BGP-FILTER-{unique_suffix}"
        cleanup_resource(client.bgp_filtering_profile, name, FOLDER)

        config = {
            "name": name,
            "ipv4": {
                "unicast": {
                    "route_maps": {"inbound": "", "outbound": ""},
                },
                "multicast": {"inherit": True},
            },
            "folder": FOLDER,
        }

        print(f"\n  Creating BGP Filtering Profile: {name}")
        result = client.bgp_filtering_profile.create(config)

        assert isinstance(result, BgpFilteringProfileResponseModel)
        assert result.id is not None
        assert result.name == name
        print(f"  Created: id={result.id}, name={result.name}")

        self.__class__._filter_id = str(result.id)
        self.__class__._filter_name = name
        time.sleep(1)

    def test_03_create_bgp_route_map(self, client, unique_suffix):
        """Create a BGP Route Map with permit and deny entries."""
        name = f"SDK-E2E-BGP-RMAP-{unique_suffix}"
        cleanup_resource(client.bgp_route_map, name, FOLDER)

        config = {
            "name": name,
            "route_map": [
                {
                    "name": 10,
                    "action": "permit",
                    "set": {"local_preference": 200},
                },
                {
                    "name": 20,
                    "action": "deny",
                },
            ],
            "folder": FOLDER,
        }

        print(f"\n  Creating BGP Route Map: {name}")
        result = client.bgp_route_map.create(config)

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id is not None
        assert result.name == name
        print(f"  Created: id={result.id}, name={result.name}")

        self.__class__._rmap_id = str(result.id)
        self.__class__._rmap_name = name
        time.sleep(1)

    def test_04_create_bgp_route_map_redistribution(self, client, unique_suffix):
        """Create a BGP Route Map Redistribution with bgp->ospf crossover."""
        name = f"SDK-E2E-BGP-RMAP-REDIST-{unique_suffix}"
        cleanup_resource(client.bgp_route_map_redistribution, name, FOLDER)

        config = {
            "name": name,
            "bgp": {
                "ospf": {
                    "route_map": [
                        {
                            "name": 10,
                            "action": "permit",
                            "set": {"metric": {"action": "set", "value": 100}, "tag": 500},
                        },
                    ],
                },
            },
            "folder": FOLDER,
        }

        print(f"\n  Creating BGP Route Map Redistribution: {name}")
        result = client.bgp_route_map_redistribution.create(config)

        assert isinstance(result, BgpRouteMapRedistributionResponseModel)
        assert result.id is not None
        assert result.name == name
        print(f"  Created: id={result.id}, name={result.name}")

        self.__class__._rmap_redist_id = str(result.id)
        self.__class__._rmap_redist_name = name
        time.sleep(1)

    # ------------------------------------------------------------------
    # Phase 2: Fetch all profiles by name
    # ------------------------------------------------------------------

    def test_05_fetch_all_profiles(self, client):
        """Fetch each profile by name and verify correct ResponseModel and key fields."""
        time.sleep(2)  # Allow API propagation after creates

        # Fetch BGP Redistribution Profile
        redist = client.bgp_redistribution_profile.fetch(
            name=self.__class__._redist_name, folder=FOLDER
        )
        assert isinstance(redist, BgpRedistributionProfileResponseModel)
        assert redist.name == self.__class__._redist_name
        assert redist.id is not None
        assert redist.ipv4 is not None
        assert redist.ipv4.unicast is not None
        assert redist.ipv4.unicast.static is not None
        assert redist.ipv4.unicast.static.enable is True
        assert redist.ipv4.unicast.static.metric == 100
        assert redist.ipv4.unicast.connected is not None
        assert redist.ipv4.unicast.connected.enable is True
        assert redist.ipv4.unicast.connected.metric == 50
        print(f"\n  Fetched BGP Redistribution Profile: {redist.name}")
        print(
            f"    static: enable={redist.ipv4.unicast.static.enable}, metric={redist.ipv4.unicast.static.metric}"
        )
        print(
            f"    connected: enable={redist.ipv4.unicast.connected.enable}, metric={redist.ipv4.unicast.connected.metric}"
        )

        # Fetch BGP Filtering Profile
        filt = client.bgp_filtering_profile.fetch(name=self.__class__._filter_name, folder=FOLDER)
        assert isinstance(filt, BgpFilteringProfileResponseModel)
        assert filt.name == self.__class__._filter_name
        assert filt.id is not None
        assert filt.ipv4 is not None
        assert filt.ipv4.multicast is not None
        assert filt.ipv4.multicast.inherit is True
        print(f"  Fetched BGP Filtering Profile: {filt.name}")
        print(f"    multicast inherit={filt.ipv4.multicast.inherit}")

        # Fetch BGP Route Map
        rmap = client.bgp_route_map.fetch(name=self.__class__._rmap_name, folder=FOLDER)
        assert isinstance(rmap, BgpRouteMapResponseModel)
        assert rmap.name == self.__class__._rmap_name
        assert rmap.id is not None
        assert rmap.route_map is not None
        assert len(rmap.route_map) == 2
        assert rmap.route_map[0].name == 10
        assert rmap.route_map[0].action == "permit"
        assert rmap.route_map[1].name == 20
        assert rmap.route_map[1].action == "deny"
        print(f"  Fetched BGP Route Map: {rmap.name}")
        print(f"    entries: {len(rmap.route_map)}")
        for entry in rmap.route_map:
            print(f"      seq={entry.name}, action={entry.action}")

        # Fetch BGP Route Map Redistribution
        rmap_redist = client.bgp_route_map_redistribution.fetch(
            name=self.__class__._rmap_redist_name, folder=FOLDER
        )
        assert isinstance(rmap_redist, BgpRouteMapRedistributionResponseModel)
        assert rmap_redist.name == self.__class__._rmap_redist_name
        assert rmap_redist.id is not None
        assert rmap_redist.bgp is not None
        assert rmap_redist.bgp.ospf is not None
        assert rmap_redist.bgp.ospf.route_map is not None
        assert len(rmap_redist.bgp.ospf.route_map) == 1
        entry = rmap_redist.bgp.ospf.route_map[0]
        assert entry.name == 10
        assert entry.action == "permit"
        print(f"  Fetched BGP Route Map Redistribution: {rmap_redist.name}")
        print(f"    bgp->ospf entries: {len(rmap_redist.bgp.ospf.route_map)}")

    # ------------------------------------------------------------------
    # Phase 3: Get by UUID
    # ------------------------------------------------------------------

    def test_06_get_by_id(self, client):
        """Get each profile by its UUID and verify correct ResponseModel."""
        # Get BGP Redistribution Profile
        redist = client.bgp_redistribution_profile.get(self.__class__._redist_id)
        assert isinstance(redist, BgpRedistributionProfileResponseModel)
        assert str(redist.id) == self.__class__._redist_id
        print(f"\n  Got BGP Redistribution Profile by ID: {redist.name} (id={redist.id})")

        # Get BGP Filtering Profile
        filt = client.bgp_filtering_profile.get(self.__class__._filter_id)
        assert isinstance(filt, BgpFilteringProfileResponseModel)
        assert str(filt.id) == self.__class__._filter_id
        print(f"  Got BGP Filtering Profile by ID: {filt.name} (id={filt.id})")

        # Get BGP Route Map
        rmap = client.bgp_route_map.get(self.__class__._rmap_id)
        assert isinstance(rmap, BgpRouteMapResponseModel)
        assert str(rmap.id) == self.__class__._rmap_id
        print(f"  Got BGP Route Map by ID: {rmap.name} (id={rmap.id})")

        # Get BGP Route Map Redistribution
        rmap_redist = client.bgp_route_map_redistribution.get(self.__class__._rmap_redist_id)
        assert isinstance(rmap_redist, BgpRouteMapRedistributionResponseModel)
        assert str(rmap_redist.id) == self.__class__._rmap_redist_id
        print(f"  Got BGP Route Map Redistribution by ID: {rmap_redist.name} (id={rmap_redist.id})")

    # ------------------------------------------------------------------
    # Phase 4: Update BGP Route Map (add third entry)
    # ------------------------------------------------------------------

    def test_07_update_bgp_route_map(self, client):
        """Update the BGP Route Map to add a third entry and verify."""
        from scm.models.network import BgpRouteMapUpdateModel

        rmap = client.bgp_route_map.fetch(name=self.__class__._rmap_name, folder=FOLDER)

        update_data = rmap.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(rmap.id)

        # Add a third route map entry
        update_data["route_map"].append(
            {
                "name": 30,
                "action": "permit",
                "set": {"local_preference": 300},
            }
        )

        update_model = BgpRouteMapUpdateModel(**update_data)
        updated = client.bgp_route_map.update(update_model)

        assert isinstance(updated, BgpRouteMapResponseModel)
        print(f"\n  Updated BGP Route Map: {updated.name}")

        # Re-fetch and verify 3 entries
        time.sleep(1)
        fetched = client.bgp_route_map.fetch(name=self.__class__._rmap_name, folder=FOLDER)
        assert fetched.route_map is not None
        assert len(fetched.route_map) == 3
        seq_numbers = [entry.name for entry in fetched.route_map]
        assert 10 in seq_numbers
        assert 20 in seq_numbers
        assert 30 in seq_numbers
        print(f"  Verified: {len(fetched.route_map)} entries (seq={seq_numbers})")

        # Verify the new entry's set action
        entry_30 = next(e for e in fetched.route_map if e.name == 30)
        assert entry_30.action == "permit"
        assert entry_30.set is not None
        assert entry_30.set.local_preference == 300
        print(
            f"  Entry 30: action={entry_30.action}, local_preference={entry_30.set.local_preference}"
        )

    # ------------------------------------------------------------------
    # Phase 5: Update BGP Redistribution Profile (add OSPF)
    # ------------------------------------------------------------------

    def test_08_update_bgp_redistribution_profile(self, client):
        """Update the BGP Redistribution Profile to add OSPF redistribution."""
        from scm.models.network import BgpRedistributionProfileUpdateModel

        redist = client.bgp_redistribution_profile.fetch(
            name=self.__class__._redist_name, folder=FOLDER
        )

        update_data = redist.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(redist.id)

        # Add OSPF redistribution alongside existing static and connected
        update_data["ipv4"]["unicast"]["ospf"] = {
            "enable": True,
            "metric": 200,
        }

        update_model = BgpRedistributionProfileUpdateModel(**update_data)
        updated = client.bgp_redistribution_profile.update(update_model)

        assert isinstance(updated, BgpRedistributionProfileResponseModel)
        print(f"\n  Updated BGP Redistribution Profile: {updated.name}")

        # Re-fetch and verify all 3 protocols are present
        time.sleep(1)
        fetched = client.bgp_redistribution_profile.fetch(
            name=self.__class__._redist_name, folder=FOLDER
        )
        assert fetched.ipv4 is not None
        assert fetched.ipv4.unicast is not None
        assert fetched.ipv4.unicast.static is not None
        assert fetched.ipv4.unicast.connected is not None
        assert fetched.ipv4.unicast.ospf is not None
        assert fetched.ipv4.unicast.ospf.enable is True
        assert fetched.ipv4.unicast.ospf.metric == 200
        print("  Verified 3 protocols present:")
        print(
            f"    static: enable={fetched.ipv4.unicast.static.enable}, metric={fetched.ipv4.unicast.static.metric}"
        )
        print(
            f"    connected: enable={fetched.ipv4.unicast.connected.enable}, metric={fetched.ipv4.unicast.connected.metric}"
        )
        print(
            f"    ospf: enable={fetched.ipv4.unicast.ospf.enable}, metric={fetched.ipv4.unicast.ospf.metric}"
        )

    # ------------------------------------------------------------------
    # Phase 6: Delete all profiles (reverse order)
    # ------------------------------------------------------------------

    def test_09_delete_all_profiles(self, client):
        """Delete all 4 profiles in reverse order and verify each is deleted."""
        # Delete BGP Route Map Redistribution
        if hasattr(self.__class__, "_rmap_redist_id"):
            client.bgp_route_map_redistribution.delete(self.__class__._rmap_redist_id)
            print(f"\n  Deleted BGP Route Map Redistribution: {self.__class__._rmap_redist_name}")
            time.sleep(1)

        # Delete BGP Route Map
        if hasattr(self.__class__, "_rmap_id"):
            client.bgp_route_map.delete(self.__class__._rmap_id)
            print(f"  Deleted BGP Route Map: {self.__class__._rmap_name}")
            time.sleep(1)

        # Delete BGP Filtering Profile
        if hasattr(self.__class__, "_filter_id"):
            client.bgp_filtering_profile.delete(self.__class__._filter_id)
            print(f"  Deleted BGP Filtering Profile: {self.__class__._filter_name}")
            time.sleep(1)

        # Delete BGP Redistribution Profile
        if hasattr(self.__class__, "_redist_id"):
            client.bgp_redistribution_profile.delete(self.__class__._redist_id)
            print(f"  Deleted BGP Redistribution Profile: {self.__class__._redist_name}")
            time.sleep(1)

        # Verify all cleaned up
        for svc, name in [
            (
                client.bgp_route_map_redistribution,
                getattr(self.__class__, "_rmap_redist_name", None),
            ),
            (client.bgp_route_map, getattr(self.__class__, "_rmap_name", None)),
            (client.bgp_filtering_profile, getattr(self.__class__, "_filter_name", None)),
            (client.bgp_redistribution_profile, getattr(self.__class__, "_redist_name", None)),
        ]:
            if name:
                try:
                    svc.fetch(name=name, folder=FOLDER)
                    print(f"  WARNING: {name} still exists after delete")
                except Exception:
                    print(f"  Confirmed deleted: {name}")
