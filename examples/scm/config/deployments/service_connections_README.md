# Service Connections Example

## Overview

This script demonstrates comprehensive examples of managing Service Connection objects in Palo Alto Networks' Strata Cloud Manager using the PAN-SCM-SDK. Service Connections allow for secure connectivity between a customer network and cloud service providers.

## Features

- **Multiple Configuration Types**: Examples of basic, BGP-enabled, QoS-enabled, and advanced service connections
- **CRUD Operations**: Creating, reading, updating, and deleting service connections
- **Searching & Filtering**: Finding service connections by various criteria
- **Reporting**: Generating detailed CSV reports of service connections
- **Error Handling**: Robust error handling and clear error messages
- **Colorized Logging**: Well-formatted, color-coded console output

## Prerequisites

- Python 3.8+
- PAN-SCM-SDK installed
- API credentials for Strata Cloud Manager
- Appropriate permissions to manage service connections
- **IMPORTANT**: Existing IPsec tunnels must be available in your SCM environment
  - You must provide the names of these tunnels when running the script
  - The tunnels must already be configured and available in SCM

## Configuration

Create a `.env` file in the same directory as the script with:

```
SCM_CLIENT_ID=your_client_id
SCM_CLIENT_SECRET=your_client_secret
SCM_TSG_ID=your_tsg_id
SCM_LOG_LEVEL=DEBUG  # Optional
SKIP_CLEANUP=false   # Optional, set to true to preserve created objects
```

## Usage

### Important: IPsec Tunnel Requirement

All examples require an existing IPsec tunnel in your SCM environment. You must provide this with the `--ipsec-tunnel` parameter:

```bash
python service_connections.py --ipsec-tunnel "your-existing-tunnel-name"
```

For advanced connections with secondary tunnels:

```bash
python service_connections.py --ipsec-tunnel "primary-tunnel" --secondary-tunnel "backup-tunnel"
```

### Basic Usage

Run all examples (with required tunnel parameter):

```bash
python service_connections.py --ipsec-tunnel "your-existing-tunnel-name"
```

### Selective Examples

Run only specific types of service connections:

```bash
python service_connections.py --basic --ipsec-tunnel "your-tunnel-name"      # Only basic service connections
python service_connections.py --bgp --ipsec-tunnel "your-tunnel-name"        # Only BGP service connections
python service_connections.py --qos --ipsec-tunnel "your-tunnel-name"        # Only QoS service connections
python service_connections.py --advanced --ipsec-tunnel "your-tunnel-name"   # Only advanced service connections
```

### Skip Cleanup

Preserve the created objects for further inspection:

```bash
python service_connections.py --ipsec-tunnel "your-tunnel-name" --skip-cleanup
```

### Reporting

Disable CSV report generation:

```bash
python service_connections.py --ipsec-tunnel "your-tunnel-name" --no-report
```

### Custom Pagination Limit

Set custom maximum limit for API requests:

```bash
python service_connections.py --ipsec-tunnel "your-tunnel-name" --max-limit 500
```

## Service Connection Types

1. **Basic Service Connection**:
   - Minimal configuration
   - Region and subnets
   - Source NAT enabled

2. **BGP Service Connection**:
   - BGP peering configuration
   - AS number and local/peer IP addresses
   - Fast failover and default route origination

3. **QoS Service Connection**:
   - Quality of Service enabled
   - QoS profile association

4. **Advanced Service Connection**:
   - Secondary IPsec tunnel
   - Backup service connection
   - Combined BGP and QoS settings
   - No export community configuration

## Reporting

The script generates a detailed CSV report with:
- Service connection details
- BGP configuration summary
- QoS settings
- IPsec tunnel information
- Execution statistics

## Troubleshooting

### IPsec Tunnel Reference Errors

If you see errors like this:

```
✘ ERROR: Invalid IPsec tunnel reference - The specified IPsec tunnel does not exist
```

This means the IPsec tunnel name you provided doesn't exist in your SCM environment. To fix this:

1. Verify that you have provided the `--ipsec-tunnel` parameter with an existing tunnel name
2. Check in the SCM console that the tunnel exists and is correctly configured
3. Make sure you have appropriate permissions to access the tunnel

### Other Common Issues

If you encounter other errors:

1. Verify your API credentials
2. Ensure you have appropriate permissions
3. Check that the IPsec tunnel names exist in your environment
4. Verify network connectivity to the SCM API
5. Check the script output for detailed error information
6. Try running with `SCM_LOG_LEVEL=DEBUG` for more detailed logs

## License

See the LICENSE file in the repository root directory.
