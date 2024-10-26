# Security Rule Configuration Object

The `SecurityRule` class manages Security Rules in Palo Alto Networks' Strata Cloud Manager.
It provides methods to create, retrieve, update, delete, list, and move Security Rule objects.

---

## Creating an API client object

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm

api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)
```

</div>

---

## Importing the SecurityRule Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.security import SecurityRule

security_rule = SecurityRule(api_client)
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> SecurityRuleResponseModel`

Creates a new Security Rule object.

**Example 1: Basic Allow Rule**

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Allow_Web",
    "folder": "Shared",
    "from_": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "action": "allow",
    "log_end": True
}

new_rule = security_rule.create(rule_data)
print(f"Created rule: {new_rule.name}")
```

</div>

**Example 2: Rule with Profile Settings**

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Secure_Web",
    "folder": "Shared",
    "from_": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["web-browsing"],
    "profile_setting": {
        "group": ["strict-security"]
    },
    "action": "allow"
}

new_rule = security_rule.create(rule_data)
```

</div>

### `move(rule_id: str, data: Dict[str, Any]) -> None`

Moves a security rule to a new position within the rulebase.

**Example:**

<div class="termy">

<!-- termynal -->

```python
move_data = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}

security_rule.move("123e4567-e89b-12d3-a456-426655440000", move_data)
```

</div>

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, offset: Optional[int] = None, limit: Optional[int] = None, name: Optional[str] = None, **filters) -> List[SecurityRuleResponseModel]`

Lists Security Rule objects with optional filtering.

**Example:**

<div class="termy">

<!-- termynal -->

```python
# List rules with pagination
rules = security_rule.list(
    folder="Shared",
    offset=0,
    limit=10,
    name="Allow"
)

for rule in rules:
    print(f"Rule: {rule.name}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> SecurityRuleResponseModel`

Updates an existing Security Rule object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated rule description",
    "application": ["web-browsing", "ssl", "http2"],
    "tag": ["updated", "modified"]
}

updated_rule = security_rule.update(rule_id, update_data)
```

</div>

### `delete(object_id: str) -> None`

Deletes a Security Rule object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
security_rule.delete(rule_id)
```

</div>

## Complete Example: Managing Security Rules

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import SecurityRule

# Initialize client
api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create SecurityRule instance
security_rule = SecurityRule(api_client)

# Create a new rule
rule_data = {
    "name": "Comprehensive_Web_Rule",
    "description": "Allow web traffic with security profiles",
    "folder": "Shared",
    "from_": ["trust", "internal"],
    "to": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl", "http2"],
    "service": ["application-default"],
    "action": "allow",
    "profile_setting": {
        "group": ["strict-security"]
    },
    "tag": ["web", "internal"],
    "log_setting": "default-logging",
    "log_end": True
}

new_rule = security_rule.create(rule_data)
print(f"Created rule: {new_rule.name}")

# Move the rule
move_data = {
    "destination": "top",
    "rulebase": "pre"
}
security_rule.move(new_rule.id, move_data)

# Update the rule
update_data = {
    "description": "Updated comprehensive web rule",
    "application": ["web-browsing", "ssl", "http2", "webex-meeting"],
}
updated_rule = security_rule.update(new_rule.id, update_data)

# List rules
rules = security_rule.list(folder="Shared", limit=5)
for rule in rules:
    print(f"Rule: {rule.name}")

# Clean up
security_rule.delete(new_rule.id)
```

</div>

