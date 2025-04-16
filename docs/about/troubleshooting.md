# Troubleshooting Guide

If you encounter issues while using `pan-scm-sdk`, this guide provides solutions to common problems.

## Common Issues and Solutions

### 1. Authentication Failures

**Problem:** Unable to authenticate with the SCM API.

**Solutions:**

- **Check Credentials**: Ensure your `client_id`, `client_secret`, and `tsg_id` are correct.
- **Permissions**: Verify that your credentials have the necessary permissions to access the API.
- **Network Issues**: Ensure there are no network issues blocking access to the authentication endpoint.

### 2. API Errors

**Problem:** Receiving errors when making API calls.

**Solutions:**

- **Inspect Error Messages**: Review the exception messages and logs for details.
- **Validate Input Data**: Ensure that all required fields are provided and correctly formatted.
- **Check Resource Existence**: Confirm that the resources you are trying to access or modify exist.

### 3. Validation Errors

**Problem:** Validation errors when creating or updating resources.

**Solutions:**

- **Use Correct Models**: Ensure you are using the appropriate data models for requests.
- **Field Constraints**: Check that field values meet length, pattern, and type requirements.
- **Exclusive Fields**: Respect mutual exclusivity constraints (e.g., only one of `folder` or `snippet`).

### 4. Token Expiration

**Problem:** Authentication token has expired.

**Solution:**

- **Automatic Refresh**: The SDK automatically refreshes tokens. Ensure that the `Scm` client is properly initialized.
- **Time Synchronization**: Verify that your system clock is accurate.

## Logging

The SDK uses the `logging` module to provide debug information. You can configure logging to display more detailed
output.

**Example:**

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Now, when you use the SDK, it will output debug information
```

## Getting Help

If you're unable to resolve an issue, please open an issue on
the [GitHub repository](https://github.com/cdot65/pan-scm-sdk/issues) with details about the problem.
