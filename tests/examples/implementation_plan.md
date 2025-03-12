# Test Restructuring Implementation Plan

## Phase 1: Initial Setup and Planning (Week 1)

### Goals
- Add pytest markers to existing tests without moving files
- Update pytest configuration to support test categories
- Document the test restructuring plan for the team

### Tasks
1. **Define Test Categories and Markers**
   - Create pytest markers for each test category
   - Document marker purpose and usage guidelines

2. **Update Pytest Configuration**
   - Add markers to `pytest.ini`:
     ```
     [pytest]
     markers =
         unit: Unit tests for individual components
         integration: Tests for component interactions
         functional: End-to-end workflow tests
         mock: Tests using mocks for external dependencies
         parametrized: Tests with multiple input variations
         configuration: Tests for SDK configuration options
         documentation: Tests validating documentation examples
     ```

3. **Create Helper Fixtures**
   - Add shared fixtures for each test category
   - Ensure proper test isolation

4. **Document Test Categories**
   - Create guidelines document for categorizing tests
   - Share with team for feedback

## Phase 2: Marker Implementation (Weeks 2-3)

### Goals
- Add appropriate test markers to existing tests
- Verify that tests can be run by category
- Start creating new tests with the proper markers

### Tasks
1. **Add Markers to Existing Tests**
   - Start with core services like Address, SecurityRule
   - Add markers based on the test's purpose
   - Example:
     ```python
     @pytest.mark.unit
     def test_validation_logic():
         ...
     
     @pytest.mark.integration
     def test_api_interaction():
         ...
     ```

2. **Run Tests by Category**
   - Verify that tests run correctly when filtered by marker
   - Update CI configuration to run tests by category
   - Sample commands:
     ```bash
     poetry run pytest -m unit
     poetry run pytest -m integration
     poetry run pytest -m "not integration"  # Run all except integration tests
     ```

3. **Refactor Ambiguous Tests**
   - Review tests that fit multiple categories
   - Split tests into more focused tests if needed
   - Add documentation for complex test cases

## Phase 3: Directory Restructuring (Weeks 4-6)

### Goals
- Create new directory structure for tests
- Gradually move tests to appropriate directories
- Update imports and references

### Tasks
1. **Create New Directory Structure**
   - Create directories for each test category:
     ```
     tests/
       unit/
       integration/
       functional/
       mocks/
       parametrized/
       configuration/
       documentation/
       conftest.py  # Shared fixtures
     ```

2. **Move Tests by Module**
   - Start with one module at a time (e.g., address)
   - Move tests to appropriate directories
   - Update imports and references
   - Example:
     ```python
     # Before: tests/scm/config/objects/test_address.py
     # After: tests/unit/config/objects/test_address_validation.py
     #        tests/integration/config/objects/test_address_api.py
     #        tests/functional/workflows/test_address_lifecycle.py
     ```

3. **Fix CI/CD Pipeline**
   - Update CI configuration to use new directory structure
   - Ensure all tests continue to run in CI

## Phase 4: Documentation and Training (Week 7)

### Goals
- Document the new test structure
- Train team on the new approach
- Establish guidelines for future tests

### Tasks
1. **Update Test Documentation**
   - Create a test strategy document
   - Document test categories and when to use each

2. **Create Test Templates**
   - Provide example test files for each category
   - Include docstring templates

3. **Team Training**
   - Present the new test structure to the team
   - Explain benefits and usage

## Phase 5: Refinement and Completion (Week 8)

### Goals
- Review the new structure in practice
- Address any issues or gaps
- Finalize the approach

### Tasks
1. **Collect Feedback**
   - Get feedback from team on the new structure
   - Identify any friction points

2. **Refine Guidelines**
   - Update test guidelines based on feedback
   - Document best practices that emerged during implementation

3. **Create New Test Metrics**
   - Update test coverage reporting
   - Add category-specific metrics
   - Consider test speed and reliability metrics

## Usage Examples

### Running Tests by Category

```bash
# Run all unit tests
poetry run pytest -m unit

# Run all integration tests
poetry run pytest -m integration

# Run functional and mock tests
poetry run pytest -m "functional or mock"

# Run unit tests for address objects
poetry run pytest -m unit tests/unit/config/objects/test_address*.py
```

### Writing New Tests

```python
# Unit test example
@pytest.mark.unit
def test_address_validation():
    """Test address validation logic."""
    # Test in isolation
    ...

# Integration test example
@pytest.mark.integration
def test_address_api_interaction():
    """Test address API request/response handling."""
    # Test component interactions
    ...

# Functional test example
@pytest.mark.functional
def test_address_workflow():
    """Test complete address object lifecycle."""
    # CRUD workflow
    ...
```

## Benefits of the New Approach

1. **Improved Test Focus**
   - Clear separation of test types
   - Tests organized by purpose, not structure

2. **Better Test Performance**
   - Fast unit tests can be run separately
   - Slow integration tests can be run less frequently

3. **Enhanced Test Coverage**
   - Easier to identify coverage gaps by test type
   - More targeted test development

4. **Simplified Maintenance**
   - Tests with similar patterns grouped together
   - Easier to update tests when APIs change

5. **Clearer Documentation**
   - Tests serve as examples for different use cases
   - Easier to locate relevant test examples