# Authentication Rule Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Authentication Rule Model Attributes](#authentication-rule-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Authentication Rules](#creating-authentication-rules)
    - [Retrieving Authentication Rules](#retrieving-authentication-rules)
    - [Updating Authentication Rules](#updating-authentication-rules)
    - [Listing Authentication Rules](#listing-authentication-rules)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Moving Authentication Rules](#moving-authentication-rules)
    - [Deleting Authentication Rules](#deleting-authentication-rules)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `AuthenticationRule` class provides functionality to manage authentication rules in Palo Alto Networks' Strata Cloud
Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting
authentication rules that enforce identity-based policy for traffic flowing between zones, addresses, and users. The
service interacts with the `/config/identity/v1/authentication-rules` API endpoint.

## Core Methods

| Method     | Description                          | Parameters                                       | Return Type                             |
|------------|--------------------------------------|--------------------------------------------------|-----------------------------------------|
| `create()` | Creates a new authentication rule    | `data: Dict[str, Any]`, `rulebase: str`          | `AuthenticationRuleResponseModel`       |
| `get()`    | Retrieves a rule by ID              | `object_id: str`, `rulebase: str`                | `AuthenticationRuleResponseModel`       |
| `update()` | Updates an existing rule            | `rule: AuthenticationRuleUpdateModel`            | `AuthenticationRuleResponseModel`       |
| `delete()` | Deletes a rule                      | `object_id: str`, `rulebase: str`                | `None`                                  |
| `list()`   | Lists rules with filtering          | `folder: str`, `rulebase: str`                   | `List[AuthenticationRuleResponseModel]` |
| `fetch()`  | Gets rule by name and container     | `name: str`, `folder: str`                       | `AuthenticationRuleResponseModel`       |
| `move()`   | Moves rule within rulebase          | `rule_id: UUID`, `data: Dict[str, Any]`          | `None`                                  |

## Authentication Rule Model Attributes

| Attribute                    | Type                           | Required | Default      | Description                                              |
|------------------------------|--------------------------------|----------|--------------|----------------------------------------------------------|
| `name`                       | str                            | Yes      | None         | Name of rule. Pattern: `^[a-zA-Z0-9_ \.-]+$`             |
| `id`                         | UUID                           | Yes*     | None         | Unique identifier (*response/update only)                |
| `disabled`                   | bool                           | No       | False        | Whether the rule is disabled                             |
| `description`                | str                            | No       | None         | Rule description                                         |
| `tag`                        | List[str]                      | No       | []           | Associated tags                                          |
| `from_`                      | List[str]                      | No       | ["any"]      | Source zones                                             |
| `source`                     | List[str]                      | No       | ["any"]      | Source addresses                                         |
| `negate_source`              | bool                           | No       | False        | Negate source addresses                                  |
| `source_user`                | List[str]                      | No       | ["any"]      | Source users/groups                                      |
| `source_hip`                 | List[str]                      | No       | ["any"]      | Source Host Integrity Profiles                           |
| `to_`                        | List[str]                      | No       | ["any"]      | Destination zones                                        |
| `destination`                | List[str]                      | No       | ["any"]      | Destination addresses                                    |
| `negate_destination`         | bool                           | No       | False        | Negate destination addresses                             |
| `destination_hip`            | List[str]                      | No       | ["any"]      | Destination Host Integrity Profiles                      |
| `service`                    | List[str]                      | No       | ["any"]      | Allowed services                                         |
| `category`                   | List[str]                      | No       | ["any"]      | URL categories                                           |
| `authentication_enforcement` | str                            | No       | None         | Authentication profile name                              |
| `hip_profiles`               | List[str]                      | No       | None         | Source Host Integrity Profiles                           |
| `group_tag`                  | str                            | No       | None         | Group tag                                                |
| `timeout`                    | int                            | No       | None         | Auth session timeout in minutes (1-1440)                 |
| `log_setting`                | str                            | No       | None         | Log forwarding profile                                   |
| `log_authentication_timeout` | bool                           | No       | False        | Log authentication timeouts                              |
| `rulebase`                   | AuthenticationRuleRulebase     | No       | None         | Which rulebase (pre/post)                                |
| `folder`                     | str                            | No**     | None         | Folder location. Max 64 chars                            |
| `snippet`                    | str                            | No**     | None         | Snippet location. Max 64 chars                           |
| `device`                     | str                            | No**     | None         | Device location. Max 64 chars                            |

\* Only required for response and update models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## Exceptions

| Exception                    | HTTP Code | Description                 |
|------------------------------|-----------|-----------------------------|
| `InvalidObjectError`         | 400       | Invalid rule data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters |
| `NameNotUniqueError`         | 409       | Rule name already exists    |
| `ObjectNotPresentError`      | 404       | Rule not found              |
| `ReferenceNotZeroError`      | 409       | Rule still referenced       |
| `AuthenticationError`        | 401       | Authentication failed       |
| `ServerError`                | 500       | Internal server error       |

## Basic Configuration

The Authentication Rule service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Authentication Rule service directly through the client
# No need to create a separate AuthenticationRule instance
rules = client.authentication_rule
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.security import AuthenticationRule

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize AuthenticationRule object explicitly
rules = AuthenticationRule(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Authentication Rules

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Basic authentication rule with auth enforcement
basic_rule = {
    "name": "auth-web-traffic",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["internal-net"],
    "destination": ["any"],
    "service": ["service-http", "service-https"],
    "authentication_enforcement": "auth-profile-1",
    "log_authentication_timeout": True
}

# Create basic authentication rule
created_rule = client.authentication_rule.create(basic_rule, rulebase="pre")

# Authentication rule with timeout
timeout_rule = {
    "name": "auth-timeout-rule",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "service": ["application-default"],
    "authentication_enforcement": "auth-profile-2",
    "timeout": 60,
    "log_authentication_timeout": True,
    "log_setting": "detailed-logging"
}

# Create rule with timeout
timeout_created = client.authentication_rule.create(timeout_rule, rulebase="pre")

# Authentication rule with HIP profiles
hip_rule = {
    "name": "auth-hip-rule",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source_user": ["domain\\jsmith", "domain\\jdoe"],
    "source": ["any"],
    "destination": ["any"],
    "service": ["any"],
    "category": ["any"],
    "hip_profiles": ["hip-compliant", "hip-patched"],
    "authentication_enforcement": "strict-auth-profile",
    "group_tag": "compliance-group",
    "tag": ["Compliance", "HIP"]
}

# Create rule with HIP profiles
hip_created = client.authentication_rule.create(hip_rule, rulebase="pre")
```

### Retrieving Authentication Rules

```python
# Fetch by name and folder
rule = client.authentication_rule.fetch(
    name="auth-web-traffic",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")

# Get by ID
rule_by_id = client.authentication_rule.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Authentication enforcement: {rule_by_id.authentication_enforcement}")
```

### Updating Authentication Rules

```python
# Fetch existing rule
existing_rule = client.authentication_rule.fetch(
    name="auth-web-traffic",
    folder="Texas",
    rulebase="pre"
)

# Update attributes
existing_rule.description = "Updated authentication rule for web traffic"
existing_rule.timeout = 120
existing_rule.authentication_enforcement = "updated-auth-profile"
existing_rule.log_authentication_timeout = True

# Perform update
updated_rule = client.authentication_rule.update(existing_rule, rulebase="pre")
```

### Listing Authentication Rules

```python
# Pass filters directly into the list method
filtered_rules = client.authentication_rule.list(
    folder='Texas',
    rulebase='pre',
    service=['service-http', 'service-https']
)

# Process results
for rule in filtered_rules:
    print(f"Name: {rule.name}")
    print(f"Auth enforcement: {rule.authentication_enforcement}")
    print(f"Timeout: {rule.timeout}")

# Define filter parameters as a dictionary
list_params = {
    "folder": "Texas",
    "rulebase": "pre",
    "from_": ["trust"],
    "to_": ["untrust"],
    "tag": ["Compliance"]
}

# List with filters as kwargs
filtered_rules = client.authentication_rule.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `service`, `category`, and `tag`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return authentication rules defined exactly in 'Texas'
exact_rules = client.authentication_rule.list(
   folder='Texas',
   rulebase='pre',
   exact_match=True
)

for rule in exact_rules:
   print(f"Exact match: {rule.name} in {rule.folder}")

# Exclude all authentication rules from the 'All' folder
no_all_rules = client.authentication_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_folders=['All']
)

for rule in no_all_rules:
   assert rule.folder != 'All'
   print(f"Filtered out 'All': {rule.name}")

# Exclude authentication rules that come from 'default' snippet
no_default_snippet = client.authentication_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_snippets=['default']
)

for rule in no_default_snippet:
   assert rule.snippet != 'default'
   print(f"Filtered out 'default' snippet: {rule.name}")

# Exclude authentication rules associated with 'DeviceA'
no_deviceA = client.authentication_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_devices=['DeviceA']
)

for rule in no_deviceA:
   assert rule.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {rule.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.authentication_rule.list(
   folder='Texas',
   rulebase='pre',
   exact_match=True,
   exclude_folders=['All'],
   exclude_snippets=['default'],
   exclude_devices=['DeviceA']
)

for rule in combined_filters:
   print(f"Combined filters result: {rule.name} in {rule.folder}")
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
client.authentication_rule.max_limit = 4000

# List all rules - auto-paginates through results
all_rules = client.authentication_rule.list(folder='Texas', rulebase='pre')

# The rules are fetched in chunks according to the max_limit setting.
```

### Moving Authentication Rules

```python
# Move rule to top of rulebase
top_move = {
    "destination": "top",
    "rulebase": "pre"
}
client.authentication_rule.move(rule.id, top_move)

# Move rule before another rule
before_move = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
client.authentication_rule.move(rule.id, before_move)

# Move rule after another rule
after_move = {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
client.authentication_rule.move(rule.id, after_move)
```

### Deleting Authentication Rules

```python
# Delete by ID
rule_id = "123e4567-e89b-12d3-a456-426655440000"
client.authentication_rule.delete(rule_id, rulebase="pre")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated authentication rules",
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
    # Create rule configuration
    rule_config = {
        "name": "test-auth-rule",
        "folder": "Texas",
        "from_": ["trust"],
        "to_": ["untrust"],
        "source": ["internal-net"],
        "destination": ["any"],
        "service": ["application-default"],
        "authentication_enforcement": "auth-profile-1"
    }

    # Create the rule using the unified client interface
    new_rule = client.authentication_rule.create(rule_config, rulebase="pre")

    # Move the rule
    move_config = {
        "destination": "top",
        "rulebase": "pre"
    }
    client.authentication_rule.move(new_rule.id, move_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Texas"],
        description="Added authentication rule",
        sync=True
    )

    # Check job status directly from the client
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid rule data: {e.message}")
except NameNotUniqueError as e:
    print(f"Rule name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Rule not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Rule still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.authentication_rule`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Rule Organization**
    - Use descriptive rule names
    - Order rules by specificity
    - Group related rules together
    - Document rule purposes
    - Use consistent naming conventions

3. **Authentication Enforcement**
    - Apply appropriate authentication profiles
    - Set reasonable timeout values (1-1440 minutes)
    - Use HIP profiles for device compliance checks
    - Monitor authentication enforcement effectiveness
    - Document authentication profile choices

4. **Logging and Monitoring**
    - Enable `log_authentication_timeout` for timeout visibility
    - Use log forwarding profiles
    - Monitor rule hits
    - Track rule changes
    - Audit rule effectiveness

5. **Performance**
    - Optimize rule order
    - Use specific sources/destinations
    - Minimize rule count
    - Monitor rule processing
    - Clean up unused rules

6. **Change Management**
    - Test rules before deployment
    - Document all changes
    - Use proper commit messages
    - Monitor commit status
    - Maintain rule backups

## Full Script Examples

Refer to
the [authentication_rule.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security_services/authentication_rule.py).

## Related Models

- [AuthenticationRuleBaseModel](../../models/security_services/authentication_rule_models.md#Overview)
- [AuthenticationRuleCreateModel](../../models/security_services/authentication_rule_models.md#Overview)
- [AuthenticationRuleUpdateModel](../../models/security_services/authentication_rule_models.md#Overview)
- [AuthenticationRuleResponseModel](../../models/security_services/authentication_rule_models.md#Overview)
- [AuthenticationRuleMoveModel](../../models/security_services/authentication_rule_models.md#Overview)
- [AuthenticationRuleRulebase](../../models/security_services/authentication_rule_models.md#Overview)
- [AuthenticationRuleMoveDestination](../../models/security_services/authentication_rule_models.md#Overview)
