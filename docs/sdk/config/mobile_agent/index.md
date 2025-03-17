# Mobile Agent Configuration Objects

## Table of Contents

1. [Overview](#overview)
2. [Available Configuration Objects](#available-configuration-objects)
3. [Common Features](#common-features)
4. [Usage Examples](#usage-examples)

## Overview

This section covers the Mobile Agent configuration objects provided by the Palo Alto Networks Strata Cloud Manager SDK. These configuration objects correspond to resources related to GlobalProtect mobile VPN services in the Strata Cloud Manager.

## Available Configuration Objects

- [Authentication Settings](auth_settings.md) - Configuration for GlobalProtect authentication based on operating system
- [Agent Versions](agent_versions.md) - Available GlobalProtect agent versions (read-only)

## Common Features

All configuration objects provide standard operations where supported:

- Read existing objects
- List and filter objects with pagination support

These objects enforce:

- Data validation with detailed error messages
- Consistent API patterns across object types

## Usage Examples

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# List all authentication settings
auth_settings = client.auth_settings.list()
for setting in auth_settings:
    print(f"Auth Setting: {setting.name}, OS: {setting.os}")

# Get available agent versions
versions = client.agent_versions.list()
print(f"Available agent versions: {versions}")

# Filter by version
filtered_versions = client.agent_versions.list(version="5.3")
print(f"Filtered versions: {filtered_versions}")
```

</div>

Select an object from the list above to view detailed documentation, including methods, parameters, and examples.
