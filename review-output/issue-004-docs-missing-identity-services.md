# [docs] Add documentation for identity services and missing security services

**Labels:** `documentation`

## Problem

11 implemented and registered services are missing from documentation:

**Identity Services (6 — completely undocumented):**
- `authentication_profile`
- `kerberos_server_profile`
- `ldap_server_profile`
- `radius_server_profile`
- `saml_server_profile`
- `tacacs_server_profile`

**Security Services (5 — missing from README table):**
- `app_override_rule`
- `authentication_rule`
- `decryption_rule`
- `file_blocking_profile`
- `url_access_profile`

## Location

- `README.md` — "Available Client Services" table is incomplete
- `mkdocs.yml` — no nav entries for identity services
- `docs/sdk/config/` — no doc files for identity services
- `CLAUDE.md` — architecture diagram missing `identity/` and `mobile_agent/` directories

## Suggested Fix

1. Add all 6 identity services to README "Available Client Services" table
2. Add 5 missing security services to README table
3. Create doc pages in `docs/sdk/config/identity_services/` for each identity service
4. Add identity services nav section to `mkdocs.yml`
5. Update CLAUDE.md architecture diagram to include `identity/`, `mobile_agent/`, and `setup/` directories

## Acceptance Criteria

- [ ] README lists all 76 registered services
- [ ] mkdocs.yml nav includes identity services section
- [ ] Each identity service has a documentation page
- [ ] CLAUDE.md architecture diagram is complete and accurate
- [ ] `mkdocs build` succeeds without warnings
