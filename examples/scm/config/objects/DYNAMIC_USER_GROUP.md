# Comprehensive Dynamic User Group SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage dynamic user groups across a wide range of real-world enterprise scenarios.

## Overview

The `dynamic_user_group.py` script showcases enterprise-ready dynamic user group configurations addressing common access control needs, including:

1. **Simple Tag-Based Filtering**:
   - Filtering users based on individual tag attributes
   - Executive-level access groups
   - Basic role-based filtering

2. **Complex Boolean Expressions**:
   - Advanced filtering with AND, OR, and NOT operators
   - Multi-condition logic for sophisticated access policies
   - Combining multiple tag attributes in boolean expressions

3. **Multi-Attribute Filtering**:
   - Filtering based on multiple user attributes simultaneously
   - Fine-grained targeting of specific user populations
   - Combining attribute types for precise segmentation

4. **Department-Based Filtering**:
   - Organizational division-based groups
   - Department-specific access control
   - Functional area delineation

5. **Role-Based Filtering**:
   - Functional role-based grouping
   - Cross-departmental access control
   - Job function-based segmentation

6. **Operational Functions**:
   - Bulk creation capabilities - for mass configuration
   - Advanced filtering and search capabilities
   - Comprehensive error handling
   - Safe cleanup procedures

7. **Reporting and Documentation**:
   - Detailed CSV report generation with group details
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

The script is organized into modular functions that each demonstrate a specific dynamic user group type or operational task:

### Dynamic User Group Creation Examples
- `create_simple_tag_based_group()` - Basic tag-based filtering
- `create_complex_boolean_group()` - Advanced boolean expression filtering
- `create_multi_attribute_group()` - Filtering on multiple attributes
- `create_department_based_group()` - Department-specific filtering
- `create_role_based_group()` - Role-based access filtering

### Bulk Operations
- `create_bulk_dynamic_user_group_objects()` - Creating multiple groups programmatically

### Operational Functions
- `fetch_and_update_dynamic_user_group()` - Modifying existing groups
- `list_and_filter_dynamic_user_groups()` - Finding and filtering groups
- `cleanup_dynamic_user_group_objects()` - Safely removing test objects
- `generate_dynamic_user_group_report()` - Creating comprehensive CSV reports

## Real-World Dynamic User Group Scenarios

The example script demonstrates these common real-world dynamic user group patterns:

### 1. Simple Tag-Based Group
```python
simple_group_config = {
    "name": "exec-users-example",
    "description": "Executive users identified by role tag",
    "folder": "Texas",
    "tag": ["Automation", "Executive"],
    "filter": "tag.role.executive",  # Simple tag-based filter
}
```

### 2. Complex Boolean Expression Group
```python
complex_group_config = {
    "name": "it-admins-example",
    "description": "IT administrators with specific access requirements",
    "folder": "Texas",
    "tag": ["Automation", "IT"],
    # Using AND and OR operators to create complex logic
    "filter": "(tag.department.it AND tag.role.administrator) OR (tag.access.systems AND tag.level.admin)",
}
```

### 3. Multi-Attribute Group
```python
multi_attr_config = {
    "name": "contractors-example",
    "description": "External contractors with specific access requirements",
    "folder": "Texas",
    "tag": ["Automation", "Contractors"],
    # Filtering on employment status, location, and security clearance
    "filter": "tag.employment.contractor AND tag.location.remote AND tag.clearance.standard",
}
```

### 4. Department-Based Group
```python
department_group_config = {
    "name": "finance-users-example",
    "description": "All users in the finance department",
    "folder": "Texas",
    "tag": ["Automation", "Finance"],
    "filter": "tag.department.finance",  # Simple department tag filtering
}
```

### 5. Role-Based Group
```python
role_group_config = {
    "name": "developers-example",
    "description": "Software developers across all departments",
    "folder": "Texas",
    "tag": ["Automation", "Developers"],
    "filter": "tag.role.developer OR tag.role.engineer",  # Role-based filtering with OR condition
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
   - Filter expressions to match your tagging schema
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     SKIP_CLEANUP=true  # To preserve created objects
     ```

4. Run the script with various options:
   ```bash
   # Run all examples
   python dynamic_user_group.py
   
   # Create only simple tag-based dynamic user groups
   python dynamic_user_group.py --simple
   
   # Create only complex boolean dynamic user groups
   python dynamic_user_group.py --complex
   
   # Create only multi-attribute dynamic user groups
   python dynamic_user_group.py --multi
   
   # Create only department-based dynamic user groups
   python dynamic_user_group.py --department
   
   # Create only role-based dynamic user groups
   python dynamic_user_group.py --role
   
   # Create only bulk dynamic user groups
   python dynamic_user_group.py --bulk
   
   # Skip cleaning up created objects
   python dynamic_user_group.py --skip-cleanup
   
   # Skip CSV report generation
   python dynamic_user_group.py --no-report
   
   # Specify a different folder
   python dynamic_user_group.py --folder=Production
   ```

5. Examine the console output to understand:
   - The dynamic user groups being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## Dynamic User Group Model Structure

The examples demonstrate the proper structure for dynamic user group configurations:

### Simple Tag-Based Group

```python
{
    "name": "finance-dept",
    "description": "All finance department users",
    "folder": "Texas",  # Container - folder, snippet, or device required
    "tag": ["Finance", "Department"],  # Optional object tags
    "filter": "tag.department.finance"  # Tag-based filter expression
}
```

### Complex Boolean Expression Group

```python
{
    "name": "high-privilege-users",
    "description": "Users with elevated access privileges",
    "folder": "Texas",
    "tag": ["Security", "Access-Control"],
    "filter": "(tag.role.admin OR tag.role.executive) AND tag.clearance.high"
}
```

### Container Options

```python
# Using snippet container instead of folder
{
    "name": "remote-workers",
    "description": "All remote employees",
    "snippet": "shared",  # Using snippet container
    "filter": "tag.location.remote"
}

# Using device container
{
    "name": "device-admins",
    "description": "Device administrators",
    "device": "firewall1",  # Using device container
    "filter": "tag.access.device-admin"
}
```

## Filter Expression Syntax

Dynamic user group filter expressions follow a specific syntax:

1. **Simple tag references**:
   - `tag.category.value`
   - Example: `tag.department.finance`

2. **Boolean operators**:
   - `AND`: Logical AND - both conditions must be true
   - `OR`: Logical OR - either condition can be true
   - `NOT`: Logical NOT - inverts the condition
   - Example: `tag.department.it AND tag.role.admin`

3. **Grouping with parentheses**:
   - Use parentheses to establish precedence
   - Example: `(tag.department.it OR tag.department.security) AND tag.level.admin`

4. **Compound expressions**:
   - Combine multiple conditions for precise targeting
   - Example: `tag.location.remote AND (tag.role.dev OR tag.role.qa) AND NOT tag.status.contractor`

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Unique Naming** - Using UUID suffixes to avoid name conflicts
3. **Modular Code Organization** - Separate functions for each group type
4. **Proper Cleanup** - Ensuring all created objects are deleted
5. **Logging** - Consistent and informative log messages with color coding
6. **Command-line Arguments** - Flexible script execution with various options
7. **Environment Variable Support** - Using .env files for credentials
8. **Progress Tracking** - Showing progress during lengthy operations
9. **Performance Metrics** - Tracking and reporting execution statistics

## Best Practices

1. **Dynamic User Group Design**
   - Use clear, descriptive names that indicate the purpose of the group
   - Keep filter expressions as simple as possible while achieving the desired targeting
   - Document the purpose of the filter expression in the description field
   - Test filter expressions thoroughly to ensure they match the intended users

2. **Filter Expression Development**
   - Start with simple expressions and build complexity incrementally
   - Test expressions against known user sets to verify correct matching
   - Use parentheses to clarify operator precedence, even when not strictly required
   - Keep expressions focused on a single logical access control need

3. **Naming Conventions**
   - Include the group purpose in the name (e.g., "finance-users", "admin-access")
   - Use consistent naming patterns across related groups
   - Consider including filter criteria highlights in the name for easy identification

4. **API Usage**
   - Handle all exceptions appropriately
   - Validate filter expressions before API calls
   - Implement proper error handling and logging
   - Consider the performance impact of complex filter expressions

5. **Security Considerations**
   - Document the security implications of each dynamic user group
   - Regularly audit filter expressions to ensure they remain accurate
   - Consider the principle of least privilege when designing filter expressions
   - Implement change management processes for modifying dynamic user groups