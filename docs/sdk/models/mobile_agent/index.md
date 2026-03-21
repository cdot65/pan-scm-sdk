# Mobile Agent Models

Data models for GlobalProtect mobile agent resources in Strata Cloud Manager.

## Overview

The Mobile Agent models provide Pydantic-based data validation and serialization for GlobalProtect mobile agent resources. These models ensure that data sent to and received from the Strata Cloud Manager API adheres to the expected structure and constraints.

Key model patterns:

- Container validation (folder/snippet/device)
- String length and pattern validation
- Data type validation and conversion
- Required field enforcement

!!! note
    Some resources, like Agent Versions, are read-only and only have response models.

## Available Models

- [Authentication Settings Models](auth_settings_models.md) - Models for GlobalProtect authentication rules
- [Agent Version Models](agent_versions_models.md) - Models for GlobalProtect agent version information

## Usage Examples

```python
from scm.client import Scm
from scm.models.mobile_agent.auth_settings import (
    AuthSettingsCreateModel,
    OperatingSystem
)

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create an authentication setting using a model
auth_setting = AuthSettingsCreateModel(
   name="windows-auth",
   authentication_profile="windows-profile",
   os=OperatingSystem.WINDOWS,
   user_credential_or_client_cert_required=True,
   folder="Mobile Users"
)

# Convert the model to a dictionary for the API call
auth_dict = auth_setting.model_dump(exclude_unset=True)
result = client.auth_setting.create(auth_dict)

# List and filter agent versions
agent_versions = client.agent_version.list()
windows_versions = [v for v in agent_versions if "win" in v.lower()]
print(f"Windows versions: {windows_versions}")
```
