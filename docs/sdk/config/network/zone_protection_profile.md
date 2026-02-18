# Zone Protection Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Zone Protection Profile Model Attributes](#zone-protection-profile-model-attributes)
4. [Nested Model Structures](#nested-model-structures)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating Zone Protection Profiles](#creating-zone-protection-profiles)
    - [Retrieving Zone Protection Profiles](#retrieving-zone-protection-profiles)
    - [Updating Zone Protection Profiles](#updating-zone-protection-profiles)
    - [Listing Zone Protection Profiles](#listing-zone-protection-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Zone Protection Profiles](#deleting-zone-protection-profiles)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `ZoneProtectionProfile` class manages zone protection profile objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete zone protection profiles. These profiles provide protection against floods, reconnaissance scans, and packet-based attacks at the zone level. Zone protection profiles feature deeply nested model structures for flood protection, scan protection, and various packet discard options.

## Core Methods

| Method     | Description                                                                | Parameters                                                                                                                       | Return Type                                  |
|------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| `create()` | Creates a new zone protection profile                                      | `data: Dict[str, Any]`                                                                                                           | `ZoneProtectionProfileResponseModel`         |
| `get()`    | Retrieves a zone protection profile by its unique ID                       | `object_id: str`                                                                                                                 | `ZoneProtectionProfileResponseModel`         |
| `update()` | Updates an existing zone protection profile                                | `profile: ZoneProtectionProfileUpdateModel`                                                                                      | `ZoneProtectionProfileResponseModel`         |
| `list()`   | Lists zone protection profiles with optional filtering                     | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[ZoneProtectionProfileResponseModel]`   |
| `fetch()`  | Fetches a single zone protection profile by name within a container        | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `ZoneProtectionProfileResponseModel`         |
| `delete()` | Deletes a zone protection profile by its ID                                | `object_id: str`                                                                                                                 | `None`                                       |

## Zone Protection Profile Model Attributes

| Attribute                                       | Type                     | Required | Default | Description                                       |
|-------------------------------------------------|--------------------------|----------|---------|---------------------------------------------------|
| `name`                                          | str                      | Yes      | None    | Profile name. Max 31 chars                        |
| `id`                                            | UUID                     | Yes*     | None    | Unique identifier (*response/update only)         |
| `description`                                   | str                      | No       | None    | Description. Max 255 chars                        |
| `flood`                                         | FloodProtection          | No       | None    | Flood protection configuration (nested)           |
| `scan`                                          | List[ScanEntry]          | No       | None    | Scan protection entries (nested list)             |
| `scan_white_list`                               | List[ScanWhiteListEntry] | No       | None    | Scan whitelist entries                            |
| `spoofed_ip_discard`                            | bool                     | No       | None    | Discard spoofed IP packets                        |
| `strict_ip_check`                               | bool                     | No       | None    | Enable strict IP address checking                 |
| `fragmented_traffic_discard`                    | bool                     | No       | None    | Discard fragmented traffic                        |
| `strict_source_routing_discard`                 | bool                     | No       | None    | Discard strict source routing packets             |
| `loose_source_routing_discard`                  | bool                     | No       | None    | Discard loose source routing packets              |
| `timestamp_discard`                             | bool                     | No       | None    | Discard timestamp option packets                  |
| `record_route_discard`                          | bool                     | No       | None    | Discard record route option packets               |
| `security_discard`                              | bool                     | No       | None    | Discard security option packets                   |
| `stream_id_discard`                             | bool                     | No       | None    | Discard stream ID option packets                  |
| `unknown_option_discard`                        | bool                     | No       | None    | Discard unknown option packets                    |
| `malformed_option_discard`                      | bool                     | No       | None    | Discard malformed option packets                  |
| `mismatched_overlapping_tcp_segment_discard`    | bool                     | No       | None    | Discard mismatched overlapping TCP segments        |
| `tcp_handshake_discard`                         | bool                     | No       | None    | Discard incomplete TCP handshake packets          |
| `tcp_syn_with_data_discard`                     | bool                     | No       | None    | Discard TCP SYN packets with data                 |
| `tcp_synack_with_data_discard`                  | bool                     | No       | None    | Discard TCP SYN-ACK packets with data             |
| `reject_non_syn_tcp`                            | str                      | No       | None    | Reject non-SYN TCP: `global`, `yes`, or `no`     |
| `asymmetric_path`                               | str                      | No       | None    | Asymmetric path handling: `global`, `drop`, or `bypass` |
| `mptcp_option_strip`                            | str                      | No       | None    | MPTCP option strip: `no`, `yes`, or `global`      |
| `tcp_timestamp_strip`                           | bool                     | No       | None    | Strip TCP timestamp option                        |
| `tcp_fast_open_and_data_strip`                  | bool                     | No       | None    | Strip TCP Fast Open and data                      |
| `icmp_ping_zero_id_discard`                     | bool                     | No       | None    | Discard ICMP ping with zero ID                    |
| `icmp_frag_discard`                             | bool                     | No       | None    | Discard fragmented ICMP packets                   |
| `icmp_large_packet_discard`                     | bool                     | No       | None    | Discard large ICMP packets                        |
| `discard_icmp_embedded_error`                   | bool                     | No       | None    | Discard ICMP embedded error messages              |
| `suppress_icmp_timeexceeded`                    | bool                     | No       | None    | Suppress ICMP time exceeded messages              |
| `suppress_icmp_needfrag`                        | bool                     | No       | None    | Suppress ICMP need fragmentation messages         |
| `ipv6`                                          | Dict[str, Any]           | No       | None    | IPv6 protection configuration                     |
| `non_ip_protocol`                               | NonIpProtocol            | No       | None    | Non-IP protocol configuration                     |
| `l2_sec_group_tag_protection`                   | L2SecGroupTagProtection  | No       | None    | Layer 2 Security Group Tag protection             |
| `folder`                                        | str                      | No**     | None    | Folder location. Max 64 chars                     |
| `snippet`                                       | str                      | No**     | None    | Snippet location. Max 64 chars                    |
| `device`                                        | str                      | No**     | None    | Device location. Max 64 chars                     |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## Nested Model Structures

Zone protection profiles use a deeply nested model structure. Below are the key nested components.

### Flood Protection (FloodProtection)

The `flood` attribute contains sub-objects for each flood type:

| Sub-Attribute | Type          | Description                     |
|---------------|---------------|---------------------------------|
| `tcp_syn`     | TcpSynFlood   | TCP SYN flood protection        |
| `udp`         | UdpFlood      | UDP flood protection            |
| `sctp_init`   | SctpInitFlood | SCTP INIT flood protection      |
| `icmp`        | IcmpFlood     | ICMP flood protection           |
| `icmpv6`      | Icmpv6Flood   | ICMPv6 flood protection         |
| `other_ip`    | OtherIpFlood  | Other IP flood protection       |

Each flood type supports `enable` (bool) and `red` (FloodRed with `alarm_rate`, `activate_rate`, `maximal_rate`). TCP SYN flood also supports `syn_cookies` as an alternative to `red` (mutually exclusive).

### Scan Protection (ScanEntry)

Each scan entry has:

| Attribute   | Type       | Description                                         |
|-------------|------------|-----------------------------------------------------|
| `name`      | str        | Scan entry ID: `8001`, `8002`, `8003`, or `8006`    |
| `action`    | ScanAction | Action: `allow`, `alert`, `block`, or `block_ip`    |
| `interval`  | int        | Scan interval (2-65535)                              |
| `threshold` | int        | Scan threshold (2-65535)                             |

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Profile name already exists                                                   |
| `ObjectNotPresentError`      | 404       | Profile not found                                                             |
| `ReferenceNotZeroError`      | 409       | Profile still referenced by a security zone                                   |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The Zone Protection Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the Zone Protection Profile service directly through the client
zone_profiles = client.zone_protection_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import ZoneProtectionProfile

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize ZoneProtectionProfile object explicitly
zone_profiles = ZoneProtectionProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Zone Protection Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a basic zone protection profile with flood protection
profile_data = {
   "name": "basic-zone-protection",
   "description": "Basic zone protection with SYN flood mitigation",
   "flood": {
      "tcp_syn": {
         "enable": True,
         "red": {
            "alarm_rate": 10000,
            "activate_rate": 20000,
            "maximal_rate": 40000
         }
      },
      "udp": {
         "enable": True,
         "red": {
            "alarm_rate": 10000,
            "activate_rate": 20000,
            "maximal_rate": 40000
         }
      },
      "icmp": {
         "enable": True,
         "red": {
            "alarm_rate": 5000,
            "activate_rate": 10000,
            "maximal_rate": 20000
         }
      }
   },
   "spoofed_ip_discard": True,
   "strict_ip_check": True,
   "reject_non_syn_tcp": "yes",
   "folder": "Texas"
}

new_profile = client.zone_protection_profile.create(profile_data)
print(f"Created zone protection profile with ID: {new_profile.id}")

# Create a profile with scan protection
scan_profile_data = {
   "name": "scan-protection",
   "description": "Zone protection with scan detection",
   "scan": [
      {
         "name": "8001",
         "action": {"alert": {}},
         "interval": 2,
         "threshold": 100
      },
      {
         "name": "8002",
         "action": {"block_ip": {"track_by": "source", "duration": 300}},
         "interval": 5,
         "threshold": 50
      }
   ],
   "fragmented_traffic_discard": True,
   "malformed_option_discard": True,
   "folder": "Texas"
}

scan_profile = client.zone_protection_profile.create(scan_profile_data)
print(f"Created scan protection profile with ID: {scan_profile.id}")
```

### Retrieving Zone Protection Profiles

```python
# Fetch by name and folder
profile = client.zone_protection_profile.fetch(
   name="basic-zone-protection",
   folder="Texas"
)
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.zone_protection_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Description: {profile_by_id.description}")
```

### Updating Zone Protection Profiles

```python
# Fetch existing profile
existing_profile = client.zone_protection_profile.fetch(
   name="basic-zone-protection",
   folder="Texas"
)

# Enable additional discard settings
existing_profile.strict_source_routing_discard = True
existing_profile.loose_source_routing_discard = True
existing_profile.timestamp_discard = True
existing_profile.unknown_option_discard = True

# Update description
existing_profile.description = "Enhanced zone protection with IP option discards"

# Perform update
updated_profile = client.zone_protection_profile.update(existing_profile)
```

### Listing Zone Protection Profiles

```python
# List all profiles in a folder
profiles = client.zone_protection_profile.list(
   folder="Texas"
)

# Process results
for profile in profiles:
   print(f"Name: {profile.name}")
   print(f"  Description: {profile.description}")
   if profile.flood and profile.flood.tcp_syn and profile.flood.tcp_syn.enable:
      print("  TCP SYN flood protection: Enabled")
   if profile.spoofed_ip_discard:
      print("  Spoofed IP discard: Enabled")

# List with description filter
filtered_profiles = client.zone_protection_profile.list(
   folder="Texas",
   description="scan"
)

for profile in filtered_profiles:
   print(f"Filtered profile: {profile.name}")
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters,
you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control
which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return profiles defined exactly in 'Texas'
exact_profiles = client.zone_protection_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.zone_protection_profile.list(
   folder='Texas',
   exclude_folders=['All']
)

for profile in no_all_profiles:
   assert profile.folder != 'All'
   print(f"Filtered out 'All': {profile.name}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.zone_protection_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.zone_protection_profile.list(folder='Texas')
```

### Deleting Zone Protection Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.zone_protection_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated zone protection profiles",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   NameNotUniqueError,
   ObjectNotPresentError,
   ReferenceNotZeroError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create zone protection profile configuration
   profile_config = {
      "name": "test-zone-protection",
      "description": "Test zone protection profile",
      "flood": {
         "tcp_syn": {
            "enable": True,
            "red": {
               "alarm_rate": 10000,
               "activate_rate": 20000,
               "maximal_rate": 40000
            }
         }
      },
      "spoofed_ip_discard": True,
      "folder": "Texas"
   }

   # Create the profile using the unified client interface
   new_profile = client.zone_protection_profile.create(profile_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Texas"],
      description="Added test zone protection profile",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid profile data: {e.message}")
except NameNotUniqueError as e:
   print(f"Profile name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Profile not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Profile still in use by a security zone: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.zone_protection_profile`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Profile Configuration**
   - Enable flood protection for all common attack vectors (TCP SYN, UDP, ICMP)
   - Set appropriate rate thresholds based on your network traffic patterns
   - Use SYN Cookies for high-traffic environments (`syn_cookies` instead of `red` in TCP SYN flood config)
   - Enable packet discard options to harden the zone against known attack techniques
   - Configure scan protection entries for port scan and host sweep detection

3. **Nested Model Structure**
   - Understand that flood protection uses deeply nested objects (e.g., `flood.tcp_syn.red.alarm_rate`)
   - Note that `red` and `syn_cookies` are mutually exclusive in TCP SYN flood configuration
   - Scan actions (`allow`, `alert`, `block`, `block_ip`) are also mutually exclusive
   - Use `block_ip` with appropriate `track_by` and `duration` for aggressive scan blocking

4. **Container Management**
   - Always specify exactly one container (folder, snippet, or device)
   - Use consistent container names across operations
   - Validate container existence before operations

5. **Error Handling**
   - Implement comprehensive error handling for all operations
   - Check job status after commits
   - Handle specific exceptions before generic ones
   - Log error details for troubleshooting

6. **Performance**
   - Use appropriate pagination for list operations
   - Cache frequently accessed profiles
   - Implement proper retry mechanisms

7. **Security**
   - Apply zone protection profiles to all security zones
   - Tune flood thresholds to balance between security and legitimate traffic
   - Regularly review and update discard settings
   - Monitor zone protection logs for attack patterns

## Related Models

- [ZoneProtectionProfileBaseModel](../../models/network/zone_protection_profile_models.md#Overview)
- [ZoneProtectionProfileCreateModel](../../models/network/zone_protection_profile_models.md#Overview)
- [ZoneProtectionProfileUpdateModel](../../models/network/zone_protection_profile_models.md#Overview)
- [ZoneProtectionProfileResponseModel](../../models/network/zone_protection_profile_models.md#Overview)
- [FloodProtection](../../models/network/zone_protection_profile_models.md#Overview)
- [ScanEntry](../../models/network/zone_protection_profile_models.md#Overview)
- [NonIpProtocol](../../models/network/zone_protection_profile_models.md#Overview)
- [L2SecGroupTagProtection](../../models/network/zone_protection_profile_models.md#Overview)
