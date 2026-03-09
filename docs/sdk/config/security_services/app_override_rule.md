# App Override Rule Configuration Object

Manages app override rules that force application identification for specific traffic in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `AppOverrideRule` class inherits from `BaseObject` and provides CRUD operations plus rule positioning for app override rules that force specific applications to be identified for matching traffic based on zone, address, port, and protocol.

### Methods

| Method     | Description                      | Parameters                                    | Return Type                          |
|------------|----------------------------------|-----------------------------------------------|--------------------------------------|
| `create()` | Creates a new app override rule  | `data: Dict[str, Any]`, `rulebase: str`       | `AppOverrideRuleResponseModel`       |
| `get()`    | Retrieves a rule by ID           | `object_id: str`, `rulebase: str`             | `AppOverrideRuleResponseModel`       |
| `update()` | Updates an existing rule         | `rule: AppOverrideRuleUpdateModel`            | `AppOverrideRuleResponseModel`       |
| `delete()` | Deletes a rule                   | `object_id: str`, `rulebase: str`             | `None`                               |
| `list()`   | Lists rules with filtering       | `folder: str`, `rulebase: str`                | `List[AppOverrideRuleResponseModel]` |
| `fetch()`  | Gets rule by name and container  | `name: str`, `folder: str`                    | `AppOverrideRuleResponseModel`       |
| `move()`   | Moves rule within rulebase       | `rule_id: UUID`, `data: Dict[str, Any]`       | `None`                               |

### Model Attributes

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
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

rules = client.app_override_rule
```

## Methods

### List App Override Rules

```python
filtered_rules = client.app_override_rule.list(
    folder='Texas',
    rulebase='pre',
    application=['custom-app'],
    protocol=['tcp']
)

for rule in filtered_rules:
    print(f"Name: {rule.name}")
    print(f"Application: {rule.application}")
    print(f"Protocol: {rule.protocol}")
    print(f"Port: {rule.port}")
```

**Filtering responses:**

```python
# Only return rules defined exactly in 'Texas'
exact_rules = client.app_override_rule.list(
    folder='Texas',
    rulebase='pre',
    exact_match=True
)

# Combine exact_match with multiple exclusions
combined_filters = client.app_override_rule.list(
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
client.app_override_rule.max_limit = 4000

all_rules = client.app_override_rule.list(folder='Texas', rulebase='pre')
```

### Fetch an App Override Rule

```python
rule = client.app_override_rule.fetch(
    name="override-custom-app-tcp",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")
```

### Create an App Override Rule

```python
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
voip_rule = client.app_override_rule.create(udp_rule, rulebase="pre")
```

### Update an App Override Rule

```python
existing_rule = client.app_override_rule.fetch(
    name="override-custom-app-tcp",
    folder="Texas",
    rulebase="pre"
)

existing_rule.description = "Updated app override rule for custom application"
existing_rule.source = ["internal-net", "guest-net"]
existing_rule.port = "8080,8443"

updated_rule = client.app_override_rule.update(existing_rule, rulebase="pre")
```

### Delete an App Override Rule

```python
client.app_override_rule.delete("123e4567-e89b-12d3-a456-426655440000", rulebase="pre")
```

### Move an App Override Rule

```python
# Move rule to top of rulebase
client.app_override_rule.move(rule.id, {
    "destination": "top",
    "rulebase": "pre"
})

# Move rule before another rule
client.app_override_rule.move(rule.id, {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
})

# Move rule after another rule
client.app_override_rule.move(rule.id, {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
})
```

### Get an App Override Rule by ID

```python
rule_by_id = client.app_override_rule.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Application: {rule_by_id.application}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated app override rules",
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
    new_rule = client.app_override_rule.create(rule_config, rulebase="pre")
    client.app_override_rule.move(new_rule.id, {
        "destination": "top",
        "rulebase": "pre"
    })
    result = client.commit(
        folders=["Texas"],
        description="Added app override rule",
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

- [App Override Rule Models](../../models/security_services/app_override_rule_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security_services/app_override_rule.py)
