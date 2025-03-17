# Mobile Agent Data Models

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Common Model Patterns](#common-model-patterns)
4. [Available Models](#available-models)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)

## Overview

The Strata Cloud Manager SDK uses Pydantic models for data validation and serialization for Mobile Agent related resources. These models ensure that the data being sent to and received from the Strata Cloud Manager API adheres to the expected structure and constraints.

## Model Types

The Mobile Agent models follow the standard pattern where applicable:

- **Create Models**: Used when creating new resources (`{Object}CreateModel`)
- **Update Models**: Used when updating existing resources (`{Object}UpdateModel`)
- **Response Models**: Used when parsing data retrieved from the API (`{Object}ResponseModel`)
- **Base Models**: Common shared attributes for related models (`{Object}BaseModel`)

Note that some resources, like Agent Versions, are read-only and only have response models.

## Common Model Patterns

Mobile Agent models share common patterns:

- Container validation (folder/snippet/device)
- String length and pattern validation
- Data type validation and conversion
- Required field enforcement

## Available Models

- [Authentication Settings Models](auth_settings_models.md) - Models for GlobalProtect authentication rules
- [Agent Version Models](agent_versions_models.md) - Models for GlobalProtect agent version information

## Usage Examples

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient
from scm.models.mobile_agent.auth_settings import (
    AuthSettingsCreateModel,
    OperatingSystem
)

# Initialize client
client = ScmClient(
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
result = client.auth_settings.create(auth_dict)

# List and filter agent versions
agent_versions = client.agent_versions.list()
windows_versions = [v for v in agent_versions if "win" in v.lower()]
print(f"Windows versions: {windows_versions}")
```

</div>

## Best Practices

1. **Model Validation**
   - Always validate input data with models before sending to the API
   - Handle validation errors appropriately
   - Use model_dump(exclude_unset=True) to avoid sending default values

2. **Error Handling**
   - Catch and handle ValueError exceptions from model validation
   - Implement proper error messages for validation failures
   - Validate model data before executing API calls

Select a model from the available models above for detailed documentation on specific model attributes and validation rules.
