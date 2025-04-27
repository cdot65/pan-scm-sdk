# Application Object Examples

This guide provides examples of creating, managing, and working with Application objects in the Palo Alto Networks Strata Cloud Manager (SCM) using the SCM SDK.

> **IMPORTANT NOTE**: The current `ApplicationResponseModel` in the SCM SDK **does not have a tag field**. Examples in this document that reference the `tag` field need to be modified. See the [Tag Field Error](#tag-field-error) section under Troubleshooting for details.

## Table of Contents

1. [Overview](#overview)
2. [Application Object Types](#application-object-types)
3. [Example Script Capabilities](#example-script-capabilities)
4. [Running the Examples](#running-the-examples)
5. [Code Snippets](#code-snippets)
   - [Creating Business Applications](#creating-business-applications)
   - [Creating Secure Applications](#creating-secure-applications)
   - [Creating High-Risk Applications](#creating-high-risk-applications)
   - [Creating Protocol Applications](#creating-protocol-applications)
   - [Updating Application Objects](#updating-application-objects)
   - [Listing and Filtering Applications](#listing-and-filtering-applications)
   - [Bulk Operations](#bulk-operations)
   - [Cleanup Operations](#cleanup-operations)
   - [Report Generation](#report-generation)
6. [Common Scenarios](#common-scenarios)
7. [Troubleshooting](#troubleshooting)

## Overview {#Overview}

Applications in Strata Cloud Manager define the characteristics of specific applications that can be used in security policies. The Application SDK service allows you to create, retrieve, update, delete, and list custom applications with various security attributes.

This example shows how to work with various application types and demonstrates real-world usage patterns of the Application service in the SCM SDK.

## Application Object Types

The example script demonstrates creating several types of application objects:

1. **Business Applications**: Standard applications for business systems (databases, ERP, etc.)
   - Moderate risk level (typically 2-3)
   - Specific ports and protocols
   - Business-related categorization

2. **Secure Applications**: Trusted applications with higher security profiles
   - Lower risk level (typically 1-2)
   - Security attributes indicated safety (no vulnerabilities, not evasive)
   - May have file transfer capabilities

3. **High-Risk Applications**: Applications with security concerns
   - Higher risk level (4-5)
   - Security attributes flagged (evasive, used by malware, etc.)
   - Often file-sharing or potentially dangerous applications

4. **Protocol Applications**: Specific network protocols
   - Custom TCP/UDP port definitions
   - Typically networking-related categories
   - Technical implementation details

## Example Script Capabilities

The example script (`application.py`) demonstrates:

- Creating different types of applications with appropriate attributes
- Setting security characteristics (evasive, transfers_files, etc.)
- Updating existing applications
- Listing applications with filtering based on category, risk, etc.
- Bulk operations for creating multiple objects
- Generating detailed CSV reports of created objects
- Proper cleanup of created objects

## Running the Examples

To run the examples:

1. Ensure you have the SCM SDK installed:
   ```bash
   pip install pan-scm-sdk
   ```

2. Set up your credentials using either:
   - Environment variables:
     ```bash
     export SCM_CLIENT_ID="your_client_id"
     export SCM_CLIENT_SECRET="your_client_secret"
     export SCM_TSG_ID="your_tsg_id"
     ```
   - Or create a `.env` file with the same variables

3. Run the script:
   ```bash
   python application.py
   ```

### Command Line Options

The script supports several command-line options:

- `--skip-cleanup`: Preserve created objects (don't delete them)
- `--business`: Create only business application examples
- `--secure`: Create only secure application examples
- `--high-risk`: Create only high-risk application examples
- `--protocol`: Create only protocol application examples
- `--bulk`: Create only bulk application examples
- `--all`: Create all application object types (default)
- `--no-report`: Skip CSV report generation
- `--folder [name]`: Folder to create objects in (default: "Texas")

Example:
```bash
python application.py --high-risk --secure --folder Production --skip-cleanup
```

## Code Snippets

### Creating Business Applications

```python
business_app_config = {
    "name": "custom-db-app",
    "description": "Custom database application",
    "folder": "Texas",  # Folder must exist in SCM
    # Note: The tag field is not supported in ApplicationResponseModel
    # "tag": ["Finance", "Database"],  # This would be ignored
    "category": "business-systems",
    "subcategory": "database",
    "technology": "client-server",
    "risk": 3,
    "ports": ["tcp/1521", "tcp/1525"],
}

application = applications.create(business_app_config)
```

### Creating Secure Applications

```python
secure_app_config = {
    "name": "secure-messaging",
    "description": "Secure internal messaging application",
    "folder": "Texas",
    "tag": ["Secure", "Internal"],
    "category": "collaboration",
    "subcategory": "instant-messaging",
    "technology": "peer-to-peer",
    "risk": 1,
    "ports": ["tcp/8443"],
    "transfers_files": True,
    "has_known_vulnerabilities": False,
    "evasive": False,
    "pervasive": True,
}

secure_app = applications.create(secure_app_config)
```

### Creating High-Risk Applications

```python
risk_app_config = {
    "name": "p2p-file-sharing",
    "description": "High-risk file sharing application",
    "folder": "Texas",
    "tag": ["HighRisk", "FileSharing"],
    "category": "file-sharing",
    "subcategory": "p2p",
    "technology": "peer-to-peer",
    "risk": 5,
    "ports": ["tcp/6881-6889"],
    "transfers_files": True,
    "has_known_vulnerabilities": True,
    "evasive": True,
    "used_by_malware": True,
    "prone_to_misuse": True,
    "no_certifications": True,
}

risk_app = applications.create(risk_app_config)
```

### Creating Protocol Applications

```python
protocol_app_config = {
    "name": "custom-network-protocol",
    "description": "Custom network protocol for internal use",
    "folder": "Texas",
    "tag": ["Internal", "Protocol"],
    "category": "networking",
    "subcategory": "protocol",
    "technology": "network-protocol",
    "risk": 2,
    "ports": ["tcp/9000", "udp/9000"],
}

protocol_app = applications.create(protocol_app_config)
```

### Updating Application Objects

```python
# First retrieve the application
app = applications.get(application_id)

# Update attributes
app.description = "Updated description"
app.risk = 4  # Increase risk level
app.ports = app.ports + ["tcp/1526"]  # Add another port
app.tag = app.tag + ["Updated"]  # Add a tag

# Submit the update
updated_app = applications.update(app)
```

### Listing and Filtering Applications

```python
# List all applications in a folder
all_apps = applications.list(folder="Texas")

# Filter by category
business_apps = applications.list(folder="Texas", category=["business-systems"])

# Filter by risk level
high_risk_apps = applications.list(folder="Texas", risk=[4, 5])

# Combined filters
combined = applications.list(
    folder="Texas",
    category=["file-sharing"],
    subcategory=["p2p"],
    risk=[5]
)
```

### Bulk Operations

```python
# Define multiple application configurations
app_configs = [
    {
        "name": "bulk-app-1",
        "category": "business-systems",
        "subcategory": "erp",
        "technology": "client-server",
        "risk": 2,
        "folder": "Texas",
        "ports": ["tcp/8080"],
    },
    {
        "name": "bulk-app-2",
        "category": "media",
        "subcategory": "streaming",
        "technology": "client-server",
        "risk": 3,
        "folder": "Texas",
        "ports": ["tcp/1935"],
    }
]

# Create each application
created_ids = []
for config in app_configs:
    try:
        app = applications.create(config)
        created_ids.append(app.id)
    except Exception as e:
        print(f"Error creating {config['name']}: {str(e)}")
```

### Cleanup Operations

```python
# Delete applications created during the session
for app_id in created_application_ids:
    try:
        applications.delete(app_id)
        print(f"Deleted application {app_id}")
    except NotFoundError:
        print(f"Application {app_id} not found")
    except Exception as e:
        print(f"Error deleting application {app_id}: {str(e)}")
```

### Report Generation

```python
# Create CSV report of applications
with open("applications_report.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Write headers
    writer.writerow([
        "ID", "Name", "Category", "Subcategory",
        "Technology", "Risk", "Ports", "Security Attributes"
    ])

    # Write application data
    for app_id in application_ids:
        app = applications.get(app_id)

        # Collect security attributes
        security_attrs = []
        if hasattr(app, "evasive") and app.evasive:
            security_attrs.append("Evasive")
        if hasattr(app, "used_by_malware") and app.used_by_malware:
            security_attrs.append("Used by Malware")
        # Add more attributes as needed

        writer.writerow([
            app.id,
            app.name,
            app.category,
            app.subcategory,
            app.technology,
            app.risk,
            ", ".join(app.ports) if hasattr(app, "ports") and app.ports else "None",
            ", ".join(security_attrs)
        ])
```

## Common Scenarios

### Creating Applications for Security Rules

Applications are commonly used in security rules, so you might create applications to:

1. Create custom applications for internal services not covered by pre-defined applications
2. Define applications with specific port ranges for your organization
3. Set appropriate risk levels for applications in your environment
4. Tag applications for easier management in security policies

Example for a custom internal application for use in security policies:

```python
internal_app = {
    "name": "custom-internal-app",
    "description": "Internal application for departmental use",
    "folder": "Texas",
    "tag": ["Internal", "Approved"],
    "category": "business-systems",
    "subcategory": "custom",
    "technology": "client-server",
    "risk": 1,  # Low risk as it's internal and approved
    "ports": ["tcp/8888"],
    "transfers_files": False,
    "has_known_vulnerabilities": False,
}

app = applications.create(internal_app)
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Ensure your credentials (client_id, client_secret, tsg_id) are correct
   - Check that your authentication token hasn't expired

2. **Name Conflicts**:
   - Application names must be unique within a container
   - Use unique naming patterns or UUIDs to avoid conflicts

3. **Invalid Parameters**:
   - Ensure category, subcategory, and technology values are valid
   - Risk must be an integer between 1-5
   - At least one container (folder or snippet) must be specified

4. **Unknown Folders**:
   - Verify the folder exists in your SCM environment
   - Check for typos in folder names

5. <a name="tag-field-error"></a>**Tag Field Error**:
   - The current `ApplicationResponseModel` in the SCM SDK **does not include a tag field**
   - You'll see the error: `'ApplicationResponseModel' object has no attribute 'tag'` if you try to access it
   - When creating objects, any provided `tag` field will be ignored
   - When generating reports, use a placeholder like "None" for the tag column
   - The examples in this document showing `tag` fields won't work without modifying the SDK
   - To fix the tag field error in your code:
     - Remove any `tag` field from your application configuration dictionaries
     - Don't reference `app.tag` in your code when processing application objects
     - Use `hasattr(app, 'tag')` to check if the field exists before accessing it
     - If you need tagging functionality, consider using the SDK's separate tag management capabilities

### Debugging Tips

1. Enable DEBUG logging:
   ```bash
   export SCM_LOG_LEVEL=DEBUG
   ```

2. Use `try/except` blocks to catch specific exceptions:
   ```python
   try:
       app = applications.create(app_config)
   except InvalidObjectError as e:
       print(f"Invalid object data: {e.message}")
       if e.details:
           print(f"Details: {e.details}")
   except NameNotUniqueError as e:
       print(f"Name already exists: {e.message}")
   except Exception as e:
       print(f"Unexpected error: {str(e)}")
   ```

3. Check SDK version to ensure you have the latest features:
   ```python
   import scm
   print(f"SCM SDK Version: {scm.__version__}")
   ```
