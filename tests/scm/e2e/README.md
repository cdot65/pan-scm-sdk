# End-to-End Tests for SCM SDK

This directory contains end-to-end tests for the SCM SDK. These tests are designed to validate that the SDK components work correctly together and interact with the SCM API as expected.

## Test Categories

The end-to-end tests are divided into two categories:

1. **Mocked API Tests**: These tests use mock API responses to validate the SDK's behavior without making actual API calls. They ensure that the SDK handles API responses correctly and transforms data between models correctly.

2. **Real API Tests**: These tests make actual API calls to validate the SDK's behavior with the real SCM API. They are skipped by default and require valid API credentials to run.

## Using the MockScm Class

For mocked API tests, use the `MockScm` class from `tests.scm.mock_scm`:

```python
from tests.scm.mock_scm import MockScm
from scm.config.deployment import BandwidthAllocations

class TestMyFeatureE2E(unittest.TestCase):
    def setUp(self):
        # Create a mock API client
        self.api_client = MockScm()

        # Create the service
        self.service = BandwidthAllocations(self.api_client)

        # Configure mock responses
        self.api_client.get.return_value = {"your": "mock_data"}
```

See the detailed documentation in `tests/scm/README.md` for more information on how to use `MockScm`.

## Running the Tests

### Mocked API Tests

To run the mocked API tests, use the following command:

```bash
poetry run pytest tests/scm/e2e/ -v
```

### Real API Tests

To run the real API tests, you need to:

1. Create a `.env` file in the project root with your API credentials:

```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
TSG_ID=your_tsg_id_here
```

2. Run the tests with the `--real-api` marker:

```bash
poetry run pytest tests/scm/e2e/ -v -m real_api
```

**WARNING**: The real API tests will create, update, and delete actual resources in your SCM instance. Use with caution and only with test data.

## Test Structure

The tests are structured as follows:

- `setup`: Set up the test environment, including mock responses or real API client
- `test_*`: Individual test methods that validate specific aspects of the SDK
- `teardown`: Clean up any resources created during the test (for real API tests)

Each test class focuses on a specific service or feature of the SDK.

## Adding New Tests

When adding new end-to-end tests, follow these guidelines:

1. Create a new test file with the naming convention `test_*_e2e.py`
2. Use descriptive test method names that indicate what aspect of the SDK is being tested
3. Use the `MockScm` class for mocked API tests
4. If appropriate, add real API tests that validate the SDK's behavior with the real SCM API
5. Mark real API tests with `@pytest.mark.skip` and `@pytest.mark.real_api`
6. Add proper cleanup logic to ensure no test resources are left behind
