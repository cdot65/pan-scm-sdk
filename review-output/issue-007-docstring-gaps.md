# [docs] Add missing Args/Returns sections to docstrings in service and model files

**Labels:** `documentation`, `enhancement`

## Problem

Multiple service and model files have incomplete Google-style docstrings — missing `Args:` or `Returns:` sections on public methods with parameters and return types.

## Location

**Service classes missing `Args:` on CRUD methods (6 files):**
- `scm/config/deployment/remote_networks.py` — `create()`, `get()`
- `scm/config/identity/authentication_profile.py` — `create()`, `get()`
- `scm/config/identity/kerberos_server_profile.py` — `create()`, `get()`
- `scm/config/identity/ldap_server_profile.py` — `create()`, `get()`
- `scm/config/identity/radius_server_profile.py` — `create()`, `get()`
- `scm/config/identity/saml_server_profile.py` — `create()`, `get()`

**Model files missing `Args:`/`Returns:` on validators (11+ files):**
- `scm/models/deployment/bgp_routing.py`
- `scm/models/deployment/internal_dns_servers.py`
- `scm/models/insights/alerts.py`
- `scm/models/mobile_agent/auth_settings.py`
- `scm/models/network/ipsec_crypto_profile.py`
- `scm/models/network/nat_rules.py`
- `scm/models/objects/schedules.py`
- `scm/models/operations/candidate_push.py`
- `scm/models/security/decryption_profiles.py`
- `scm/models/setup/snippet.py`
- `scm/models/setup/variable.py`

## Suggested Fix

Add `Args:` and `Returns:` sections following Google-style docstring format. Use `scm/config/objects/address.py` and `scm/auth.py` as reference examples.

## Acceptance Criteria

- [ ] All public CRUD methods have `Args:` and `Returns:` sections
- [ ] `ruff check --select D scm` produces no new docstring violations
- [ ] Docstrings accurately reflect method signatures and types
