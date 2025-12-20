# GlobalProtect Authentication Settings Models

## Overview {#Overview}

The GlobalProtect Authentication Settings models provide a structured way to manage authentication settings for mobile users in Palo Alto Networks' Strata Cloud Manager. These models support different operating system configurations and authentication preferences. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `AuthSettingsBaseModel`: Base model with fields common to all authentication settings operations
- `AuthSettingsCreateModel`: Model for creating new authentication settings
- `AuthSettingsUpdateModel`: Model for updating existing authentication settings
- `AuthSettingsResponseModel`: Response model for authentication settings operations
- `AuthSettingsMoveModel`: Model for moving/reordering authentication settings
- `OperatingSystem`: Enum for available operating systems
- `MovePosition`: Enum for move position options

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute                                 | Type              | Required | Default | Description                                                                  |
|-------------------------------------------|-------------------|----------|---------|------------------------------------------------------------------------------|
| name                                      | str               | Yes      | None    | Name of the authentication settings. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
| authentication_profile                    | str               | Yes      | None    | The authentication profile to use                                            |
| os                                        | OperatingSystem   | No       | Any     | The operating system this authentication setting applies to                   |
| user_credential_or_client_cert_required   | bool              | No       | None    | Whether user credentials or client certificate is required                   |
| folder                                    | str               | Yes*     | None    | Must be "Mobile Users" for all operations                                    |

\* Required for create operations, optional for update

## Enumerations

### OperatingSystem

| Value        | Description                   |
|--------------|-------------------------------|
| ANY          | Any operating system          |
| ANDROID      | Android devices               |
| BROWSER      | Browser based access          |
| CHROME       | Chrome OS devices             |
| IOT          | Internet of Things devices    |
| LINUX        | Linux systems                 |
| MAC          | macOS systems                 |
| SATELLITE    | Satellite systems             |
| WINDOWS      | Windows systems               |
| WINDOWS_UWP  | Windows UWP applications      |
| IOS          | iOS devices                   |

### MovePosition

| Value        | Description                                |
|--------------|--------------------------------------------|
| BEFORE       | Move settings before a target setting      |
| AFTER        | Move settings after a target setting       |
| TOP          | Move settings to the top of the list       |
| BOTTOM       | Move settings to the bottom of the list    |

## Exceptions

The Authentication Settings models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When the folder value is not "Mobile Users"
    - When folder is not provided for create operations
    - For move operations:
      - When destination is not provided for BEFORE/AFTER positions
      - When destination is provided for TOP/BOTTOM positions

## Model Validators

### Folder Validation

The models enforce that the folder must be "Mobile Users":

```python
# This will raise a validation error
from scm.models.mobile_agent import AuthSettingsCreateModel

# Error: invalid folder value
try:
    settings = AuthSettingsCreateModel(
        name="windows-auth",
        authentication_profile="windows-profile",
        os="Windows",
        folder="Invalid"  # Must be "Mobile Users"
    )
except ValueError as e:
    print(e)  # "Folder must be 'Mobile Users' for GlobalProtect Authentication Settings"
```

### Container Validation for Create Model

For create operations, the folder field is required:

```python
# This will raise a validation error
try:
    settings = AuthSettingsCreateModel(
        name="windows-auth",
        authentication_profile="windows-profile",
        os="Windows"
        # Missing required folder field
    )
except ValueError as e:
    print(e)  # "Folder is required for GlobalProtect Authentication Settings"
```

### Move Operation Validation

The move model enforces validation for destination field based on the move position:

```python
# Missing destination for BEFORE position
from scm.models.mobile_agent import AuthSettingsMoveModel

try:
    move_model = AuthSettingsMoveModel(
        name="windows-auth",
        where="before"
        # Missing required destination
    )
except ValueError as e:
    print(e)  # "Destination is required when where is 'before' or 'after'"

# Providing destination for TOP position
try:
    move_model = AuthSettingsMoveModel(
        name="windows-auth",
        where="top",
        destination="linux-auth"  # Not allowed for TOP position
    )
except ValueError as e:
    print(e)  # "Destination should not be provided when where is 'top' or 'bottom'"
```

## Usage Examples

### Creating Authentication Settings

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
auth_dict = {
    "name": "windows-auth",
    "authentication_profile": "windows-profile",
    "os": "Windows",
    "user_credential_or_client_cert_required": True,
    "folder": "Mobile Users"
}

response = client.auth_setting.create(auth_dict)
print(f"Created authentication settings: {response.name}")

# Using model directly
from scm.models.mobile_agent import AuthSettingsCreateModel

auth_obj = AuthSettingsCreateModel(
    name="ios-auth",
    authentication_profile="mobile-profile",
    os="iOS",
    user_credential_or_client_cert_required=True,
    folder="Mobile Users"
)

payload = auth_obj.model_dump(exclude_unset=True)
response = client.auth_setting.create(payload)
```

### Creating Authentication Settings for Multiple Operating Systems

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create settings for Android
android_auth = {
    "name": "android-auth",
    "authentication_profile": "android-profile",
    "os": "Android",
    "user_credential_or_client_cert_required": True,
    "folder": "Mobile Users"
}

response = client.auth_setting.create(android_auth)

# Create default settings for any OS
default_auth = {
    "name": "default-auth",
    "authentication_profile": "default-profile",
    "os": "Any",  # Default value
    "user_credential_or_client_cert_required": True,
    "folder": "Mobile Users"
}

response = client.auth_setting.create(default_auth)
```

### Updating Authentication Settings

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing authentication settings
existing = client.auth_setting.fetch(name="windows-auth", folder="Mobile Users")

# Modify attributes using dot notation
existing.name = "windows-auth-updated"
existing.authentication_profile = "updated-profile"
existing.user_credential_or_client_cert_required = False

# Pass modified object to update()
response = client.auth_setting.update(existing.id, existing.model_dump(exclude_unset=True))
print(f"Updated authentication settings: {response.name}")
```

### Moving Authentication Settings

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Move settings to top of evaluation order
move_to_top = {
    "name": "windows-auth",
    "where": "top"
}
client.auth_setting.move(move_to_top)

# Move settings before another setting
move_before = {
    "name": "ios-auth",
    "where": "before",
    "destination": "android-auth"
}
client.auth_setting.move(move_before)
```
