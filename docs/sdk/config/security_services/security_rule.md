# Security Rule Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Security Rule Model Attributes](#security-rule-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Security Rules](#creating-security-rules)
    - [Retrieving Security Rules](#retrieving-security-rules)
    - [Updating Security Rules](#updating-security-rules)
    - [Listing Security Rules](#listing-security-rules)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Moving Security Rules](#moving-security-rules)
    - [Deleting Security Rules](#deleting-security-rules)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `SecurityRule` class provides functionality to manage security rules in Palo Alto Networks' Strata Cloud Manager.
This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting security rules
that control traffic flow between zones, applications, and users.

## Core Methods

| Method     | Description                     | Parameters                              | Return Type                       |
|------------|---------------------------------|-----------------------------------------|-----------------------------------|
| `create()` | Creates a new security rule     | `data: Dict[str, Any]`, `rulebase: str` | `SecurityRuleResponseModel`       |
| `get()`    | Retrieves a rule by ID          | `object_id: str`, `rulebase: str`       | `SecurityRuleResponseModel`       |
| `update()` | Updates an existing rule        | `rule: SecurityRuleUpdateModel`         | `SecurityRuleResponseModel`       |
| `delete()` | Deletes a rule                  | `object_id: str`, `rulebase: str`       | `None`                            |
| `list()`   | Lists rules with filtering      | `folder: str`, `rulebase: str`          | `List[SecurityRuleResponseModel]` |
| `fetch()`  | Gets rule by name and container | `name: str`, `folder: str`              | `SecurityRuleResponseModel`       |
| `move()`   | Moves rule within rulebase      | `rule_id: UUID`, `data: Dict[str, Any]` | `None`                            |

## Security Rule Model Attributes

| Attribute         | Type                | Required | Description                                 |
|-------------------|---------------------|----------|---------------------------------------------|
| `name`            | str                 | Yes      | Name of rule (max 63 chars)                 |
| `id`              | UUID                | Yes*     | Unique identifier (*response only)          |
| `action`          | SecurityRuleAction  | Yes      | Rule action (allow, deny, etc.)             |
| `from_`           | List[str]           | Yes      | Source zones                                |
| `to_`             | List[str]           | Yes      | Destination zones                           |
| `source`          | List[str]           | Yes      | Source addresses                            |
| `destination`     | List[str]           | Yes      | Destination addresses                       |
| `application`     | List[str]           | Yes      | Allowed applications                        |
| `service`         | List[str]           | Yes      | Allowed services                            |
| `category`        | List[str]           | Yes      | URL categories                              |
| `profile_setting` | SecurityRuleProfile | No       | Security profile settings                   |
| `log_setting`     | str                 | No       | Log forwarding profile                      |
| `description`     | str                 | No       | Rule description                            |
| `disabled`        | bool                | No       | Rule enabled/disabled status                |
| `tag`             | List[str]           | No       | Associated tags                             |
| `folder`          | str                 | Yes**    | Folder location (**one container required)  |
| `snippet`         | str                 | Yes**    | Snippet location (**one container required) |
| `device`          | str                 | Yes**    | Device location (**one container required)  |

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

The Security Rule service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Security Rule service directly through the client
# No need to create a separate SecurityRule instance
rules = client.security_rule
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.security_services import SecurityRule

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize SecurityRule object explicitly
rules = SecurityRule(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Security Rules

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Basic allow rule configuration
allow_rule = {
    "name": "allow-web",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["internal-net"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "service": ["application-default"],
    "action": "allow",
    "log_end": True
}

# Create basic allow rule
basic_rule = client.security_rule.create(allow_rule, rulebase="pre")

# Security profile rule configuration
secure_rule = {
    "name": "secure-web",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["internal-net"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "service": ["application-default"],
    "profile_setting": {
        "group": ["best-practice"]
    },
    "action": "allow",
    "log_start": False,
    "log_end": True
}

# Create rule with security profiles
profile_rule = client.security_rule.create(secure_rule, rulebase="pre")
```

### Retrieving Security Rules

```python
# Fetch by name and folder
rule = client.security_rule.fetch(
    name="allow-web",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")

# Get by ID
rule_by_id = client.security_rule.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Applications: {rule_by_id.application}")
```

### Updating Security Rules

```python
# Fetch existing rule
existing_rule = client.security_rule.fetch(
    name="allow-web",
    folder="Texas",
    rulebase="pre"
)

# Update attributes
existing_rule.description = "Updated web access rule"
existing_rule.application = ["web-browsing", "ssl", "http2"]
existing_rule.profile_setting = {
    "group": ["strict-security"]
}

# Perform update
updated_rule = client.security_rule.update(existing_rule, rulebase="pre")
```

### Listing Security Rules

```python
# Pass filters directly into the list method
filtered_rules = client.security_rule.list(
    folder='Texas',
    rulebase='pre',
    action=['allow'],
    application=['web-browsing', 'ssl']
)

# Process results
for rule in filtered_rules:
    print(f"Name: {rule.name}")
    print(f"Action: {rule.action}")
    print(f"Applications: {rule.application}")

# Define filter parameters as a dictionary
list_params = {
    "folder": "Texas",
    "rulebase": "pre",
    "from_": ["trust"],
    "to_": ["untrust"],
    "tag": ["Production"]
}

# List with filters as kwargs
filtered_rules = client.security_rule.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return security rules defined exactly in 'Texas'
exact_rules = client.security_rule.list(
   folder='Texas',
   rulebase='pre',
   exact_match=True
)

for rule in exact_rules:
   print(f"Exact match: {rule.name} in {rule.folder}")

# Exclude all security rules from the 'All' folder
no_all_rules = client.security_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_folders=['All']
)

for rule in no_all_rules:
   assert rule.folder != 'All'
   print(f"Filtered out 'All': {rule.name}")

# Exclude security rules that come from 'default' snippet
no_default_snippet = client.security_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_snippets=['default']
)

for rule in no_default_snippet:
   assert rule.snippet != 'default'
   print(f"Filtered out 'default' snippet: {rule.name}")

# Exclude security rules associated with 'DeviceA'
no_deviceA = client.security_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_devices=['DeviceA']
)

for rule in no_deviceA:
   assert rule.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {rule.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.security_rule.list(
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
from scm.config.security_services import SecurityRule

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom SecurityRule instance with max_limit
security_rule_service = SecurityRule(client, max_limit=4321)
all_rules1 = security_rule_service.list(folder='Texas', rulebase='pre')

# Option 2: Use the unified client interface directly
# This will use the default max_limit (2500)
all_rules2 = client.security_rule.list(folder='Texas', rulebase='pre')

# Both options will auto-paginate through all available objects.
# The rules are fetched in chunks according to the max_limit.
```

### Moving Security Rules

```python
# Move rule to top of rulebase
top_move = {
    "destination": "top",
    "rulebase": "pre"
}
client.security_rule.move(rule.id, top_move)

# Move rule before another rule
before_move = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
client.security_rule.move(rule.id, before_move)

# Move rule after another rule
after_move = {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
client.security_rule.move(rule.id, after_move)
```

### Deleting Security Rules

```python
# Delete by ID
rule_id = "123e4567-e89b-12d3-a456-426655440000"
client.security_rule.delete(rule_id, rulebase="pre")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated security rules",
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
        "name": "test-rule",
        "folder": "Texas",
        "from_": ["trust"],
        "to_": ["untrust"],
        "source": ["internal-net"],
        "destination": ["any"],
        "application": ["web-browsing"],
        "service": ["application-default"],
        "action": "allow"
    }

    # Create the rule using the unified client interface
    new_rule = client.security_rule.create(rule_config, rulebase="pre")

    # Move the rule
    move_config = {
        "destination": "top",
        "rulebase": "pre"
    }
    client.security_rule.move(new_rule.id, move_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Texas"],
        description="Added test rule",
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
    - Use the unified client interface (`client.security_rule`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Rule Organization**
    - Use descriptive rule names
    - Order rules by specificity
    - Group related rules together
    - Document rule purposes
    - Use consistent naming conventions

3. **Security Profiles**
    - Apply appropriate security profiles
    - Use profile groups when possible
    - Monitor profile impacts
    - Update profiles regularly
    - Document profile choices

4. **Logging and Monitoring**
    - Enable appropriate logging
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
the [security_rule.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security_services/security_rule.py).

## Related Models

- [SecurityRuleCreateModel](../../models/security_services/security_rule_models.md#Overview)
- [SecurityRuleUpdateModel](../../models/security_services/security_rule_models.md#Overview)
- [SecurityRuleResponseModel](../../models/security_services/security_rule_models.md#Overview)
- [SecurityRuleMoveModel](../../models/security_services/security_rule_models.md#Overview)
