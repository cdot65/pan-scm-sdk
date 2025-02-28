# Comprehensive HIP Profiles SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage Host Information Profiles (HIP profiles) across a wide range of enterprise security scenarios.

## Overview

The `hip_profile.py` script showcases enterprise-ready HIP profile configurations addressing common host-based security needs, including:

1. **Basic HIP Profile Configurations**:
   - Simple match criteria - matching basic host attributes
   - Complex match criteria - using logical operators (AND, OR, NOT)
   - Security-focused profiles - checking for security software and controls
   - Compliance-focused profiles - checking for encryption and patch management

2. **HIP Profile Management Operations**:
   - Creating HIP profiles in different locations (folders, snippets, devices)
   - Retrieving and filtering profiles using various criteria
   - Updating existing profiles to modify match expressions
   - Bulk creation of profiles for different operating systems

3. **Match Expressions**:
   - Single condition matches (e.g., `"is-win"`)
   - Multiple condition matches with AND/OR logic (e.g., `"is-win" and "is-firewall-enabled"`)
   - Negated conditions using NOT operator (e.g., `not ("is-win")`)
   - Complex expressions with nested conditions

4. **Operational Functions**:
   - Bulk operations for mass configuration
   - Advanced filtering and search capabilities
   - Comprehensive error handling
   - Safe cleanup procedures
   - CSV report generation

## Prerequisites

Before running the examples, you need:

1. A Strata Cloud Manager account with appropriate permissions
2. Your SCM API credentials (client ID, client secret, and TSG ID)
3. Python 3.10 or higher
4. The PAN-SCM-SDK package installed (`pip install pan-scm-sdk`)
5. A folder named "Texas" in your SCM environment (or modify the script)
6. Existing HIP objects in your environment that match the ones used in the script

## Script Organization

The script is organized into modular functions that each demonstrate a specific HIP profile configuration pattern or operational task:

### Basic HIP Profile Examples
- `create_basic_hip_profile()` - Simple single-condition profiles
- `create_complex_hip_profile()` - Multi-condition profiles with AND/OR logic
- `create_security_focused_hip_profile()` - Profiles checking for security software
- `create_compliance_hip_profile()` - Profiles checking for compliance requirements

### Container-Specific Examples
- `create_hip_profile_with_snippet()` - Creating profiles in snippet containers
- `create_hip_profile_with_device()` - Creating profiles in device containers
- `create_negative_match_hip_profile()` - Creating profiles with NOT conditions

### Operational Functions
- `fetch_and_update_hip_profile()` - Updating existing profiles
- `list_and_filter_hip_profiles()` - Filtering profiles with various criteria
- `fetch_hip_profile_by_name()` - Retrieving a profile by name
- `cleanup_hip_profiles()` - Safely removing test profiles
- `generate_hip_profile_report()` - Creating CSV reports of profiles

### Bulk Management
- `create_bulk_hip_profiles()` - Creating multiple profiles programmatically

## Real-World HIP Profile Scenarios

The example script demonstrates these common real-world HIP profile scenarios:

### 1. Basic Windows Host Profile
```python
basic_profile_config = {
    "name": "basic-hip-profile-12345",
    "description": "Example basic HIP profile with simple match criteria",
    "folder": "Texas",
    "match": '"is-win"',
}
```

### 2. Windows Host with Security Software
```python
security_profile_config = {
    "name": "security-hip-profile-12345",
    "description": "Security-focused HIP profile checking for security software",
    "folder": "Texas",
    "match": '"is-win" and "is-anti-malware-and-rtp-enabled" and "is-firewall-enabled"',
}
```

### 3. Compliance Requirements Profile
```python
compliance_profile_config = {
    "name": "compliance-hip-profile-12345",
    "description": "Compliance-focused HIP profile checking for encryption and patches",
    "folder": "Texas",
    "match": '"disk-encryption" = "yes" and "patch-management" = "yes"',
}
```

### 4. Negative Match Expression
```python
negative_profile_config = {
    "name": "negative-hip-profile-12345",
    "description": "HIP profile with negative match criteria",
    "folder": "Texas",
    "match": 'not ("is-win")',
}
```

### 5. OS-Specific Profiles (Bulk Creation)
```python
# Create multiple similar HIP profiles for different operating systems
operating_systems = [
    {"name": "Windows 10", "match": '"is-win" and "os-version" >= "10.0.0"'},
    {"name": "Windows 11", "match": '"is-win" and "os-version" >= "11.0.0"'},
    {"name": "macOS", "match": '"is-mac"'},
    {"name": "Linux", "match": '"is-linux"'},
]

for os_info in operating_systems:
    profile_config = {
        "name": f"{os_info['name'].lower()}-hip-profile-12345",
        "description": f"HIP profile for {os_info['name']} systems",
        "folder": "Texas",
        "match": os_info["match"],
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
     ```

4. Run the script with options to customize behavior:
   ```bash
   # Run all examples with default settings
   python hip_profile.py
   
   # Run only the basic profile examples
   python hip_profile.py --basic
   
   # Run only the security profile examples
   python hip_profile.py --security
   
   # Skip cleanup to preserve created profiles
   python hip_profile.py --skip-cleanup
   
   # Use a different folder
   python hip_profile.py --folder "Production"
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
hip_profile_update = HIPProfileUpdateModel(
    id=profile_id,               # Required - UUID of the profile to update
    name="profile-name",         # Required
    match="new-match-expression", # Required
    description="new-description", # Optional
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

### Common Match Expression Examples

```
# Windows systems
"is-win"

# Windows systems with firewall
"is-win" and "is-firewall-enabled"

# Windows systems with anti-malware and real-time protection
"is-win" and "is-anti-malware-and-rtp-enabled"

# Windows systems with recent anti-malware scans (within 1 day)
"is-win" and "is-anti-malware-installed-1day"

# Windows systems with recent anti-malware scans (within 7 days)
"is-win" and "is-anti-malware-installed-7days"

# Windows systems with patch management
"is-win" and "is-patch-management-enabled"

# Non-Windows systems
not ("is-win")
```

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Pydantic Model Construction** - Both direct dictionary and explicit model building approaches
3. **Bulk Operations** - Creating multiple related objects programmatically  
4. **Unique Naming** - Using UUID suffixes to avoid name conflicts
5. **Modular Code Organization** - Separate functions for each profile type
6. **Proper Cleanup** - Ensuring all created objects are deleted
7. **Logging** - Consistent and informative log messages
8. **Object Model Conversion** - Converting between Pydantic models and dictionaries

## Best Practices

1. **HIP Profile Design**
   - Use clear, descriptive names with consistent naming conventions
   - Document the purpose in the description field
   - Keep match expressions as simple as possible while meeting requirements
   - Test match expressions against actual endpoints

2. **Match Expression Selection**
   - Use simple expressions for basic profiling
   - Use compound expressions with AND/OR/NOT for complex requirements
   - Consider using negated expressions to exclude specific hosts

3. **Organization Best Practices**
   - Group related profiles in a consistent folder structure
   - Consider using naming conventions that reflect the purpose or policy requirement

4. **API Usage**
   - Handle all exceptions appropriately
   - Use proper data validation before API calls
   - Implement retry logic for production code
   - Consider rate limiting for large bulk operations

5. **Security Considerations**
   - Validate match expressions against sample devices
   - Test on a limited set of endpoints before wide deployment
   - Consider the performance impact of complex match expressions

## Example Output

```bash
❯ poetry run python hip_profile.py --skip-cleanup
2025-02-28 07:30:22 INFO
2025-02-28 07:30:22 INFO     ================================================================================
2025-02-28 07:30:22 INFO        AUTHENTICATION & INITIALIZATION
2025-02-28 07:30:22 INFO     ================================================================================
2025-02-28 07:30:22 INFO     ▶ STARTING: Loading credentials and initializing client
2025-02-28 07:30:22 INFO     ✓ Loaded environment variables from /Users/cdot/PycharmProjects/cdot65/pan-scm-sdk/examples/scm/config/objects/.env
2025-02-28 07:30:22 INFO     ✓ All required credentials found
2025-02-28 07:30:22 INFO     ▶ STARTING: Creating SCM client
2025-02-28 07:30:23 INFO     ✓ COMPLETED: SCM client initialization - TSG ID: 1540**2209
2025-02-28 07:30:23 INFO
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:23 INFO        HIP PROFILE CONFIGURATION
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:23 INFO     ▶ STARTING: Initializing HIP profile manager
2025-02-28 07:30:23 INFO     ✓ COMPLETED: HIP profile manager initialization
2025-02-28 07:30:23 INFO
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:23 INFO        HIP PROFILE CREATION
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:23 INFO     Demonstrating HIP profile creation with various match expressions
2025-02-28 07:30:23 INFO     Using folder: Texas
2025-02-28 07:30:23 INFO     ▶ STARTING: Creating basic HIP profile with simple match criteria
2025-02-28 07:30:23 INFO     Profile name: basic-hip-profile-9139c7
2025-02-28 07:30:23 INFO     Configuration details:
2025-02-28 07:30:23 INFO       - Name: basic-hip-profile-9139c7
2025-02-28 07:30:23 INFO       - Match: "is-win"
2025-02-28 07:30:23 INFO       - Container: folder 'Texas'
2025-02-28 07:30:23 INFO     Sending request to Strata Cloud Manager API...
2025-02-28 07:30:23 INFO     ✓ Created HIP profile: basic-hip-profile-9139c7
2025-02-28 07:30:23 INFO       - Profile ID: 4c4530cd-01af-473b-a2f7-b46bdee68dc5
2025-02-28 07:30:23 INFO       - Match criteria: "is-win"
2025-02-28 07:30:23 INFO     ✓ COMPLETED: Basic HIP profile creation - Profile: basic-hip-profile-9139c7
2025-02-28 07:30:23 INFO     ▶ STARTING: Creating HIP profile with complex match criteria
2025-02-28 07:30:23 INFO     Profile name: complex-hip-profile-212e13
2025-02-28 07:30:23 INFO     Configuration details:
2025-02-28 07:30:23 INFO       - Name: complex-hip-profile-212e13
2025-02-28 07:30:23 INFO       - Match: "is-win" and "is-firewall-enabled"
2025-02-28 07:30:23 INFO       - Container: folder 'Texas'
2025-02-28 07:30:23 INFO     Sending request to Strata Cloud Manager API...
2025-02-28 07:30:23 INFO     ✓ Created HIP profile: complex-hip-profile-212e13
2025-02-28 07:30:23 INFO       - Profile ID: 18a69eca-e198-40ec-8c56-9c4d1fc8588b
2025-02-28 07:30:23 INFO       - Match criteria: "is-win" and "is-firewall-enabled"
2025-02-28 07:30:23 INFO     ✓ COMPLETED: Complex HIP profile creation - Profile: complex-hip-profile-212e13
2025-02-28 07:30:23 INFO
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:23 INFO        LISTING AND FILTERING HIP PROFILES
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:28 INFO     ▶ STARTING: Listing and filtering HIP profiles
2025-02-28 07:30:29 INFO     ✓ Found 21 HIP profiles in the Texas folder
2025-02-28 07:30:29 INFO     Found 1 HIP profiles directly in the Texas folder
2025-02-28 07:30:29 INFO     Found 21 HIP profiles excluding 'Texas/SubFolder'
2025-02-28 07:30:29 INFO
Details of HIP profiles:
2025-02-28 07:30:29 INFO       - Profile: is-win-and-anti-malware
2025-02-28 07:30:29 INFO         ID: c56a5f2c-6f6a-459d-a223-e3e7718391f3
2025-02-28 07:30:29 INFO         Match: "is-win"  and "is-anti-malware-and-rtp-enabled"
2025-02-28 07:30:29 INFO         Description: Matches Windows endpoints that have anti-malware software installed
2025-02-28 07:30:29 INFO
2025-02-28 07:30:29 INFO       - Profile: is-win-and-anti-malware-1day
2025-02-28 07:30:29 INFO         ID: e08e8d45-426d-4a50-b0f7-d1c6a609b4fd
2025-02-28 07:30:29 INFO         Match: "is-win"  and "is-anti-malware-installed-1day"
2025-02-28 07:30:29 INFO         Description: Matches Windows endpoints that have anti-malware software installed and a Last Scan Time and Virus Definition within 1 day
2025-02-28 07:30:29 INFO
2025-02-28 07:30:29 INFO       - Profile: is-win-and-anti-malware-7days
2025-02-28 07:30:29 INFO         ID: 40291007-729a-445e-9431-cc6c6593d5af
2025-02-28 07:30:29 INFO         Match: "is-win"  and "is-anti-malware-installed-7days"
2025-02-28 07:30:29 INFO         Description: Matches Windows endpoints that have anti-malware software installed and a Last Scan Time and Virus Definition within 7 days
2025-02-28 07:30:29 INFO
2025-02-28 07:30:29 INFO       - Profile: is-win-and-firewall
2025-02-28 07:30:29 INFO         ID: 62882bd5-631e-4b93-8bd9-a06b8ff03208
2025-02-28 07:30:29 INFO         Match: "is-win"  and "is-firewall-enabled"
2025-02-28 07:30:29 INFO         Description: Matches Windows endpoints that have firewall software installed and enabled
2025-02-28 07:30:29 INFO
2025-02-28 07:30:29 INFO       - Profile: is-win-and-patch-management
2025-02-28 07:30:29 INFO         ID: d015823d-cf5a-4c65-819c-bf902b23ace4
2025-02-28 07:30:29 INFO         Match: "is-win"  and "is-patch-management-enabled"
2025-02-28 07:30:29 INFO         Description: Matches Windows endpoints that have patch management software installed and enabled
2025-02-28 07:30:29 INFO
2025-02-28 07:30:29 INFO
2025-02-28 07:30:29 INFO     ================================================================================
2025-02-28 07:30:29 INFO        EXECUTION SUMMARY
2025-02-28 07:30:29 INFO     ================================================================================
2025-02-28 07:30:29 INFO     ✓ Example script completed successfully
2025-02-28 07:30:29 INFO     Total HIP profiles created: 2
2025-02-28 07:30:29 INFO     Total execution time: 0 minutes 7 seconds
```

## CSV Report Example

When the script generates a CSV report, it will look similar to the following:

```csv
Profile ID,Name,Description,Match Criteria,Folder,Report Generation Time
4c4530cd-01af-473b-a2f7-b46bdee68dc5,basic-hip-profile-9139c7,Example basic HIP profile with simple match criteria,"is-win",Texas,2025-02-28 07:30:29
18a69eca-e198-40ec-8c56-9c4d1fc8588b,complex-hip-profile-212e13,Example HIP profile with complex match criteria using AND/OR logic,"is-win" and "is-firewall-enabled",Texas,2025-02-28 07:30:29
d015823d-cf5a-4c65-819c-bf902b23ace4,is-win-and-patch-management,Matches Windows endpoints that have patch management software installed and enabled,"is-win"  and "is-patch-management-enabled",Texas,2025-02-28 07:30:29
62882bd5-631e-4b93-8bd9-a06b8ff03208,is-win-and-firewall,Matches Windows endpoints that have firewall software installed and enabled,"is-win"  and "is-firewall-enabled",Texas,2025-02-28 07:30:29
40291007-729a-445e-9431-cc6c6593d5af,is-win-and-anti-malware-7days,Matches Windows endpoints that have anti-malware software installed and a Last Scan Time and Virus Definition within 7 days,"is-win"  and "is-anti-malware-installed-7days",Texas,2025-02-28 07:30:29
e08e8d45-426d-4a50-b0f7-d1c6a609b4fd,is-win-and-anti-malware-1day,Matches Windows endpoints that have anti-malware software installed and a Last Scan Time and Virus Definition within 1 day,"is-win"  and "is-anti-malware-installed-1day",Texas,2025-02-28 07:30:29
c56a5f2c-6f6a-459d-a223-e3e7718391f3,is-win-and-anti-malware,Matches Windows endpoints that have anti-malware software installed,"is-win"  and "is-anti-malware-and-rtp-enabled",Texas,2025-02-28 07:30:29

SUMMARY
Total Profiles Processed,7
Successfully Retrieved,7
Failed to Retrieve,0
Execution Time (so far),6.82 seconds
Report Generated On,2025-02-28 07:30:29
```