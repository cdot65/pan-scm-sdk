# Authentication Rule Configuration Object

Manages authentication rules that enforce identity-based policy for network traffic in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `AuthenticationRule` class inherits from `BaseObject` and provides CRUD operations plus rule positioning for authentication rules that enforce identity-based policy for traffic flowing between zones, addresses, and users.

### Methods

| Method     | Description                          | Parameters                                       | Return Type                             |
|------------|--------------------------------------|--------------------------------------------------|-----------------------------------------|
| `create()` | Creates a new authentication rule    | `data: Dict[str, Any]`, `rulebase: str`          | `AuthenticationRuleResponseModel`       |
| `get()`    | Retrieves a rule by ID              | `object_id: str`, `rulebase: str`                | `AuthenticationRuleResponseModel`       |
| `update()` | Updates an existing rule            | `rule: AuthenticationRuleUpdateModel`            | `AuthenticationRuleResponseModel`       |
| `delete()` | Deletes a rule                      | `object_id: str`, `rulebase: str`                | `None`                                  |
| `list()`   | Lists rules with filtering          | `folder: str`, `rulebase: str`                   | `List[AuthenticationRuleResponseModel]` |
| `fetch()`  | Gets rule by name and container     | `name: str`, `folder: str`                       | `AuthenticationRuleResponseModel`       |
| `move()`   | Moves rule within rulebase          | `rule_id: UUID`, `data: Dict[str, Any]`          | `None`                                  |

### Model Attributes

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

rules = client.authentication_rule
```

## Methods

### List Authentication Rules

```python
filtered_rules = client.authentication_rule.list(
    folder='Texas',
    rulebase='pre',
    service=['service-http', 'service-https']
)

for rule in filtered_rules:
    print(f"Name: {rule.name}")
    print(f"Auth enforcement: {rule.authentication_enforcement}")
    print(f"Timeout: {rule.timeout}")
```

**Filtering responses:**

```python
exact_rules = client.authentication_rule.list(
    folder='Texas',
    rulebase='pre',
    exact_match=True
)

combined_filters = client.authentication_rule.list(
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
client.authentication_rule.max_limit = 4000

all_rules = client.authentication_rule.list(folder='Texas', rulebase='pre')
```

### Fetch an Authentication Rule

```python
rule = client.authentication_rule.fetch(
    name="auth-web-traffic",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")
```

### Create an Authentication Rule

```python
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
created_rule = client.authentication_rule.create(basic_rule, rulebase="pre")

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
hip_created = client.authentication_rule.create(hip_rule, rulebase="pre")
```

### Update an Authentication Rule

```python
existing_rule = client.authentication_rule.fetch(
    name="auth-web-traffic",
    folder="Texas",
    rulebase="pre"
)

existing_rule.description = "Updated authentication rule for web traffic"
existing_rule.timeout = 120
existing_rule.authentication_enforcement = "updated-auth-profile"

updated_rule = client.authentication_rule.update(existing_rule, rulebase="pre")
```

### Delete an Authentication Rule

```python
client.authentication_rule.delete("123e4567-e89b-12d3-a456-426655440000", rulebase="pre")
```

### Move an Authentication Rule

```python
# Move rule to top of rulebase
client.authentication_rule.move(rule.id, {
    "destination": "top",
    "rulebase": "pre"
})

# Move rule before another rule
client.authentication_rule.move(rule.id, {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
})

# Move rule after another rule
client.authentication_rule.move(rule.id, {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
})
```

### Get an Authentication Rule by ID

```python
rule_by_id = client.authentication_rule.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Authentication enforcement: {rule_by_id.authentication_enforcement}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated authentication rules",
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
        "name": "test-auth-rule",
        "folder": "Texas",
        "from_": ["trust"],
        "to_": ["untrust"],
        "source": ["internal-net"],
        "destination": ["any"],
        "service": ["application-default"],
        "authentication_enforcement": "auth-profile-1"
    }
    new_rule = client.authentication_rule.create(rule_config, rulebase="pre")
    client.authentication_rule.move(new_rule.id, {
        "destination": "top",
        "rulebase": "pre"
    })
    result = client.commit(
        folders=["Texas"],
        description="Added authentication rule",
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

- [Authentication Rule Models](../../models/security_services/authentication_rule_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security_services/authentication_rule.py)
