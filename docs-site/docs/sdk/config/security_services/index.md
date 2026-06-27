# Security Services Configuration

Security services configuration objects for managing security policies, profiles, and rules in Strata Cloud Manager.

## Overview

This section covers security services provided by the Palo Alto Networks Strata Cloud Manager SDK. Each configuration object corresponds to a resource in Strata Cloud Manager and provides methods for managing security policies and profiles.

## Security Rules and Policy Management

### [Security Rule](security_rule.md)

Manage security rules that define core security policies for network traffic, including source/destination zones, applications, services, and security profiles.

### [App Override Rule](app_override_rule.md)

Manage app override rules to force application identification for specific traffic based on zone, address, port, and protocol.

### [Authentication Rule](authentication_rule.md)

Manage authentication rules to define identity-based policies for network traffic.

### [Decryption Rule](decryption_rule.md)

Manage decryption rules to control SSL/TLS traffic inspection policies.

## Security Profiles

### [Anti-Spyware Profile](anti_spyware_profile.md)

Configure anti-spyware profiles to protect against spyware, command-and-control traffic, and data exfiltration.

### [Decryption Profile](decryption_profile.md)

Manage SSL/TLS decryption profiles to control encrypted traffic inspection and certificate validation.

### [DNS Security Profile](dns_security_profile.md)

Configure DNS security profiles to protect against DNS tunneling, DGA, and malicious domains.

### [File Blocking Profile](file_blocking_profile.md)

Manage file blocking profiles to control file transfers based on file type and direction.

### [URL Access Profile](url_access_profile.md)

Configure URL access profiles to control website access by category with credential enforcement.

### [URL Categories](url_categories.md)

Manage custom URL categories for granular policy control.

### [Vulnerability Protection Profile](vulnerability_protection_profile.md)

Manage vulnerability protection profiles to protect against known CVEs and exploit attempts.

### [Wildfire Antivirus Profile](wildfire_antivirus.md)

Configure WildFire and antivirus profiles for real-time malware analysis and zero-day protection.

## Common Features

All security services configuration objects provide:

- Standard CRUD operations (create, read, update, delete)
- Pagination support for large collections
- Filtering capabilities
- Container-aware operations (`folder`, `snippet`, or `device`)
- Validation of configuration parameters

## Usage Pattern

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access any security service through the client
rules = client.security_rule.list(folder="Texas", rulebase="pre")
profiles = client.anti_spyware_profile.list(folder="Texas")
```

## Related Documentation

- [Security Models](../../models/security_services/index.md)
- [API Client](../../client.md)
- [Operations](../../models/operations/jobs.md)
