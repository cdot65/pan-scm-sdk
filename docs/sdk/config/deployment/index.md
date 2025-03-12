# Deployment Configuration Objects

## Table of Contents

1. [Overview](#overview)
2. [Available Deployment Objects](#available-deployment-objects)
3. [Common Features](#common-features)
4. [Usage Example](#usage-example)

## Overview

This section covers the configuration of SASE deployments provided by the Palo Alto Networks Strata Cloud Manager SDK. Each configuration object corresponds to a resource in the Strata Cloud Manager and provides methods for CRUD (Create, Read, Update, Delete) operations.

## Available Deployment Objects

- [Remote Networks](remote_networks.md) - Configure remote network connections for Prisma Access
- [Service Connections](service_connections.md) - Configure service connections to cloud service providers

## Common Features

All deployment configuration objects provide standard operations:

- Create new deployments
- Read existing deployment configurations
- Update deployment properties
- Delete deployments
- List and filter deployments with pagination support

The deployment objects also enforce:

- Container validation (folder/device/snippet)
- Data validation with detailed error messages
- Consistent API patterns across all deployment types

## Usage Example

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

# Create a remote network
client.remote_networks.create({
   "name": "branch-office-nyc",
   "region": "us-east-1",
   "spn_name": "Service",
   "folder": "Remote Networks",
   "protocol": {
      "ipsec": {
         "auth_type": "pre-shared-key",
         "pre_shared_key": "your-pre-shared-key"
      }
   },
   "subnets": ["10.1.0.0/16"]
})

# List remote networks
remote_networks = client.remote_networks.list(folder="Remote Networks")

# Print the results
for network in remote_networks:
   print(f"Remote Network: {network.name}, Region: {network.region}")
```

</div>

Select an object from the list above to view detailed documentation, including methods, parameters, and examples.
