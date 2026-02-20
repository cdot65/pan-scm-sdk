"""Live E2E tests for Logical Router service with Routing Profiles.

These tests CREATE, READ, UPDATE, and DELETE logical routers against the real SCM API.
They validate that our Pydantic models correctly serialize/deserialize with the live API.

v0.8.0 additions: Creates BGP Auth Profile, OSPF Auth Profile, and BGP Address Family
Profile resources, then wires them into the Logical Router's BGP/OSPF configuration
to validate the cross-service dependency chain.

v0.9.0 additions: Creates BGP Filtering Profile and BGP Route Map resources, then
wires BGP Filtering Profile into the Logical Router's peer group filtering_profile
to validate the v0.9.0 cross-service dependency chain.

Run with:
    PYTHONPATH=. python -m pytest tests/scm/api/test_logical_router_e2e.py -v -s

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
from scm.models.network.logical_router import (
    LogicalRouterResponseModel,
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
def unique_name():
    """Generate a unique name for the test router to avoid collisions."""
    short_id = uuid.uuid4().hex[:6]
    return f"SDK-E2E-LR-{short_id}"


# ---------------------------------------------------------------------------
# Helper to clean up router if it exists
# ---------------------------------------------------------------------------


def cleanup_router(client, name, folder):
    """Delete a logical router by name if it exists."""
    try:
        router = client.logical_router.fetch(name=name, folder=folder)
        client.logical_router.delete(str(router.id))
        logger.info(f"Cleaned up router: {name} (id={router.id})")
        time.sleep(1)
    except Exception:
        pass  # Router doesn't exist, nothing to clean up


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
class TestLogicalRouterE2E:
    """End-to-end tests that CREATE, READ, UPDATE, DELETE logical routers."""

    # ------------------------------------------------------------------
    # Phase 1: List existing logical routers
    # ------------------------------------------------------------------

    def test_01_list_existing_routers(self, client):
        """List existing logical routers to verify API connectivity and model parsing."""
        routers = client.logical_router.list(folder=FOLDER)
        assert isinstance(routers, list)
        print(f"\n  Found {len(routers)} existing logical routers in '{FOLDER}'")
        for router in routers:
            assert isinstance(router, LogicalRouterResponseModel)
            assert router.id is not None
            assert router.name is not None
            vrf_count = len(router.vrf) if router.vrf else 0
            print(
                f"    - {router.name} (id={router.id}, vrf_count={vrf_count}, routing_stack={router.routing_stack})"
            )

    # ------------------------------------------------------------------
    # Phase 2: Create a minimal logical router
    # ------------------------------------------------------------------

    def test_02_create_minimal_router(self, client, unique_name):
        """Create a minimal logical router with just a name and VRF."""
        cleanup_router(client, unique_name, FOLDER)

        config = {
            "name": unique_name,
            "folder": FOLDER,
            "vrf": [
                {
                    "name": "default",
                }
            ],
        }

        print(f"\n  Creating minimal router: {unique_name}")
        router = client.logical_router.create(config)

        assert isinstance(router, LogicalRouterResponseModel)
        assert router.id is not None
        assert router.name == unique_name
        print(f"  Created: id={router.id}, name={router.name}")

        # Store for subsequent tests
        self.__class__._router_id = str(router.id)
        self.__class__._router_name = unique_name

    # ------------------------------------------------------------------
    # Phase 3: Fetch the created router
    # ------------------------------------------------------------------

    def test_03_fetch_created_router(self, client, unique_name):
        """Fetch the router we just created and verify all fields parsed."""
        router = client.logical_router.fetch(name=unique_name, folder=FOLDER)

        assert isinstance(router, LogicalRouterResponseModel)
        assert router.name == unique_name
        assert router.id is not None
        assert router.vrf is not None
        assert len(router.vrf) >= 1
        assert router.vrf[0].name == "default"
        print(f"\n  Fetched router: {router.name}, vrf_count={len(router.vrf)}")

    # ------------------------------------------------------------------
    # Phase 4: Get by ID
    # ------------------------------------------------------------------

    def test_04_get_by_id(self, client):
        """Get the router by its UUID."""
        router_id = self.__class__._router_id
        router = client.logical_router.get(router_id)

        assert isinstance(router, LogicalRouterResponseModel)
        assert str(router.id) == router_id
        print(f"\n  Got by ID: {router.name} (id={router_id})")

    # ------------------------------------------------------------------
    # Phase 5: Update with static routes
    # ------------------------------------------------------------------

    def test_05_update_with_static_routes(self, client, unique_name):
        """Update the router to add static routes to the VRF."""
        router = client.logical_router.fetch(name=unique_name, folder=FOLDER)

        from scm.models.network.logical_router import LogicalRouterUpdateModel

        update_data = router.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(router.id)

        # Add static routes to the default VRF
        for vrf in update_data.get("vrf", []):
            if vrf["name"] == "default":
                vrf["routing_table"] = {
                    "ip": {
                        "static_route": [
                            {
                                "name": "default-route",
                                "destination": "0.0.0.0/0",
                                "nexthop": {"ip_address": "10.0.0.1"},
                                "metric": 10,
                            },
                            {
                                "name": "internal-route",
                                "destination": "192.168.0.0/16",
                                "nexthop": {"ip_address": "10.0.1.1"},
                                "metric": 20,
                                "admin_dist": 15,
                            },
                        ]
                    },
                    "ipv6": {
                        "static_route": [
                            {
                                "name": "ipv6-default",
                                "destination": "::/0",
                                "nexthop": {"ipv6_address": "fd00::1"},
                                "metric": 10,
                            },
                        ]
                    },
                }
                break

        update_model = LogicalRouterUpdateModel(**update_data)
        updated = client.logical_router.update(update_model)

        assert isinstance(updated, LogicalRouterResponseModel)
        print(f"\n  Updated with static routes: {updated.name}")

        # Verify the routes stuck
        fetched = client.logical_router.fetch(name=unique_name, folder=FOLDER)
        default_vrf = next(v for v in fetched.vrf if v.name == "default")

        assert default_vrf.routing_table is not None
        assert default_vrf.routing_table.ip is not None
        ipv4_routes = default_vrf.routing_table.ip.static_route
        assert len(ipv4_routes) == 2
        print(f"  Verified: {len(ipv4_routes)} IPv4 static routes")

        route_names = [r.name for r in ipv4_routes]
        assert "default-route" in route_names
        assert "internal-route" in route_names

        default_rt = next(r for r in ipv4_routes if r.name == "default-route")
        assert default_rt.nexthop.ip_address == "10.0.0.1"
        assert default_rt.metric == 10
        print(
            f"  default-route: nexthop={default_rt.nexthop.ip_address}, metric={default_rt.metric}"
        )

        if default_vrf.routing_table.ipv6 and default_vrf.routing_table.ipv6.static_route:
            ipv6_routes = default_vrf.routing_table.ipv6.static_route
            print(f"  Verified: {len(ipv6_routes)} IPv6 static routes")

    # ------------------------------------------------------------------
    # Phase 5.5: Create routing profile resources (v0.8.0)
    # ------------------------------------------------------------------

    def test_05a_create_bgp_auth_profile(self, client, unique_name):
        """Create a BGP auth profile for use in BGP peer group config."""
        profile_name = f"{unique_name}-bgp-auth"
        cleanup_resource(client.bgp_auth_profile, profile_name, FOLDER)

        profile = client.bgp_auth_profile.create(
            {
                "name": profile_name,
                "secret": "e2eTestSecret123",
                "folder": FOLDER,
            }
        )

        assert profile.id is not None
        assert profile.name == profile_name
        self.__class__._bgp_auth_id = str(profile.id)
        self.__class__._bgp_auth_name = profile_name
        print(f"\n  Created BGP Auth Profile: {profile_name} (id={profile.id})")

    def test_05b_create_ospf_auth_profile(self, client, unique_name):
        """Create an OSPF auth profile for use in OSPF config."""
        profile_name = f"{unique_name}-ospf-auth"
        cleanup_resource(client.ospf_auth_profile, profile_name, FOLDER)

        profile = client.ospf_auth_profile.create(
            {
                "name": profile_name,
                "password": "ospfPas1",
                "folder": FOLDER,
            }
        )

        assert profile.id is not None
        assert profile.name == profile_name
        self.__class__._ospf_auth_id = str(profile.id)
        self.__class__._ospf_auth_name = profile_name
        print(f"\n  Created OSPF Auth Profile: {profile_name} (id={profile.id})")

    def test_05c_create_bgp_address_family_profile(self, client, unique_name):
        """Create a BGP Address Family Profile for peer group AFI/SAFI config."""
        profile_name = f"{unique_name}-bgp-af"
        cleanup_resource(client.bgp_address_family_profile, profile_name, FOLDER)

        profile = client.bgp_address_family_profile.create(
            {
                "name": profile_name,
                "ipv4": {
                    "unicast": {
                        "enable": True,
                        "soft_reconfig_with_stored_info": True,
                    },
                },
                "folder": FOLDER,
            }
        )

        assert profile.id is not None
        assert profile.name == profile_name
        self.__class__._bgp_af_id = str(profile.id)
        self.__class__._bgp_af_name = profile_name
        print(f"\n  Created BGP AF Profile: {profile_name} (id={profile.id})")

    def test_05d_fetch_routing_profiles(self, client):
        """Fetch all three routing profiles and verify model parsing."""
        time.sleep(2)  # Allow API propagation after creates

        bgp_auth = client.bgp_auth_profile.get(self.__class__._bgp_auth_id)
        assert bgp_auth.name == self.__class__._bgp_auth_name
        print(f"\n  Fetched BGP Auth: {bgp_auth.name}")

        ospf_auth = client.ospf_auth_profile.get(self.__class__._ospf_auth_id)
        assert ospf_auth.name == self.__class__._ospf_auth_name
        print(f"  Fetched OSPF Auth: {ospf_auth.name}")

        bgp_af = client.bgp_address_family_profile.get(self.__class__._bgp_af_id)
        assert bgp_af.name == self.__class__._bgp_af_name
        assert bgp_af.ipv4 is not None
        assert bgp_af.ipv4.unicast is not None
        assert bgp_af.ipv4.unicast.enable is True
        print(f"  Fetched BGP AF: {bgp_af.name}, unicast_enabled={bgp_af.ipv4.unicast.enable}")

    # ------------------------------------------------------------------
    # Phase 5.7: Create v0.9.0 routing profile resources
    # ------------------------------------------------------------------

    def test_05e_create_bgp_filtering_profile(self, client, unique_name):
        """Create a BGP Filtering Profile for peer group filtering config (v0.9.0)."""
        profile_name = f"{unique_name}-bgp-filter"
        cleanup_resource(client.bgp_filtering_profile, profile_name, FOLDER)

        profile = client.bgp_filtering_profile.create(
            {
                "name": profile_name,
                "ipv4": {
                    "unicast": {
                        "route_maps": {"inbound": "", "outbound": ""},
                    },
                    "multicast": {"inherit": True},
                },
                "folder": FOLDER,
            }
        )

        assert profile.id is not None
        assert profile.name == profile_name
        self.__class__._bgp_filter_id = str(profile.id)
        self.__class__._bgp_filter_name = profile_name
        print(f"\n  Created BGP Filtering Profile: {profile_name} (id={profile.id})")

    def test_05f_create_bgp_route_map(self, client, unique_name):
        """Create a BGP Route Map resource (v0.9.0)."""
        rmap_name = f"{unique_name}-bgp-rmap"
        cleanup_resource(client.bgp_route_map, rmap_name, FOLDER)

        rmap = client.bgp_route_map.create(
            {
                "name": rmap_name,
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
        )

        assert rmap.id is not None
        assert rmap.name == rmap_name
        self.__class__._bgp_rmap_id = str(rmap.id)
        self.__class__._bgp_rmap_name = rmap_name
        print(f"\n  Created BGP Route Map: {rmap_name} (id={rmap.id})")

    def test_05g_fetch_v090_profiles(self, client):
        """Fetch v0.9.0 routing profiles and verify model parsing."""
        time.sleep(2)  # Allow API propagation after creates

        bgp_filter = client.bgp_filtering_profile.get(self.__class__._bgp_filter_id)
        assert bgp_filter.name == self.__class__._bgp_filter_name
        assert bgp_filter.ipv4 is not None
        print(f"\n  Fetched BGP Filtering Profile: {bgp_filter.name}")
        if bgp_filter.ipv4.multicast:
            print(f"    multicast inherit={bgp_filter.ipv4.multicast.inherit}")

        bgp_rmap = client.bgp_route_map.get(self.__class__._bgp_rmap_id)
        assert bgp_rmap.name == self.__class__._bgp_rmap_name
        assert bgp_rmap.route_map is not None
        assert len(bgp_rmap.route_map) == 2
        print(f"  Fetched BGP Route Map: {bgp_rmap.name}, entries={len(bgp_rmap.route_map)}")

    # ------------------------------------------------------------------
    # Phase 6: Update with BGP configuration + peer groups using profiles
    # ------------------------------------------------------------------

    def test_06_update_with_bgp(self, client, unique_name):
        """Update the router with BGP base config and a peer group referencing routing profiles.

        This validates the cross-service dependency chain:
        Logical Router -> BGP Peer Group -> BGP Address Family Profile (v0.8.0)
        Logical Router -> BGP Peer Group -> BGP Auth Profile (v0.8.0, via connection_options)
        Logical Router -> BGP Peer Group -> BGP Filtering Profile (v0.9.0, via filtering_profile)

        Note: Full peer config with local_address requires real interfaces on the router.
        This test creates a peer group with address_family, connection_options, and
        filtering_profile references but no peers, which validates the profile references
        are accepted by the API.
        """
        router = client.logical_router.fetch(name=unique_name, folder=FOLDER)

        from scm.models.network.logical_router import LogicalRouterUpdateModel

        update_data = router.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(router.id)

        bgp_af_name = self.__class__._bgp_af_name
        bgp_auth_name = self.__class__._bgp_auth_name
        bgp_filter_name = self.__class__._bgp_filter_name

        for vrf in update_data.get("vrf", []):
            if vrf["name"] == "default":
                vrf["bgp"] = {
                    "enable": True,
                    "router_id": "10.0.0.1",
                    "local_as": "65001",
                    "reject_default_route": True,
                    "graceful_restart": {
                        "enable": True,
                        "stale_route_time": 120,
                        "max_peer_restart_time": 120,
                        "local_restart_time": 120,
                    },
                    "peer_group": [
                        {
                            "name": "ibgp-peers",
                            "enable": True,
                            "type": {
                                "ibgp": {},
                            },
                            "address_family": {
                                "ipv4": bgp_af_name,
                            },
                            "filtering_profile": {
                                "ipv4": bgp_filter_name,
                            },
                            "connection_options": {
                                "authentication": bgp_auth_name,
                            },
                        },
                    ],
                }
                break

        update_model = LogicalRouterUpdateModel(**update_data)
        updated = client.logical_router.update(update_model)

        assert isinstance(updated, LogicalRouterResponseModel)
        print(f"\n  Updated with BGP + peer group: {updated.name}")

        # Verify BGP config
        fetched = client.logical_router.fetch(name=unique_name, folder=FOLDER)
        default_vrf = next(v for v in fetched.vrf if v.name == "default")

        assert default_vrf.bgp is not None
        assert default_vrf.bgp.enable is True
        assert default_vrf.bgp.router_id == "10.0.0.1"
        assert default_vrf.bgp.local_as == "65001"
        print(f"  BGP: router_id={default_vrf.bgp.router_id}, local_as={default_vrf.bgp.local_as}")

        if default_vrf.bgp.graceful_restart:
            print(
                f"  BGP GR: enable={default_vrf.bgp.graceful_restart.enable}, stale_route_time={default_vrf.bgp.graceful_restart.stale_route_time}"
            )

        # Verify peer group with routing profile references
        assert default_vrf.bgp.peer_group is not None
        assert len(default_vrf.bgp.peer_group) >= 1
        pg = default_vrf.bgp.peer_group[0]
        assert pg.name == "ibgp-peers"
        print(f"  Peer Group: {pg.name}")
        if pg.address_family:
            print(f"    Address Family IPv4: {pg.address_family.ipv4}")
            assert pg.address_family.ipv4 == bgp_af_name
        if pg.filtering_profile:
            print(f"    Filtering Profile IPv4: {pg.filtering_profile.ipv4}")
            assert pg.filtering_profile.ipv4 == bgp_filter_name
        if pg.connection_options and pg.connection_options.authentication:
            print(f"    Auth Profile: {pg.connection_options.authentication}")
            assert pg.connection_options.authentication == bgp_auth_name

    # ------------------------------------------------------------------
    # Phase 7: Update with OSPF configuration
    # ------------------------------------------------------------------

    def test_07_update_with_ospf(self, client, unique_name):
        """Update the router to add OSPF configuration."""
        router = client.logical_router.fetch(name=unique_name, folder=FOLDER)

        from scm.models.network.logical_router import LogicalRouterUpdateModel

        update_data = router.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(router.id)

        for vrf in update_data.get("vrf", []):
            if vrf["name"] == "default":
                vrf["ospf"] = {
                    "enable": True,
                    "router_id": "10.0.0.1",
                    "area": [
                        {
                            "name": "0.0.0.0",
                            "type": {
                                "normal": {},
                            },
                        },
                    ],
                    "graceful_restart": {
                        "enable": True,
                        "grace_period": 120,
                    },
                }
                break

        update_model = LogicalRouterUpdateModel(**update_data)
        updated = client.logical_router.update(update_model)

        assert isinstance(updated, LogicalRouterResponseModel)
        print(f"\n  Updated with OSPF: {updated.name}")

        # Verify OSPF config
        fetched = client.logical_router.fetch(name=unique_name, folder=FOLDER)
        default_vrf = next(v for v in fetched.vrf if v.name == "default")

        assert default_vrf.ospf is not None
        assert default_vrf.ospf.enable is True
        assert default_vrf.ospf.router_id == "10.0.0.1"
        print(f"  OSPF: router_id={default_vrf.ospf.router_id}")

        assert default_vrf.ospf.area is not None
        assert len(default_vrf.ospf.area) >= 1
        area0 = default_vrf.ospf.area[0]
        assert area0.name == "0.0.0.0"
        print(
            f"  Area: {area0.name}, type={'normal' if area0.type and area0.type.normal is not None else 'other'}"
        )

        # Check if BGP persisted from previous test
        if default_vrf.bgp is not None:
            print(f"  BGP also present: router_id={default_vrf.bgp.router_id}")
        else:
            print("  BGP not present (test_06 may have been skipped or failed)")

    # ------------------------------------------------------------------
    # Phase 8: Update with ECMP configuration
    # ------------------------------------------------------------------

    def test_08_update_with_ecmp(self, client, unique_name):
        """Update the router to add ECMP configuration."""
        router = client.logical_router.fetch(name=unique_name, folder=FOLDER)

        from scm.models.network.logical_router import LogicalRouterUpdateModel

        update_data = router.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(router.id)

        for vrf in update_data.get("vrf", []):
            if vrf["name"] == "default":
                vrf["ecmp"] = {
                    "enable": True,
                    "max_path": 4,
                    "algorithm": {
                        "ip_hash": {
                            "src_only": True,
                            "use_port": True,
                            "hash_seed": 42,
                        },
                    },
                }
                break

        update_model = LogicalRouterUpdateModel(**update_data)
        updated = client.logical_router.update(update_model)

        assert isinstance(updated, LogicalRouterResponseModel)
        print(f"\n  Updated with ECMP: {updated.name}")

        # Verify ECMP config
        fetched = client.logical_router.fetch(name=unique_name, folder=FOLDER)
        default_vrf = next(v for v in fetched.vrf if v.name == "default")

        assert default_vrf.ecmp is not None
        assert default_vrf.ecmp.enable is True
        assert default_vrf.ecmp.max_path == 4
        assert default_vrf.ecmp.algorithm is not None
        assert default_vrf.ecmp.algorithm.ip_hash is not None
        assert default_vrf.ecmp.algorithm.ip_hash.src_only is True
        print(f"  ECMP: max_path={default_vrf.ecmp.max_path}, algorithm=ip_hash(src_only=True)")

    # ------------------------------------------------------------------
    # Phase 9: Update with admin distances
    # ------------------------------------------------------------------

    def test_09_update_admin_distances(self, client, unique_name):
        """Update VRF with custom administrative distances."""
        router = client.logical_router.fetch(name=unique_name, folder=FOLDER)

        from scm.models.network.logical_router import LogicalRouterUpdateModel

        update_data = router.model_dump(exclude_none=True, by_alias=True)
        update_data["id"] = str(router.id)

        for vrf in update_data.get("vrf", []):
            if vrf["name"] == "default":
                vrf["admin_dists"] = {
                    "static": 10,
                    "static_ipv6": 10,
                    "ospf_inter": 110,
                    "ospf_intra": 110,
                    "ospf_ext": 150,
                    "bgp_internal": 200,
                    "bgp_external": 20,
                    "bgp_local": 200,
                }
                break

        update_model = LogicalRouterUpdateModel(**update_data)
        updated = client.logical_router.update(update_model)

        assert isinstance(updated, LogicalRouterResponseModel)
        print(f"\n  Updated admin distances: {updated.name}")

        fetched = client.logical_router.fetch(name=unique_name, folder=FOLDER)
        default_vrf = next(v for v in fetched.vrf if v.name == "default")

        assert default_vrf.admin_dists is not None
        assert default_vrf.admin_dists.static == 10
        assert default_vrf.admin_dists.bgp_external == 20
        assert default_vrf.admin_dists.ospf_inter == 110
        print(
            f"  Admin dists: static={default_vrf.admin_dists.static}, bgp_ext={default_vrf.admin_dists.bgp_external}, ospf_inter={default_vrf.admin_dists.ospf_inter}"
        )

    # ------------------------------------------------------------------
    # Phase 10: Verify complete round-trip with model_dump
    # ------------------------------------------------------------------

    def test_10_verify_complete_roundtrip(self, client, unique_name):
        """Fetch the fully configured router and verify the complete model parses."""
        router = client.logical_router.fetch(name=unique_name, folder=FOLDER)

        assert isinstance(router, LogicalRouterResponseModel)
        print("\n  Complete router state:")
        print(f"    Name: {router.name}")
        print(f"    ID: {router.id}")
        print(f"    Folder: {router.folder}")
        print(f"    Routing Stack: {router.routing_stack}")
        print(f"    VRFs: {len(router.vrf)}")

        for vrf in router.vrf:
            print(f"\n    VRF: {vrf.name}")
            if vrf.interface:
                print(f"      Interfaces: {vrf.interface}")
            if vrf.admin_dists:
                print(f"      Admin dists: static={vrf.admin_dists.static}")
            if vrf.routing_table and vrf.routing_table.ip and vrf.routing_table.ip.static_route:
                for rt in vrf.routing_table.ip.static_route:
                    nh = "N/A"
                    if rt.nexthop:
                        if rt.nexthop.ip_address:
                            nh = rt.nexthop.ip_address
                        elif rt.nexthop.ipv6_address:
                            nh = rt.nexthop.ipv6_address
                    print(f"      Static route: {rt.name} -> {rt.destination} via {nh}")
            if vrf.ospf:
                print(
                    f"      OSPF: router_id={vrf.ospf.router_id}, areas={len(vrf.ospf.area) if vrf.ospf.area else 0}"
                )
            if vrf.bgp:
                print(
                    f"      BGP: AS={vrf.bgp.local_as}, peer_groups={len(vrf.bgp.peer_group) if vrf.bgp.peer_group else 0}"
                )
                if vrf.bgp.peer_group:
                    for pg in vrf.bgp.peer_group:
                        peers = len(pg.peer) if pg.peer else 0
                        print(f"        PeerGroup: {pg.name} ({peers} peers)")
            if vrf.ecmp:
                print(f"      ECMP: enabled={vrf.ecmp.enable}, max_path={vrf.ecmp.max_path}")

        # Verify model_dump round-trip
        dumped = router.model_dump(exclude_unset=True, by_alias=True)
        assert "name" in dumped
        assert "vrf" in dumped
        assert "id" in dumped
        print(f"\n  model_dump() produced {len(str(dumped))} chars of JSON-ready data")

    # ------------------------------------------------------------------
    # Phase 11: List with routing_stack filter
    # ------------------------------------------------------------------

    def test_11_list_with_filter(self, client):
        """Test listing routers with routing_stack filter."""
        all_routers = client.logical_router.list(folder=FOLDER)

        if all_routers:
            # Check if any routers have a routing_stack value
            stacks = set()
            for r in all_routers:
                if r.routing_stack:
                    stacks.add(
                        r.routing_stack.value
                        if hasattr(r.routing_stack, "value")
                        else str(r.routing_stack)
                    )
            print(f"\n  Found routing_stack values: {stacks}")

    # ------------------------------------------------------------------
    # Phase 12: Delete the router (cleanup)
    # ------------------------------------------------------------------

    def test_12_delete_router(self, client, unique_name):
        """Delete the test router and verify it's gone."""
        router = client.logical_router.fetch(name=unique_name, folder=FOLDER)
        router_id = str(router.id)

        client.logical_router.delete(router_id)
        print(f"\n  Deleted router: {unique_name} (id={router_id})")

        # Verify deletion
        time.sleep(1)
        try:
            client.logical_router.fetch(name=unique_name, folder=FOLDER)
            pytest.fail(f"Router {unique_name} should have been deleted")
        except Exception as e:
            print(f"  Confirmed deleted (fetch raised: {type(e).__name__})")

    # ------------------------------------------------------------------
    # Phase 13: Delete routing profiles (cleanup, v0.8.0 + v0.9.0)
    # ------------------------------------------------------------------

    def test_13_delete_routing_profiles(self, client):
        """Delete the routing profile resources created for this E2E test."""
        # Delete v0.9.0 profiles first (no dependencies)
        if hasattr(self.__class__, "_bgp_rmap_id"):
            client.bgp_route_map.delete(self.__class__._bgp_rmap_id)
            print(f"\n  Deleted BGP Route Map: {self.__class__._bgp_rmap_name}")

        if hasattr(self.__class__, "_bgp_filter_id"):
            client.bgp_filtering_profile.delete(self.__class__._bgp_filter_id)
            print(f"  Deleted BGP Filtering Profile: {self.__class__._bgp_filter_name}")

        # Delete v0.8.0 profiles
        if hasattr(self.__class__, "_bgp_af_id"):
            client.bgp_address_family_profile.delete(self.__class__._bgp_af_id)
            print(f"  Deleted BGP AF Profile: {self.__class__._bgp_af_name}")

        if hasattr(self.__class__, "_ospf_auth_id"):
            client.ospf_auth_profile.delete(self.__class__._ospf_auth_id)
            print(f"  Deleted OSPF Auth Profile: {self.__class__._ospf_auth_name}")

        if hasattr(self.__class__, "_bgp_auth_id"):
            client.bgp_auth_profile.delete(self.__class__._bgp_auth_id)
            print(f"  Deleted BGP Auth Profile: {self.__class__._bgp_auth_name}")

        # Verify all cleaned up
        time.sleep(1)
        for svc, name in [
            (client.bgp_route_map, getattr(self.__class__, "_bgp_rmap_name", None)),
            (client.bgp_filtering_profile, getattr(self.__class__, "_bgp_filter_name", None)),
            (client.bgp_auth_profile, getattr(self.__class__, "_bgp_auth_name", None)),
            (client.ospf_auth_profile, getattr(self.__class__, "_ospf_auth_name", None)),
            (client.bgp_address_family_profile, getattr(self.__class__, "_bgp_af_name", None)),
        ]:
            if name:
                try:
                    svc.fetch(name=name, folder=FOLDER)
                    print(f"  WARNING: {name} still exists after delete")
                except Exception:
                    print(f"  Confirmed deleted: {name}")
