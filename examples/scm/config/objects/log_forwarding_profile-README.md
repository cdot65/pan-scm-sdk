# Log Forwarding Profile Example Script

## Overview {#Overview}

The `log_forwarding_profile.py` script demonstrates comprehensive examples of working with Log Forwarding Profile objects in Palo Alto Networks' Strata Cloud Manager (SCM). Log forwarding profiles define how logs are handled and forwarded to external systems, allowing you to configure match criteria for different log types and specify where the matching logs should be sent.

## Features

- Creation of various log forwarding profile types:
  - Traffic log forwarding profiles
  - Threat log forwarding profiles
  - URL log forwarding profiles
  - WildFire log forwarding profiles
  - Multi-type log forwarding profiles with multiple match lists
- Searching and filtering profiles by log type and other criteria
- Updating existing log forwarding profiles
- Bulk operations for creating multiple profiles
- Detailed CSV report generation
- Formatted output with color-coded logging
- Execution statistics and performance metrics
- Support for command-line arguments to customize execution

## Prerequisites

Before running this example script:

1. Replace the authentication credentials with your own or create a `.env` file:
   ```
   SCM_CLIENT_ID=your_client_id
   SCM_CLIENT_SECRET=your_client_secret
   SCM_TSG_ID=your_tsg_id
   SCM_LOG_LEVEL=DEBUG  # Optional
   ```

2. Make sure you have a folder named "Texas" in your SCM environment or modify the folder name using the `--folder` command-line argument.

3. Ensure that your SCM environment has a Syslog server profile named "test123" or modify the script to use an existing Syslog server profile in your environment.

## Usage

### Basic Usage

Run the script with default settings:

```bash
python log_forwarding_profile.py
```

This will create one of each log forwarding profile type (traffic, threat, URL, WildFire, multi-type), and a set of bulk profiles. After completion, all created profiles will be cleaned up unless the `--skip-cleanup` flag is used.

### Command-Line Arguments

Customize script execution with the following arguments:

```bash
python log_forwarding_profile.py --traffic --threat --skip-cleanup --folder "Production"
```

#### Available Arguments:

- `--traffic`: Create only traffic log profile examples
- `--threat`: Create only threat log profile examples
- `--url`: Create only URL log profile examples
- `--wildfire`: Create only WildFire log profile examples
- `--multi`: Create only multi-type log profile examples
- `--bulk`: Create only bulk profile examples
- `--all`: Create all profile types (default behavior)
- `--no-report`: Skip CSV report generation
- `--skip-cleanup`: Preserve created profiles (don't delete them)
- `--folder FOLDER`: Folder name in SCM to create profiles in (default: "Texas")

## Script Structure

The script is organized into several key functions:

1. `initialize_client()`: Sets up credentials and creates the SCM client
2. Profile creation functions for each log type:
   - `create_traffic_log_profile()`
   - `create_threat_log_profile()`
   - `create_url_log_profile()`
   - `create_wildfire_log_profile()`
   - `create_multi_type_profile()`
   - `create_bulk_profiles()`
3. `fetch_and_update_profile()`: Demonstrates updating an existing profile
4. `list_and_filter_profiles()`: Shows how to list and filter profiles
5. `generate_profile_report()`: Creates a detailed CSV report
6. `cleanup_profiles()`: Removes created profiles
7. `parse_arguments()`: Handles command-line argument parsing
8. `main()`: Orchestrates the overall script execution

## Example Configurations

### Traffic Log Profile

```python
{
    "name": "traffic-logs-example",
    "description": "Example traffic log forwarding profile",
    "folder": "Texas",
    "match_list": [
        {
            "name": "internal-traffic",
            "log_type": "traffic",
            "filter": "addr.src in 10.0.0.0/8",
            "send_syslog": ["test123"],  # Use an existing Syslog server profile
            "send_to_panorama": True
        }
    ]
}
```

### Multi-Type Log Profile

```python
{
    "name": "multi-type-logs-example",
    "description": "Example multi-type log forwarding profile",
    "folder": "Texas",
    "match_list": [
        {
            "name": "critical-traffic",
            "log_type": "traffic",
            "filter": "flags.set eq emergency",
            "send_syslog": ["test123"]  # Use an existing Syslog server profile
        },
        {
            "name": "high-severity-threats",
            "log_type": "threat",
            "filter": "severity eq high",
            "send_syslog": ["test123"]  # Use an existing Syslog server profile
        },
        {
            "name": "malicious-urls",
            "log_type": "url",
            "filter": "category.member eq malware",
            "send_syslog": ["test123"]  # Use an existing Syslog server profile
        }
    ],
    "enhanced_application_logging": True
}
```

## Report Generation

When executed, the script generates a comprehensive CSV report containing:

- Profile IDs and names
- Descriptions
- Match list count
- Log types handled
- HTTP and Syslog servers configured
- Panorama forwarding status
- Enhanced application logging status
- Creation timestamps

The report is saved with a timestamp in the filename format: `log_forwarding_profiles_report_YYYYMMDD_HHMMSS.csv`.

## Error Handling

The script includes robust error handling for:

- Authentication failures
- Non-existent folders
- Invalid profile configurations
- Name conflicts
- API request failures
- Report generation issues

## Best Practices

When creating your own log forwarding profile implementations, consider the following:

1. Use specific filter expressions to target only the logs you need
2. Implement appropriate error handling
3. Consider using both HTTP and syslog servers for critical log types
4. Use enhanced application logging for applications that require detailed logging
5. Group related log forwarding configurations in multi-type profiles where appropriate
6. Verify HTTP and syslog server profiles exist before referencing them

## SDK Documentation

For more information on log forwarding profiles, see the [Log Forwarding Profile Configuration](https://github.com/PaloAltoNetworks/pan-scm-sdk/blob/main/docs/sdk/config/objects/log_forwarding_profile.md) documentation.
