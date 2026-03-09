# [tests] Add missing factory files for 25 network services and 2 mobile_agent services

**Labels:** `enhancement`, `tests`

## Problem

25 out of 30 network services and both mobile_agent services have no test factory files. Factories are essential for consistent test data generation and TDD workflows.

## Location

**Network services missing factories (25):**
- `aggregate_interface`, `bgp_address_family_profile`, `bgp_auth_profile`, `bgp_filtering_profile`
- `bgp_redistribution_profile`, `bgp_route_map`, `bgp_route_map_redistribution`
- `dhcp_interface`, `ethernet_interface`, `ike_crypto_profile`, `ike_gateway`
- `interface_management_profile`, `ipsec_crypto_profile`, `ipsec_tunnel`
- `layer2_subinterface`, `layer3_subinterface`, `logical_router`, `loopback_interface`
- `ospf_auth_profile`, `route_access_list`, `route_prefix_list`, `security_zone`
- `tunnel_interface`, `vlan_interface`, `zone_protection_profile`

**Mobile agent services missing factories (2):**
- `agent_versions`, `auth_settings`

**Security service missing factory (1):**
- `authentication_rule`

## Suggested Fix

Create factory files in `tests/factories/network/`, `tests/factories/mobile_agent/`, and `tests/factories/security/` following the established patterns (see `tests/factories/objects/address.py` for reference). Each factory should:
- Use `factory.Factory` or `factory.DictFactory`
- Mirror the corresponding Pydantic model fields
- Include base, create, update, and response variants

## Acceptance Criteria

- [ ] All 30 network services have factory files
- [ ] Both mobile_agent services have factory files
- [ ] `authentication_rule` security factory exists
- [ ] Factory fields match corresponding Pydantic model fields
- [ ] All existing tests still pass
