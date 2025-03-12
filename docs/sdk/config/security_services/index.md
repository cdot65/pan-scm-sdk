# Security Services Configuration Objects

## Table of Contents

1. [Overview](#overview)
2. [Security Rules and Policy Management](#security-rules-and-policy-management)
3. [Security Profiles](#security-profiles)
4. [Common Features](#common-features)
5. [Usage Pattern](#usage-pattern)
6. [Related Documentation](#related-documentation)

## Overview

This section covers the configuration security services provided by the Palo Alto Networks Strata Cloud Manager SDK. Each configuration object corresponds to a resource in the Strata Cloud Manager and provides methods for managing security policies and profiles.

## Security Rules and Policy Management

### [Security Rule](security_rule.md)

Manage Security Rules, which define the core security policies for your network traffic. These rules determine:

- Source and destination zones/addresses
- Applications and services allowed/denied
- Security profiles to be applied
- Logging and monitoring settings

## Security Profiles

### [Anti Spyware Profile](anti_spyware_profile.md)

Configure Anti-Spyware profiles to protect against:

- Spyware downloads and installations
- Command-and-control (C2) traffic
- Data exfiltration attempts
- Known malicious sites and patterns

### [Decryption Profile](decryption_profile.md)

Manage SSL/TLS Decryption profiles to:

- Control encrypted traffic inspection
- Define certificate validation settings
- Configure SSL/TLS protocol settings
- Manage trusted certificates

### [DNS Security Profile](dns_security_profile.md)

Configure DNS Security profiles to protect against:

- DNS tunneling
- Domain generation algorithms (DGA)
- Fast-flux DNS attacks
- Known malicious domains

### [URL Categories](url_categories.md)

Manage URL Categories to:

- Create custom URL categories
- Define custom URL lists
- Override default category settings
- Apply granular policy control

### [Vulnerability Protection Profile](vulnerability_protection_profile.md)

Manage Vulnerability Protection profiles to:

- Protect against known CVEs
- Block exploit attempts
- Prevent buffer overflows
- Protect against code execution attempts

### [Wildfire Antivirus Profile](wildfire_antivirus.md)

Configure WildFire and Antivirus profiles for:

- Real-time malware analysis
- Zero-day threat protection
- Known malware blocking
- File type controls

## Common Features

All configuration objects provide standard CRUD operations:

- **Create**: Add new security profiles or rules
- **Read**: Retrieve existing configurations
- **Update**: Modify existing profiles or rules
- **Delete**: Remove unwanted configurations
- **List**: Enumerate and filter configurations

Additional features include:

- Pagination support for large collections
- Filtering capabilities
- Container-aware operations (folder/device/snippet)
- Validation of configuration parameters

## Usage Pattern

All configuration objects follow a consistent pattern:

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize the client using unified interface
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Define your intended object as a Python dictionary
sec_rule_dictionary = {
   "name": "test-rule",
   "folder": "Texas",
   "source": ["any"],
   "destination": ["any"],
   "application": ["web-browsing"],
   "service": ["application-default"],
   "action": "allow"
}

# Perform operations using the unified client
result = client.security_rule.create(sec_rule_dictionary)
print(f"Created security rule with ID: {result.id}")
```

</div>

You can also use the traditional approach:

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.security import SecurityRule  # Or other config object

# Initialize the client
api_client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create configuration object instance
security_rule = SecurityRule(api_client)

# Define your intended object as a Python dictionary
sec_rule_dictionary = {
   "name": "test-rule",
   "folder": "Texas",
   "source": ["any"],
   "destination": ["any"],
   "application": ["web-browsing"],
   "service": ["application-default"],
   "action": "allow"
}

# Perform operations
result = security_rule.create(sec_rule_dictionary)
print(f"Created security rule with ID: {result.id}")
```

</div>

## Related Documentation

- [Security Models](../../models/security_services/index.md)
- [API Client](../../client.md)
- [Operations](../../models/operations/jobs.md)

Select a configuration object above to view detailed documentation, including methods, parameters, and examples.
