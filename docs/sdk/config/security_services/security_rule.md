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

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import SecurityRule

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize SecurityRule object
security_rules = SecurityRule(client)
```

</div>

## Usage Examples

### Creating Security Rules

<div class="termy">

<!-- termynal -->

```python
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
basic_rule = security_rules.create(allow_rule, rulebase="pre")

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
profile_rule = security_rules.create(secure_rule, rulebase="pre")
```

</div>

### Retrieving Security Rules

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
rule = security_rules.fetch(
    name="allow-web",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")

# Get by ID
rule_by_id = security_rules.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Applications: {rule_by_id.application}")
```

</div>

### Updating Security Rules

<div class="termy">

<!-- termynal -->

```python
# Fetch existing rule
existing_rule = security_rules.fetch(
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
updated_rule = security_rules.update(existing_rule, rulebase="pre")
```

</div>

### Listing Security Rules

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_rules = security_rules.list(
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

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "rulebase": "pre",
    "from_": ["trust"],
    "to_": ["untrust"],
    "tag": ["Production"]
}

# List with filters as kwargs
filtered_rules = security_rules.list(**list_params)
```

</div>

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

<div class="termy">

<!-- termynal -->

```python
# Only return security_rules defined exactly in 'Texas'
exact_security_rules = security_rules.list(
    folder='Texas',
    exact_match=True
)

for app in exact_security_rules:
    print(f"Exact match: {app.name} in {app.folder}")

# Exclude all security_rules from the 'All' folder
no_all_security_rules = security_rules.list(
    folder='Texas',
    exclude_folders=['All']
)

for app in no_all_security_rules:
    assert app.folder != 'All'
    print(f"Filtered out 'All': {app.name}")

# Exclude security_rules that come from 'default' snippet
no_default_snippet = security_rules.list(
    folder='Texas',
    exclude_snippets=['default']
)

for app in no_default_snippet:
    assert app.snippet != 'default'
    print(f"Filtered out 'default' snippet: {app.name}")

# Exclude security_rules associated with 'DeviceA'
no_deviceA = security_rules.list(
    folder='Texas',
    exclude_devices=['DeviceA']
)

for app in no_deviceA:
    assert app.device != 'DeviceA'
    print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = security_rules.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)

for app in combined_filters:
    print(f"Combined filters result: {app.name} in {app.folder}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

<div class="termy">

<!-- termynal -->

```python
# Initialize the SecurityRule object with a custom max_limit
# This will retrieve up to 4321 objects per API call, up to the API limit of 5000.
rule_client = SecurityRule(api_client=client, max_limit=4321)

# Now when we call list(), it will use the specified max_limit for each request
# while auto-paginating through all available objects.
all_rules = rule_client.list(folder='Texas', rulebase='pre')

# 'all_rules' contains all objects from 'Texas', fetched in chunks of up to 4321 at a time.
```

</div>

### Moving Security Rules

<div class="termy">

<!-- termynal -->

```python
# Move rule to top of rulebase
top_move = {
    "destination": "top",
    "rulebase": "pre"
}
security_rules.move(rule.id, top_move)

# Move rule before another rule
before_move = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
security_rules.move(rule.id, before_move)

# Move rule after another rule
after_move = {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
security_rules.move(rule.id, after_move)
```

</div>

### Deleting Security Rules

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
rule_id = "123e4567-e89b-12d3-a456-426655440000"
security_rules.delete(rule_id, rulebase="pre")
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated security rules",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = security_rules.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = security_rules.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = security_rules.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
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

    # Create the rule
    new_rule = security_rules.create(rule_config, rulebase="pre")

    # Move the rule
    move_config = {
        "destination": "top",
        "rulebase": "pre"
    }
    security_rules.move(new_rule.id, move_config)

    # Commit changes
    result = security_rules.commit(
        folders=["Texas"],
        description="Added test rule",
        sync=True
    )

    # Check job status
    status = security_rules.get_job_status(result.job_id)

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

</div>

## Best Practices

1. **Rule Organization**
    - Use descriptive rule names
    - Order rules by specificity
    - Group related rules together
    - Document rule purposes
    - Use consistent naming conventions

2. **Security Profiles**
    - Apply appropriate security profiles
    - Use profile groups when possible
    - Monitor profile impacts
    - Update profiles regularly
    - Document profile choices

3. **Logging and Monitoring**
    - Enable appropriate logging
    - Use log forwarding profiles
    - Monitor rule hits
    - Track rule changes
    - Audit rule effectiveness

4. **Performance**
    - Optimize rule order
    - Use specific sources/destinations
    - Minimize rule count
    - Monitor rule processing
    - Clean up unused rules

5. **Change Management**
    - Test rules before deployment
    - Document all changes
    - Use proper commit messages
    - Monitor commit status
    - Maintain rule backups

## Full Script Examples

Refer to
the [security_rule.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/security_rule.py).

## Related Models

- [SecurityRuleCreateModel](../../models/security_services/security_rule_models.md#Overview)
- [SecurityRuleUpdateModel](../../models/security_services/security_rule_models.md#Overview)
- [SecurityRuleResponseModel](../../models/security_services/security_rule_models.md#Overview)
- [SecurityRuleMoveModel](../../models/security_services/security_rule_models.md#Overview)
