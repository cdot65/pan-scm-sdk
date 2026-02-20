# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.9.0] - 2026-02-20

### Added
- **BGP Filtering Profile**: New `scm.bgp_filtering_profile` service for managing BGP filtering profiles with inbound/outbound filter lists, network filters, route maps, and conditional advertisement. Supports full CRUD operations against `/config/network/v1/bgp-filtering-profiles`. Includes multicast oneOf pattern (inherit vs explicit filter configuration).
- **BGP Redistribution Profile**: New `scm.bgp_redistribution_profile` service for managing BGP redistribution profiles that control route redistribution between protocols (static, OSPF, connected). Supports full CRUD operations against `/config/network/v1/bgp-redistribution-profiles`. All three protocol redistributions can coexist (non-mutually-exclusive).
- **BGP Route Map**: New `scm.bgp_route_map` service for managing BGP route maps with sequenced entries containing match/set criteria for import/export policy control. Supports full CRUD operations against `/config/network/v1/bgp-route-maps`. Complex match criteria (AS path, communities, origin, metric, peer, IPv4) and set actions (local preference, weight, metric, communities, aggregator).
- **BGP Route Map Redistribution**: New `scm.bgp_route_map_redistribution` service for managing BGP route map redistribution rules with protocol-specific crossover patterns. Supports full CRUD operations against `/config/network/v1/bgp-route-map-redistributions`. 31 Pydantic model classes implementing 2-level oneOf discrimination across 7 crossover variants (BGP->OSPF, BGP->RIB, OSPF->BGP, OSPF->RIB, Connected/Static->BGP, Connected/Static->OSPF, Connected/Static->RIB).
- Added 336 new tests (220 model validation + 116 service tests) across 8 test files

## [0.8.0] - 2026-02-18

### Added
- **Route Access List**: New `scm.route_access_list` service for managing route access lists that filter routes by network/mask. Supports get, update, list, and fetch operations (no-POST pattern) against `/config/network/v1/route-access-lists`.
- **Route Prefix List**: New `scm.route_prefix_list` service for managing route prefix lists with prefix-based route filtering including ge/le constraints. Supports get, update, list, and fetch operations against `/config/network/v1/route-prefix-lists`.
- **BGP Authentication Profile**: New `scm.bgp_auth_profile` service for managing BGP authentication profiles (MD5 authentication for BGP sessions). Supports get, update, list, and fetch operations against `/config/network/v1/bgp-auth-profiles`.
- **OSPF Authentication Profile**: New `scm.ospf_auth_profile` service for managing OSPF authentication profiles with MD5 key list and simple password authentication modes (mutually exclusive). Supports get, update, list, and fetch operations against `/config/network/v1/ospf-auth-profiles`.
- **BGP Address Family Profile**: New `scm.bgp_address_family_profile` service for managing BGP address family profiles with IPv4/IPv6 unicast/multicast configuration including allowas_in, maximum_prefix, next_hop, remove_private_AS, send_community, and ORF settings. Supports get, update, list, and fetch operations against `/config/network/v1/bgp-address-family-profiles`.
- Added 269 new tests (165 model validation + 104 service tests) across 10 test files

## [0.7.0] - 2026-02-18

### Added
- **Logical Router**: New `scm.logical_router` service for managing logical routers - the most complex networking service with VRF-based routing configuration. Supports full CRUD operations (create, get, update, delete, list, fetch) against the `/config/network/v1/logical-routers` endpoint.
  - 93 Pydantic model classes covering VRF, static routes (IPv4/IPv6), OSPF, BGP, ECMP, RIP, and administrative distance configuration
  - 20 `model_validator` implementations for oneOf discriminator patterns (nexthop types, OSPF area types, ECMP algorithms, BGP peer group types, etc.)
  - IPv4 static routes support 8 nexthop types: receive, discard, ip_address, ipv6_address, fqdn, next_lr, next_vr, tunnel
  - IPv6 static routes support 7 nexthop types (no ip_address)
  - BGP configuration with peer groups, peers, aggregate routes, redistribution rules, and policy import/export
  - OSPF configuration with areas (normal/stub/NSSA), interfaces, virtual links, authentication profiles, and export rules
  - ECMP with 4 algorithm options: ip_modulo, ip_hash, weighted_round_robin, balanced_round_robin
  - RIP with interface-level configuration including mode, split horizon, and distribute lists
  - Multicast and OSPFv3 configurations accepted as `Dict[str, Any]` for forward compatibility
  - `routing_stack` filter support on `list()` for filtering by "legacy" or "advanced" routing stack
- Added 134 new tests (106 model validation + 28 service CRUD tests)

## [0.6.0] - 2026-02-17

### Added
- **Interface Management Profile**: New `scm.interface_management_profile` service for managing interface management profiles (HTTPS, SSH, ping, SNMP access control). Full CRUD with kebab-case field alias support.
- **Zone Protection Profile**: New `scm.zone_protection_profile` service for managing zone protection profiles with deeply nested flood protection, scan protection, packet-based attack protection, IPv6 protection, and non-IP protocol filtering.
- **DHCP Interface**: New `scm.dhcp_interface` service for configuring DHCP server and relay settings on interfaces, with server/relay mutual exclusivity validation.
- **IPsec Tunnel**: New `scm.ipsec_tunnel` service for managing IPsec tunnel objects, completing the VPN stack alongside existing IKE crypto, IKE gateway, and IPsec crypto profile services.

### Changed
- Added 233 new tests across 8 test files (4 service tests + 4 model tests)
- All new ResponseModels use `extra="ignore"` pattern established in v0.5.0

## [0.5.1] - 2026-02-17

### Fixed
- **DeviceResponseModel & ApplicationResponseModel**: Restored `extra="allow"` on these two models that intentionally expose undocumented API fields via `__pydantic_extra__`. The v0.5.0 migration incorrectly changed them to `extra="ignore"` which silently dropped extra fields.

## [0.5.0] - 2026-02-17

### Fixed
- **EthernetInterface.list()**: Added missing `slot: Optional[int]` field to `EthernetInterfaceBaseModel` that caused `ValidationError` when the API returned slot data (PA-5000/PA-7000 series)
- **tag.list()**: Fixed validation errors caused by `extra="forbid"` rejecting unknown fields in API responses
- **snippet.associate_folder()**: Now raises `NotImplementedError` immediately instead of making a failing API call and masking the 404 error

### Changed
- **Response Model Resilience**: Migrated all 50 `*ResponseModel` classes from `extra="forbid"` to `extra="ignore"` so the SDK gracefully handles new fields added by the SCM API. `*CreateModel` and `*UpdateModel` classes retain `extra="forbid"` for strict input validation.
- Updated 41 test methods to validate the new `extra="ignore"` behavior on response models

## [0.4.0] - 2024-12-20

### Added
- Bearer token authentication support for stateless automation scenarios
- New `access_token` parameter in Scm and ScmClient constructors
- Example scripts demonstrating bearer token usage
- Unit and integration tests for bearer token functionality
- Support for Ansible and other automation frameworks

### Changed
- Comprehensive documentation updates for setup services (device, folder, label, snippet, variable)
- All documentation now uses unified ScmClient interface pattern
- Update examples use fetch → dot notation → update workflow
- Added Default column to all model attribute tables
- Added Filter Parameters tables documenting server-side and client-side filters
- Expanded Related Models sections with links to all model types
- Added Variable Types and Enum documentation throughout

### Fixed
- Documentation inconsistencies between config class and model docs
- Corrected parameter types in Core Methods tables

## [0.3.14] - 2025-02-28

### Added
- Unified client interface that allows attribute-based access to services
- New example demonstrating the unified client pattern
- New `ScmClient` class as an alias for `Scm`
- Added comprehensive tests for the unified client functionality

### Changed
- Updated documentation to demonstrate both traditional and unified client patterns
- Updated version number in pyproject.toml

## [0.3.13] - 2025-02-22

### Added
- Support for HTTP Server Profiles
- Integration with CI/CD
- More tests

## [0.3.12] - 2025-02-15

### Fixed
- DNS Security profiles list method fixed

## [0.3.11] - 2025-02-04

### Added
- Added Anti Spyware Profile model
- Improved error handling
- Various bug fixes
