# Decryption Rule Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Decryption Rule Model Attributes](#decryption-rule-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Decryption Rules](#creating-decryption-rules)
    - [Retrieving Decryption Rules](#retrieving-decryption-rules)
    - [Updating Decryption Rules](#updating-decryption-rules)
    - [Listing Decryption Rules](#listing-decryption-rules)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Moving Decryption Rules](#moving-decryption-rules)
    - [Deleting Decryption Rules](#deleting-decryption-rules)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `DecryptionRule` class provides functionality to manage decryption rules in Palo Alto Networks' Strata Cloud Manager.
This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting decryption
rules that control SSL/TLS traffic inspection policies between zones, addresses, and users via the endpoint
`/config/security/v1/decryption-rules`.

## Core Methods

| Method     | Description                      | Parameters                                | Return Type                          |
|------------|----------------------------------|-------------------------------------------|--------------------------------------|
| `create()` | Creates a new decryption rule    | `data: Dict[str, Any]`, `rulebase: str`   | `DecryptionRuleResponseModel`        |
| `get()`    | Retrieves a rule by ID           | `object_id: str`, `rulebase: str`         | `DecryptionRuleResponseModel`        |
| `update()` | Updates an existing rule         | `rule: DecryptionRuleUpdateModel`         | `DecryptionRuleResponseModel`        |
| `delete()` | Deletes a rule                   | `object_id: str`, `rulebase: str`         | `None`                               |
| `list()`   | Lists rules with filtering       | `folder: str`, `rulebase: str`            | `List[DecryptionRuleResponseModel]`  |
| `fetch()`  | Gets rule by name and container  | `name: str`, `folder: str`               | `DecryptionRuleResponseModel`        |
| `move()`   | Moves rule within rulebase       | `rule_id: UUID`, `data: Dict[str, Any]`   | `None`                               |

## Decryption Rule Model Attributes

| Attribute            | Type                   | Required | Default      | Description                                              |
|----------------------|------------------------|----------|--------------|----------------------------------------------------------|
| `name`               | str                    | Yes      | None         | Name of rule. Pattern: `^[a-zA-Z0-9_ \.-]+$`            |
| `id`                 | UUID                   | Yes*     | None         | Unique identifier (*response/update only)                |
| `action`             | DecryptionRuleAction   | Yes      | None         | Rule action (decrypt/no-decrypt)                         |
| `disabled`           | bool                   | No       | False        | Whether the rule is disabled                             |
| `description`        | str                    | No       | None         | Rule description                                         |
| `tag`                | List[str]              | No       | []           | Associated tags                                          |
| `from_`              | List[str]              | No       | ["any"]      | Source zones                                             |
| `to_`                | List[str]              | No       | ["any"]      | Destination zones                                        |
| `source`             | List[str]              | No       | ["any"]      | Source addresses                                         |
| `destination`        | List[str]              | No       | ["any"]      | Destination addresses                                    |
| `source_user`        | List[str]              | No       | ["any"]      | Source users/groups                                      |
| `category`           | List[str]              | No       | ["any"]      | URL categories                                           |
| `service`            | List[str]              | No       | ["any"]      | Services                                                 |
| `source_hip`         | List[str]              | No       | ["any"]      | Source Host Integrity Profiles                           |
| `destination_hip`    | List[str]              | No       | ["any"]      | Destination Host Integrity Profiles                      |
| `negate_source`      | bool                   | No       | False        | Negate source addresses                                  |
| `negate_destination` | bool                   | No       | False        | Negate destination addresses                             |
| `profile`            | str                    | No       | None         | Decryption profile name                                  |
| `type`               | DecryptionRuleType     | No       | None         | Decryption type (ssl_forward_proxy/ssl_inbound_inspection) |
| `log_setting`        | str                    | No       | None         | Log forwarding profile                                   |
| `log_fail`           | bool                   | No       | None         | Log failed decryption events                             |
| `log_success`        | bool                   | No       | None         | Log successful decryption events                         |
| `rulebase`           | DecryptionRuleRulebase | No       | None         | Which rulebase (pre/post)                                |
| `folder`             | str                    | No**     | None         | Folder location. Max 64 chars                            |
| `snippet`            | str                    | No**     | None         | Snippet location. Max 64 chars                           |
| `device`             | str                    | No**     | None         | Device location. Max 64 chars                            |

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

The Decryption Rule service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Decryption Rule service directly through the client
# No need to create a separate DecryptionRule instance
rules = client.decryption_rule
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.security import DecryptionRule

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize DecryptionRule object explicitly
rules = DecryptionRule(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Decryption Rules

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Basic decrypt rule configuration
decrypt_rule = {
    "name": "decrypt-web-traffic",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["internal-net"],
    "destination": ["any"],
    "service": ["application-default"],
    "action": "decrypt",
    "log_success": True,
    "log_fail": True
}

# Create basic decrypt rule
basic_rule = client.decryption_rule.create(decrypt_rule, rulebase="pre")

# No-decrypt rule configuration
no_decrypt_rule = {
    "name": "no-decrypt-finance",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["finance-net"],
    "destination": ["any"],
    "category": ["financial-services"],
    "service": ["application-default"],
    "action": "no-decrypt",
    "description": "Exclude financial traffic from decryption"
}

# Create no-decrypt rule
bypass_rule = client.decryption_rule.create(no_decrypt_rule, rulebase="pre")

# Decrypt rule with SSL forward proxy type
ssl_forward_rule = {
    "name": "ssl-forward-proxy",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "service": ["application-default"],
    "action": "decrypt",
    "type": {
        "ssl_forward_proxy": {}
    },
    "log_success": True,
    "log_fail": True
}

# Create rule with SSL forward proxy type
forward_proxy_rule = client.decryption_rule.create(ssl_forward_rule, rulebase="pre")

# Decrypt rule with decryption profile
profile_rule = {
    "name": "decrypt-with-profile",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["internal-net"],
    "destination": ["any"],
    "service": ["application-default"],
    "action": "decrypt",
    "profile": "strict-decryption",
    "type": {
        "ssl_forward_proxy": {}
    },
    "log_success": True,
    "log_fail": True
}

# Create rule with decryption profile
profiled_rule = client.decryption_rule.create(profile_rule, rulebase="pre")
```

### Retrieving Decryption Rules

```python
# Fetch by name and folder
rule = client.decryption_rule.fetch(
    name="decrypt-web-traffic",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")

# Get by ID
rule_by_id = client.decryption_rule.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Action: {rule_by_id.action}")
```

### Updating Decryption Rules

```python
# Fetch existing rule
existing_rule = client.decryption_rule.fetch(
    name="decrypt-web-traffic",
    folder="Texas",
    rulebase="pre"
)

# Update attributes
existing_rule.description = "Updated decryption rule for web traffic"
existing_rule.source = ["internal-net", "guest-net"]
existing_rule.profile = "strict-decryption"

# Perform update
updated_rule = client.decryption_rule.update(existing_rule, rulebase="pre")
```

### Listing Decryption Rules

```python
# Pass filters directly into the list method
filtered_rules = client.decryption_rule.list(
    folder='Texas',
    rulebase='pre',
    action=['decrypt'],
    category=['web-browsing']
)

# Process results
for rule in filtered_rules:
    print(f"Name: {rule.name}")
    print(f"Action: {rule.action}")
    print(f"Service: {rule.service}")

# Define filter parameters as a dictionary
list_params = {
    "folder": "Texas",
    "rulebase": "pre",
    "from_": ["trust"],
    "to_": ["untrust"],
    "tag": ["Decryption"]
}

# List with filters as kwargs
filtered_rules = client.decryption_rule.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `action`, `category`, and `tag`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return decryption rules defined exactly in 'Texas'
exact_rules = client.decryption_rule.list(
   folder='Texas',
   rulebase='pre',
   exact_match=True
)

for rule in exact_rules:
   print(f"Exact match: {rule.name} in {rule.folder}")

# Exclude all decryption rules from the 'All' folder
no_all_rules = client.decryption_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_folders=['All']
)

for rule in no_all_rules:
   assert rule.folder != 'All'
   print(f"Filtered out 'All': {rule.name}")

# Exclude decryption rules that come from 'default' snippet
no_default_snippet = client.decryption_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_snippets=['default']
)

for rule in no_default_snippet:
   assert rule.snippet != 'default'
   print(f"Filtered out 'default' snippet: {rule.name}")

# Exclude decryption rules associated with 'DeviceA'
no_deviceA = client.decryption_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_devices=['DeviceA']
)

for rule in no_deviceA:
   assert rule.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {rule.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.decryption_rule.list(
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
client.decryption_rule.max_limit = 4000

# List all rules - auto-paginates through results
all_rules = client.decryption_rule.list(folder='Texas', rulebase='pre')

# The rules are fetched in chunks according to the max_limit setting.
```

### Moving Decryption Rules

```python
# Move rule to top of rulebase
top_move = {
    "destination": "top",
    "rulebase": "pre"
}
client.decryption_rule.move(rule.id, top_move)

# Move rule before another rule
before_move = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
client.decryption_rule.move(rule.id, before_move)

# Move rule after another rule
after_move = {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
client.decryption_rule.move(rule.id, after_move)
```

### Deleting Decryption Rules

```python
# Delete by ID
rule_id = "123e4567-e89b-12d3-a456-426655440000"
client.decryption_rule.delete(rule_id, rulebase="pre")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated decryption rules",
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
        "name": "test-decrypt-rule",
        "folder": "Texas",
        "from_": ["trust"],
        "to_": ["untrust"],
        "source": ["internal-net"],
        "destination": ["any"],
        "service": ["application-default"],
        "action": "decrypt",
        "type": {
            "ssl_forward_proxy": {}
        }
    }

    # Create the rule using the unified client interface
    new_rule = client.decryption_rule.create(rule_config, rulebase="pre")

    # Move the rule
    move_config = {
        "destination": "top",
        "rulebase": "pre"
    }
    client.decryption_rule.move(new_rule.id, move_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Texas"],
        description="Added decryption rule",
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
    - Use the unified client interface (`client.decryption_rule`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Rule Organization**
    - Use descriptive rule names
    - Order rules by specificity
    - Group related rules together
    - Document rule purposes
    - Use consistent naming conventions

3. **Decryption Strategy**
    - Apply no-decrypt rules for sensitive categories (e.g., financial, health)
    - Use SSL forward proxy for outbound traffic inspection
    - Use SSL inbound inspection for inbound traffic to internal servers
    - Associate appropriate decryption profiles
    - Document decryption policy choices

4. **Logging and Monitoring**
    - Enable `log_fail` to track decryption failures
    - Enable `log_success` to monitor successful decryptions
    - Use log forwarding profiles for centralized logging
    - Monitor decryption rule hits
    - Track rule changes

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
the [decryption_rule.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security_services/decryption_rule.py).

## Related Models

- [DecryptionRuleBaseModel](../../models/security_services/decryption_rule_models.md#Overview)
- [DecryptionRuleCreateModel](../../models/security_services/decryption_rule_models.md#Overview)
- [DecryptionRuleUpdateModel](../../models/security_services/decryption_rule_models.md#Overview)
- [DecryptionRuleResponseModel](../../models/security_services/decryption_rule_models.md#Overview)
- [DecryptionRuleMoveModel](../../models/security_services/decryption_rule_models.md#Overview)
- [DecryptionRuleType](../../models/security_services/decryption_rule_models.md#Overview)
- [DecryptionRuleAction](../../models/security_services/decryption_rule_models.md#Overview)
- [DecryptionRuleRulebase](../../models/security_services/decryption_rule_models.md#Overview)
- [DecryptionRuleMoveDestination](../../models/security_services/decryption_rule_models.md#Overview)
