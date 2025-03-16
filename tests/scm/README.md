# Mocking the SCM Client for Testing

This directory contains mocking utilities for testing components that depend on the SCM API client.

## Using MockScm in Tests

The `MockScm` class is a special mock implementation that inherits from both `unittest.mock.MagicMock` and `scm.client.Scm`. This allows it to pass the `isinstance(api_client, Scm)` check in the `BaseObject` class while providing the mocking functionality of `MagicMock`.

### Basic Usage

```python
from tests.scm.mock_scm import MockScm
from scm.config.deployment import BandwidthAllocations

# In your test setup
def setUp(self):
    # Create a mock API client
    self.api_client = MockScm()
    
    # Initialize the service with the mock client
    self.service = BandwidthAllocations(self.api_client)
    
    # Configure mock API responses
    self.api_client.get.return_value = {"your": "mock_data"}
    self.api_client.post.return_value = {"created": "item"}
```

### Default Behavior

The `MockScm` class automatically configures the following default mock behaviors:

- `oauth_client` is a MagicMock with `is_expired = False`
- `get`, `post`, `put`, and `delete` methods are MagicMock instances returning `None` by default
- `_services` is initialized as an empty dictionary

You'll need to configure specific return values for these methods in your test setup to simulate API responses.

### Mocking API Responses

For each test, you should configure the mock API responses according to what you expect the API to return:

```python
# Mock a GET response for a list endpoint
self.api_client.get.return_value = {
    "data": [
        {"id": "1", "name": "item1"},
        {"id": "2", "name": "item2"}
    ],
    "limit": 100,
    "offset": 0,
    "total": 2
}

# Mock a GET response for a single item endpoint
self.api_client.get.return_value = {"id": "1", "name": "item1"}

# Mock a POST response (creating an item)
self.api_client.post.return_value = {"id": "3", "name": "new-item"}

# Mock a PUT response (updating an item)
self.api_client.put.return_value = {"id": "1", "name": "updated-item"}

# Mock a DELETE response (typically None)
self.api_client.delete.return_value = None
```

### Asserting API Calls

You can use the standard MagicMock assertion methods to verify that your service is making the correct API calls:

```python
# Verify that get was called with the correct parameters
self.api_client.get.assert_called_once_with(
    "/your/endpoint",
    params={"name": "item1"}
)

# Verify that post was called with the correct JSON payload
self.api_client.post.assert_called_once_with(
    "/your/endpoint",
    json={"name": "new-item"}
)
```

For more complex assertions, you can access the call history:

```python
# Get the list of all calls to a method
calls = self.api_client.get.call_args_list

# Check specific arguments of a call
first_call_args = self.api_client.get.call_args_list[0][0]  # Positional args of first call
first_call_kwargs = self.api_client.get.call_args_list[0][1]  # Keyword args of first call
```

## Important Notes

1. The `MockScm` class does not actually make any API requests. All responses must be mocked.
2. When testing error conditions, you can configure the mock methods to raise exceptions:

   ```python
   from scm.exceptions import APIError
   
   # Mock an API error
   self.api_client.get.side_effect = APIError("API request failed", error_code="E001")
   ```

3. For testing service methods that depend on multiple API calls, you can configure the mock methods to return different values on subsequent calls:

   ```python
   self.api_client.get.side_effect = [
       {"first": "response"},
       {"second": "response"}
   ]
   ```
