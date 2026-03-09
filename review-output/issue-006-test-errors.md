# [tests] Fix 12 test errors in test_address.py and test_snippet.py

**Labels:** `bug`, `tests`

## Problem

12 tests produce errors (not failures — likely import or fixture issues):

**test_address.py (1 error):**
- `TestAddressDeleteErrorHandling::test_delete_logs_error_on_non_404`

**test_snippet.py (11 errors):**
- `TestSnippetFetchSingleMatch::test_fetch_returns_none_when_no_results`
- `TestSnippetFetchSingleMatch::test_fetch_returns_none_when_no_exact_match`
- `TestSnippetFetchSingleMatch::test_fetch_returns_first_exact_match`
- `TestSnippetListEdgeCases::test_list_invalid_response_format`
- `TestSnippetListEdgeCases::test_list_single_object_no_data_key`
- `TestSnippetListEdgeCases::test_list_data_key_not_list`
- `TestSnippetListEdgeCases::test_list_pagination_offset_increment`
- `TestSnippetListEdgeCases::test_list_labels_param_passed_to_api`
- `TestSnippetListEdgeCases::test_list_types_param_passed_to_api`
- `TestSnippetFetchEdgeCases::test_fetch_returns_none_when_no_results`
- `TestSnippetFetchEdgeCases::test_fetch_returns_first_match`

## Location

- `tests/scm/config/objects/test_address.py`
- `tests/scm/config/setup/test_snippet.py`

## Suggested Fix

Investigate the error tracebacks. These are likely fixture/mock setup issues (not assertion failures). Run with `-v --tb=long` to diagnose root cause.

## Acceptance Criteria

- [ ] All 12 erroring tests pass cleanly
- [ ] No regressions in the remaining 6000 passing tests
- [ ] `pytest -m "not api" tests/` shows 0 errors
