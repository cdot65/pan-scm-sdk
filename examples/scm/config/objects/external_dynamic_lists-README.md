# Comprehensive External Dynamic Lists SDK Examples

This directory contains extensive example scripts demonstrating how to use the Palo Alto Networks Strata Cloud Manager (SCM) SDK to manage External Dynamic Lists (EDLs) across a wide range of real-world enterprise scenarios.

## Overview {#Overview}

The `external_dynamic_lists.py` script showcases enterprise-ready EDL configurations addressing common threat intelligence consumption needs, including:

1. **List Types and Formats**:
   - IP-based EDLs for blocking malicious IP addresses
   - Domain-based EDLs for domain reputation filtering
   - URL-based EDLs for web threat intelligence
   - Predefined EDLs from Palo Alto Networks
   - IMSI/IMEI-based EDLs for mobile network security

2. **Update Frequencies**:
   - Five-minute updates for critical threat feeds
   - Hourly updates for moderate-risk intelligence
   - Daily updates for standard threat feeds
   - Weekly and monthly updates for slowly changing datasets

3. **Authentication Methods**:
   - HTTP basic authentication for protected sources
   - Certificate-based authentication for secure connections

4. **Special Features**:
   - Domain expansion for subdomains
   - Exception lists
   - Predefined list integration

5. **Operational Functions**:
   - Bulk creation capabilities - for mass configuration
   - Advanced filtering and search capabilities
   - Comprehensive error handling
   - Safe cleanup procedures

6. **Reporting and Documentation**:
   - Detailed CSV report generation with EDL details
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

The script is organized into modular functions that each demonstrate a specific EDL type or operational task:

### External Dynamic List Creation Examples
- `create_ip_edl_hourly()` - IP-based EDL with hourly updates
- `create_domain_edl_daily()` - Domain-based EDL with daily updates
- `create_url_edl_five_minute()` - URL-based EDL with five-minute updates
- `create_predefined_ip_edl()` - Predefined IP EDL from Palo Alto Networks
- `create_imsi_edl_weekly()` - IMSI-based EDL with weekly updates
- `create_imei_edl_monthly()` - IMEI-based EDL with monthly updates

### Bulk Operations
- `create_bulk_edl_objects()` - Creating multiple EDL objects programmatically

### Operational Functions
- `fetch_and_update_edl()` - Modifying existing EDL objects
- `list_and_filter_edls()` - Finding and filtering EDLs
- `cleanup_edl_objects()` - Safely removing test objects
- `generate_edl_report()` - Creating comprehensive CSV reports

## Real-World External Dynamic List Scenarios

The example script demonstrates these common real-world EDL patterns:

### 1. IP-Based EDL with Hourly Updates
```python
# Create the hourly recurring schedule
hourly_schedule = HourlyRecurringModel(
    hourly={}  # The model expects a dict object for hourly field
)

# Create the IP list model
ip_list = IpModel(
    url="https://www.example.com/threat-feeds/ip-blocklist.txt",
    description="Hourly updated IP threat intelligence feed",
    recurring=hourly_schedule
)

# Create the EDL configuration
ip_edl_config = {
    "name": "ip-threat-feed-example",
    "folder": "Texas",
    "type": IpType(ip=ip_list)
}
```

### 2. Domain-Based EDL with Daily Updates
```python
# Create the daily recurring schedule
daily_schedule = DailyRecurringModel(
    daily={"at": "01"}  # Update at 1:00 AM each day, format is hour only (00-23)
)

# Create the domain list model
domain_list = DomainModel(
    url="https://www.example.com/threat-feeds/domain-blocklist.txt",
    description="Daily updated domain blocklist",
    recurring=daily_schedule,
    expand_domain=True  # Automatically expand subdomains
)

# Create the EDL configuration
domain_edl_config = {
    "name": "domain-blocklist-example",
    "folder": "Texas",
    "type": DomainType(domain=domain_list)
}
```

### 3. URL-Based EDL with Five-Minute Updates
```python
# Create the five-minute recurring schedule
five_minute_schedule = FiveMinuteRecurringModel(
    five_minute={}  # The model expects a dict object for five_minute field
)

# Create the authentication model for protected feed
auth = AuthModel(
    username="feed_reader",
    password="example_password"
)

# Create the URL list model
url_list = UrlTypeModel(  # Using correct UrlTypeModel to match the SDK
    url="https://www.example.com/threat-feeds/malware-urls.txt",
    description="High-frequency malware URL blocklist",
    recurring=five_minute_schedule,
    certificate_profile="default",  # Certificate profile required when using auth
    auth=auth  # Use basic authentication
)

# Create the EDL configuration
url_edl_config = {
    "name": "url-malware-feed-example",
    "folder": "Texas",
    "type": UrlType(url=url_list)
}
```

### 4. Predefined IP EDL
```python
# Create the predefined IP list model
predefined_ip_list = PredefinedIpModel(
    url="panw-bulletproof-ip-list",  # The predefined list name provided as url field
    description="Palo Alto Networks maintained bulletproof IP blocklist"
)

# Create the EDL configuration
predefined_ip_edl_config = {
    "name": "panw-ip-blocklist-example",
    "folder": "Texas",
    "type": PredefinedIpType(predefined_ip=predefined_ip_list)
}
```

### 5. IMSI-Based EDL with Weekly Updates
```python
# Create the weekly recurring schedule
weekly_schedule = WeeklyRecurringModel(
    weekly={
        "day_of_week": "monday",
        "at": "02"  # Update at 2:00 AM each Monday, format is hour only (00-23)
    }
)

# Create the IMSI list model
imsi_list = ImsiModel(
    url="https://www.example.com/mobile/blocked-imsi.txt",
    description="Weekly updated IMSI blocklist",
    recurring=weekly_schedule
)

# Create the EDL configuration
imsi_edl_config = {
    "name": "blocked-imsi-example",
    "folder": "Texas",
    "type": ImsiType(imsi=imsi_list)
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
   - URL values for feeds
   - You can also add these settings to your `.env` file:
     ```
     SCM_FOLDER=Texas
     SKIP_CLEANUP=true  # To preserve created objects
     ```

4. Run the script with various options:
   ```bash
   # Run all examples
   python external_dynamic_lists.py

   # Create only IP-based EDLs
   python external_dynamic_lists.py --ip

   # Create only domain-based EDLs
   python external_dynamic_lists.py --domain

   # Create only URL-based EDLs
   python external_dynamic_lists.py --url

   # Create only predefined EDLs
   python external_dynamic_lists.py --predefined

   # Create only IMSI and IMEI EDLs
   python external_dynamic_lists.py --mobile

   # Create only bulk EDLs
   python external_dynamic_lists.py --bulk

   # Skip cleaning up created objects
   python external_dynamic_lists.py --skip-cleanup

   # Skip CSV report generation
   python external_dynamic_lists.py --no-report

   # Specify a different folder
   python external_dynamic_lists.py --folder=Production
   ```

5. Examine the console output to understand:
   - The EDLs being created
   - Any errors or warnings
   - The filtering and listing operations
   - The cleanup process

> **Security Note**: The `.env` file contains sensitive credentials. Add it to your `.gitignore` file to prevent accidentally committing it to version control.

## External Dynamic List Model Structure

The examples demonstrate the proper structure for each EDL type:

### IP-Based EDL Structure
```python
{
    "name": "malicious-ips",
    "folder": "Texas",  # Container (folder, snippet, or device required)
    "type": IpType(
        ip=IpModel(
            url="https://example.com/feeds/malicious-ips.txt",
            description="Malicious IP feed from Example, Inc.",
            recurring=DailyRecurringModel(daily=True, at="01:00")
        )
    )
}
```

### Domain-Based EDL Structure
```python
{
    "name": "malware-domains",
    "folder": "Texas",
    "type": DomainType(
        domain=DomainModel(
            url="https://example.com/feeds/malware-domains.txt",
            description="Malware domain blocklist",
            recurring=HourlyRecurringModel(hourly=True, at=30),
            expand_domain=True  # Automatically expand subdomains
        )
    )
}
```

### URL-Based EDL with Authentication
```python
{
    "name": "malicious-urls",
    "folder": "Texas",
    "type": UrlType(
        url=UrlTypeModel(  # Using correct UrlTypeModel to match the SDK
            url="https://example.com/feeds/malicious-urls.txt",
            description="Malicious URL blocklist",
            recurring=FiveMinuteRecurringModel(five_minute={}),
            certificate_profile="default",  # Required when using auth
            auth=AuthModel(
                username="feed_user",
                password="feed_password"
            )
        )
    )
}
```

## Update Schedule Options

The SDKs supports several update frequency options:

### 1. Five-Minute Updates
```python
five_minute_schedule = FiveMinuteRecurringModel(
    five_minute={}  # Empty dict required
)
```

### 2. Hourly Updates
```python
hourly_schedule = HourlyRecurringModel(
    hourly={}  # Empty dict required
)
```

### 3. Daily Updates
```python
daily_schedule = DailyRecurringModel(
    daily={"at": "02"}  # Hour in 24-hour format (00-23)
)
```

### 4. Weekly Updates
```python
weekly_schedule = WeeklyRecurringModel(
    weekly={
        "day_of_week": "monday",  # Day of the week
        "at": "03"  # Hour in 24-hour format (00-23)
    }
)
```

### 5. Monthly Updates
```python
monthly_schedule = MonthlyRecurringModel(
    monthly={
        "day_of_month": 1,  # Day of the month (1-31)
        "at": "04"  # Hour in 24-hour format (00-23)
    }
)
```

## Programming Techniques Demonstrated

The example script showcases several important programming techniques:

1. **Error Handling** - Comprehensive try/except blocks for each API call
2. **Unique Naming** - Using UUID suffixes to avoid name conflicts
3. **Modular Code Organization** - Separate functions for each EDL type
4. **Proper Cleanup** - Ensuring all created objects are deleted
5. **Logging** - Consistent and informative log messages with color coding
6. **Command-line Arguments** - Flexible script execution with various options
7. **Environment Variable Support** - Using .env files for credentials
8. **Progress Tracking** - Showing progress during lengthy operations
9. **Performance Metrics** - Tracking and reporting execution statistics

## Best Practices

1. **EDL Source Selection**
   - Use reputable, reliable threat intelligence sources
   - Verify source availability and update frequency
   - Use HTTPS URLs for all sources
   - Consider authentication for sensitive feeds
   - Verify list format compatibility

2. **Update Frequency Selection**
   - Choose update frequency based on the criticality of the feed
   - Use five-minute updates only for critical, rapidly changing feeds
   - Consider network impact when selecting update frequencies
   - Stagger update times to avoid simultaneous updates

3. **Naming Conventions**
   - Use descriptive names that indicate the feed's purpose
   - Include source information in the description
   - Consider including update frequency in the name
   - Use consistent naming patterns across similar EDLs

4. **Security Best Practices**
   - Use strong, unique credentials for authenticated feeds
   - Periodically rotate feed credentials
   - Document feed sources for security compliance
   - Consider certificate-based authentication for high-security environments
   - Never store feed credentials in the script itself

5. **Content Format Requirements**
   - Understand the required format for each list type:
     - IP Lists: One IP address or CIDR per line
     - Domain Lists: One domain per line
     - URL Lists: One URL per line
   - Verify your sources provide correctly formatted data
   - Consider pre-processing feeds with incorrect formats
