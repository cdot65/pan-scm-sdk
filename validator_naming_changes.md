# Validator Method Naming Standardization

## Overview
This document summarizes the changes made to standardize validator method naming across the Palo Alto Networks Strata Cloud Manager (SCM) SDK codebase. The goal was to follow consistent naming patterns to improve code clarity and maintainability.

## Naming Convention Guidelines

We followed these naming conventions:
- `validate_*` for general validation methods
- `ensure_*` for methods that enforce specific constraints
- `convert_*` for methods that transform or convert data

## Changes Made

### 1. Renamed `check_*` Methods

Methods that were prefixed with "check_" have been renamed to more descriptive names that better indicate their purpose:

| File | Old Name | New Name |
|------|----------|----------|
| `scm/models/security/anti_spyware_profiles.py` | `check_action` | `validate_action` |
| `scm/models/security/anti_spyware_profiles.py` | `check_and_transform_action` | `convert_action` |
| `scm/models/security/dns_security_profiles.py` | `check_and_transform_action` | `convert_action` |
| `scm/models/security/vulnerability_protection_profiles.py` | `check_action` | `validate_action` |
| `scm/models/security/vulnerability_protection_profiles.py` | `check_and_transform_action` | `convert_action` |

### 2. Standardized Container Validation Methods

Methods that validate exactly one container type is provided have been consistently renamed to `validate_container_type`:

| File | Old Name | New Name |
|------|----------|----------|
| `scm/models/security/security_rules.py` | `validate_container` | `validate_container_type` |
| `scm/models/security/decryption_profiles.py` | `validate_container` | `validate_container_type` |
| `scm/models/security/anti_spyware_profiles.py` | `validate_container` | `validate_container_type` |
| `scm/models/security/dns_security_profiles.py` | `validate_container` | `validate_container_type` |
| `scm/models/security/vulnerability_protection_profiles.py` | `validate_container` | `validate_container_type` |
| `scm/models/security/url_categories.py` | `validate_container` | `validate_container_type` |
| `scm/models/security/wildfire_antivirus_profiles.py` | `validate_container` | `validate_container_type` |
| `scm/models/network/ike_crypto_profile.py` | `validate_container` | `validate_container_type` |
| `scm/models/network/nat_rules.py` | `validate_container` | `validate_container_type` |
| `scm/models/network/ipsec_crypto_profile.py` | `validate_container` | `validate_container_type` |
| `scm/models/network/ike_gateway.py` | `validate_container` | `validate_container_type` |
| `scm/models/network/security_zone.py` | `validate_container` | `validate_container_type` |

### 3. Made Schedule Validation Method Names Consistent

In the `scm/models/objects/schedules.py` file:

| Old Name | New Name |
|----------|----------|
| `validate_at_least_one_day` | `ensure_at_least_one_day` |
| `validate_exactly_one_type` | `ensure_exactly_one_type` |
| `validate_datetime_ranges` | `validate_time_ranges` |

### 4. Renamed Generic Method Names

Methods with generic names have been renamed to better describe their purpose:

| File | Old Name | New Name |
|------|----------|----------|
| `scm/models/auth.py` | `construct_scope` | `convert_scope` |
| `scm/models/network/ipsec_crypto_profile.py` | `convert_string_to_enum` | `convert_enum_values` |

## Testing
All tests pass after these changes, confirming that the renamed methods maintain the same functionality.

## Benefits

These naming standardizations provide the following benefits:
1. **Improved readability** - Names more clearly indicate the purpose of the method
2. **Enhanced maintainability** - Consistent naming patterns make it easier to understand the codebase
3. **Better documentation** - Method names now serve as implicit documentation
4. **Easier onboarding** - New developers can more quickly understand the validation patterns
