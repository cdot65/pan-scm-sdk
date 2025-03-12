# Test Restructuring Proposal

## Current Structure Analysis

Your current test organization follows a structure that mirrors your codebase organization:

- Tests for SDK services are in `tests/scm/config/...`
- Tests for Pydantic models are in `tests/scm/models/...`
- Integration tests are mixed with unit tests in class-based test files

This is a solid foundation, but we can reorganize tests to focus on test types rather than the structure of the code being tested. This will make it easier to run specific types of tests and understand test coverage by functionality.

## Proposed Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual functions, classes, and methods in isolation
**Characteristics**: Fast, focused, no external dependencies

```
tests/unit/
  models/  # Tests for Pydantic models
    test_address_models.py
    test_security_rule_models.py
    ...
  config/  # Tests for service class methods
    test_address_validation.py
    test_security_rule_validation.py
    ...
  utils/  # Tests for utility functions
    test_logging.py
    test_tag_colors.py
  exceptions/
    test_exception_hierarchy.py
```

Example from your codebase:
- Tests in `test_address_models.py` that validate Pydantic model constraints
- Tests that verify filtering logic in the `Address._apply_filters` method

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test how components work together
**Characteristics**: Test interactions between parts of the SDK

```
tests/integration/
  client/
    test_auth_client_integration.py
    test_client_request_handling.py
  config/
    objects/
      test_address_service_integration.py
    security/
      test_security_rule_service_integration.py
  models/
    test_model_serialization.py
```

Example from your codebase:
- Tests in `TestOAuth2Client` that verify token refresh and authentication flow
- Tests that check if API services properly handle model validation and API requests

### 3. Functional Tests (`tests/functional/`)

**Purpose**: Test complete features from end to end
**Characteristics**: Verify that entire workflows operate correctly

```
tests/functional/
  workflows/
    test_address_lifecycle.py  # Create, list, update, delete
    test_security_rule_workflow.py
  operations/
    test_commit_operations.py
    test_candidate_push.py
```

Example from your codebase:
- A test that simulates a complete CRUD workflow for an address object
- Testing the commit and candidate push operations end-to-end

### 4. Mock Tests (`tests/mocks/`)

**Purpose**: Simulate external dependencies
**Characteristics**: Replace API calls with controlled test doubles

```
tests/mocks/
  api/
    test_api_error_handling.py
    test_http_retry_logic.py
  auth/
    test_token_refresh_mocks.py
```

Example from your codebase:
- Tests in `test_auth.py` that mock the JWT and OAuth behaviors
- Tests that use `raise_mock_http_error` to simulate API errors

### 5. Parametrized Tests (`tests/parametrized/`)

**Purpose**: Run the same test with different inputs
**Characteristics**: Efficient way to test multiple scenarios

```
tests/parametrized/
  config/
    test_address_edge_cases.py
    test_security_rule_validation_cases.py
  models/
    test_model_validation_cases.py
```

Example from your codebase:
- Tests that verify different combinations of address types
- Tests that check handling of various error conditions with different parameters

### 6. Configuration Tests (`tests/configuration/`)

**Purpose**: Verify SDK behaves correctly with different configurations
**Characteristics**: Test initialization, environment variables, etc.

```
tests/configuration/
  test_sdk_initialization.py
  test_client_configuration.py
  test_environment_variables.py
```

Example from your codebase:
- Tests in `TestAddressMaxLimit` that verify max_limit behavior
- Tests that verify configuration parameter handling

### 7. Documentation Tests (`tests/documentation/`)

**Purpose**: Ensure examples in documentation work
**Characteristics**: Validate code examples accuracy

```
tests/documentation/
  test_readme_examples.py
  test_api_examples.py
```

This would be a new category focusing on testing documented examples.

## Implementation Approach

### Option 1: Gradual Migration

1. Create the new directory structure
2. Start moving tests to appropriate categories
3. Maintain backward compatibility with pytest path specifications
4. Update CI/CD pipeline to run tests by category

### Option 2: Marker-Based Approach

Instead of physically moving files, you could use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_address_validation():
    ...

@pytest.mark.integration
def test_address_service_integration():
    ...

@pytest.mark.functional
def test_address_lifecycle():
    ...
```

Then run tests by category with:
```bash
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m functional
```

This approach requires less file restructuring but achieves the same goal of organizing tests by functionality.

## Recommended Implementation Plan

1. Start with the marker-based approach (Option 2) to categorize tests
2. Run tests by category to ensure proper isolation
3. Gradually refactor test files to match the new directory structure (Option 1)
4. Update documentation and CI/CD pipeline to reflect the new organization

This phased approach minimizes disruption while improving test organization over time.

## Example Test Markers for Your Existing Tests

```python
# In test_address.py
@pytest.mark.unit
class TestAddressMaxLimit(TestAddressBase):
    """Unit tests for max_limit functionality."""
    ...

@pytest.mark.integration
class TestAddressList(TestAddressBase):
    """Integration tests for listing Address objects."""
    ...

@pytest.mark.functional
def test_address_lifecycle():
    """Functional test for complete address object lifecycle."""
    # Create
    # List
    # Update
    # Delete
    ...

@pytest.mark.parametrized
@pytest.mark.parametrize("address_type,address_value", [
    ("ip_netmask", "192.168.1.0/24"),
    ("ip_range", "192.168.1.1-192.168.1.10"),
    ("fqdn", "example.com"),
    ("ip_wildcard", "192.168.1.0/0.0.0.255"),
])
def test_address_types(address_type, address_value):
    """Parametrized test for different address types."""
    ...
```

This approach allows you to keep your existing file structure while starting to organize tests by functionality.