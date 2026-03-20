# URL Access Profile Models

## Overview

The URL Access Profile models provide a structured way to manage URL access profiles in Palo Alto Networks' Strata Cloud Manager.
These models support defining URL filtering policies with category-based actions (alert, allow, block, continue, redirect),
credential enforcement settings, and logging options. Profiles can be defined in folders, snippets, or devices. The models
handle validation of inputs and outputs when interacting with the SCM API.

## Models

The module provides the following Pydantic models:

- `URLAccessProfileBaseModel`: Base model with fields common to all profile operations
- `URLAccessProfileCreateModel`: Model for creating new URL access profiles
- `URLAccessProfileUpdateModel`: Model for updating existing URL access profiles
- `URLAccessProfileResponseModel`: Response model for URL access profile operations
- `CredentialEnforcement`: Model for credential enforcement settings
- `CredentialEnforcementMode`: Model for credential enforcement mode configuration

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### URLAccessProfileBaseModel

| Attribute                | Type                     | Required | Default  | Description                                             |
|--------------------------|--------------------------|----------|----------|---------------------------------------------------------|
| name                     | str                      | Yes      | None     | Profile name                                            |
| description              | str                      | No       | None     | Description of the profile. Max 255 chars               |
| alert                    | List[str]                | No       | None     | URL categories for alert action                         |
| allow                    | List[str]                | No       | None     | URL categories for allow action                         |
| block                    | List[str]                | No       | None     | URL categories for block action                         |
| continue_                | List[str]                | No       | None     | URL categories for continue action (alias: `continue`)  |
| redirect                 | List[str]                | No       | None     | URL categories for redirect action                      |
| cloud_inline_cat         | bool                     | No       | None     | Enable cloud inline categorization                      |
| local_inline_cat         | bool                     | No       | None     | Enable local inline categorization                      |
| credential_enforcement   | CredentialEnforcement    | No       | None     | Credential enforcement settings                         |
| mlav_category_exception  | List[str]                | No       | None     | MLAV category exceptions                                |
| log_container_page_only  | bool                     | No       | None     | Log container page only                                 |
| log_http_hdr_referer     | bool                     | No       | None     | Log HTTP header referer                                 |
| log_http_hdr_user_agent  | bool                     | No       | None     | Log HTTP header user agent                              |
| log_http_hdr_xff         | bool                     | No       | None     | Log HTTP header X-Forwarded-For                         |
| safe_search_enforcement  | bool                     | No       | None     | Enable safe search enforcement                          |
| folder                   | str                      | No**     | None     | Folder location. Max 64 chars                           |
| snippet                  | str                      | No**     | None     | Snippet location. Max 64 chars                          |
| device                   | str                      | No**     | None     | Device location. Max 64 chars                           |

\** Exactly one container (folder/snippet/device) must be provided for create operations

!!! note
    The `continue_` field uses a Python-safe name because `continue` is a reserved keyword in Python. The field
    has an alias of `"continue"`, so when passing data as a dictionary you can use either `"continue_"` or
    `"continue"` as the key. When serializing the model (e.g., for API requests), the alias `"continue"` is used.

### URLAccessProfileCreateModel

Inherits all fields from `URLAccessProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### URLAccessProfileUpdateModel

Extends `URLAccessProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

### URLAccessProfileResponseModel

Extends `URLAccessProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

The response model uses `extra="ignore"` configuration instead of `extra="forbid"`, allowing it to accept additional
fields returned by the API without raising validation errors.

## Component Models

### CredentialEnforcement

Defines the credential enforcement settings for a URL access profile. Controls how the system handles credential
submissions to websites based on URL categories.

| Attribute    | Type                      | Required | Default  | Description                                             |
|--------------|---------------------------|----------|----------|---------------------------------------------------------|
| alert        | List[str]                 | No       | None     | URL categories for alert action on credential submission |
| allow        | List[str]                 | No       | None     | URL categories for allow action on credential submission |
| block        | List[str]                 | No       | None     | URL categories for block action on credential submission |
| continue_    | List[str]                 | No       | None     | URL categories for continue action (alias: `continue`)   |
| log_severity | str                       | No       | "medium" | Log severity level for credential enforcement events    |
| mode         | CredentialEnforcementMode | No       | None     | Credential enforcement mode configuration               |

### CredentialEnforcementMode

Defines the mode configuration for credential enforcement. Exactly one mode should typically be configured.

| Attribute          | Type        | Required | Default | Description                          |
|--------------------|-------------|----------|---------|--------------------------------------|
| disabled           | Dict        | No       | None    | Disabled mode (empty dict `{}`)      |
| domain_credentials | Dict        | No       | None    | Domain credentials mode (empty dict) |
| ip_user            | Dict        | No       | None    | IP user mode (empty dict)            |
| group_mapping      | str         | No       | None    | Group mapping mode (string value)    |

## Exceptions

The URL Access Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When container field pattern validation fails
    - When field length limits are exceeded (description max 255, container max 64)

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security import URLAccessProfileCreateModel

# Error: multiple containers specified
try:
    profile = URLAccessProfileCreateModel(
        name="invalid-profile",
        folder="Texas",
        device="fw01",  # Can't specify both folder and device
        block=["malware", "phishing"]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    profile = URLAccessProfileCreateModel(
        name="invalid-profile",
        block=["malware", "phishing"]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Using the Continue Field Alias

The `continue_` field supports the alias `"continue"` for use in dictionary data:

```python
from scm.models.security import URLAccessProfileCreateModel

# Using the alias in dictionary form
profile = URLAccessProfileCreateModel(
    name="url-profile",
    folder="Texas",
    block=["malware"],
    **{"continue": ["streaming-media", "social-networking"]}
)

# Using the Python-safe name directly
profile = URLAccessProfileCreateModel(
    name="url-profile",
    folder="Texas",
    block=["malware"],
    continue_=["streaming-media", "social-networking"]
)
```

## Usage Examples

### Creating a Basic Profile

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
profile_dict = {
    "name": "basic-url-filtering",
    "description": "Basic URL filtering profile",
    "folder": "Texas",
    "block": ["malware", "phishing", "command-and-control"],
    "alert": ["unknown", "newly-registered-domain"],
    "allow": ["business-and-economy", "technology"]
}

response = client.url_access_profile.create(profile_dict)
print(f"Created profile: {response.name}")
```

### Creating a Profile with Credential Enforcement

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create the profile with credential enforcement using dictionary
credential_config = {
    "name": "credential-protection",
    "description": "URL profile with credential enforcement",
    "folder": "Texas",
    "block": ["malware", "phishing"],
    "alert": ["unknown"],
    "allow": ["business-and-economy"],
    "continue": ["social-networking"],
    "credential_enforcement": {
        "mode": {
            "domain_credentials": {}
        },
        "block": ["malware", "phishing"],
        "alert": ["unknown"],
        "log_severity": "high"
    }
}

response = client.url_access_profile.create(credential_config)
print(f"Created profile with credential enforcement: {response.name}")
```

### Creating a Profile with Logging and Inline Categorization

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create profile with full logging and categorization
logging_config = {
    "name": "full-logging-url-profile",
    "description": "URL profile with comprehensive logging",
    "folder": "Texas",
    "block": ["malware", "phishing", "command-and-control"],
    "alert": ["unknown", "newly-registered-domain"],
    "allow": ["business-and-economy"],
    "cloud_inline_cat": True,
    "local_inline_cat": True,
    "safe_search_enforcement": True,
    "log_container_page_only": False,
    "log_http_hdr_referer": True,
    "log_http_hdr_user_agent": True,
    "log_http_hdr_xff": True
}

response = client.url_access_profile.create(logging_config)
print(f"Created profile: {response.name}")
print(f"Cloud inline categorization: {response.cloud_inline_cat}")
print(f"Safe search enforcement: {response.safe_search_enforcement}")
```

### Updating a Profile

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing profile
existing = client.url_access_profile.fetch(name="basic-url-filtering", folder="Texas")

# Modify attributes using dot notation
existing.description = "Updated URL filtering profile"
existing.block = ["malware", "phishing", "command-and-control", "grayware"]
existing.safe_search_enforcement = True

# Pass modified object to update()
updated = client.url_access_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

### Listing and Filtering Profiles

```python
# List all URL access profiles in a folder
all_profiles = client.url_access_profile.list(folder="Texas")
print(f"Found {len(all_profiles)} profiles")

# Process results
for profile in all_profiles:
    print(f"Profile: {profile.name}")
    if profile.block:
        print(f"  Blocked categories: {profile.block}")
    if profile.allow:
        print(f"  Allowed categories: {profile.allow}")
    if profile.alert:
        print(f"  Alert categories: {profile.alert}")
    if profile.credential_enforcement:
        print(f"  Credential enforcement: enabled")
```
