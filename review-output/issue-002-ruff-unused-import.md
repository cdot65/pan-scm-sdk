# [lint] Remove unused import in test_aggregate_interface_models.py

**Labels:** `enhancement`, `lint`

## Problem

Ruff detected 1 unused import (F401):

`AggregateLayer2` is imported but unused in `tests/scm/models/network/test_aggregate_interface_models.py` at line 12.

## Location

- `tests/scm/models/network/test_aggregate_interface_models.py:12`

## Suggested Fix

Remove the unused import `AggregateLayer2` from the import statement.

## Acceptance Criteria

- [ ] `ruff check scm tests` passes with zero errors
- [ ] All existing tests still pass
