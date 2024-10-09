# Troubleshooting Guide

If you encounter issues while using `pan-scm-sdk`, this guide provides solutions to common problems.

## Common Issues and Solutions

### 1. Authentication Failures

**Problem:** Error authenticating with source or destination tenant.

**Solution:**

- Ensure that your credentials in `.secrets.yaml` are correct.
- Verify that your client IDs and secrets are valid.
- Check for typos in the tenant TSG values.

### 2. Network Connectivity Issues

**Problem:** Unable to connect to the SCM tenants.

**Solution:**

- Check your internet connection.
- Ensure that there are no firewall rules blocking outbound connections.
- Verify that the token URL is correct.

### 3. Errors During Cloning

**Problem:** Errors occur when cloning address objects or groups.

**Solution:**

- Ensure that the source tenant has the configurations you're trying to clone.
- Check if there are any naming conflicts in the destination tenant.
- Review the logs for detailed error messages.

### 4. Invalid Folder Names

**Problem:** Specified folder does not exist.

**Solution:**

- Verify that the folder names specified in `.secrets.yaml` are correct.
- Ensure that the folders exist in both source and destination tenants.

## Logging

`pan-scm-sdk` provides logging to help diagnose issues. Check the console output for informative messages.

## Getting Help

If you're unable to resolve an issue, please open an issue on our [GitHub repository](https://github.com/cdot65/pan-scm-sdk/issues) with details about the problem.
