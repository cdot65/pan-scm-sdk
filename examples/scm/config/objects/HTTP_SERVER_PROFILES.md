# Comprehensive HTTP Server Profiles SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage HTTP Server Profiles across a wide range of enterprise logging and monitoring scenarios.

## Overview

The `http_server_profiles.py` script showcases enterprise-ready HTTP server profile configurations addressing common log collection needs, including:

1. **Basic HTTP Server Profile Configurations**:
   - HTTP profiles with simple server configuration
   - HTTPS profiles with TLS settings and certificate configuration
   - Multi-server profiles for redundancy and load distribution
   - Format configuration for different log types

2. **HTTP Server Profile Management Operations**:
   - Creating profiles in different locations (folders, snippets, devices)
   - Retrieving and filtering profiles using various criteria
   - Updating existing profiles to modify server configurations
   - Bulk management of profiles for multiple log servers

3. **Server Configurations**:
   - HTTP protocol configuration with various ports
   - HTTPS protocol with different TLS versions
   - Certificate profile settings
   - HTTP method specification (GET, POST, PUT, DELETE)

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

## Script Organization

The script is organized into modular functions that each demonstrate a specific HTTP server profile configuration pattern or operational task:

### Basic HTTP Server Profile Examples
- `create_basic_http_server_profile()` - Simple HTTP server configuration
- `create_https_server_profile()` - HTTPS server with TLS settings
- `create_multi_server_profile()` - Profile with multiple servers
- `create_http_server_profile_with_snippet()` - Creating profiles in snippet containers
- `create_http_server_profile_with_device()` - Creating profiles in device containers

### Operational Functions
- `fetch_and_update_http_server_profile()` - Updating existing profiles
- `list_and_filter_http_server_profiles()` - Filtering profiles with various criteria
- `fetch_http_server_profile_by_name()` - Retrieving a profile by name
- `delete_http_server_profile()` - Deleting a profile
- `cleanup_http_server_profiles()` - Safely removing test profiles
- `generate_http_server_profile_report()` - Creating CSV reports of profiles

## Real-World HTTP Server Profile Scenarios

The example script demonstrates these common real-world HTTP server profile scenarios:

### 1. Basic HTTP Server Profile
```python
basic_profile_config = {
    "name": "basic-http-profile-12345",
    "description": "Example basic HTTP server profile",
    "folder": "Texas",
    "tag_registration": True,
    "server": [
        {
            "name": "log-collector",
            "address": "192.168.1.100",
            "protocol": "HTTP",
            "port": 80,
            "http_method": "POST"
        }
    ],
    "format": {
        "traffic": {},
        "threat": {},
        "url": {},
    }
}
```

### 2. HTTPS Server with TLS Configuration
```python
https_profile_config = {
    "name": "https-server-profile-12345",
    "description": "Example HTTPS server profile with TLS configuration",
    "folder": "Texas",
    "tag_registration": True,
    "server": [
        {
            "name": "secure-log-collector",
            "address": "secure.example.com",
            "protocol": "HTTPS",
            "port": 443,
            "tls_version": "1.2",
            "certificate_profile": "default",
            "http_method": "POST"
        }
    ],
    "format": {
        "traffic": {},
        "threat": {},
        "url": {},
        "wildfire": {},
        "data": {},
    }
}
```

### 3. Multi-Server Profile for Redundancy
```python
multi_server_config = {
    "name": "multi-server-profile-12345",
    "description": "Example HTTP server profile with multiple server configurations",
    "folder": "Texas",
    "tag_registration": True,
    "server": [
        {
            "name": "primary-log-collector",
            "address": "192.168.1.100",
            "protocol": "HTTP",
            "port": 80,
            "http_method": "POST"
        },
        {
            "name": "backup-log-collector",
            "address": "192.168.1.101",
            "protocol": "HTTP",
            "port": 80,
            "http_method": "POST"
        },
        {
            "name": "secure-log-collector",
            "address": "secure.example.com",
            "protocol": "HTTPS",
            "port": 443,
            "tls_version": "1.2",
            "certificate_profile": "default",
            "http_method": "POST"
        }
    ],
    "format": {
        "traffic": {},
        "threat": {},
        "wildfire": {},
    }
}
```

### 4. Snippet Container Profile
```python
snippet_profile_config = {
    "name": "snippet-http-profile-12345",
    "description": "Example HTTP server profile in a snippet container",
    "snippet": "TestSnippet",  # Specify snippet instead of folder
    "tag_registration": True,
    "server": [
        {
            "name": "snippet-server",
            "address": "192.168.5.100",
            "protocol": "HTTP",
            "port": 80,
            "http_method": "POST"
        }
    ],
    "format": {
        "traffic": {},
        "threat": {},
    }
}
```

### 5. Device Container Profile
```python
device_profile_config = {
    "name": "device-http-profile-12345",
    "description": "Example HTTP server profile in a device container",
    "device": "TestDevice",  # Specify device instead of folder
    "server": [
        {
            "name": "device-server",
            "address": "10.0.0.100",
            "protocol": "HTTP",
            "port": 514,
            "http_method": "POST"
        }
    ],
    "format": {
        "traffic": {},
        "threat": {},
    }
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
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     ```

4. Run the script with options to customize behavior:
   ```bash
   # Run all examples with default settings
   python http_server_profiles.py
   
   # Run only the creation examples
   python http_server_profiles.py --create
   
   # Run only listing examples
   python http_server_profiles.py --list
   
   # Skip CSV report generation
   python http_server_profiles.py --no-report
   
   # Skip cleanup to preserve created profiles
   python http_server_profiles.py --skip-cleanup
   
   # Use a different folder
   python http_server_profiles.py --folder "Production"
   ```

5. Examine the console output to understand:
   - The HTTP server profiles being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## HTTP Server Profile Model Structure

The examples demonstrate the proper structure for HTTP server profile models:

### HTTP Server Profile Create Model

```python
# Basic structure
http_profile_create = {
    "name": "profile-name",           # Required
    "description": "description",     # Optional
    "tag_registration": True,         # Optional
    "server": [                       # Required - at least one server
        {
            "name": "server-name",            # Required
            "address": "server-address",      # Required
            "protocol": "HTTP",               # Required - HTTP or HTTPS
            "port": 80,                       # Required
            "tls_version": "1.2",             # Optional - only for HTTPS
            "certificate_profile": "default", # Optional - only for HTTPS
            "http_method": "POST"             # Optional
        }
    ],
    "format": {                       # Optional
        "traffic": {},
        "threat": {},
        # Other log types...
    },
    "folder": "folder-name",          # Container - one of these is required
    # "snippet": "snippet-name",      # Alternative container
    # "device": "device-name",        # Alternative container
}
```

### HTTP Server Profile Update Model

```python
# Update model requires an ID
http_profile_update = HTTPServerProfileUpdateModel(
    id=profile_id,               # Required - UUID of the profile to update
    name="profile-name",         # Required
    server=[                     # Required - at least one server
        {
            "name": "server-name",
            "address": "server-address",
            "protocol": "HTTP",
            "port": 80,
            "http_method": "POST"
        }
    ],
    # Other fields as needed
)
```

### Server Configuration Options

HTTP server profiles support the following server configuration options:

```python
# HTTP server
http_server = {
    "name": "log-collector",
    "address": "192.168.1.100",
    "protocol": "HTTP",
    "port": 80,
    "http_method": "POST"  # Optional - GET, POST, PUT, DELETE
}

# HTTPS server
https_server = {
    "name": "secure-log-collector",
    "address": "secure.example.com",
    "protocol": "HTTPS",
    "port": 443,
    "tls_version": "1.2",         # Optional - 1.0, 1.1, 1.2, 1.3
    "certificate_profile": "default",  # Optional
    "http_method": "POST"         # Optional - GET, POST, PUT, DELETE
}
```

### Format Configuration

The format field allows you to configure different log types:

```python
format = {
    "traffic": {},     # Traffic logs
    "threat": {},      # Threat logs
    "url": {},         # URL filtering logs
    "wildfire": {},    # WildFire logs
    "data": {},        # Data filtering logs
    "gtp": {},         # GTP logs
    "tunnel": {},      # Tunnel logs
    "auth": {},        # Authentication logs
    # Other log types...
}
```

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Pydantic Model Construction** - Both direct dictionary and explicit model building approaches
3. **CSV Report Generation** - Generating detailed reports of created resources
4. **Unique Naming** - Using UUID suffixes to avoid name conflicts
5. **Modular Code Organization** - Separate functions for each profile type
6. **Proper Cleanup** - Ensuring all created objects are deleted
7. **Logging** - Consistent and informative log messages
8. **Object Model Conversion** - Converting between Pydantic models and dictionaries

## Best Practices

1. **HTTP Server Profile Design**
   - Use clear, descriptive names with consistent naming conventions
   - Document the purpose in the description field
   - Configure the appropriate log types in the format field
   - Consider security implications with HTTPS vs HTTP

2. **Server Configuration Selection**
   - Use HTTPS with TLS 1.2 or higher for secure log transmission
   - Configure multiple servers for redundancy
   - Use appropriate HTTP methods (usually POST for logging)
   - Consider certificate validation for HTTPS connections

3. **Organization Best Practices**
   - Group related profiles in a consistent folder structure
   - Consider using naming conventions that reflect the log types or destinations

4. **API Usage**
   - Handle all exceptions appropriately
   - Use proper data validation before API calls
   - Implement retry logic for production code
   - Consider rate limiting for large bulk operations

5. **Security Considerations**
   - Always use HTTPS for sensitive log data
   - Configure appropriate certificate validation
   - Consider tag registration implications
   - Use the latest TLS version supported by your log collectors

## Example Output

```bash
❯ poetry run python http_server_profiles.py --skip-cleanup
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
2025-02-28 07:30:23 INFO        HTTP SERVER PROFILE CONFIGURATION
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:23 INFO     ▶ STARTING: Initializing HTTP server profile manager
2025-02-28 07:30:23 INFO     ✓ COMPLETED: HTTP server profile manager initialization
2025-02-28 07:30:23 INFO
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:23 INFO        HTTP SERVER PROFILE CREATION
2025-02-28 07:30:23 INFO     ================================================================================
2025-02-28 07:30:23 INFO     Demonstrating HTTP server profile creation with various configurations
2025-02-28 07:30:23 INFO     Using folder: Texas
2025-02-28 07:30:23 INFO     ▶ STARTING: Creating basic HTTP server profile with HTTP protocol
2025-02-28 07:30:23 INFO     Profile name: basic-http-profile-9139c7
2025-02-28 07:30:23 INFO     Configuration details:
2025-02-28 07:30:23 INFO       - Name: basic-http-profile-9139c7
2025-02-28 07:30:23 INFO       - Server: log-collector (192.168.1.100)
2025-02-28 07:30:23 INFO       - Protocol: HTTP
2025-02-28 07:30:23 INFO       - Port: 80
2025-02-28 07:30:23 INFO       - Container: folder 'Texas'
2025-02-28 07:30:23 INFO     Sending request to Strata Cloud Manager API...
2025-02-28 07:30:23 INFO     ✓ Created HTTP server profile: basic-http-profile-9139c7
2025-02-28 07:30:23 INFO       - Profile ID: 4c4530cd-01af-473b-a2f7-b46bdee68dc5
2025-02-28 07:30:23 INFO       - Server: log-collector (192.168.1.100)
2025-02-28 07:30:23 INFO     ✓ COMPLETED: Basic HTTP server profile creation - Profile: basic-http-profile-9139c7
2025-02-28 07:30:23 INFO     ▶ STARTING: Creating HTTP server profile with HTTPS protocol
2025-02-28 07:30:23 INFO     Profile name: https-server-profile-212e13
```

## CSV Report Example

When the script generates a CSV report, it will look similar to the following:

```csv
Profile ID,Name,Description,Container Type,Container Name,Server Count,Server Names,Server Protocols,Server Ports,TLS Versions,Tag Registration,Format Types,Report Generation Time
4c4530cd-01af-473b-a2f7-b46bdee68dc5,basic-http-profile-9139c7,Example basic HTTP server profile,Folder,Texas,1,log-collector,HTTP,80,None,Enabled,"traffic, threat, url",2025-02-28 07:30:29
18a69eca-e198-40ec-8c56-9c4d1fc8588b,https-server-profile-212e13,Example HTTPS server profile with TLS configuration,Folder,Texas,1,secure-log-collector,HTTPS,443,secure-log-collector: 1.2,Enabled,"traffic, threat, url, wildfire, data",2025-02-28 07:30:29
d015823d-cf5a-4c65-819c-bf902b23ace4,multi-server-profile-abc123,Example HTTP server profile with multiple server configurations,Folder,Texas,3,"primary-log-collector, backup-log-collector, secure-log-collector","HTTP, HTTP, HTTPS","80, 80, 443",secure-log-collector: 1.2,Enabled,"traffic, threat, wildfire",2025-02-28 07:30:29
62882bd5-631e-4b93-8bd9-a06b8ff03208,snippet-http-profile-def456,Example HTTP server profile in a snippet container,Snippet,TestSnippet,1,snippet-server,HTTP,80,None,Enabled,"traffic, threat",2025-02-28 07:30:29
40291007-729a-445e-9431-cc6c6593d5af,device-http-profile-ghi789,Example HTTP server profile in a device container,Device,TestDevice,1,device-server,HTTP,514,None,Enabled,"traffic, threat",2025-02-28 07:30:29

SUMMARY
Total Profiles Processed,5
Successfully Retrieved,5
Failed to Retrieve,0
Execution Time (so far),6.82 seconds
Report Generated On,2025-02-28 07:30:29
```