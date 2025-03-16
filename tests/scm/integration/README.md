# Integration Tests for SCM SDK

This directory contains integration tests for the SCM SDK. These tests focus on the integration between different components of the SDK, such as the client, services, and models.

## Purpose

The integration tests verify that:

1. The unified client access pattern works correctly
2. Models properly serialize and deserialize data
3. Services correctly transform data between models
4. Components interact correctly when used together

## Running the Tests

To run the integration tests, use the following command:

```bash
poetry run pytest tests/scm/integration/ -v
```

## Test Structure

Each test class focuses on a specific service or feature of the SDK. The tests typically:

1. Set up mock dependencies (like API clients)
2. Test the interaction between components
3. Verify that data flows correctly between components

## Adding New Tests

When adding new integration tests, follow these guidelines:

1. Create a new test file with the naming convention `test_*_integration.py`
2. Use descriptive test method names that indicate what aspect of integration is being tested
3. Focus on the integration between components, not the specific API interactions
4. Use mocks for external dependencies like the API client

## Difference from End-to-End Tests

Integration tests differ from end-to-end tests in that they:

1. Focus on the interaction between components, not the API
2. Do not validate the SDK's behavior with the real API
3. Are more focused on specific interactions rather than complete workflows

For tests that validate the SDK's behavior with the real API, see the [end-to-end tests](../e2e/).
