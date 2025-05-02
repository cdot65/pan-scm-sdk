# Validator Method Naming Inconsistency Report

This report identifies validator methods with inconsistent naming patterns across the codebase. Methods are grouped by naming pattern to facilitate bulk updates.

## Recommended Naming Conventions
- `validate_*` for general validation
- `ensure_*` for enforcing specific constraints
- `convert_*` for type conversion

## Methods to Rename

### Generic Method Names That Need More Specific Naming

| File Path | Current Method Name | Recommended Name |
|-----------|-------------------|-----------------|
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/auth.py` | `construct_scope` | `convert_scope` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/anti_spyware_profiles.py` | `check_action` | `validate_action` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/dns_security_profiles.py` | `check_and_transform_action` | `convert_action` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/vulnerability_protection_profiles.py` | `check_and_transform_action` | `convert_action` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/vulnerability_protection_profiles.py` | `check_action` | `validate_action` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ipsec_crypto_profile.py` | `convert_string_to_enum` | `convert_enum_values` |

### Methods Performing Type Conversion But Not Named with 'convert_*'

| File Path | Current Method Name | Recommended Name |
|-----------|-------------------|-----------------|
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/nat_rules.py` | `convert_boolean_to_enum` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ipsec_crypto_profile.py` | `convert_string_to_enum` | ✓ Already follows convention |

### Methods Using 'ensure_*' Prefix Correctly

| File Path | Current Method Name | Recommended Name |
|-----------|-------------------|-----------------|
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/address.py` | `ensure_list_of_strings` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/address.py` | `ensure_unique_items` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/regions.py` | `ensure_list_of_strings` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/regions.py` | `ensure_unique_addresses` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/regions.py` | `ensure_unique_tags` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/dynamic_user_group.py` | `ensure_list_of_strings` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/dynamic_user_group.py` | `ensure_unique_items` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/address_group.py` | `ensure_list_of_strings` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/address_group.py` | `ensure_unique_items` | ✓ Already follows convention |

### Methods Validating Container Types That Need Consistent Naming

| File Path | Current Method Name | Recommended Name |
|-----------|-------------------|-----------------|
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/security_rules.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/decryption_profiles.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/anti_spyware_profiles.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/dns_security_profiles.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/wildfire_antivirus_profiles.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/url_categories.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/vulnerability_protection_profiles.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ike_crypto_profile.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/nat_rules.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ipsec_crypto_profile.py` | `validate_container` | `validate_container_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ike_gateway.py` | `validate_container` | `validate_container_type` |

### Methods with Inconsistent Naming in Schedule Validations

| File Path | Current Method Name | Recommended Name |
|-----------|-------------------|-----------------|
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/schedules.py` | `validate_time_ranges` (repeated for different fields) | `validate_time_ranges` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/schedules.py` | `validate_at_least_one_day` | `ensure_at_least_one_day` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/schedules.py` | `validate_exactly_one_type` (repeated) | `ensure_exactly_one_type` |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/schedules.py` | `validate_datetime_ranges` | `validate_time_ranges` (for consistency) |

### Methods Validating Model-Specific Logic

| File Path | Current Method Name | Recommended Name |
|-----------|-------------------|-----------------|
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/security_rules.py` | `validate_move_configuration` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/security/decryption_profiles.py` | `validate_versions` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/nat_rules.py` | `validate_dynamic_ip_and_port` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/nat_rules.py` | `validate_source_translation` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/nat_rules.py` | `validate_nat64_dns_rewrite_compatibility` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/nat_rules.py` | `validate_bidirectional_nat_compatibility` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/nat_rules.py` | `validate_move_configuration` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ipsec_crypto_profile.py` | `validate_security_protocol` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ike_gateway.py` | `validate_auth_method` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ike_gateway.py` | `validate_protocol_config` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/ike_gateway.py` | `validate_peer_address` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/network/security_zone.py` | `validate_network_type` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/address.py` | `validate_address_type` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/service.py` | `validate_protocol` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/external_dynamic_lists.py` | `validate_predefined_snippet` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/log_forwarding_profile.py` | `validate_id_for_non_predefined` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/objects/address_group.py` | `validate_address_group_type` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/deployment/remote_networks.py` | `validate_remote_network_logic` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/deployment/bgp_routing.py` | `validate_routing_preference_type` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/deployment/bgp_routing.py` | `validate_update_model` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/deployment/internal_dns_servers.py` | `validate_create_model` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/deployment/internal_dns_servers.py` | `validate_update_model` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/deployment/internal_dns_servers.py` | `validate_response_model` | ✓ Already follows convention |
| `/Users/cdot/development/cdot65/pan-scm-sdk/scm/models/mobile_agent/auth_settings.py` | `validate_destination_required` | ✓ Already follows convention |

## Summary of Recommendations

1. **Change `check_*` to `validate_*` or `convert_*`**: Methods that check and validate data should use the `validate_*` prefix, while methods that also transform data should use the `convert_*` prefix.

2. **Standardize container validation methods**: All methods that validate container types should be consistently named `validate_container_type`.

3. **Make schedule validations consistent**: The schedule validation methods should use consistent naming, with constraint enforcement using the `ensure_*` prefix.

4. **Address the generic method names**: Methods with generic names like `construct_scope` should be renamed to more clearly indicate their purpose.
