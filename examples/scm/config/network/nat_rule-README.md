# Comprehensive NAT Rules SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage NAT rules across a wide range of real-world enterprise scenarios.

## Overview

The `nat_rule.py` script showcases enterprise-ready NAT configurations addressing common network translation needs, including:

1. **Source NAT (SNAT) Configurations**:
   - Dynamic IP and Port (PAT/Overloading) - the most common outbound NAT method
   - Dynamic IP with address pool - preserving source ports for application compatibility
   - Dynamic IP with fallback options - for high availability
   - Static IP translation (1:1 mapping) - for servers requiring fixed public IPs
   - Interface-based translation - dynamic addressing from interface configuration

2. **Destination NAT (DNAT) Configurations**:
   - Single port forwarding - standard inbound service publishing
   - Multiple-port service publishing - exposing multiple ports on a single server
   - Load balancing with various distribution methods - for high-availability services
   - Bi-directional NAT - combining source and destination translation

3. **Special NAT Types**:
   - DNS64 with DNS rewrite - for IPv6 to IPv4 name resolution
   - NPTv6 for IPv6 prefix translation - enterprise IPv6 deployment scenarios
   - NAT64 for IPv6-to-IPv4 communication - mixed environment connectivity

4. **Enterprise Automation Scenarios**:
   - Multi-site branch office NAT configuration
   - Service publishing automation
   - Pre and post-rulebase positioning
   - Interface-specific routing with NAT

5. **Operational Functions**:
   - Bulk operations for mass configuration
   - Advanced filtering and search capabilities
   - Comprehensive error handling
   - Safe cleanup procedures

## Prerequisites

Before running the examples, you need:

1. A Strata Cloud Manager account with appropriate permissions
2. Your SCM API credentials (client ID, client secret, and TSG ID)
3. Python 3.10 or higher
4. The PAN-SCM-SDK package installed (`pip install pan-scm-sdk`)
5. A folder named "Texas" in your SCM environment (or modify the script)
6. Security zones ("trust", "untrust", "dmz") configured in your environment

## Script Organization

The script is organized into modular functions that each demonstrate a specific NAT configuration pattern or operational task:

### Basic Source NAT Examples
- `create_source_nat_rule()` - Dynamic IP and port (PAT) outbound NAT
- `create_source_nat_rule_with_interface()` - Interface-based outbound NAT
- `create_static_nat_rule()` - 1:1 static NAT for specific devices
- `create_dynamic_ip_with_fallback()` - High-availability NAT with fallback

### Basic Destination NAT Examples
- `create_destination_nat_rule()` - Simple port forwarding
- `create_dynamic_dest_nat_rule()` - Load-balanced destination NAT

### Special NAT Types
- `create_dns64_nat_rule()` - IPv6-to-IPv4 DNS translation
- `create_nptv6_rule()` - IPv6 prefix translation without port translation

### Advanced NAT Configurations
- `create_bidirectional_nat_rule()` - Combined source and destination NAT
- `create_multi_port_forwarding_rule()` - Publishing multiple ports to one server
- `create_outbound_nat_different_interfaces()` - Interface-specific NAT
- `create_post_nat_rule()` - Post-rulebase NAT configuration

### Enterprise Automation Examples
- `create_bulk_nat_rules()` - Creating multiple similar NAT rules programmatically
- `create_nat_rules_for_multiple_sites()` - Multi-branch NAT configuration

### Operational Functions
- `fetch_and_update_nat_rule()` - Modifying existing NAT rules
- `list_and_filter_nat_rules()` - Finding and filtering NAT rules
- `cleanup_nat_rules()` - Safely removing test objects

## Real-World NAT Scenarios

The example script demonstrates these common real-world NAT scenarios:

### 1. Basic Internet Access (Outbound NAT)
```python
source_nat_config = {
    "name": "source-nat-example",
    "description": "Example source NAT rule with dynamic IP and port",
    "folder": "Texas",
    "tag": ["API", "Example", "Python"],
    "disabled": False,
    "nat_type": "ipv4",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/24"],    # Internal network
    "destination": ["any"],       # Any internet destination
    "service": "any",
    "source_translation": {
        "dynamic_ip_and_port": {
            "type": "dynamic_ip_and_port",
            "translated_address": ["192.168.1.100", "192.168.1.101"]  # Public IPs
        }
    }
}
```

### 2. Web Server Publishing (Inbound NAT)
```python
dest_nat_config = {
    "name": "dest-nat-example",
    "description": "Example destination NAT rule",
    "folder": "Texas",
    "tag": ["API", "Example", "DestNAT"],
    "from_": ["untrust"],         # From internet
    "to_": ["dmz"],               # To DMZ zone
    "source": ["any"],            # Any source
    "destination": ["203.0.113.10/32"],  # Public IP address
    "service": "service-http",    # HTTP service
    "destination_translation": {
        "translated_address": "10.0.0.100",  # Internal web server
        "translated_port": 80
    }
}
```

### 3. Multi-Port Service Publishing
```python
multi_port_config = {
    "name": "multi-port-nat",
    "description": "Multi-port forwarding NAT rule",
    "folder": "Texas",
    "tag": ["API", "Example", "MultiPort"],
    "from_": ["untrust"],
    "to_": ["dmz"],
    "source": ["any"],
    "destination": ["203.0.113.100/32"],
    "service": "multi-port-service",  # Service object with multiple ports
    "destination_translation": {
        "translated_address": "10.10.20.150"  # Internal server
    }
}
```

### 4. Load-Balanced Services
```python
dynamic_dest_config = {
    "name": "lb-nat",
    "description": "Example load balancing NAT rule",
    "folder": "Texas",
    "tag": ["API", "Example", "LoadBalancing"],
    "from_": ["untrust"],
    "to_": ["dmz"],
    "source": ["any"],
    "destination": ["203.0.113.20/32"],  # Single public IP
    "service": "service-http",
    "destination_translation": {
        "translated_address": "10.0.0.200",  # Backend server pool
        "translated_port": 8080,
        "distribution": "round-robin"  # Load balancing method
    }
}
```

### 5. Dual ISP Configuration
```python
outbound_config = {
    "name": "outbound-primary",
    "description": "Outbound NAT using primary internet connection",
    "folder": "Texas",
    "tag": ["API", "Example", "Outbound", "Primary"],
    "from_": ["trust"],
    "to_": ["untrust"],
    "to_interface": "ethernet1/3",  # Specify egress interface
    "source": ["10.1.0.0/16"],      # Internal subnet
    "destination": ["any"],
    "service": "any",
    "source_translation": {
        "dynamic_ip_and_port": {
            "interface_address": {
                "interface": "ethernet1/3",  # Primary internet connection
                "ip": "203.0.113.50"         # Public IP on this interface
            }
        }
    }
}
```

### 6. Branch Office NAT
```python
# Create multiple similar NAT rules for different branch offices
for site in branch_sites:
    site_nat_config = {
        "name": f"outbound-{site['name'].lower().replace(' ', '-')}",
        "description": f"Outbound NAT for {site['name']} branch",
        "folder": "Texas",
        "tag": ["API", "Example", "BranchSite", site["name"]],
        "from_": ["trust"],
        "to_": ["untrust"],
        "source": [site["internal_subnet"]],  # Branch-specific subnet
        "destination": ["any"],
        "service": "any",
        "source_translation": {
            "dynamic_ip_and_port": {
                "translated_address": [site["external_ip"]]  # Branch-specific public IP
            }
        }
    }
```

## Running the Example

Follow these steps to run the example:

1. Set up authentication credentials in one of the following ways:

   **Option A: Using a .env file (recommended)**
   - Copy the provided `.env.example` file to a new file named `.env`
   - Edit the `.env` file and fill in your Strata Cloud Manager credentials:
     ```
     SCM_CLIENT_ID=your-oauth2-client-id
     SCM_CLIENT_SECRET=your-oauth2-client-secret
     SCM_TSG_ID=your-tenant-service-group-id
     ```

   **Option B: Using environment variables**
   - Set the environment variables directly in your shell:
     ```bash
     export SCM_CLIENT_ID=your-oauth2-client-id
     export SCM_CLIENT_SECRET=your-oauth2-client-secret
     export SCM_TSG_ID=your-tenant-service-group-id
     ```

   **Option C: Modify the script directly (not recommended for production)**
   - Edit the `initialize_client()` function if you prefer hardcoding credentials (not recommended)

2. Install additional dependencies:
   ```bash
   pip install python-dotenv
   ```

3. Verify or adjust environment-specific settings:
   - Folder name (default is "Texas")
   - Security zones (using "local" and "internet")
   - Network interfaces (using "$eth-local" and "$eth-internet")
   - Service object names
   - IP addresses and networks
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     SCM_SOURCE_ZONE=local
     SCM_DESTINATION_ZONE=internet
     SCM_LOCAL_INTERFACE=$eth-local
     SCM_INTERNET_INTERFACE=$eth-internet
     ```

4. Run the script:
   ```bash
   python nat_rule.py
   ```

5. Examine the console output to understand:
   - The NAT rules being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## NAT Rule Model Structure

The examples demonstrate the proper structure for the two main translation types:

### Source Translation

The `source_translation` field supports three translation types:

1. **Dynamic IP and Port** (PAT/Overloading)
   ```python
   # Option 1: Using a pool of translated addresses
   "source_translation": {
       "dynamic_ip_and_port": {
           "type": "dynamic_ip_and_port",
           "translated_address": ["192.168.1.100", "192.168.1.101"]
       }
   }

   # Option 2: Using an interface address
   "source_translation": {
       "dynamic_ip_and_port": {
           "type": "dynamic_ip_and_port",
           "interface_address": {
               "interface": "ethernet1/1",
               "ip": "192.168.1.1"
           }
       }
   }
   ```

2. **Dynamic IP** (SNAT without PAT)
   ```python
   "source_translation": {
       "dynamic_ip": {
           "translated_address": ["192.168.2.100", "192.168.2.101", "192.168.2.102"],
           "fallback": {  # Optional fallback configuration
               "interface": "ethernet1/2",
               "ip": "192.168.2.1"
           }
       }
   }
   ```

3. **Static IP** (1:1 mapping)
   ```python
   "source_translation": {
       "static_ip": {
           "translated_address": "192.168.1.5",
           "bi_directional": True  # Optional, enables traffic in both directions
       }
   }
   ```

### Destination Translation

The `destination_translation` field supports several formats:

1. **Basic Destination NAT**
   ```python
   "destination_translation": {
       "translated_address": "10.0.0.100",
       "translated_port": 80  # Optional port translation
   }
   ```

2. **Load Balancing NAT**
   ```python
   "destination_translation": {
       "translated_address": "10.0.0.200",
       "translated_port": 8080,
       "distribution": "round-robin"  # Options: "round-robin", "source-ip-hash", "ip-modulo", etc.
   }
   ```

3. **DNS64 with DNS Rewrite**
   ```python
   "destination_translation": {
       "translated_address": "2001:db8::1",
       "dns_rewrite": {
           "direction": "forward"  # Options: "forward" or "reverse"
       }
   }
   ```

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Pydantic Model Construction** - Both direct dictionary and explicit model building approaches
3. **Bulk Operations** - Creating multiple related objects programmatically
4. **Unique Naming** - Using UUID suffixes to avoid name conflicts
5. **Modular Code Organization** - Separate functions for each NAT type
6. **Proper Cleanup** - Ensuring all created objects are deleted
7. **Logging** - Consistent and informative log messages
8. **Object Model Conversion** - Converting between Pydantic models and dictionaries

## Best Practices

1. **NAT Rule Design**
   - Use clear, descriptive names with consistent naming conventions
   - Apply appropriate tags for rule categorization
   - Document the purpose in the description field
   - Minimize the scope of rules (specific sources, destinations, and services)

2. **Source Translation Selection**
   - Use Dynamic IP and Port for general outbound traffic
   - Use Dynamic IP when applications require consistent source ports
   - Use Static IP for bidirectional connections or when fixed IPs are required

3. **Destination Translation Selection**
   - Use basic port forwarding for single servers
   - Use distribution methods for load balancing
   - Consider DNS rewrite for DNS64 implementations

4. **API Usage**
   - Handle all exceptions appropriately
   - Use proper data validation before API calls
   - Implement retry logic for production code
   - Consider rate limiting for large bulk operations

5. **Security Considerations**
   - Avoid overly permissive rules (e.g., source: any, destination: any)
   - Implement the principle of least privilege
   - Consider auditing and logging requirements
   - Thoroughly test NAT configurations in non-production environments first

## Example Output

```bash

❯ poetry run python nat_rule.py --skip-cleanup
2025-02-27 20:14:55 INFO
2025-02-27 20:14:55 INFO     ================================================================================
2025-02-27 20:14:55 INFO        AUTHENTICATION & INITIALIZATION
2025-02-27 20:14:55 INFO     ================================================================================
2025-02-27 20:14:55 INFO     ▶ STARTING: Loading credentials and initializing client
2025-02-27 20:14:55 INFO     ✓ Loaded environment variables from /Users/cdot/PycharmProjects/cdot65/pan-scm-sdk/examples/scm/config/network/.env
2025-02-27 20:14:55 INFO     ✓ All required credentials found
2025-02-27 20:14:55 INFO     ▶ STARTING: Creating SCM client
2025-02-27 20:14:56 INFO     ✓ COMPLETED: SCM client initialization - TSG ID: 1540**2209
2025-02-27 20:14:56 INFO
2025-02-27 20:14:56 INFO     ================================================================================
2025-02-27 20:14:56 INFO        NAT RULE CONFIGURATION
2025-02-27 20:14:56 INFO     ================================================================================
2025-02-27 20:14:56 INFO     ▶ STARTING: Initializing NAT rule manager
2025-02-27 20:14:56 INFO     ✓ COMPLETED: NAT rule manager initialization
2025-02-27 20:14:56 INFO
2025-02-27 20:14:56 INFO     ================================================================================
2025-02-27 20:14:56 INFO        BASIC SOURCE NAT CONFIGURATIONS
2025-02-27 20:14:56 INFO     ================================================================================
2025-02-27 20:14:56 INFO     Creating common outbound NAT rule patterns used for internet access
2025-02-27 20:14:56 INFO     Using folder: Texas
2025-02-27 20:14:56 INFO     ▶ STARTING: Creating source NAT rule with dynamic IP and port (PAT)
2025-02-27 20:14:56 INFO     Rule name: source-nat-example-9db32a
2025-02-27 20:14:56 INFO     Configuration details:
2025-02-27 20:14:56 INFO       - Type: Source NAT with dynamic IP and port
2025-02-27 20:14:56 INFO       - Source: 10.0.0.0/24 (internal network)
2025-02-27 20:14:56 INFO       - Translated addresses: 192.168.1.100, 192.168.1.101 (public IPs)
2025-02-27 20:14:56 INFO     Sending request to Strata Cloud Manager API...
2025-02-27 20:14:56 INFO     ✓ Created source NAT rule: source-nat-example-9db32a
2025-02-27 20:14:56 INFO       - Rule ID: f8bba462-266e-40f2-8a57-942aa7f7fb93
2025-02-27 20:14:56 INFO       - Translation: Internal → Public with PAT
2025-02-27 20:14:56 INFO     ✓ COMPLETED: Source NAT rule creation - Rule: source-nat-example-9db32a
2025-02-27 20:14:56 INFO     Creating a source NAT rule with interface address
2025-02-27 20:14:57 INFO     Created source NAT with interface: source-nat-interface-025b0e with ID: f89f70f7-ca27-4e82-824a-cb8b50d4d6d4
2025-02-27 20:14:57 INFO     Creating a static NAT rule
2025-02-27 20:14:57 INFO     Created static NAT rule: static-nat-041448 with ID: bc4c13f3-8c6c-4b7c-a43b-f4d71da84662
2025-02-27 20:14:57 INFO     Creating a dynamic IP NAT rule with fallback
2025-02-27 20:14:57 INFO     Created dynamic IP NAT rule: dynamic-ip-fallback-3da071 with ID: 58ab4494-1cea-4ac2-8cd5-3a402fe4d6c3
2025-02-27 20:14:57 INFO     ✓ Created 4 source NAT rules so far
2025-02-27 20:14:57 INFO
2025-02-27 20:14:57 INFO     ================================================================================
2025-02-27 20:14:57 INFO        BASIC DESTINATION NAT CONFIGURATIONS
2025-02-27 20:14:57 INFO     ================================================================================
2025-02-27 20:14:57 INFO     Creating common inbound NAT rule patterns used for service publishing
2025-02-27 20:14:57 INFO     Using folder: Texas
2025-02-27 20:14:57 INFO     Creating a destination NAT rule
2025-02-27 20:14:58 INFO     Created destination NAT rule: dest-nat-cd4a5f with ID: e37aed86-ed64-480f-bc7a-87392f2b8eed
2025-02-27 20:14:58 INFO     Creating a dynamic destination NAT rule for load balancing
2025-02-27 20:14:58 INFO     Created dynamic destination NAT rule: lb-nat-9bf5b0 with ID: 98d21247-c296-418b-af99-bda5e2f6fe10
2025-02-27 20:14:58 INFO
2025-02-27 20:14:58 INFO     ================================================================================
2025-02-27 20:14:58 INFO        SPECIAL NAT RULE TYPES
2025-02-27 20:14:58 INFO     ================================================================================
2025-02-27 20:14:58 INFO     Creating specialized NAT rules for IPv6 transition
2025-02-27 20:14:58 INFO     Using folder: Texas
2025-02-27 20:14:58 INFO     Creating a DNS64 NAT rule
2025-02-27 20:14:58 INFO     Created DNS64 NAT rule: dns64-nat-b4e4e8 with ID: 4b3309e8-053d-4212-9bc4-9450ca4ae393
2025-02-27 20:14:58 INFO     Creating an NPTv6 NAT rule
2025-02-27 20:14:58 INFO     Created NPTv6 NAT rule: nptv6-d75718 with ID: f564a6e3-7784-482d-89a0-3254bc39ec20
2025-02-27 20:14:58 INFO
2025-02-27 20:14:58 INFO     ================================================================================
2025-02-27 20:14:58 INFO        ADVANCED NAT CONFIGURATIONS
2025-02-27 20:14:58 INFO     ================================================================================
2025-02-27 20:14:58 INFO     Creating complex NAT scenarios for enterprise networks
2025-02-27 20:14:58 INFO     Using folder: Texas
2025-02-27 20:14:58 INFO     Creating a bi-directional NAT rule
2025-02-27 20:14:59 INFO     Created bi-directional NAT rule: bidir-nat-2c2f68 with ID: d4df5267-bb98-4c59-8dbd-21cca7391523
2025-02-27 20:14:59 INFO     Creating a multi-port forwarding NAT rule
2025-02-27 20:14:59 INFO     Created multi-port forwarding NAT rule: multi-port-nat-5aee1b with ID: 77a32594-1279-4804-aab7-c6524a1be5bf
2025-02-27 20:14:59 INFO     Creating a port forwarding NAT rule
2025-02-27 20:14:59 INFO     Created port forwarding NAT rule: port-forward-239c13 with ID: 9946a772-8f5e-4112-91f7-f0296da35714
2025-02-27 20:14:59 INFO     Creating an outbound NAT rule with interface selection
2025-02-27 20:15:00 INFO     Created outbound NAT rule with interface selection: outbound-primary-22940f with ID: 5b7cb1f3-9dba-40ea-97c4-a1dfbc784672
2025-02-27 20:15:00 INFO
2025-02-27 20:15:00 INFO     ================================================================================
2025-02-27 20:15:00 INFO        POSITION-SPECIFIC NAT RULES
2025-02-27 20:15:00 INFO     ================================================================================
2025-02-27 20:15:00 INFO     Creating NAT rules in specific rulebase positions
2025-02-27 20:15:00 INFO     Using folder: Texas
2025-02-27 20:15:00 INFO     Creating a post-rulebase NAT rule
2025-02-27 20:15:00 INFO     Created post-rulebase NAT rule: post-nat-8a2264 with ID: 32dbb51b-d2b7-4a3c-9a4f-4766d9c8d277
2025-02-27 20:15:00 INFO
2025-02-27 20:15:00 INFO     ================================================================================
2025-02-27 20:15:00 INFO        BULK NAT RULE CREATION
2025-02-27 20:15:00 INFO     ================================================================================
2025-02-27 20:15:00 INFO     Demonstrating programmatic creation of multiple NAT rules
2025-02-27 20:15:00 INFO     Using folder: Texas
2025-02-27 20:15:00 INFO     Creating a batch of NAT rules for different services
2025-02-27 20:15:00 INFO     Created HTTP forwarding NAT rule: dnat-http-da7b1f with ID: 2300af38-9081-42e2-a0f0-d50a8e8a184e
2025-02-27 20:15:01 INFO     Created HTTPS forwarding NAT rule: dnat-https-a2e6f6 with ID: eb8cd948-a940-464b-b5de-183140660b25
2025-02-27 20:15:01 INFO     Created SSH forwarding NAT rule: dnat-ssh-8b70ee with ID: a5304724-8ad7-4d30-81a4-38e51e3bdb7f
2025-02-27 20:15:01 INFO     Created FTP forwarding NAT rule: dnat-ftp-d9d55a with ID: 93c68d53-85bb-47e9-afbc-2a78faf2e19b
2025-02-27 20:15:01 INFO     ✓ Created 4 bulk NAT rules
2025-02-27 20:15:01 INFO     Creating NAT rules for multiple branch sites
2025-02-27 20:15:02 INFO     Created outbound NAT for New York: outbound-new-york-2f7064 with ID: 15e58a92-3471-4d0f-b34b-a9ef1da453be
2025-02-27 20:15:02 INFO     Created outbound NAT for Chicago: outbound-chicago-776033 with ID: b13f2f7f-472a-4e61-bcfc-b2cb3d8173ef
2025-02-27 20:15:02 INFO     Created outbound NAT for Los Angeles: outbound-los-angeles-648c49 with ID: 840d9b48-f835-4eb7-a5d7-fa00f183926a
2025-02-27 20:15:02 INFO     ✓ Created 3 branch site NAT rules
2025-02-27 20:15:02 INFO
2025-02-27 20:15:02 INFO     ================================================================================
2025-02-27 20:15:02 INFO        UPDATING NAT RULES
2025-02-27 20:15:02 INFO     ================================================================================
2025-02-27 20:15:02 INFO     Demonstrating how to update existing NAT rules
2025-02-27 20:15:02 INFO     Fetching and updating NAT rule with ID: f8bba462-266e-40f2-8a57-942aa7f7fb93
2025-02-27 20:15:02 INFO     Found NAT rule: source-nat-example-9db32a
2025-02-27 20:15:02 INFO     Updating translated addresses to: ['192.168.1.100', '192.168.1.101', '192.168.1.200']
2025-02-27 20:15:03 INFO     Updated NAT rule: source-nat-example-9db32a with description: Updated description for source-nat-example-9db32a
2025-02-27 20:15:03 INFO
2025-02-27 20:15:03 INFO     ================================================================================
2025-02-27 20:15:03 INFO        LISTING AND FILTERING NAT RULES
2025-02-27 20:15:03 INFO     ================================================================================
2025-02-27 20:15:03 INFO     Demonstrating how to search and filter NAT rules
2025-02-27 20:15:03 INFO     Listing and filtering NAT rules
2025-02-27 20:15:03 INFO     Found 93 NAT rules in the Texas folder
2025-02-27 20:15:03 INFO     Found 0 NAT rules with 'API' tag
2025-02-27 20:15:03 INFO     Found 85 IPv4 NAT rules
2025-02-27 20:15:04 INFO     Found 0 NAT rules with 'trust' source zone
2025-02-27 20:15:04 INFO     Found 0 NAT rules with 'untrust' destination zone
2025-02-27 20:15:04 INFO
Details of NAT rules:
2025-02-27 20:15:04 INFO       - Rule: default
2025-02-27 20:15:04 INFO         ID: 9cbc9ec8-abb9-46b7-89c3-5ffe0a1f25eb
2025-02-27 20:15:04 INFO         Description: None
2025-02-27 20:15:04 INFO         Tags: []
2025-02-27 20:15:04 INFO         From: ['any'], To: ['any']
2025-02-27 20:15:04 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:15:04 INFO
2025-02-27 20:15:04 INFO       - Rule: Web-Security-Default
2025-02-27 20:15:04 INFO         ID: a6ca47b5-0575-49d9-954b-c2895e21ff39
2025-02-27 20:15:04 INFO         Description: None
2025-02-27 20:15:04 INFO         Tags: []
2025-02-27 20:15:04 INFO         From: ['any'], To: ['any']
2025-02-27 20:15:04 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:15:04 INFO
2025-02-27 20:15:04 INFO       - Rule: hip-default
2025-02-27 20:15:04 INFO         ID: 29472dcf-4d9a-4b2a-836a-b65b04ae5010
2025-02-27 20:15:04 INFO         Description: None
2025-02-27 20:15:04 INFO         Tags: []
2025-02-27 20:15:04 INFO         From: ['any'], To: ['any']
2025-02-27 20:15:04 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:15:04 INFO
2025-02-27 20:15:04 INFO       - Rule: Auto-VPN-Default-Snippet
2025-02-27 20:15:04 INFO         ID: f15871d5-e7b8-4558-bb0b-4ff3d48b5c51
2025-02-27 20:15:04 INFO         Description: None
2025-02-27 20:15:04 INFO         Tags: []
2025-02-27 20:15:04 INFO         From: ['any'], To: ['any']
2025-02-27 20:15:04 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:15:04 INFO
2025-02-27 20:15:04 INFO       - Rule: app-tagging
2025-02-27 20:15:04 INFO         ID: b15925f5-e572-4dae-8d4f-fb0b7e2448cc
2025-02-27 20:15:04 INFO         Description: None
2025-02-27 20:15:04 INFO         Tags: []
2025-02-27 20:15:04 INFO         From: ['any'], To: ['any']
2025-02-27 20:15:04 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:15:04 INFO
2025-02-27 20:15:04 INFO
2025-02-27 20:15:04 INFO     ================================================================================
2025-02-27 20:15:04 INFO        REPORT GENERATION
2025-02-27 20:15:04 INFO     ================================================================================
2025-02-27 20:15:04 INFO     ▶ STARTING: Generating NAT rules CSV report
2025-02-27 20:15:04 INFO     Processing rule 1 of 20
2025-02-27 20:15:04 INFO     Processing rule 5 of 20
2025-02-27 20:15:05 INFO     Processing rule 10 of 20
2025-02-27 20:15:06 INFO     Processing rule 15 of 20
2025-02-27 20:15:07 INFO     Processing rule 20 of 20
2025-02-27 20:15:07 INFO     ✓ Generated NAT rules report: nat_rules_report_20250227_201504.csv
2025-02-27 20:15:07 INFO     The report contains details of all 20 NAT rules created
2025-02-27 20:15:07 INFO
2025-02-27 20:15:07 INFO     ================================================================================
2025-02-27 20:15:07 INFO        CLEANUP
2025-02-27 20:15:07 INFO     ================================================================================
2025-02-27 20:15:07 INFO     SKIP_CLEANUP is set to true - preserving 20 NAT rules
2025-02-27 20:15:07 INFO     To clean up these rules, run the script again with SKIP_CLEANUP unset or set to false
2025-02-27 20:15:07 INFO
2025-02-27 20:15:07 INFO     ================================================================================
2025-02-27 20:15:07 INFO        EXECUTION SUMMARY
2025-02-27 20:15:07 INFO     ================================================================================
2025-02-27 20:15:07 INFO     ✓ Example script completed successfully
2025-02-27 20:15:07 INFO     Total NAT rules created: 20
2025-02-27 20:15:07 INFO     Total execution time: 0 minutes 11 seconds
2025-02-27 20:15:07 INFO     Average time per rule: 0.58 seconds

```

and if you want the rules cleaned up

```bash

❯ poetry run python nat_rule.py
2025-02-27 20:16:58 INFO
2025-02-27 20:16:58 INFO     ================================================================================
2025-02-27 20:16:58 INFO        AUTHENTICATION & INITIALIZATION
2025-02-27 20:16:58 INFO     ================================================================================
2025-02-27 20:16:58 INFO     ▶ STARTING: Loading credentials and initializing client
2025-02-27 20:16:58 INFO     ✓ Loaded environment variables from /Users/cdot/PycharmProjects/cdot65/pan-scm-sdk/examples/scm/config/network/.env
2025-02-27 20:16:58 INFO     ✓ All required credentials found
2025-02-27 20:16:58 INFO     ▶ STARTING: Creating SCM client
2025-02-27 20:16:59 INFO     ✓ COMPLETED: SCM client initialization - TSG ID: 1540**2209
2025-02-27 20:16:59 INFO
2025-02-27 20:16:59 INFO     ================================================================================
2025-02-27 20:16:59 INFO        NAT RULE CONFIGURATION
2025-02-27 20:16:59 INFO     ================================================================================
2025-02-27 20:16:59 INFO     ▶ STARTING: Initializing NAT rule manager
2025-02-27 20:16:59 INFO     ✓ COMPLETED: NAT rule manager initialization
2025-02-27 20:16:59 INFO
2025-02-27 20:16:59 INFO     ================================================================================
2025-02-27 20:16:59 INFO        BASIC SOURCE NAT CONFIGURATIONS
2025-02-27 20:16:59 INFO     ================================================================================
2025-02-27 20:16:59 INFO     Creating common outbound NAT rule patterns used for internet access
2025-02-27 20:16:59 INFO     Using folder: Texas
2025-02-27 20:16:59 INFO     ▶ STARTING: Creating source NAT rule with dynamic IP and port (PAT)
2025-02-27 20:16:59 INFO     Rule name: source-nat-example-64971f
2025-02-27 20:16:59 INFO     Configuration details:
2025-02-27 20:16:59 INFO       - Type: Source NAT with dynamic IP and port
2025-02-27 20:16:59 INFO       - Source: 10.0.0.0/24 (internal network)
2025-02-27 20:16:59 INFO       - Translated addresses: 192.168.1.100, 192.168.1.101 (public IPs)
2025-02-27 20:16:59 INFO     Sending request to Strata Cloud Manager API...
2025-02-27 20:16:59 INFO     ✓ Created source NAT rule: source-nat-example-64971f
2025-02-27 20:16:59 INFO       - Rule ID: e8562d20-68d1-420d-8c90-38d3c7e49573
2025-02-27 20:16:59 INFO       - Translation: Internal → Public with PAT
2025-02-27 20:16:59 INFO     ✓ COMPLETED: Source NAT rule creation - Rule: source-nat-example-64971f
2025-02-27 20:16:59 INFO     Creating a source NAT rule with interface address
2025-02-27 20:17:00 INFO     Created source NAT with interface: source-nat-interface-496ef8 with ID: 13078c9a-afe2-492d-8a37-4434e0411d51
2025-02-27 20:17:00 INFO     Creating a static NAT rule
2025-02-27 20:17:00 INFO     Created static NAT rule: static-nat-1e103c with ID: 240463dc-5e0a-46ae-b031-7a5a3f871ca9
2025-02-27 20:17:00 INFO     Creating a dynamic IP NAT rule with fallback
2025-02-27 20:17:00 INFO     Created dynamic IP NAT rule: dynamic-ip-fallback-c0ef9c with ID: 3909e45b-7cc9-437f-a523-25da41213563
2025-02-27 20:17:00 INFO     ✓ Created 4 source NAT rules so far
2025-02-27 20:17:00 INFO
2025-02-27 20:17:00 INFO     ================================================================================
2025-02-27 20:17:00 INFO        BASIC DESTINATION NAT CONFIGURATIONS
2025-02-27 20:17:00 INFO     ================================================================================
2025-02-27 20:17:00 INFO     Creating common inbound NAT rule patterns used for service publishing
2025-02-27 20:17:00 INFO     Using folder: Texas
2025-02-27 20:17:00 INFO     Creating a destination NAT rule
2025-02-27 20:17:01 INFO     Created destination NAT rule: dest-nat-6e17e1 with ID: f64e5aee-f122-4b11-a475-a7a9526ba2cd
2025-02-27 20:17:01 INFO     Creating a dynamic destination NAT rule for load balancing
2025-02-27 20:17:01 INFO     Created dynamic destination NAT rule: lb-nat-fe5465 with ID: 39f47f59-4fd2-4d51-9679-269309f02188
2025-02-27 20:17:01 INFO
2025-02-27 20:17:01 INFO     ================================================================================
2025-02-27 20:17:01 INFO        SPECIAL NAT RULE TYPES
2025-02-27 20:17:01 INFO     ================================================================================
2025-02-27 20:17:01 INFO     Creating specialized NAT rules for IPv6 transition
2025-02-27 20:17:01 INFO     Using folder: Texas
2025-02-27 20:17:01 INFO     Creating a DNS64 NAT rule
2025-02-27 20:17:01 INFO     Created DNS64 NAT rule: dns64-nat-e797e5 with ID: a10aa020-af90-4478-8bb8-0acf4ac3c0f8
2025-02-27 20:17:01 INFO     Creating an NPTv6 NAT rule
2025-02-27 20:17:02 INFO     Created NPTv6 NAT rule: nptv6-4b04dc with ID: 6b38e9fd-32f6-487d-96fe-8ddde513200f
2025-02-27 20:17:02 INFO
2025-02-27 20:17:02 INFO     ================================================================================
2025-02-27 20:17:02 INFO        ADVANCED NAT CONFIGURATIONS
2025-02-27 20:17:02 INFO     ================================================================================
2025-02-27 20:17:02 INFO     Creating complex NAT scenarios for enterprise networks
2025-02-27 20:17:02 INFO     Using folder: Texas
2025-02-27 20:17:02 INFO     Creating a bi-directional NAT rule
2025-02-27 20:17:02 INFO     Created bi-directional NAT rule: bidir-nat-61107a with ID: e1cdca48-dcfd-434c-96f6-9e7415ec5347
2025-02-27 20:17:02 INFO     Creating a multi-port forwarding NAT rule
2025-02-27 20:17:02 INFO     Created multi-port forwarding NAT rule: multi-port-nat-792326 with ID: 52893814-22a6-487d-9639-6e0e4875d57a
2025-02-27 20:17:02 INFO     Creating a port forwarding NAT rule
2025-02-27 20:17:03 INFO     Created port forwarding NAT rule: port-forward-59b797 with ID: 21cc0af4-7b0b-45c3-a91f-d657b23e6b42
2025-02-27 20:17:03 INFO     Creating an outbound NAT rule with interface selection
2025-02-27 20:17:03 INFO     Created outbound NAT rule with interface selection: outbound-primary-c99ca3 with ID: 444852cb-0450-4726-a61b-c931af9063ec
2025-02-27 20:17:03 INFO
2025-02-27 20:17:03 INFO     ================================================================================
2025-02-27 20:17:03 INFO        POSITION-SPECIFIC NAT RULES
2025-02-27 20:17:03 INFO     ================================================================================
2025-02-27 20:17:03 INFO     Creating NAT rules in specific rulebase positions
2025-02-27 20:17:03 INFO     Using folder: Texas
2025-02-27 20:17:03 INFO     Creating a post-rulebase NAT rule
2025-02-27 20:17:03 INFO     Created post-rulebase NAT rule: post-nat-4876f9 with ID: 53931f49-d559-4eea-80c3-5cd3ba3742e1
2025-02-27 20:17:03 INFO
2025-02-27 20:17:03 INFO     ================================================================================
2025-02-27 20:17:03 INFO        BULK NAT RULE CREATION
2025-02-27 20:17:03 INFO     ================================================================================
2025-02-27 20:17:03 INFO     Demonstrating programmatic creation of multiple NAT rules
2025-02-27 20:17:03 INFO     Using folder: Texas
2025-02-27 20:17:03 INFO     Creating a batch of NAT rules for different services
2025-02-27 20:17:03 INFO     Created HTTP forwarding NAT rule: dnat-http-a65a86 with ID: 173e1a12-6534-4c83-8da1-0c8449f2aef2
2025-02-27 20:17:04 INFO     Created HTTPS forwarding NAT rule: dnat-https-e4a525 with ID: a9abc87d-0ec0-4222-8c61-9c492f0fb0af
2025-02-27 20:17:04 INFO     Created SSH forwarding NAT rule: dnat-ssh-8f2ff2 with ID: 299a0cbe-acfa-4663-8da4-8ac7588d0bf9
2025-02-27 20:17:04 INFO     Created FTP forwarding NAT rule: dnat-ftp-1ecf72 with ID: e9bc6e35-1017-47b8-b2e6-5c87d99d1920
2025-02-27 20:17:04 INFO     ✓ Created 4 bulk NAT rules
2025-02-27 20:17:04 INFO     Creating NAT rules for multiple branch sites
2025-02-27 20:17:05 INFO     Created outbound NAT for New York: outbound-new-york-00b0b8 with ID: 676ff6bf-dfb2-46ba-82f4-b9f0c20fbfb2
2025-02-27 20:17:05 INFO     Created outbound NAT for Chicago: outbound-chicago-17ff64 with ID: 3a800e91-c156-4bcc-8af2-20ed73c83cc0
2025-02-27 20:17:05 INFO     Created outbound NAT for Los Angeles: outbound-los-angeles-626aa6 with ID: 2dd50db0-f338-4553-92b5-92475088a5e5
2025-02-27 20:17:05 INFO     ✓ Created 3 branch site NAT rules
2025-02-27 20:17:05 INFO
2025-02-27 20:17:05 INFO     ================================================================================
2025-02-27 20:17:05 INFO        UPDATING NAT RULES
2025-02-27 20:17:05 INFO     ================================================================================
2025-02-27 20:17:05 INFO     Demonstrating how to update existing NAT rules
2025-02-27 20:17:05 INFO     Fetching and updating NAT rule with ID: e8562d20-68d1-420d-8c90-38d3c7e49573
2025-02-27 20:17:05 INFO     Found NAT rule: source-nat-example-64971f
2025-02-27 20:17:05 INFO     Updating translated addresses to: ['192.168.1.100', '192.168.1.101', '192.168.1.200']
2025-02-27 20:17:06 INFO     Updated NAT rule: source-nat-example-64971f with description: Updated description for source-nat-example-64971f
2025-02-27 20:17:06 INFO
2025-02-27 20:17:06 INFO     ================================================================================
2025-02-27 20:17:06 INFO        LISTING AND FILTERING NAT RULES
2025-02-27 20:17:06 INFO     ================================================================================
2025-02-27 20:17:06 INFO     Demonstrating how to search and filter NAT rules
2025-02-27 20:17:06 INFO     Listing and filtering NAT rules
2025-02-27 20:17:06 INFO     Found 112 NAT rules in the Texas folder
2025-02-27 20:17:06 INFO     Found 0 NAT rules with 'API' tag
2025-02-27 20:17:06 INFO     Found 102 IPv4 NAT rules
2025-02-27 20:17:07 INFO     Found 0 NAT rules with 'trust' source zone
2025-02-27 20:17:07 INFO     Found 0 NAT rules with 'untrust' destination zone
2025-02-27 20:17:07 INFO
Details of NAT rules:
2025-02-27 20:17:07 INFO       - Rule: default
2025-02-27 20:17:07 INFO         ID: 9cbc9ec8-abb9-46b7-89c3-5ffe0a1f25eb
2025-02-27 20:17:07 INFO         Description: None
2025-02-27 20:17:07 INFO         Tags: []
2025-02-27 20:17:07 INFO         From: ['any'], To: ['any']
2025-02-27 20:17:07 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:17:07 INFO
2025-02-27 20:17:07 INFO       - Rule: Web-Security-Default
2025-02-27 20:17:07 INFO         ID: a6ca47b5-0575-49d9-954b-c2895e21ff39
2025-02-27 20:17:07 INFO         Description: None
2025-02-27 20:17:07 INFO         Tags: []
2025-02-27 20:17:07 INFO         From: ['any'], To: ['any']
2025-02-27 20:17:07 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:17:07 INFO
2025-02-27 20:17:07 INFO       - Rule: hip-default
2025-02-27 20:17:07 INFO         ID: 29472dcf-4d9a-4b2a-836a-b65b04ae5010
2025-02-27 20:17:07 INFO         Description: None
2025-02-27 20:17:07 INFO         Tags: []
2025-02-27 20:17:07 INFO         From: ['any'], To: ['any']
2025-02-27 20:17:07 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:17:07 INFO
2025-02-27 20:17:07 INFO       - Rule: Auto-VPN-Default-Snippet
2025-02-27 20:17:07 INFO         ID: f15871d5-e7b8-4558-bb0b-4ff3d48b5c51
2025-02-27 20:17:07 INFO         Description: None
2025-02-27 20:17:07 INFO         Tags: []
2025-02-27 20:17:07 INFO         From: ['any'], To: ['any']
2025-02-27 20:17:07 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:17:07 INFO
2025-02-27 20:17:07 INFO       - Rule: app-tagging
2025-02-27 20:17:07 INFO         ID: b15925f5-e572-4dae-8d4f-fb0b7e2448cc
2025-02-27 20:17:07 INFO         Description: None
2025-02-27 20:17:07 INFO         Tags: []
2025-02-27 20:17:07 INFO         From: ['any'], To: ['any']
2025-02-27 20:17:07 INFO         Source: ['any'], Destination: ['any']
2025-02-27 20:17:07 INFO
2025-02-27 20:17:07 INFO
2025-02-27 20:17:07 INFO     ================================================================================
2025-02-27 20:17:07 INFO        REPORT GENERATION
2025-02-27 20:17:07 INFO     ================================================================================
2025-02-27 20:17:07 INFO     ▶ STARTING: Generating NAT rules CSV report
2025-02-27 20:17:07 INFO     Processing rule 1 of 20
2025-02-27 20:17:07 INFO     Processing rule 5 of 20
2025-02-27 20:17:08 INFO     Processing rule 10 of 20
2025-02-27 20:17:09 INFO     Processing rule 15 of 20
2025-02-27 20:17:10 INFO     Processing rule 20 of 20
2025-02-27 20:17:10 INFO     ✓ Generated NAT rules report: nat_rules_report_20250227_201707.csv
2025-02-27 20:17:10 INFO     The report contains details of all 20 NAT rules created
2025-02-27 20:17:10 INFO
2025-02-27 20:17:10 INFO     ================================================================================
2025-02-27 20:17:10 INFO        CLEANUP
2025-02-27 20:17:10 INFO     ================================================================================
2025-02-27 20:17:10 INFO     ▶ STARTING: Cleaning up 20 created NAT rules
2025-02-27 20:17:10 INFO     Cleaning up NAT rules
2025-02-27 20:17:10 INFO     Deleted NAT rule with ID: e8562d20-68d1-420d-8c90-38d3c7e49573
2025-02-27 20:17:11 INFO     Deleted NAT rule with ID: 13078c9a-afe2-492d-8a37-4434e0411d51
2025-02-27 20:17:11 INFO     Deleted NAT rule with ID: 240463dc-5e0a-46ae-b031-7a5a3f871ca9
2025-02-27 20:17:11 INFO     Deleted NAT rule with ID: 3909e45b-7cc9-437f-a523-25da41213563
2025-02-27 20:17:11 INFO     Deleted NAT rule with ID: f64e5aee-f122-4b11-a475-a7a9526ba2cd
2025-02-27 20:17:12 INFO     Deleted NAT rule with ID: 39f47f59-4fd2-4d51-9679-269309f02188
2025-02-27 20:17:12 INFO     Deleted NAT rule with ID: a10aa020-af90-4478-8bb8-0acf4ac3c0f8
2025-02-27 20:17:12 INFO     Deleted NAT rule with ID: 6b38e9fd-32f6-487d-96fe-8ddde513200f
2025-02-27 20:17:12 INFO     Deleted NAT rule with ID: e1cdca48-dcfd-434c-96f6-9e7415ec5347
2025-02-27 20:17:13 INFO     Deleted NAT rule with ID: 52893814-22a6-487d-9639-6e0e4875d57a
2025-02-27 20:17:13 INFO     Deleted NAT rule with ID: 21cc0af4-7b0b-45c3-a91f-d657b23e6b42
2025-02-27 20:17:13 INFO     Deleted NAT rule with ID: 444852cb-0450-4726-a61b-c931af9063ec
2025-02-27 20:17:14 INFO     Deleted NAT rule with ID: 53931f49-d559-4eea-80c3-5cd3ba3742e1
2025-02-27 20:17:14 INFO     Deleted NAT rule with ID: 173e1a12-6534-4c83-8da1-0c8449f2aef2
2025-02-27 20:17:14 INFO     Deleted NAT rule with ID: a9abc87d-0ec0-4222-8c61-9c492f0fb0af
2025-02-27 20:17:14 INFO     Deleted NAT rule with ID: 299a0cbe-acfa-4663-8da4-8ac7588d0bf9
2025-02-27 20:17:15 INFO     Deleted NAT rule with ID: e9bc6e35-1017-47b8-b2e6-5c87d99d1920
2025-02-27 20:17:15 INFO     Deleted NAT rule with ID: 676ff6bf-dfb2-46ba-82f4-b9f0c20fbfb2
2025-02-27 20:17:15 INFO     Deleted NAT rule with ID: 3a800e91-c156-4bcc-8af2-20ed73c83cc0
2025-02-27 20:17:15 INFO     Deleted NAT rule with ID: 2dd50db0-f338-4553-92b5-92475088a5e5
2025-02-27 20:17:15 INFO
2025-02-27 20:17:15 INFO     ================================================================================
2025-02-27 20:17:15 INFO        EXECUTION SUMMARY
2025-02-27 20:17:15 INFO     ================================================================================
2025-02-27 20:17:15 INFO     ✓ Example script completed successfully
2025-02-27 20:17:15 INFO     Total NAT rules created: 20
2025-02-27 20:17:15 INFO     Total execution time: 0 minutes 17 seconds
2025-02-27 20:17:15 INFO     Average time per rule: 0.85 seconds

```
