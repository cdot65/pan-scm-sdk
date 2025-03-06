# Comprehensive HIP Objects SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage Host Information Profile (HIP) objects across a wide range of real-world enterprise scenarios.

## Overview

The `hip_object.py` script showcases enterprise-ready HIP object configurations addressing common endpoint posture assessment needs, including:

1. **Host Information Based HIP Objects**:
   - OS detection criteria - for identifying specific operating systems
   - Domain membership - for validating corporate domain membership
   - Managed state - for ensuring endpoints are under management

2. **Network Information Based HIP Objects**:
   - Network type criteria - for validating connection types (wired vs. wireless)
   - Connection security - for enforcing secure network connections

3. **Patch Management Based HIP Objects**:
   - Vendor product validation - for ensuring proper patch tools are installed
   - Missing patches severity - for validating patch compliance levels
   - Update recency - for enforcing timely patch installation

4. **Disk Encryption Based HIP Objects**:
   - Encryption status - for ensuring sensitive data is protected
   - Vendor compliance - for validating approved encryption solutions
   - Location-specific requirements - for enforcing drive-level encryption policies

5. **Mobile Device Based HIP Objects**:
   - Jailbreak detection - for preventing compromised devices
   - Encryption status - for ensuring sensitive data is protected
   - Passcode enforcement - for basic security compliance
   - Check-in time validation - for ensuring ongoing compliance
   - Application requirements - for enforcing MDM or security tools

6. **Certificate Based HIP Objects**:
   - Certificate attribute validation - for identifying trusted devices
   - Organization validation - for ensuring proper certificate issuance

## Prerequisites

Before running the examples, you need:

1. A Strata Cloud Manager account with appropriate permissions
2. Your SCM API credentials (client ID, client secret, and TSG ID)
3. Python 3.10 or higher
4. The PAN-SCM-SDK package installed (`pip install pan-scm-sdk`)
5. A folder named "Texas" in your SCM environment (or modify the script)

## Script Organization

The script is organized into modular functions that each demonstrate a specific HIP object type or operational task:

### HIP Object Type Examples
- `create_host_info_hip_object()` - Host information based HIP object
- `create_network_info_hip_object()` - Network information based HIP object
- `create_patch_management_hip_object()` - Patch management based HIP object
- `create_disk_encryption_hip_object()` - Disk encryption based HIP object
- `create_mobile_device_hip_object()` - Mobile device based HIP object
- `create_certificate_hip_object()` - Certificate based HIP object

### Bulk Operations
- `create_bulk_hip_objects()` - Creating multiple HIP objects programmatically

### Operational Functions
- `fetch_and_update_hip_object()` - Modifying existing HIP objects
- `list_and_filter_hip_objects()` - Finding and filtering HIP objects
- `cleanup_hip_objects()` - Safely removing test objects
- `generate_hip_object_report()` - Creating comprehensive CSV reports

## Real-World HIP Object Scenarios

The example script demonstrates these common real-world HIP object patterns:

### 1. Host Information Based HIP Object
```python
host_info_config = {
    "name": "windows-workstation",
    "description": "HIP object for Windows workstations with domain membership",
    "folder": "Texas",
    "host_info": {
        "criteria": {
            "os": {
                "contains": {
                    "Microsoft": "Windows 10"
                }
            },
            "domain": {
                "contains": "example.com"
            },
            "managed": True
        }
    }
}
```

### 2. Network Information Based HIP Object
```python
network_info_config = {
    "name": "wired-connection",
    "description": "HIP object for wired network connections only",
    "folder": "Texas",
    "network_info": {
        "criteria": {
            "network": {
                "is_not": {
                    "wifi": {}
                }
            }
        }
    }
}
```

### 3. Patch Management Based HIP Object
```python
patch_management_config = {
    "name": "patched-endpoints",
    "description": "HIP object for endpoints with up-to-date patches",
    "folder": "Texas",
    "patch_management": {
        "criteria": {
            "is_installed": True,
            "is_enabled": "yes",
            "missing_patches": {
                "severity": 4,
                "check": "has-none"
            }
        },
        "vendor": [
            {
                "name": "Microsoft",
                "product": ["Windows-Update"]
            }
        ]
    }
}
```

### 4. Disk Encryption Based HIP Object
```python
disk_encryption_config = {
    "name": "encrypted-endpoints",
    "description": "HIP object for fully encrypted system drives",
    "folder": "Texas",
    "disk_encryption": {
        "criteria": {
            "is_installed": True,
            "is_enabled": "yes",
            "encrypted_locations": [
                {
                    "name": "C:",
                    "encryption_state": {"is": "encrypted"}
                }
            ]
        },
        "vendor": [
            {
                "name": "Microsoft",
                "product": ["BitLocker-Drive-Encryption"]
            },
            {
                "name": "Symantec",
                "product": ["Endpoint-Encryption"]
            }
        ]
    }
}
```

### 5. Mobile Device Based HIP Object
```python
mobile_device_config = {
    "name": "secure-mobile-device",
    "description": "HIP object for secure mobile devices",
    "folder": "Texas",
    "mobile_device": {
        "criteria": {
            "jailbroken": False,
            "disk_encrypted": True,
            "passcode_set": True,
            "last_checkin_time": {"days": 7},
            "applications": {
                "has_malware": {},
                "includes": [
                    {
                        "name": "CompanyMDM",
                        "package": "com.company.mdm"
                    }
                ]
            }
        }
    }
}
```

### 6. Certificate Based HIP Object
```python
certificate_config = {
    "name": "corporate-cert",
    "description": "HIP object for certificate validation",
    "folder": "Texas",
    "certificate": {
        "criteria": {
            "certificate_attributes": [
                {
                    "name": "O",
                    "value": "Example-Corp"
                },
                {
                    "name": "OU",
                    "value": "IT-Security"
                }
            ]
        }
    }
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
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     SKIP_CLEANUP=true  # To preserve created objects
     ```

4. Run the script with various options:
   ```bash
   # Run all examples
   python hip_object.py
   
   # Create only Host Info HIP objects
   python hip_object.py --host-info
   
   # Create only Network Info HIP objects
   python hip_object.py --network-info
   
   # Create only Patch Management HIP objects
   python hip_object.py --patch-management
   
   # Create only Disk Encryption HIP objects
   python hip_object.py --disk-encryption
   
   # Create only Mobile Device HIP objects
   python hip_object.py --mobile-device
   
   # Create only Certificate HIP objects
   python hip_object.py --certificate
   
   # Create only bulk HIP objects
   python hip_object.py --bulk
   
   # Skip cleaning up created objects
   python hip_object.py --skip-cleanup
   
   # Skip CSV report generation
   python hip_object.py --no-report
   
   # Specify a different folder
   python hip_object.py --folder=Production
   ```

5. Examine the console output to understand:
   - The HIP objects being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## HIP Object Model Structure

The examples demonstrate the proper structure for each HIP object type:

### Host Information Based HIP Object

```python
{
    "name": "win10-corp-domain",
    "description": "Windows 10 endpoints on corporate domain",
    "folder": "Texas",
    "host_info": {
        "criteria": {
            "os": {
                "contains": {
                    "Microsoft": "Windows 10"
                }
            },
            "domain": {
                "contains": "corp.example.com"
            },
            "managed": True
        }
    }
}
```

### Network Information Based HIP Object

```python
{
    "name": "secure-network",
    "description": "Secure network connection requirements",
    "folder": "Texas",
    "network_info": {
        "criteria": {
            "network": {
                "is_not": {
                    "wifi": {}
                }
            }
        }
    }
}
```

### Patch Management Based HIP Object

```python
{
    "name": "patch-compliant",
    "description": "Endpoints with proper patch management",
    "folder": "Texas",
    "patch_management": {
        "criteria": {
            "is_installed": True,
            "is_enabled": "yes",
            "missing_patches": {
                "severity": 3,
                "check": "has-none"
            }
        },
        "vendor": [
            {
                "name": "Microsoft",
                "product": ["Windows-Update"]
            }
        ]
    }
}
```

### Disk Encryption Based HIP Object

```python
{
    "name": "full-disk-encryption",
    "description": "Fully encrypted endpoint requirements",
    "folder": "Texas",
    "disk_encryption": {
        "criteria": {
            "is_installed": True,
            "is_enabled": "yes",
            "encrypted_locations": [
                {
                    "name": "C:",
                    "encryption_state": {"is": "encrypted"}
                },
                {
                    "name": "D:",
                    "encryption_state": {"is": "encrypted"}
                }
            ]
        },
        "vendor": [
            {
                "name": "Microsoft",
                "product": ["BitLocker-Drive-Encryption"]
            }
        ]
    }
}
```

### Mobile Device Based HIP Object

```python
{
    "name": "corporate-mobile",
    "description": "Corporate mobile device requirements",
    "folder": "Texas",
    "mobile_device": {
        "criteria": {
            "jailbroken": False,
            "disk_encrypted": True,
            "passcode_set": True,
            "last_checkin_time": {"days": 7},
            "applications": {
                "has_malware": {},
                "includes": [
                    {
                        "name": "CorporateMDM",
                        "package": "com.example.mdm"
                    }
                ]
            }
        }
    }
}
```

### Certificate Based HIP Object

```python
{
    "name": "certificate-validation",
    "description": "Certificate validation requirements",
    "folder": "Texas",
    "certificate": {
        "criteria": {
            "certificate_attributes": [
                {
                    "name": "O",
                    "value": "Example-Corp"
                },
                {
                    "name": "OU",
                    "value": "IT-Security"
                }
            ]
        }
    }
}
```

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Unique Naming** - Using UUID suffixes to avoid name conflicts
3. **Modular Code Organization** - Separate functions for each HIP object type
4. **Proper Cleanup** - Ensuring all created objects are deleted
5. **Logging** - Consistent and informative log messages with color coding
6. **Command-line Arguments** - Flexible script execution with various options
7. **Environment Variable Support** - Using .env files for credentials
8. **Progress Tracking** - Showing progress during lengthy operations
9. **Performance Metrics** - Tracking and reporting execution statistics

## Best Practices

1. **HIP Object Design**
   - Use clear, descriptive names that indicate criteria type
   - Document the purpose and requirements in the description field
   - Use the most specific criteria for your needs
   - Combine multiple criteria types when appropriate for comprehensive policy

2. **Criteria Type Selection**
   - Use host_info for OS, domain, and management state checks
   - Use network_info for connection type validation
   - Use patch_management for update and patch compliance
   - Use disk_encryption for data protection validation
   - Use mobile_device for mobile-specific requirements
   - Use certificate for identity validation

3. **Naming Conventions**
   - Include the primary criteria type in the name (e.g., "host-windows", "encrypt-system")
   - Use consistent prefixes for similar object types
   - Consider including security level or environment information in names

4. **API Usage**
   - Handle all exceptions appropriately
   - Use proper data validation before API calls
   - Implement retry logic for production code
   - Consider rate limiting for large bulk operations

5. **Security Considerations**
   - Define appropriate HIP profiles based on sensitivity levels
   - Create progressive HIP objects for different security tiers
   - Validate HIP objects against your security policies
   - Document the specific security requirements each HIP object enforces