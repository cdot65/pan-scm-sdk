# Decryption Rule Configuration Object

Manages decryption rules that control SSL/TLS traffic inspection policies in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `DecryptionRule` class inherits from `BaseObject` and provides CRUD operations plus rule positioning for decryption rules that control SSL/TLS traffic inspection policies between zones, addresses, and users.

### Methods

| Method     | Description                      | Parameters                                | Return Type                          |
|------------|----------------------------------|-------------------------------------------|--------------------------------------|
| `create()` | Creates a new decryption rule    | `data: Dict[str, Any]`, `rulebase: str`   | `DecryptionRuleResponseModel`        |
| `get()`    | Retrieves a rule by ID           | `object_id: str`, `rulebase: str`         | `DecryptionRuleResponseModel`        |
| `update()` | Updates an existing rule         | `rule: DecryptionRuleUpdateModel`         | `DecryptionRuleResponseModel`        |
| `delete()` | Deletes a rule                   | `object_id: str`, `rulebase: str`         | `None`                               |
| `list()`   | Lists rules with filtering       | `folder: str`, `rulebase: str`            | `List[DecryptionRuleResponseModel]`  |
| `fetch()`  | Gets rule by name and container  | `name: str`, `folder: str`               | `DecryptionRuleResponseModel`        |
| `move()`   | Moves rule within rulebase       | `rule_id: UUID`, `data: Dict[str, Any]`   | `None`                               |

### Model Attributes

| Attribute            | Type                   | Required | Default      | Description                                                |
|----------------------|------------------------|----------|--------------|------------------------------------------------------------|
| `name`               | str                    | Yes      | None         | Name of rule. Pattern: `^[a-zA-Z0-9_ \.-]+$`              |
| `id`                 | UUID                   | Yes*     | None         | Unique identifier (*response/update only)                  |
| `action`             | DecryptionRuleAction   | Yes      | None         | Rule action (decrypt/no-decrypt)                           |
| `disabled`           | bool                   | No       | False        | Whether the rule is disabled                               |
| `description`        | str                    | No       | None         | Rule description                                           |
| `tag`                | List[str]              | No       | []           | Associated tags                                            |
| `from_`              | List[str]              | No       | ["any"]      | Source zones                                               |
| `to_`                | List[str]              | No       | ["any"]      | Destination zones                                          |
| `source`             | List[str]              | No       | ["any"]      | Source addresses                                           |
| `destination`        | List[str]              | No       | ["any"]      | Destination addresses                                      |
| `source_user`        | List[str]              | No       | ["any"]      | Source users/groups                                        |
| `category`           | List[str]              | No       | ["any"]      | URL categories                                             |
| `service`            | List[str]              | No       | ["any"]      | Services                                                   |
| `source_hip`         | List[str]              | No       | ["any"]      | Source Host Integrity Profiles                             |
| `destination_hip`    | List[str]              | No       | ["any"]      | Destination Host Integrity Profiles                        |
| `negate_source`      | bool                   | No       | False        | Negate source addresses                                    |
| `negate_destination` | bool                   | No       | False        | Negate destination addresses                               |
| `profile`            | str                    | No       | None         | Decryption profile name                                    |
| `type`               | DecryptionRuleType     | No       | None         | Decryption type (ssl_forward_proxy/ssl_inbound_inspection) |
| `log_setting`        | str                    | No       | None         | Log forwarding profile                                     |
| `log_fail`           | bool                   | No       | None         | Log failed decryption events                               |
| `log_success`        | bool                   | No       | None         | Log successful decryption events                           |
| `rulebase`           | DecryptionRuleRulebase | No       | None         | Which rulebase (pre/post)                                  |
| `folder`             | str                    | No**     | None         | Folder location. Max 64 chars                              |
| `snippet`            | str                    | No**     | None         | Snippet location. Max 64 chars                             |
| `device`             | str                    | No**     | None         | Device location. Max 64 chars                              |

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

rules = client.decryption_rule
```

## Methods

### List Decryption Rules

```python
filtered_rules = client.decryption_rule.list(
    folder='Texas',
    rulebase='pre',
    action=['decrypt'],
    category=['web-browsing']
)

for rule in filtered_rules:
    print(f"Name: {rule.name}")
    print(f"Action: {rule.action}")
    print(f"Service: {rule.service}")
```

**Filtering responses:**

```python
exact_rules = client.decryption_rule.list(
    folder='Texas',
    rulebase='pre',
    exact_match=True
)

combined_filters = client.decryption_rule.list(
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
client.decryption_rule.max_limit = 4000

all_rules = client.decryption_rule.list(folder='Texas', rulebase='pre')
```

### Fetch a Decryption Rule

```python
rule = client.decryption_rule.fetch(
    name="decrypt-web-traffic",
    folder="Texas",
    rulebase="pre"
)
print(f"Found rule: {rule.name}")
```

### Create a Decryption Rule

```python
# Basic decrypt rule
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
basic_rule = client.decryption_rule.create(decrypt_rule, rulebase="pre")

# No-decrypt rule
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
bypass_rule = client.decryption_rule.create(no_decrypt_rule, rulebase="pre")

# Rule with SSL forward proxy type and decryption profile
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
profiled_rule = client.decryption_rule.create(profile_rule, rulebase="pre")
```

### Update a Decryption Rule

```python
existing_rule = client.decryption_rule.fetch(
    name="decrypt-web-traffic",
    folder="Texas",
    rulebase="pre"
)

existing_rule.description = "Updated decryption rule for web traffic"
existing_rule.source = ["internal-net", "guest-net"]
existing_rule.profile = "strict-decryption"

updated_rule = client.decryption_rule.update(existing_rule, rulebase="pre")
```

### Delete a Decryption Rule

```python
client.decryption_rule.delete("123e4567-e89b-12d3-a456-426655440000", rulebase="pre")
```

### Move a Decryption Rule

```python
# Move rule to top of rulebase
client.decryption_rule.move(rule.id, {
    "destination": "top",
    "rulebase": "pre"
})

# Move rule before another rule
client.decryption_rule.move(rule.id, {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
})

# Move rule after another rule
client.decryption_rule.move(rule.id, {
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-54ba-3210-9876-fedcba098765"
})
```

### Get a Decryption Rule by ID

```python
rule_by_id = client.decryption_rule.get(rule.id, rulebase="pre")
print(f"Retrieved rule: {rule_by_id.name}")
print(f"Action: {rule_by_id.action}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated decryption rules",
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
    new_rule = client.decryption_rule.create(rule_config, rulebase="pre")
    client.decryption_rule.move(new_rule.id, {
        "destination": "top",
        "rulebase": "pre"
    })
    result = client.commit(
        folders=["Texas"],
        description="Added decryption rule",
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

- [Decryption Rule Models](../../models/security_services/decryption_rule_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security_services/decryption_rule.py)
