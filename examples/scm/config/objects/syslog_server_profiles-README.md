# Syslog Server Profiles Guide

This guide provides comprehensive information about working with Syslog Server Profiles in Palo Alto Networks' Strata Cloud Manager (SCM) using the SCM SDK.

**📋 Note: Updated model handling in SCM SDK version 2.0**
The SCM SDK now includes robust handling for different API response formats when working with Syslog Server Profiles.

## Overview

Syslog Server Profiles are configuration objects that define how logs are sent from Palo Alto Networks devices to external syslog servers. These profiles allow you to specify:

- Which syslog servers to send logs to
- The transport protocol to use (UDP or TCP)
- The syslog format (BSD or IETF)
- Custom formats for different log types
- Character escaping for special characters in log messages

Typical use cases include:

- Central log collection and monitoring
- Security information and event management (SIEM) integration
- Compliance logging and auditing
- Backup logging to multiple destinations
- Custom log format for specific analysis tools

## Key Concepts

### Container Types

Syslog Server Profiles must be associated with exactly one container type:

- `folder`: Associates the profile with a folder in the SCM hierarchy
- `snippet`: Associates the profile with a configuration snippet
- `device`: Associates the profile with a specific device

When creating or updating a profile, you must specify exactly one of these container types.

### Server Configuration

Each Syslog Server Profile contains one or more server configurations. Each server requires:

- `name`: A unique name for the server within the profile
- `server`: The IP address or hostname of the syslog server
- `transport`: The protocol to use (`UDP` or `TCP`)
- `port`: The port number to send logs to (typically 514 for UDP, 1514 for TCP)
- `format`: The syslog format (`BSD` or `IETF`)
- `facility`: The syslog facility value (e.g., `LOG_USER`, `LOG_LOCAL0`, etc.)

### Format Templates

You can define custom format templates for different log types, such as:

- `traffic`: Format for traffic logs
- `threat`: Format for threat logs
- `system`: Format for system logs
- And many others (see [Supported Log Types](#supported-log-types))

Format templates can include variables like `${time}`, `${src}`, `${dst}`, etc.

### Character Escaping

For special characters in log messages, you can configure character escaping:

- `escape_character`: The character to use as an escape delimiter (typically `\`)
- `escaped_characters`: A string of characters to escape (e.g., `%"\\[]`)

## Example Usage

### Basic UDP Syslog Server Profile

```python
# Create a basic UDP syslog server profile
udp_profile = syslog_profiles.create({
    "name": "basic-udp-profile",
    "folder": "Shared",
    "servers": {
        "main-server": {
            "name": "main-server",
            "server": "192.168.1.100",
            "transport": "UDP",
            "port": 514,
            "format": "BSD",
            "facility": "LOG_USER"
        }
    }
})
```

### TCP Syslog Server Profile with Custom Format

```python
# Create a TCP syslog server profile with custom format templates
tcp_profile = syslog_profiles.create({
    "name": "custom-tcp-profile",
    "folder": "Shared",
    "servers": {
        "secure-server": {
            "name": "secure-server",
            "server": "logs.example.com",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL0"
        }
    },
    "format": {
        "traffic": "${time} ${src} ${dst} ${proto} ${action}",
        "threat": "${time} ${threatid} ${src} ${dst} ${severity}",
        "system": "${time} ${severity} ${actiontext}"
    }
})
```

### Multi-Server Profile with Character Escaping

```python
# Create a profile with multiple servers and character escaping
multi_profile = syslog_profiles.create({
    "name": "multi-server-profile",
    "folder": "Shared",
    "servers": {
        "primary": {
            "name": "primary",
            "server": "logs-primary.example.com",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL0"
        },
        "backup": {
            "name": "backup",
            "server": "logs-backup.example.com",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL1"
        }
    },
    "format": {
        "escaping": {
            "escape_character": "\\",
            "escaped_characters": "%\"\\[]"
        },
        "traffic": "${time} ${src} ${dst} ${proto} ${action}",
        "threat": "${time} ${threatid} ${src} ${dst} ${severity}"
    }
})
```

## Updating Profiles

To update an existing profile, first retrieve it, modify its properties, and then submit the update:

```python
# Fetch an existing profile by ID
profile = syslog_profiles.get("profile-id-here")

# Create update data
update_data = {
    "id": profile.id,
    "name": profile.name,
    "folder": profile.folder,  # Or snippet/device if applicable
    "servers": profile.servers
}

# Add a new server
update_data["servers"]["new-server"] = {
    "name": "new-server",
    "server": "192.168.10.200",
    "transport": "UDP",
    "port": 514,
    "format": "BSD",
    "facility": "LOG_LOCAL7"
}

# Update the profile
updated_profile = syslog_profiles.update(update_data)
```

## Common Operations

### Listing Profiles

```python
# List all profiles in a folder
all_profiles = syslog_profiles.list(folder="Shared")

# Filter by transport protocol
udp_profiles = syslog_profiles.list(folder="Shared", transport=["UDP"])
tcp_profiles = syslog_profiles.list(folder="Shared", transport=["TCP"])

# Filter by format type
bsd_profiles = syslog_profiles.list(folder="Shared", format=["BSD"])
ietf_profiles = syslog_profiles.list(folder="Shared", format=["IETF"])
```

### Fetching a Profile by Name

```python
# Fetch a profile by name and folder
profile = syslog_profiles.fetch(
    name="my-syslog-profile",
    folder="Shared"
)
```

### Deleting a Profile

```python
# Delete a profile by ID
syslog_profiles.delete("profile-id-here")
```

## Best Practices

### Syslog Transport Protocol Selection

- Use **UDP** when:
  - Log volume is high and occasional packet loss is acceptable
  - Network bandwidth is a concern
  - You need simpler configuration
  - Performance is a priority

- Use **TCP** when:
  - Log delivery reliability is critical
  - Regulatory compliance requires guaranteed delivery
  - Security events need assured transmission
  - Network conditions may cause packet loss

### Format Selection

- Use **BSD format** when:
  - Simplicity and compatibility with older systems is important
  - Parse performance is a priority
  - You need standard syslog format for legacy systems

- Use **IETF format** (RFC 5424) when:
  - Structured data is important
  - You need precise timestamps with milliseconds
  - Internationalization support is required
  - You need more detailed message formatting

### Custom Format Templates

When defining custom format templates:
- Include only the fields you need to minimize log size
- Order fields in a logical sequence for easier analysis
- Include correlation fields to link related log entries
- Consider readability for human analysts
- Test your format templates thoroughly

### Security Considerations

- Use TCP with TLS for sensitive log data
- Define separate profiles for different security levels
- Implement server redundancy for critical logs
- Regularly validate log delivery to ensure proper operation
- Consider network segmentation for log servers

## Supported Log Types

The following log types are supported in format templates:

| Log Type | Description |
|----------|-------------|
| `traffic` | Network traffic logs |
| `threat` | Threat detection logs |
| `wildfire` | WildFire analysis logs |
| `url` | URL filtering logs |
| `data` | Data filtering logs |
| `gtp` | GTP protocol logs |
| `sctp` | SCTP protocol logs |
| `tunnel` | Tunnel inspection logs |
| `auth` | Authentication logs |
| `userid` | User-ID mapping logs |
| `iptag` | IP tag logs |
| `decryption` | SSL/TLS decryption logs |
| `config` | Configuration change logs |
| `system` | System events logs |
| `globalprotect` | GlobalProtect VPN logs |
| `hip_match` | Host Information Profile matching logs |
| `correlation` | Correlated events logs |

## Troubleshooting

### Invalid Container Error

If you receive an error about invalid container parameters, ensure you're specifying exactly one of `folder`, `snippet`, or `device`.

```python
# Correct
profile = syslog_profiles.create({
    "name": "my-profile",
    "folder": "Shared",  # Only one container type specified
    "servers": { ... }
})

# Incorrect - multiple containers
profile = syslog_profiles.create({
    "name": "my-profile",
    "folder": "Shared",
    "device": "my-device",  # Error: multiple containers
    "servers": { ... }
})
```

### Transport Protocol Errors

The transport protocol must be either "UDP" or "TCP" (case-sensitive).

```python
# Correct
"transport": "UDP"  # or "TCP"

# Incorrect
"transport": "udp"  # wrong case
"transport": "UDP/TCP"  # invalid value
```

### Format Type Errors

The format must be either "BSD" or "IETF" (case-sensitive).

```python
# Correct
"format": "BSD"  # or "IETF"

# Incorrect
"format": "bsd"  # wrong case
"format": "syslog"  # invalid value
```

### Facility Value Errors

The facility must be one of the predefined values (all uppercase with underscore).

```python
# Correct
"facility": "LOG_USER"
"facility": "LOG_LOCAL0"

# Incorrect
"facility": "USER"  # missing LOG_ prefix
"facility": "Log_Local0"  # wrong case
```

### Port Range Errors

Port numbers must be between 1 and 65535.

```python
# Correct
"port": 514  # Standard syslog port

# Incorrect
"port": 0  # Below minimum
"port": 70000  # Above maximum
```

## References

- [Syslog Server Profiles in SCM Documentation](https://docs.paloaltonetworks.com)
- [RFC 3164 - The BSD syslog Protocol](https://datatracker.ietf.org/doc/html/rfc3164)
- [RFC 5424 - The Syslog Protocol (IETF format)](https://datatracker.ietf.org/doc/html/rfc5424)
- [Syslog Facility Values](https://en.wikipedia.org/wiki/Syslog#Facility)
