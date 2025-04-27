# Comprehensive Address Objects SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage address objects across a wide range of real-world enterprise scenarios.

## Overview {#Overview}

The `address.py` script showcases enterprise-ready address object configurations addressing common network addressing needs, including:

1. **IPv4 Address Object Types**:
   - Network addresses (CIDR notation) - for defining network segments and subnets
   - Host addresses (/32 notation) - for individual endpoints and servers
   - Address ranges - for defining ranges like DHCP pools or IP blocks

2. **IPv6 Address Object Types**:
   - Network addresses (CIDR notation) - for IPv6 network segments
   - Host addresses (/128 notation) - for individual IPv6 endpoints

3. **FQDN Address Objects**:
   - Domain-based addresses - for cloud services, websites, and dynamic hosts

4. **Operational Functions**:
   - Bulk creation capabilities - for mass configuration
   - Advanced filtering and search capabilities
   - Comprehensive error handling
   - Safe cleanup procedures

5. **Reporting and Documentation**:
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

The script is organized into modular functions that each demonstrate a specific address object type or operational task:

### IPv4 Address Object Examples
- `create_ipv4_network_address()` - Network segment with CIDR notation
- `create_ipv4_host_address()` - Single host with /32 notation
- `create_ipv4_range_address()` - Range of addresses with start-end notation

### IPv6 Address Object Examples
- `create_ipv6_address()` - IPv6 network or host

### FQDN Address Object Examples
- `create_fqdn_address()` - Domain-based object

### Bulk Operations
- `create_bulk_address_objects()` - Creating multiple address objects programmatically

### Operational Functions
- `fetch_and_update_address()` - Modifying existing address objects
- `list_and_filter_addresses()` - Finding and filtering address objects
- `cleanup_address_objects()` - Safely removing test objects
- `generate_address_report()` - Creating comprehensive CSV reports

## Real-World Address Object Scenarios

The example script demonstrates these common real-world address object patterns:

### 1. IPv4 Network Segment
```python
ipv4_network_config = {
    "name": "network-segment-example",
    "description": "Example IPv4 network segment for corporate LAN",
    "folder": "Texas",
    "tag": ["Automation", "Corporate"],
    "ip_netmask": "10.10.10.0/24",
}
```

### 2. IPv4 Host Address
```python
ipv4_host_config = {
    "name": "server-host-example",
    "description": "Example server host address",
    "folder": "Texas",
    "tag": ["Automation", "Servers"],
    "ip_netmask": "192.168.1.100/32",  # /32 for a single host
}
```

### 3. IPv4 Address Range
```python
ipv4_range_config = {
    "name": "dhcp-range-example",
    "description": "Example DHCP address range",
    "folder": "Texas",
    "tag": ["Automation", "DHCP"],
    "ip_range": "10.20.30.100-10.20.30.200",
}
```

### 4. IPv6 Network Address
```python
ipv6_network_config = {
    "name": "ipv6-segment-example",
    "description": "Example IPv6 network segment",
    "folder": "Texas",
    "tag": ["Automation", "IPv6"],
    "ip_netmask": "2001:db8:1234::/64",  # IPv6 uses the same field as IPv4
}
```

### 5. FQDN Address Object
```python
fqdn_config = {
    "name": "website-fqdn-example",
    "description": "Example website FQDN address",
    "folder": "Texas",
    "tag": ["Automation", "Web"],
    "fqdn": "www.example.com",
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
   - Tag values (using "Automation", "Corporate", "Servers", etc.)
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     SKIP_CLEANUP=true  # To preserve created objects
     ```

4. Run the script with various options:
   ```bash
   # Run all examples
   python address.py

   # Create only IPv4 address objects
   python address.py --ipv4

   # Create only IPv6 address objects
   python address.py --ipv6

   # Create only FQDN address objects
   python address.py --fqdn

   # Create only bulk address objects
   python address.py --bulk

   # Skip cleaning up created objects
   python address.py --skip-cleanup

   # Skip CSV report generation
   python address.py --no-report

   # Specify a different folder
   python address.py --folder=Production
   ```

5. Examine the console output to understand:
   - The address objects being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## Address Object Model Structure

The examples demonstrate the proper structure for each address object type:

### IPv4 Network or Host

```python
# Network segment (using CIDR notation)
{
    "name": "corporate-lan",
    "description": "Corporate LAN segment",
    "folder": "Texas",
    "tag": ["Network", "Corporate"],
    "ip_netmask": "10.1.0.0/16"
}

# Host (using /32 notation)
{
    "name": "web-server-1",
    "description": "Primary web server",
    "folder": "Texas",
    "tag": ["Server", "Web"],
    "ip_netmask": "10.1.1.100/32"
}
```

### IPv4 Address Range

```python
{
    "name": "guest-dhcp-pool",
    "description": "Guest network DHCP address pool",
    "folder": "Texas",
    "tag": ["DHCP", "Guest"],
    "ip_range": "192.168.100.50-192.168.100.150"
}
```

### IPv6 Network or Host

```python
# IPv6 network
{
    "name": "ipv6-corporate",
    "description": "Corporate IPv6 network",
    "folder": "Texas",
    "tag": ["Network", "IPv6"],
    "ip_netmask": "2001:db8:1::/48"
}

# IPv6 host
{
    "name": "ipv6-server",
    "description": "IPv6 server address",
    "folder": "Texas",
    "tag": ["Server", "IPv6"],
    "ip_netmask": "2001:db8:1::1/128"
}
```

### FQDN Address

```python
{
    "name": "google-dns",
    "description": "Google DNS servers",
    "folder": "Texas",
    "tag": ["DNS", "External"],
    "fqdn": "dns.google.com"
}
```

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Unique Naming** - Using UUID suffixes to avoid name conflicts
3. **Modular Code Organization** - Separate functions for each address type
4. **Proper Cleanup** - Ensuring all created objects are deleted
5. **Logging** - Consistent and informative log messages with color coding
6. **Command-line Arguments** - Flexible script execution with various options
7. **Environment Variable Support** - Using .env files for credentials
8. **Progress Tracking** - Showing progress during lengthy operations
9. **Performance Metrics** - Tracking and reporting execution statistics

## Best Practices

1. **Address Object Design**
   - Use clear, descriptive names with consistent naming conventions
   - Apply appropriate tags for object categorization
   - Document the purpose in the description field
   - Use the most specific address type for your needs (host vs. network)

2. **Address Type Selection**
   - Use network objects for subnets and network segments
   - Use host objects for individual endpoints
   - Use range objects for dynamic pools like DHCP
   - Use FQDN objects for domains and dynamic cloud resources

3. **Naming Conventions**
   - Include the address type in the name (e.g., "net-corporate", "host-webserver")
   - Use consistent prefixes for similar object types
   - Consider including location or environment information in names

4. **API Usage**
   - Handle all exceptions appropriately
   - Use proper data validation before API calls
   - Implement retry logic for production code
   - Consider rate limiting for large bulk operations

5. **Security Considerations**
   - Document sensitive systems and networks through tags and descriptions
   - Consider auditing and logging requirements
   - Follow the principle of least privilege when assigning permissions
   - Use consistent naming and description conventions for easier auditing
