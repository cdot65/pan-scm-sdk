# App Override Rule Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [App Override Rule Model Attributes](#app-override-rule-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating App Override Rules](#creating-app-override-rules)
    - [Retrieving App Override Rules](#retrieving-app-override-rules)
    - [Updating App Override Rules](#updating-app-override-rules)
    - [Listing App Override Rules](#listing-app-override-rules)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Moving App Override Rules](#moving-app-override-rules)
    - [Deleting App Override Rules](#deleting-app-override-rules)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `AppOverrideRule` class provides functionality to manage app override rules in Palo Alto Networks' Strata Cloud Manager.
This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting app override
rules that force specific applications to be identified for matching traffic based on zone, address, port, and protocol
via the endpoint `/config/security/v1/app-override-rules`.

## Core Methods

| Method     | Description                      | Parameters                                    | Return Type                          |
|------------|----------------------------------|-----------------------------------------------|--------------------------------------|
| `create()` | Creates a new app override rule  | `data: Dict[str, Any]`, `rulebase: str`       | `AppOverrideRuleResponseModel`       |
| `get()`    | Retrieves a rule by ID           | `object_id: str`, `rulebase: str`             | `AppOverrideRuleResponseModel`       |
| `update()` | Updates an existing rule         | `rule: AppOverrideRuleUpdateModel`            | `AppOverrideRuleResponseModel`       |
| `delete()` | Deletes a rule                   | `object_id: str`, `rulebase: str`             | `None`                               |
| `list()`   | Lists rules with filtering       | `folder: str`, `rulebase: str`                | `List[AppOverrideRuleResponseModel]` |
| `fetch()`  | Gets rule by name and container  | `name: str`, `folder: str`                    | `AppOverrideRuleResponseModel`       |
| `move()`   | Moves rule within rulebase       | `rule_id: UUID`, `data: Dict[str, Any]`       | `None`                               |

## App Override Rule Model Attributes

| Attribute            | Type                      | Required | Default      | Description                                              |
|----------------------|---------------------------|----------|--------------|----------------------------------------------------------|
| `name`               | str                       | Yes      | None         | Name of rule. Pattern: `^[a-zA-Z0-9._-]+$`. Max 63 chars |
| `id`                 | UUID                      | Yes*     | None         | Unique identifier (*response/update only)                |
| `application`        | str                       | Yes      | None         | Application to override                                  |
| `port`               | str                       | Yes      | None         | Port(s) for the rule                                     |
| `protocol`           | AppOverrideRuleProtocol   | Yes      | None         | Protocol (tcp/udp)                                       |
| `disabled`           | bool                      | No       | False        | Whether the rule is disabled                             |
| `description`        | str                       | No       | None         | Rule description. Max 1024 chars                         |
| `tag`                | List[str]                 | No       | None         | Associated tags                                          |
| `from_`              | List[str]                 | No       | ["any"]      | Source zones                                             |
| `to_`                | List[str]                 | No       | ["any"]      | Destination zones                                        |
| `source`             | List[str]                 | No       | ["any"]      | Source addresses                                         |
| `destination`        | List[str]                 | No       | ["any"]      | Destination addresses                                    |
| `negate_source`      | bool                      | No       | False        | Negate source addresses                                  |
| `negate_destination` | bool                      | No       | False        | Negate destination addresses                             |
| `group_tag`          | str                       | No       | None         | Group tag for the rule                                   |
| `rulebase`           | AppOverrideRuleRulebase   | No       | None         | Which rulebase (pre/post)                                |
| `folder`             | str                       | No**     | None         | Folder location. Max 64 chars                            |
| `snippet`            | str                       | No**     | None         | Snippet location. Max 64 chars                           |
| `device`             | str                       | No**     | None         | Device location. Max 64 chars                            |

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

The App Override Rule service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the App Override Rule service directly through the client
# No need to create a separate AppOverrideRule instance
rules = client.app_override_rule
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.security import AppOverrideRule

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize AppOverrideRule object explicitly
rules = AppOverrideRule(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating App Override Rules

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Basic TCP app override rule
tcp_rule = {
    "name": "override-custom-app-tcp",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["internal-net"],
    "destination": ["server-farm"],
    "port": "8080",
    "protocol": "tcp",
    "application": "custom-app"
}

# Create basic TCP rule
basic_rule = client.app_override_rule.create(tcp_rule, rulebase="pre")

# UDP app override rule
udp_rule = {
    "name": "override-voip-udp",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["any"],
    "destination": ["voip-servers"],
    "port": "5060-5061",
    "protocol": "udp",
    "application": "sip",
    "description": "Override SIP traffic identification"
}

# Create UDP rule
voip_rule = client.app_override_rule.create(udp_rule, rulebase="pre")

# Rule with negation and tags
tagged_rule = {
    "name": "override-with-tags",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "negate_destination": True,
    "port": "443",
    "protocol": "tcp",
    "application": "custom-ssl-app",
    "tag": ["Override", "Production"],
    "description": "Override with destination negation"
}

# Create tagged rule
tagged_rule_obj = client.app_override_rule.create(tagged_rule, rulebase="pre")

# Rule in the post rulebase
post_rule = {
    "name": "override-post-rule",
    "folder": "Texas",
    "from_": ["any"],
    "to_": ["any"],
    "source": ["any"],
    "destination": ["any"],
    "port": "9090",
    "protocol": "tcp",
    "application": "internal-monitoring",
    "description": "Post-rulebase monitoring override"
}

# Create rule in post rulebase
post_rule_obj = client.app_override_rule.create(post_rule, rulebase="post")
```

### Retrieving App Override Rules

```python
# Fetch by name and folder
rule = client.app_override_rule.fetch(
    name="override-custom-app-tcp",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")

# Get by ID
rule_by_id = client.app_override_rule.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Application: {rule_by_id.application}")
print(f"Protocol: {rule_by_id.protocol}")
print(f"Port: {rule_by_id.port}")
```

### Updating App Override Rules

```python
# Fetch existing rule
existing_rule = client.app_override_rule.fetch(
    name="override-custom-app-tcp",
    folder="Texas",
    rulebase="pre"
)

# Update attributes
existing_rule.description = "Updated app override rule for custom application"
existing_rule.source = ["internal-net", "guest-net"]
existing_rule.port = "8080,8443"

# Perform update
updated_rule = client.app_override_rule.update(existing_rule, rulebase="pre")
```

### Listing App Override Rules

```python
# Pass filters directly into the list method
filtered_rules = client.app_override_rule.list(
    folder='Texas',
    rulebase='pre',
    application=['custom-app'],
    protocol=['tcp']
)

# Process results
for rule in filtered_rules:
    print(f"Name: {rule.name}")
    print(f"Application: {rule.application}")
    print(f"Protocol: {rule.protocol}")
    print(f"Port: {rule.port}")

# Define filter parameters as a dictionary
list_params = {
    "folder": "Texas",
    "rulebase": "pre",
    "from_": ["trust"],
    "to_": ["untrust"],
    "tag": ["Override"]
}

# List with filters as kwargs
filtered_rules = client.app_override_rule.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `application`, `protocol`, and `tag`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return app override rules defined exactly in 'Texas'
exact_rules = client.app_override_rule.list(
   folder='Texas',
   rulebase='pre',
   exact_match=True
)

for rule in exact_rules:
   print(f"Exact match: {rule.name} in {rule.folder}")

# Exclude all app override rules from the 'All' folder
no_all_rules = client.app_override_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_folders=['All']
)

for rule in no_all_rules:
   assert rule.folder != 'All'
   print(f"Filtered out 'All': {rule.name}")

# Exclude app override rules that come from 'default' snippet
no_default_snippet = client.app_override_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_snippets=['default']
)

for rule in no_default_snippet:
   assert rule.snippet != 'default'
   print(f"Filtered out 'default' snippet: {rule.name}")

# Exclude app override rules associated with 'DeviceA'
no_deviceA = client.app_override_rule.list(
   folder='Texas',
   rulebase='pre',
   exclude_devices=['DeviceA']
)

for rule in no_deviceA:
   assert rule.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {rule.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.app_override_rule.list(
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
client.app_override_rule.max_limit = 4000

# List all rules - auto-paginates through results
all_rules = client.app_override_rule.list(folder='Texas', rulebase='pre')

# The rules are fetched in chunks according to the max_limit setting.
```

### Moving App Override Rules

```python
# Move rule to top of rulebase
top_move = {
    "destination": "top",
    "rulebase": "pre"
}
client.app_override_rule.move(rule.id, top_move)

# Move rule before another rule
before_move = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
client.app_override_rule.move(rule.id, before_move)

# Move rule after another rule
after_move = {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
}
client.app_override_rule.move(rule.id, after_move)
```

### Deleting App Override Rules

```python
# Delete by ID
rule_id = "123e4567-e89b-12d3-a456-426655440000"
client.app_override_rule.delete(rule_id, rulebase="pre")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated app override rules",
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
        "name": "test-app-override",
        "folder": "Texas",
        "from_": ["trust"],
        "to_": ["untrust"],
        "source": ["internal-net"],
        "destination": ["any"],
        "port": "8080",
        "protocol": "tcp",
        "application": "custom-app"
    }

    # Create the rule using the unified client interface
    new_rule = client.app_override_rule.create(rule_config, rulebase="pre")

    # Move the rule
    move_config = {
        "destination": "top",
        "rulebase": "pre"
    }
    client.app_override_rule.move(new_rule.id, move_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Texas"],
        description="Added app override rule",
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
    - Use the unified client interface (`client.app_override_rule`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Rule Organization**
    - Use descriptive rule names that indicate the overridden application
    - Order rules by specificity (most specific first)
    - Group related rules together
    - Document rule purposes with descriptions
    - Use consistent naming conventions

3. **Application Override Strategy**
    - Use app override rules only when App-ID cannot correctly identify the application
    - Be as specific as possible with source/destination and port matching
    - Prefer TCP protocol specification over UDP when both are possible
    - Document why the override is necessary
    - Review overrides periodically as App-ID signatures are updated

4. **Rule Positioning**
    - Place more specific rules before general ones
    - Use the pre-rulebase for rules that should be evaluated first
    - Use the post-rulebase for catch-all or default overrides
    - Use the move method to reorder rules after creation

5. **Performance**
    - Optimize rule order to reduce processing
    - Use specific sources/destinations to narrow matching
    - Minimize rule count where possible
    - Monitor rule processing impact
    - Clean up unused rules

6. **Change Management**
    - Test rules before deployment
    - Document all changes
    - Use proper commit messages
    - Monitor commit status
    - Maintain rule backups

## Full Script Examples

Refer to
the [app_override_rule.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security_services/app_override_rule.py).

## Related Models

- [AppOverrideRuleBaseModel](../../models/security_services/app_override_rule_models.md#Overview)
- [AppOverrideRuleCreateModel](../../models/security_services/app_override_rule_models.md#Overview)
- [AppOverrideRuleUpdateModel](../../models/security_services/app_override_rule_models.md#Overview)
- [AppOverrideRuleResponseModel](../../models/security_services/app_override_rule_models.md#Overview)
- [AppOverrideRuleMoveModel](../../models/security_services/app_override_rule_models.md#Overview)
- [AppOverrideRuleProtocol](../../models/security_services/app_override_rule_models.md#Overview)
- [AppOverrideRuleRulebase](../../models/security_services/app_override_rule_models.md#Overview)
- [AppOverrideRuleMoveDestination](../../models/security_services/app_override_rule_models.md#Overview)
