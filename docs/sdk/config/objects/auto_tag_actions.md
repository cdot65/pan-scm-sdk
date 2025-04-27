# Auto Tag Actions

The Auto Tag Actions module enables you to configure automated tag assignment based on traffic patterns, security events, and other triggers. This feature helps organizations automate their security tagging and policy enforcement.

## Class Overview

The `AutoTagActions` class provides functionality to create, update, delete, and fetch auto tag action configurations in Strata Cloud Manager.

```python
from scm.config.objects import AutoTagActions
from scm.client import Scm

# Initialize the client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize the auto tag actions service
auto_tag_actions = AutoTagActions(client)

# Alternatively, use the unified client pattern
# Access auto tag actions directly through the client
auto_tag = client.auto_tag_actions
```

## Methods

### List Auto Tag Actions

Retrieve a list of all auto tag action configurations in the specified folder.

```python
# List auto tag actions
auto_tags = client.auto_tag_actions.list(folder="Texas")

# Process the auto tag actions
for auto_tag in auto_tags:
    print(f"Auto Tag Action: {auto_tag.name}")
    print(f"  Matching Rule: {auto_tag.match_criteria}")
    print(f"  Tags Applied: {[tag.name for tag in auto_tag.tags]}")
```

### Fetch an Auto Tag Action

Retrieve a specific auto tag action configuration by name.

```python
# Fetch specific auto tag action by name
auto_tag = client.auto_tag_actions.fetch(
    name="high-risk-traffic",
    folder="Texas"
)

print(f"Auto Tag Action: {auto_tag.name}")
print(f"Description: {auto_tag.description}")
print(f"Tags: {[tag.name for tag in auto_tag.tags]}")
```

### Create an Auto Tag Action

Create a new auto tag action configuration.

```python
# Create a new auto tag action
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
    "timeout": 86400  # Duration in seconds (24 hours)
})

print(f"Created Auto Tag Action: {new_auto_tag.name} with ID: {new_auto_tag.id}")
```

### Update an Auto Tag Action

Update an existing auto tag action configuration.

```python
# Fetch the configuration first
auto_tag = client.auto_tag_actions.fetch(
    name="malware-traffic",
    folder="Texas"
)

# Modify the configuration
auto_tag.description = "Updated auto-tagging for malware detection"
auto_tag.timeout = 172800  # Update timeout to 48 hours

# Add a new tag
auto_tag.tags.append("security-incident")

# Update the configuration
updated_auto_tag = client.auto_tag_actions.update(auto_tag)
print(f"Updated Auto Tag Action: {updated_auto_tag.name}")
print(f"New tags: {[tag.name for tag in updated_auto_tag.tags]}")
```

### Delete an Auto Tag Action

Delete an auto tag action configuration.

```python
# Delete by ID
client.auto_tag_actions.delete("123456789")

# Or by providing a model
client.auto_tag_actions.delete(auto_tag)

print("Auto Tag Action deleted successfully")
```

## Use Cases

Here are some common use cases for auto tag actions:

### Tagging Infected Hosts

```python
# Create an auto tag action for infected hosts
try:
    infected_hosts_tag = client.auto_tag_actions.create({
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
        "timeout": 604800  # 7 days
    })
    print(f"Auto tag action created: {infected_hosts_tag.name}")
except ScmApiError as e:
    print(f"Failed to create auto tag action: {e}")
```

### Tagging High-Risk Applications

```python
# Create an auto tag action for high-risk application usage
high_risk_apps_tag = client.auto_tag_actions.create({
    "name": "high-risk-application-usage",
    "folder": "Texas",
    "description": "Tag hosts using high-risk applications",
    "match_criteria": {
        "application": {
            "risk": [4, 5],  # High and critical risk applications
            "category": ["peer-to-peer", "proxies", "tunneling"]
        }
    },
    "action": "add",
    "tags": ["policy-violation", "high-risk-application"],
    "timeout": 259200  # 3 days
})
```

## Error Handling

Handle potential errors when working with auto tag actions:

```python
from scm.exceptions import ScmApiError, ResourceNotFoundError

try:
    auto_tag = client.auto_tag_actions.fetch(
        name="non-existent-auto-tag",
        folder="Texas"
    )
except ResourceNotFoundError:
    print("Auto Tag Action not found")
except ScmApiError as e:
    print(f"API Error: {e}")
```

## Integration with Security Policies

Auto tag actions can be integrated with security policies to create dynamic, adaptive security controls:

```python
# First, create an auto tag action
auto_tag = client.auto_tag_actions.create({
    "name": "data-exfiltration-suspect",
    "folder": "Texas",
    "description": "Tag hosts with suspected data exfiltration",
    "match_criteria": {
        "destination": {
            "region": ["high-risk-countries"]
        },
        "application": {
            "characteristic": ["tunneling", "has-known-vulnerabilities"]
        },
        "data_pattern": ["credit-card", "ssn", "password"]
    },
    "action": "add",
    "tags": ["data-exfiltration-suspect"],
    "timeout": 604800  # 7 days
})

# Then, create a security rule that uses the tag
security_rule = client.security_rule.create({
    "name": "block-data-exfiltration-suspects",
    "folder": "Texas",
    "description": "Block hosts tagged with data exfiltration",
    "source": {
        "tags": ["data-exfiltration-suspect"]
    },
    "destination": {
        "address": ["any"]
    },
    "service": ["application-default"],
    "application": ["any"],
    "action": "deny",
    "log_setting": "detailed-logging"
})
```
