# Comprehensive Address Group SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage address groups across a wide range of real-world enterprise scenarios.

## Overview

The `address_group.py` script showcases enterprise-ready address group configurations addressing common network grouping needs, including:

1. **Static Address Groups**:
   - Explicitly defined membership - for unchanging address collections
   - Multi-member groups - combining various address types
   - Reference-based management - updating members by name

2. **Dynamic Address Groups**:
   - Tag-based membership - defining membership through tag expressions
   - Complex filter expressions - using logical operators (AND, OR, NOT)
   - Automatic membership updates - members change as tags change

3. **Nested Address Groups**:
   - Group hierarchies - groups containing other groups
   - Multi-level nesting - for complex network segmentation

4. **Operational Functions**:
   - Bulk operations - for mass configuration
   - Advanced filtering - finding groups by criteria
   - Comprehensive error handling - proper exception management
   - Safe cleanup procedures - dependency-aware removal

5. **Reporting and Documentation**:
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

The script is organized into modular functions that each demonstrate a specific address group type or operational task:

### Address Object Creation
- `create_address_objects()` - Creates address objects to be used as group members

### Static Address Group Examples
- `create_static_address_group()` - Creates a static group with explicit members

### Dynamic Address Group Examples
- `create_dynamic_address_group()` - Creates a tag-based dynamic group
- `create_complex_tag_filter_group()` - Creates a dynamic group with complex filter expression
- `Important Note:` Address groups can only be static OR dynamic, not both

### Nested Address Group Examples
- `create_nested_address_group()` - Creates a group containing other groups

### Bulk Operations
- `create_bulk_address_groups()` - Creates multiple address groups programmatically

### Operational Functions
- `fetch_and_update_address_group()` - Modifying existing address groups
- `list_and_filter_address_groups()` - Finding and filtering address groups
- `cleanup_address_objects()` - Safely removing address objects
- `cleanup_address_groups()` - Safely removing address groups
- `generate_address_group_report()` - Creating comprehensive CSV reports

## Real-World Address Group Scenarios

The example script demonstrates these common real-world address group patterns:

### 1. Static Address Group
```python
static_group_config = {
    "name": "static-servers-group",
    "description": "Example static address group for servers",
    "folder": "Texas",
    "tag": ["Automation", "Example"],
    "static": ["server1", "server2", "server3"],  # Static members by name
}
```

### 2. Simple Dynamic Address Group
```python
dynamic_group_config = {
    "name": "dynamic-web-servers",
    "description": "Example dynamic address group for web servers",
    "folder": "Texas",
    "tag": ["Automation", "Example"],
    "dynamic": {
        "filter": "'Web' and 'Production'"  # Matches addresses with both tags
    }
}
```

### 3. Complex Dynamic Address Group Filter
```python
complex_group_config = {
    "name": "complex-filter-group",
    "description": "Example dynamic address group with complex filter",
    "folder": "Texas",
    "tag": ["Automation", "Example"],
    "dynamic": {
        "filter": "'Automation' and ('Servers' or 'Database')"
    }
}
```

### 4. Nested Address Group
```python
nested_group_config = {
    "name": "nested-group-example",
    "description": "Example nested address group",
    "folder": "Texas",
    "tag": ["Automation", "Example"],
    "static": ["static-servers-group", "dynamic-web-servers"],  # Groups as members
}
```

### 5. Bulk Group Creation
```python
# Create multiple related groups at once
group_configs = [
    {
        "name": "servers-group",
        "description": "Server address group",
        "folder": "Texas",
        "tag": ["Automation", "Bulk", "Servers"],
        "static": ["server1", "server2"],
    },
    {
        "name": "workstations-group",
        "description": "Workstation address group",
        "folder": "Texas",
        "tag": ["Automation", "Bulk", "Workstations"],
        "static": ["workstation-network"],
    },
    {
        "name": "all-endpoints-group",
        "description": "All endpoints address group",
        "folder": "Texas",
        "tag": ["Automation", "Bulk"],  # Be careful with tag names - use only valid tags
        "static": ["server1", "workstation-network", "guest-network"],
    },
    {
        "name": "filter-web-group",
        "description": "Web servers filter group",
        "folder": "Texas",
        "tag": ["Automation", "Bulk", "Web"],
        "dynamic": {
            "filter": "'Web' and 'Automation'"
        },
    }
]
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
   - Tag values (using "Automation", "Web", "Servers", etc.)
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     SKIP_CLEANUP=true  # To preserve created objects
     ```

4. Run the script with various options:
   ```bash
   # Run all examples
   python address_group.py
   
   # Create only static address groups
   python address_group.py --static
   
   # Create only dynamic address groups
   python address_group.py --dynamic
   
   # Create only nested address groups
   python address_group.py --nested
   
   # Create only bulk address groups
   python address_group.py --bulk
   
   # Skip cleaning up created objects
   python address_group.py --skip-cleanup
   
   # Skip CSV report generation
   python address_group.py --no-report
   
   # Specify a different folder
   python address_group.py --folder=Production
   ```

5. Examine the console output to understand:
   - The address objects and groups being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## Address Group Model Structure

The examples demonstrate the proper structure for each address group type:

### Static Address Group

```python
{
    "name": "static-group-example",
    "description": "Static group containing explicit members",
    "folder": "Texas",
    "tag": ["Tag1", "Tag2"],
    "static": ["member1", "member2", "member3"]  # List of member names
}
```

### Dynamic Address Group

```python
{
    "name": "dynamic-group-example",
    "description": "Dynamic group using tag filter",
    "folder": "Texas",
    "tag": ["Tag1", "Tag2"],
    "dynamic": {
        "filter": "'Tag3' and 'Tag4'"  # Tag expression
    }
}
```

### Nested Address Group

```python
{
    "name": "nested-group-example",
    "description": "Group containing other groups",
    "folder": "Texas",
    "tag": ["Tag1", "Tag2"],
    "static": ["group1", "group2"]  # Other groups as members
}
```

### Complex Filter Expression

The dynamic address group filter syntax supports expressions with logical operators:

- **Basic Tag Match**: `'TagName'`
- **AND Operator**: `'Tag1' and 'Tag2'`
- **OR Operator**: `'Tag1' or 'Tag2'`
- **NOT Operator**: `not 'Tag1'`
- **Grouping**: `('Tag1' or 'Tag2') and 'Tag3'`
- **Complex Example**: `'Automation' and ('Servers' or 'Database')`

**Important Notes**:
- Ensure proper syntax in your filter expressions
- Make sure all tag names in the filter actually exist in your environment
- Keep expressions as simple as possible to avoid syntax errors
- Test your filter expressions carefully before deploying

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Unique Naming** - Using UUID suffixes to avoid name conflicts
3. **Modular Code Organization** - Separate functions for each address group type
4. **Dependency Management** - Creating address objects before groups
5. **Dependency-Aware Cleanup** - Smart deletion with retry logic and proper ordering
6. **Logging** - Consistent and informative log messages with color coding
7. **Command-line Arguments** - Flexible script execution with various options
8. **Environment Variable Support** - Using .env files for credentials
9. **Progress Tracking** - Showing progress during lengthy operations
10. **Performance Metrics** - Tracking and reporting execution statistics

## Best Practices

1. **Address Group Design**
   - Use clear, descriptive names with consistent naming conventions
   - Apply appropriate tags for group categorization
   - Document the purpose in the description field
   - Keep group hierarchies simple and logical

2. **Group Type Selection**
   - Use static groups for explicitly defined membership that changes rarely
   - Use dynamic groups for membership that should update automatically
   - Use nested groups for creating hierarchical grouping structures
   - A group must be either static OR dynamic, not both
   - Consider future maintenance when choosing between static and dynamic

3. **Naming Conventions**
   - Include the group type in the name (e.g., "static-servers", "dynamic-webapps")
   - Use consistent prefixes for similar group types
   - Consider including location or environment information in names

4. **Tag Filter Expressions**
   - Keep filter expressions as simple as possible
   - Use parentheses to clarify complex expressions
   - Ensure proper syntax in filter expressions to avoid errors
   - Make sure tags in filter expressions actually exist in your environment
   - Document complex filters in the description field
   - Test filter expressions to ensure they match expected addresses

5. **Security Considerations**
   - Document sensitive groups through tags and descriptions
   - Consider auditing and logging requirements
   - Follow the principle of least privilege when assigning permissions
   - Use consistent naming and description conventions for easier auditing