# Auto Tag Actions

The `AutoTagActions` service manages automated tag assignment configurations in Strata Cloud Manager, enabling automatic tagging based on traffic patterns, security events, and other triggers.

## Class Overview

The `AutoTagActions` class provides CRUD operations for auto tag action configurations. It is accessed through the `client.auto_tag_actions` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the AutoTagActions service
auto_tags = client.auto_tag_actions
```

## Methods

### List Auto Tag Actions

Retrieves a list of all auto tag action configurations in the specified folder.

```python
auto_tags = client.auto_tag_actions.list(folder="Texas")

for auto_tag in auto_tags:
    print(f"Auto Tag Action: {auto_tag.name}")
```

### Fetch an Auto Tag Action

Retrieves a specific auto tag action configuration by name.

```python
auto_tag = client.auto_tag_actions.fetch(
    name="high-risk-traffic",
    folder="Texas"
)

print(f"Auto Tag Action: {auto_tag.name}")
print(f"Description: {auto_tag.description}")
```

### Create an Auto Tag Action

Creates a new auto tag action configuration.

```python
new_auto_tag = client.auto_tag_actions.create({
    "name": "malware-traffic",
    "folder": "Texas",
    "description": "Automatically tag hosts with suspected malware traffic",
    "match_criteria": {
        "threat_name": "contains:malware",
        "severity": "high"
    },
    "action": "add",
    "tags": ["malware-suspect", "quarantine-required"],
    "timeout": 86400
})

print(f"Created: {new_auto_tag.name} (ID: {new_auto_tag.id})")
```

### Update an Auto Tag Action

Updates an existing auto tag action configuration.

```python
auto_tag = client.auto_tag_actions.fetch(
    name="malware-traffic",
    folder="Texas"
)

auto_tag.description = "Updated auto-tagging for malware detection"
auto_tag.timeout = 172800

updated = client.auto_tag_actions.update(auto_tag)
print(f"Updated: {updated.name}")
```

### Delete an Auto Tag Action

Deletes an auto tag action configuration.

```python
client.auto_tag_actions.delete("123456789")
```

## Use Cases

### Tagging Infected Hosts

Automatically tag hosts that exhibit signs of infection for quarantine.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

client.auto_tag_actions.create({
    "name": "infected-host-detection",
    "folder": "Texas",
    "description": "Tag hosts with confirmed infections",
    "match_criteria": {
        "severity": "critical",
        "threat_type": ["virus", "spyware"],
        "action_taken": "block"
    },
    "action": "add",
    "tags": ["infected-host", "remediation-required"],
    "timeout": 604800
})
```

### Tagging High-Risk Application Usage

Tag hosts using risky applications for policy enforcement.

```python
client.auto_tag_actions.create({
    "name": "high-risk-application-usage",
    "folder": "Texas",
    "description": "Tag hosts using high-risk applications",
    "match_criteria": {
        "application": {
            "risk": [4, 5],
            "category": ["peer-to-peer", "proxies", "tunneling"]
        }
    },
    "action": "add",
    "tags": ["policy-violation", "high-risk-application"],
    "timeout": 259200
})
```

### Integration with Security Policies

Create auto tag actions that feed into dynamic security rules.

```python
# Create auto tag action for data exfiltration detection
client.auto_tag_actions.create({
    "name": "data-exfiltration-suspect",
    "folder": "Texas",
    "description": "Tag hosts with suspected data exfiltration",
    "match_criteria": {
        "destination": {"region": ["high-risk-countries"]},
        "application": {
            "characteristic": ["tunneling", "has-known-vulnerabilities"]
        },
        "data_pattern": ["credit-card", "ssn", "password"]
    },
    "action": "add",
    "tags": ["data-exfiltration-suspect"],
    "timeout": 604800
})

# Create a security rule using the dynamic tag
client.security_rule.create({
    "name": "block-data-exfiltration-suspects",
    "folder": "Texas",
    "source": {"tags": ["data-exfiltration-suspect"]},
    "destination": {"address": ["any"]},
    "service": ["application-default"],
    "application": ["any"],
    "action": "deny"
})
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import InvalidObjectError, ObjectNotPresentError

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    auto_tag = client.auto_tag_actions.fetch(
        name="non-existent-auto-tag",
        folder="Texas"
    )
except ObjectNotPresentError:
    print("Auto Tag Action not found")
except InvalidObjectError as e:
    print(f"Invalid data: {e.message}")
```

## Related Topics

- [Tag](tag.md)
