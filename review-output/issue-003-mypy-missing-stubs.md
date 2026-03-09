# [lint] Install missing mypy type stubs for requests and oauthlib

**Labels:** `enhancement`, `lint`

## Problem

mypy reports 8 errors across 3 files due to missing library stubs for `requests`, `oauthlib`, and `requests_oauthlib`.

## Location

- `scm/insights/__init__.py:7` — missing `types-requests`
- `scm/auth.py:17-21` — missing `types-oauthlib`, `types-requests`, `types-requests-oauthlib`
- `scm/client.py:19,115` — missing `types-requests`

## Suggested Fix

Add type stub packages to dev dependencies:
```
poetry add --group dev types-requests types-oauthlib types-requests-oauthlib
```

Alternatively, add `ignore_missing_imports = True` for these specific modules in `mypy.ini`.

## Acceptance Criteria

- [ ] `mypy --config-file mypy.ini scm` passes with zero errors
- [ ] Type stubs added to `pyproject.toml` dev dependencies
- [ ] All existing tests pass
