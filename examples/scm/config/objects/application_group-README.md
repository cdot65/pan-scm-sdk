# Comprehensive Application Group SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage application groups across a wide range of real-world enterprise scenarios.

## Overview {#Overview}

The `application_group.py` script showcases enterprise-ready application group configurations addressing common use cases, including:

1. **Basic Application Groups**:
   - Standard application groups with predefined applications
   - Common application combinations for web, email, management, etc.

2. **Custom Application Groups**:
   - Organization-specific application groupings
   - Targeted application combinations for specific security needs

3. **Nested Application Groups**:
   - Hierarchical structures with groups containing other groups
   - Building complex application taxonomies

4. **Mixed Application Groups**:
   - Combinations of individual applications and existing groups
   - Hybrid configurations for flexible policy construction

5. **Operational Functions**:
   - Bulk creation capabilities - for mass configuration
   - Advanced filtering and search capabilities
   - Comprehensive error handling
   - Safe cleanup procedures with dependency handling

6. **Reporting and Documentation**:
   - Detailed CSV report generation with object details
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

## Prerequisites

Before running the examples, you need:

1. A Strata Cloud Manager account with appropriate permissions
2. Your SCM API credentials (client ID, client secret, and TSG ID)
3. Python 3.10 or higher
4. The PAN-SCM-SDK package installed (`pip install pan-scm-sdk`)
5. A folder named "Texas" in your SCM environment (or modify the script)

## Script Organization

The script is organized into modular functions that each demonstrate a specific application group type or operational task:

### Application Group Creation Examples
- `create_basic_application_group()` - Standard group with common predefined applications
- `create_custom_application_group()` - Group with custom applications
- `create_nested_application_group()` - Group containing other application groups
- `create_mixed_application_group()` - Group with both applications and other groups

### Bulk Operations
- `create_bulk_application_group_objects()` - Creating multiple application groups programmatically

### Operational Functions
- `fetch_and_update_application_group()` - Modifying existing application groups
- `list_and_filter_application_groups()` - Finding and filtering application groups
- `cleanup_application_group_objects()` - Safely removing test objects with dependency management
- `generate_application_group_report()` - Creating comprehensive CSV reports

## Real-World Application Group Scenarios

The example script demonstrates these common real-world application group patterns:

### 1. Basic Application Group
```python
basic_group_config = {
    "name": "basic-web-apps",
    "folder": "Texas",
    "members": ["web-browsing", "ssl", "dns"],  # Common web applications
}
```

### 2. Custom Application Group
```python
custom_group_config = {
    "name": "custom-network-apps",
    "folder": "Texas",
    "members": ["web-browsing", "ssl", "ping"],  # Customized application set
}
```

### 3. Nested Application Group
```python
nested_group_config = {
    "name": "nested-app-group",
    "folder": "Texas",
    "members": ["basic-web-apps", "custom-network-apps"],  # References existing groups
}
```

### 4. Mixed Application Group
```python
mixed_group_config = {
    "name": "mixed-app-group",
    "folder": "Texas",
    "members": [
        "basic-web-apps",  # Existing group
        "ping",           # Individual applications
        "dns",
        "ssl"
    ],
}
```

## Running the Example

Follow these steps to run the example:

1. Set up authentication credentials in one of the following ways:

   **Option A: Using a .env file (recommended)**
   - Create a new file named `.env`
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
   - Application names (ensure they exist in your environment)
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     SKIP_CLEANUP=true  # To preserve created objects
     ```

4. Run the script with various options:
   ```bash
   # Run all examples
   python application_group.py

   # Create only basic application groups
   python application_group.py --basic

   # Create only custom application groups
   python application_group.py --custom

   # Create only nested application groups
   python application_group.py --nested

   # Create only mixed application groups
   python application_group.py --mixed

   # Create only bulk application groups
   python application_group.py --bulk

   # Skip cleaning up created objects
   python application_group.py --skip-cleanup

   # Skip CSV report generation
   python application_group.py --no-report

   # Specify a different folder
   python application_group.py --folder=Production
   ```

5. Examine the console output to understand:
   - The application groups being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process with dependency handling

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## Application Group Model Structure

The examples demonstrate the proper structure for application group configurations:

### Basic Application Group

```python
{
    "name": "web-browsing-group",
    "folder": "Texas",  # Container - folder, snippet, or device required
    "members": ["web-browsing", "ssl", "dns"]  # List of application names
}
```

### Nested Application Group

```python
{
    "name": "security-applications",
    "folder": "Texas",
    "members": [
        "security-updates",  # Reference to another application group
        "certificate-services",  # Reference to another application group
        "dns"  # Individual application
    ]
}
```

### Application Group with Different Container

```python
# Using snippet container instead of folder
{
    "name": "compliance-apps",
    "snippet": "shared",  # Using snippet container
    "members": ["web-browsing", "dns", "ssl"]
}

# Using device container
{
    "name": "device-specific-apps",
    "device": "firewall1",  # Using device container
    "members": ["ping", "dns"]
}
```

## Important Considerations for Application Groups

When working with application groups, keep in mind:

1. **Member References**: Members must reference valid applications or application groups that exist in your environment.

2. **Container Requirements**: You must specify exactly one container (folder, snippet, or device).

3. **Circular References**: Avoid creating circular references between application groups, as this will cause API errors.

4. **Deletion Dependencies**: When deleting application groups, you must delete groups that are used as members of other groups before deleting the groups that reference them.

5. **Name Limitations**: Application group names must follow SCM naming conventions (max 63 characters, valid characters).

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Dependency Management** - Proper handling of reference dependencies in cleanup
2. **Error Handling** - Comprehensive try/except blocks for each API call
3. **Unique Naming** - Using UUID suffixes to avoid name conflicts
4. **Modular Code Organization** - Separate functions for each group type
5. **Proper Cleanup** - Ensuring all created objects are deleted in the correct order
6. **Logging** - Consistent and informative log messages with color coding
7. **Command-line Arguments** - Flexible script execution with various options
8. **Environment Variable Support** - Using .env files for credentials
9. **Progress Tracking** - Showing progress during lengthy operations
10. **Performance Metrics** - Tracking and reporting execution statistics

## Best Practices

1. **Application Group Design**
   - Use clear, descriptive names that indicate the group's purpose
   - Group applications based on functional similarity or policy requirements
   - Keep groups focused rather than creating overly broad groups
   - Consider the hierarchy when designing nested groups

2. **Group Organization**
   - Create logical hierarchies with nested groups
   - Avoid deeply nested structures that become difficult to maintain
   - Consider creating separate groups for different security zones or functions
   - Use a consistent naming convention for easier management

3. **Naming Conventions**
   - Include the group purpose in the name (e.g., "web-apps", "email-apps")
   - Use consistent prefixes for similar group types
   - Consider including environment information in names

4. **API Usage**
   - Handle all exceptions appropriately
   - Validate application names before API calls
   - Implement robust cleanup procedures that handle dependencies
   - Consider the impact of nested references when deleting objects

5. **Security Considerations**
   - Group applications based on security requirements
   - Consider least-privilege principles when designing groups
   - Document group purposes in your security documentation
   - Regularly audit application groups for unnecessary or outdated applications
