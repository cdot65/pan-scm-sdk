# Comprehensive HIP Profiles SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage Host Information Profiles (HIP profiles) across a wide range of enterprise security scenarios.

## Overview

The `hip_profile.py` script showcases enterprise-ready HIP profile configurations addressing common host-based security needs, including:

1. **Match Expression Types**:
   - Simple match expressions - for basic host identification
   - AND/OR logical operators - for combining multiple conditions
   - NOT operators - for excluding specific hosts
   - Complex nested expressions - for sophisticated policy requirements

2. **HIP Profile Use Cases**:
   - OS identification profiles (Windows, macOS, Linux)
   - Security software validation (anti-malware, firewall)
   - Compliance verification (encryption, patch management)
   - Custom security posture assessments

3. **Advanced Operations**:
   - Creating profiles in different containers (folders, snippets, devices)
   - Updating match expressions for existing profiles
   - Filtering and searching profiles with various criteria
   - Bulk creation and management operations

4. **Operational Functions**:
   - CSV report generation with profile details
   - Advanced filtering and search capabilities
   - Comprehensive error handling
   - Safe cleanup procedures

5. **Reporting and Documentation**:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

## Prerequisites

Before running the examples, you need:

1. A Strata Cloud Manager account with appropriate permissions
2. Your SCM API credentials (client ID, client secret, and TSG ID)
3. Python 3.10 or higher
4. The PAN-SCM-SDK package installed (`pip install pan-scm-sdk`)
5. A folder named "Texas" in your SCM environment (or modify the script)
6. Existing HIP objects in your environment that match the ones referenced in match expressions

## Script Organization

The script is organized into modular functions that each demonstrate a specific HIP profile type or operational task:

### HIP Profile Creation Functions
- `create_basic_hip_profile()` - Simple match expression profiles
- `create_complex_hip_profile()` - Profiles with AND/OR logical operators
- `create_negative_match_hip_profile()` - Profiles with NOT operators
- `create_hip_profile_with_snippet()` - Profiles in snippet containers
- `create_hip_profile_with_device()` - Profiles in device containers

### Operational Functions
- `fetch_and_update_hip_profile()` - Modifying existing profiles
- `list_and_filter_hip_profiles()` - Finding and filtering profiles
- `fetch_hip_profile_by_name()` - Looking up profiles by name
- `delete_hip_profile()` - Deleting individual profiles
- `cleanup_hip_profiles()` - Safely removing test profiles
- `generate_hip_profile_report()` - Creating comprehensive CSV reports

## Real-World HIP Profile Scenarios

The example script demonstrates these common real-world HIP profile patterns:

### 1. Basic Windows Host Profile
```python
basic_profile_config = {
    "name": "basic-hip-profile-example",
    "description": "Example basic HIP profile with simple match criteria",
    "folder": "Texas",
    "match": '"is-win"',
}
```

### 2. Windows Host with Security Software
```python
complex_profile_config = {
    "name": "complex-hip-profile-example",
    "description": "Example HIP profile with complex match criteria using AND/OR logic",
    "folder": "Texas",
    "match": '"is-win" and "is-firewall-enabled"',
}
```

### 3. Non-Windows Systems Profile
```python
negative_profile_config = {
    "name": "negative-hip-profile-example",
    "description": "Example HIP profile with negative match criteria",
    "folder": "Texas",
    "match": 'not ("is-win")',
}
```

### 4. Complex Nested Expression
```python
nested_profile_config = {
    "name": "nested-hip-profile-example",
    "description": "Example HIP profile with nested match criteria",
    "folder": "Texas",
    "match": '("is-win" and "is-firewall-enabled") or ("is-mac" and "is-encrypted")',
}
```

### 5. Cross-Platform Security Profile
```python
security_profile_config = {
    "name": "security-hip-profile-example",
    "description": "Security profile for all operating systems",
    "folder": "Texas",
    "match": '("is-win" and "is-firewall-enabled" and "is-anti-malware-and-rtp-enabled") or ' +
             '("is-mac" and "is-encrypted")',
}
```

## Running the Example

Follow these steps to run the example:

1. Set up authentication credentials in one of the following ways:

   **Option A: Using a .env file (recommended)**
   - Create a file named `.env` in the same directory as the script
   - Edit the `.env` file and fill in your Strata Cloud Manager credentials:
     ```
     SCM_CLIENT_ID=your-oauth2-client-id
     SCM_CLIENT_SECRET=your-oauth2-client-secret
     SCM_TSG_ID=your-tenant-service-group-id
     SCM_LOG_LEVEL=DEBUG  # Optional
     ```

   **Option B: Using environment variables**
   - Set the environment variables directly in your shell:
     ```bash
     export SCM_CLIENT_ID=your-oauth2-client-id
     export SCM_CLIENT_SECRET=your-oauth2-client-secret
     export SCM_TSG_ID=your-tenant-service-group-id
     ```

2. Install additional dependencies:
   ```bash
   pip install python-dotenv
   ```

3. Verify or adjust environment-specific settings:
   - Folder name (default is "Texas")
   - HIP objects used in match expressions
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     SKIP_CLEANUP=true  # To preserve created objects
     ```

4. Run the script with various options:
   ```bash
   # Run all examples
   python hip_profile.py
   
   # Demonstrate only creation operations
   python hip_profile.py --create
   
   # Demonstrate only update operations
   python hip_profile.py --update
   
   # Demonstrate only listing operations
   python hip_profile.py --list
   
   # Demonstrate only deletion operations
   python hip_profile.py --delete
   
   # Skip cleaning up created profiles
   python hip_profile.py --skip-cleanup
   
   # Specify a different folder
   python hip_profile.py --folder=Production
   ```

5. Examine the console output to understand:
   - The HIP profiles being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## HIP Profile Model Structure

The examples demonstrate the proper structure for HIP profile models:

### HIP Profile Create Model

```python
# Basic structure
hip_profile_create = {
    "name": "profile-name",            # Required
    "description": "description",      # Optional
    "match": "match-expression",       # Required
    "folder": "folder-name",           # Container - one of these is required
    # "snippet": "snippet-name",       # Alternative container
    # "device": "device-name",         # Alternative container
}
```

### HIP Profile Update Model

```python
# Update model requires an ID
from scm.models.objects import HIPProfileUpdateModel

update_model = HIPProfileUpdateModel(
    id=profile_id,                  # Required - UUID of the profile to update
    name="profile-name",            # Required
    match="new-match-expression",   # Required
    description="new-description",  # Optional
)
```

### Match Expression Syntax

The match expressions follow this syntax pattern:

```
# Simple match
"hipobject-name"

# AND condition
"hipobject1" and "hipobject2"

# OR condition
"hipobject1" or "hipobject2"

# NOT condition
not ("hipobject1")

# Complex condition
("hipobject1" and "hipobject2") or "hipobject3"
```

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Unique Naming** - Using UUID suffixes to avoid name conflicts
3. **Modular Code Organization** - Separate functions for each profile type
4. **Proper Cleanup** - Ensuring all created objects are deleted
5. **Logging** - Consistent and informative log messages with color coding
6. **Command-line Arguments** - Flexible script execution with various options
7. **Environment Variable Support** - Using .env files for credentials
8. **Progress Tracking** - Showing progress during lengthy operations
9. **Performance Metrics** - Tracking and reporting execution statistics

## Best Practices

1. **HIP Profile Design**
   - Use clear, descriptive names with consistent naming conventions
   - Document the purpose in the description field
   - Keep match expressions as simple as possible
   - Group related criteria logically with proper parentheses

2. **Match Expression Selection**
   - Use simple expressions for basic profiling
   - Use AND operators for combining mandatory criteria
   - Use OR operators for alternatives
   - Use NOT operators to exclude specific conditions
   - Use parentheses to control evaluation order

3. **Naming Conventions**
   - Include the primary match criteria in the name
   - Use consistent prefixes for similar profile types
   - Consider including security level or environment information

4. **API Usage**
   - Handle all exceptions appropriately
   - Use proper data validation before API calls
   - Implement retry logic for production code
   - Consider rate limiting for large bulk operations

5. **Security Considerations**
   - Validate match expressions against sample devices
   - Test on limited endpoints before wide deployment
   - Consider impact of complex expressions on performance
   - Follow principle of least privilege for permissions