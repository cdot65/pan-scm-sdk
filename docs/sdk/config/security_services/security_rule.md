# Security Rule Configuration Object

Manages security rules that control traffic flow between zones, applications, and users in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `SecurityRule` class inherits from `BaseObject` and provides CRUD operations plus rule positioning for security rules that define core security policies for network traffic.

### Methods

| Method     | Description                     | Parameters                              | Return Type                       |
|------------|---------------------------------|-----------------------------------------|-----------------------------------|
| `create()` | Creates a new security rule     | `data: Dict[str, Any]`, `rulebase: str` | `SecurityRuleResponseModel`       |
| `get()`    | Retrieves a rule by ID          | `object_id: str`, `rulebase: str`       | `SecurityRuleResponseModel`       |
| `update()` | Updates an existing rule        | `rule: SecurityRuleUpdateModel`         | `SecurityRuleResponseModel`       |
| `delete()` | Deletes a rule                  | `object_id: str`, `rulebase: str`       | `None`                            |
| `list()`   | Lists rules with filtering      | `folder: str`, `rulebase: str`          | `List[SecurityRuleResponseModel]` |
| `fetch()`  | Gets rule by name and container | `name: str`, `folder: str`              | `SecurityRuleResponseModel`       |
| `move()`   | Moves rule within rulebase      | `rule_id: UUID`, `data: Dict[str, Any]` | `None`                            |

### Model Attributes

| Attribute            | Type                        | Required | Default      | Description                                              |
|----------------------|-----------------------------|----------|--------------|----------------------------------------------------------|
| `name`               | str                         | Yes      | None         | Name of rule. Pattern: `^[a-zA-Z0-9_ \.-]+$`             |
| `id`                 | UUID                        | Yes*     | None         | Unique identifier (*response/update only)                |
| `disabled`           | bool                        | No       | False        | Whether the rule is disabled                             |
| `description`        | str                         | No       | None         | Rule description                                         |
| `tag`                | List[str]                   | No       | []           | Associated tags                                          |
| `from_`              | List[str]                   | No       | ["any"]      | Source zones                                             |
| `source`             | List[str]                   | No       | ["any"]      | Source addresses                                         |
| `negate_source`      | bool                        | No       | False        | Negate source addresses                                  |
| `source_user`        | List[str]                   | No       | ["any"]      | Source users/groups                                      |
| `source_hip`         | List[str]                   | No       | ["any"]      | Source Host Integrity Profiles                           |
| `to_`                | List[str]                   | No       | ["any"]      | Destination zones                                        |
| `destination`        | List[str]                   | No       | ["any"]      | Destination addresses                                    |
| `negate_destination` | bool                        | No       | False        | Negate destination addresses                             |
| `destination_hip`    | List[str]                   | No       | ["any"]      | Destination Host Integrity Profiles                      |
| `application`        | List[str]                   | No       | ["any"]      | Allowed applications                                     |
| `service`            | List[str]                   | No       | ["any"]      | Allowed services                                         |
| `category`           | List[str]                   | No       | ["any"]      | URL categories                                           |
| `action`             | SecurityRuleAction          | No       | allow        | Rule action (allow/deny/drop/reset-client/server/both)   |
| `profile_setting`    | SecurityRuleProfileSetting  | No       | None         | Security profile settings                                |
| `log_setting`        | str                         | No       | None         | Log forwarding profile                                   |
| `schedule`           | str                         | No       | None         | Schedule profile                                         |
| `log_start`          | bool                        | No       | None         | Log at session start                                     |
| `log_end`            | bool                        | No       | None         | Log at session end                                       |
| `rulebase`           | SecurityRuleRulebase        | No       | None         | Which rulebase (pre/post)                                |
| `folder`             | str                         | No**     | None         | Folder location. Max 64 chars                            |
| `snippet`            | str                         | No**     | None         | Snippet location. Max 64 chars                           |
| `device`             | str                         | No**     | None         | Device location. Max 64 chars                            |

\* Only required for response and update models
\** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

### Exceptions

| Exception                    | HTTP Code | Description                 |
|------------------------------|-----------|-----------------------------|
| `InvalidObjectError`         | 400       | Invalid rule data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters |
| `NameNotUniqueError`         | 409       | Rule name already exists    |
| `ObjectNotPresentError`      | 404       | Rule not found              |
| `ReferenceNotZeroError`      | 409       | Rule still referenced       |
| `AuthenticationError`        | 401       | Authentication failed       |
| `ServerError`                | 500       | Internal server error       |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

rules = client.security_rule
```

## Methods

### List Security Rules

```python
filtered_rules = client.security_rule.list(
    folder='Texas',
    rulebase='pre',
    action=['allow'],
    application=['web-browsing', 'ssl']
)

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
filtered_rules = client.security_rule.list(**list_params)
```

**Filtering responses:**

```python
# Only return rules defined exactly in 'Texas'
exact_rules = client.security_rule.list(
    folder='Texas',
    rulebase='pre',
    exact_match=True
)

# Exclude all rules from the 'All' folder
no_all_rules = client.security_rule.list(
    folder='Texas',
    rulebase='pre',
    exclude_folders=['All']
)

# Combine exact_match with multiple exclusions
combined_filters = client.security_rule.list(
    folder='Texas',
    rulebase='pre',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)
```

**Controlling pagination with max_limit:**

```python
client.security_rule.max_limit = 4000

all_rules = client.security_rule.list(folder='Texas', rulebase='pre')
```

### Fetch a Security Rule

```python
rule = client.security_rule.fetch(
    name="allow-web",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")
```

### Create a Security Rule

```python
# Basic allow rule
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
basic_rule = client.security_rule.create(allow_rule, rulebase="pre")

# Rule with security profiles
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
profile_rule = client.security_rule.create(secure_rule, rulebase="pre")
```

### Update a Security Rule

```python
existing_rule = client.security_rule.fetch(
    name="allow-web",
    folder="Texas",
    rulebase="pre"
)

existing_rule.description = "Updated web access rule"
existing_rule.application = ["web-browsing", "ssl", "http2"]
existing_rule.profile_setting = {
    "group": ["strict-security"]
}

updated_rule = client.security_rule.update(existing_rule, rulebase="pre")
```

### Delete a Security Rule

```python
client.security_rule.delete("123e4567-e89b-12d3-a456-426655440000", rulebase="pre")
```

### Move a Security Rule

```python
# Move rule to top of rulebase
client.security_rule.move(rule.id, {
    "destination": "top",
    "rulebase": "pre"
})

# Move rule before another rule
client.security_rule.move(rule.id, {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
})

# Move rule after another rule
client.security_rule.move(rule.id, {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
})
```

### Get a Security Rule by ID

```python
rule_by_id = client.security_rule.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Applications: {rule_by_id.application}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated security rules",
    sync=True,
    timeout=300
)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

try:
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
    new_rule = client.security_rule.create(rule_config, rulebase="pre")
    client.security_rule.move(new_rule.id, {
        "destination": "top",
        "rulebase": "pre"
    })
    result = client.commit(
        folders=["Texas"],
        description="Added test rule",
        sync=True
    )
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

## Related Topics

- [Security Rule Models](../../models/security_services/security_rule_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security_services/security_rule.py)
