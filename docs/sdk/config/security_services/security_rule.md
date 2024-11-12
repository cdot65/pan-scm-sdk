# Security Rule Configuration Object

The `SecurityRule` class provides functionality to manage security rules in Palo Alto Networks' Strata Cloud Manager.
Security rules define network access policies, controlling traffic flow between zones, applications, and users.

## Overview

Security rules in Strata Cloud Manager allow you to:

- Define traffic control policies between security zones
- Specify source and destination addresses
- Control application and service access
- Apply security profiles and logging settings
- Organize rules within pre and post rulebases
- Position rules for optimal policy enforcement

## Methods

| Method     | Description                                  |
|------------|----------------------------------------------|
| `create()` | Creates a new security rule                  |
| `get()`    | Retrieves a security rule by ID              |
| `update()` | Updates an existing security rule            |
| `delete()` | Deletes a security rule                      |
| `list()`   | Lists security rules with optional filtering |
| `fetch()`  | Retrieves a single security rule by name     |
| `move()`   | Moves a security rule within the rulebase    |

## Creating Security Rules

The `create()` method allows you to define new security rules. You must specify a name, zones, and exactly one
container type (folder, snippet, or device). You can also specify which rulebase to use (pre or post).

**Example: Basic Allow Rule**

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "allow-web",
    "folder": "Shared",
    "from_": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "action": "allow",
    "log_end": True
}

new_rule = security_rule.create(rule_data, rulebase="pre")
print(f"Created rule: {new_rule['name']}")
```

</div>

**Example: Rule with Security Profiles**

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "secure-web",
    "folder": "Shared",
    "from_": ["trust"],
    "to": ["untrust"],
    "source": ["internal-subnet"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "profile_setting": {
        "group": ["strict-security"]
    },
    "action": "allow",
    "log_setting": "default-logging",
    "log_end": True
}

new_rule = security_rule.create(rule_data, rulebase="pre")
print(f"Created rule: {new_rule['name']}")
```

</div>

## Getting Security Rules

Use the `get()` method to retrieve a security rule by its ID. You can specify which rulebase to search.

<div class="termy">

<!-- termynal -->

```python
rule_id = "123e4567-e89b-12d3-a456-426655440000"
rule = security_rule.get(rule_id, rulebase="pre")
print(f"Rule Name: {rule['name']}")
print(f"Applications: {rule['application']}")
```

</div>

## Updating Security Rules

The `update()` method allows you to modify existing security rules.

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "description": "Updated web access rule",
    "application": ["web-browsing", "ssl", "http2"],
    "profile_setting": {
        "group": ["strict-security"]
    },
    "folder": "Shared"
}

updated_rule = security_rule.update(update_data, rulebase="pre")
print(f"Updated rule: {updated_rule['name']}")
```

</div>

## Deleting Security Rules

Use the `delete()` method to remove a security rule.

<div class="termy">

<!-- termynal -->

```python
rule_id = "123e4567-e89b-12d3-a456-426655440000"
security_rule.delete(rule_id, rulebase="pre")
print("Rule deleted successfully")
```

</div>

## Moving Security Rules

The `move()` method allows you to reposition rules within the rulebase.

<div class="termy">

<!-- termynal -->

```python
# Move rule to top of pre-rulebase
move_data = {
    "destination": "top",
    "rulebase": "pre"
}
security_rule.move("123e4567-e89b-12d3-a456-426655440000", move_data)

# Move rule before another rule
move_data = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}
security_rule.move("123e4567-e89b-12d3-a456-426655440000", move_data)
```

</div>

## Listing Security Rules

The `list()` method retrieves multiple security rules with optional filtering. You can filter the results using the
following kwargs:

- `action`: List[str] - Filter by actions (e.g., ['allow', 'deny'])
- `category`: List[str] - Filter by categories (e.g., ['trust', 'untrust'])
- `service`: List[str] - Filter by services (e.g., ['application-default', 'service-http'])
- `application`: List[str] - Filter by applications (e.g., ['web-browsing', 'ssl'])
- `destination`: List[str] - Filter by destinations (e.g., ['any', '10.0.0.0/24'])
- `to_`: List[str] - Filter by to zones (e.g., ['untrust', 'dmz'])
- `source`: List[str] - Filter by sources (e.g., ['any', 'internal-subnet'])
- `from_`: List[str] - Filter by from zones (e.g., ['trust', 'vpn'])
- `tag`: List[str] - Filter by tags (e.g., ['Production', 'Development'])
- `disabled`: bool - Filter by disabled status (True/False)
- `profile_setting`: List[str] - Filter by profile setting groups (e.g., ['strict-security'])
- `log_setting`: List[str] - Filter by log settings (e.g., ['default-logging'])

<div class="termy">

<!-- termynal -->

```python
# List all rules in a folder's pre-rulebase
rules = security_rule.list(
    folder="Shared",
    rulebase="pre"
)

# List only allow rules
allow_rules = security_rule.list(
    folder="Shared",
    rulebase="pre",
    action=['allow']
)

# List rules with specific applications
web_rules = security_rule.list(
    folder="Shared",
    rulebase="pre",
    application=['web-browsing', 'ssl']
)

# List rules with specific zones
zone_rules = security_rule.list(
    folder="Shared",
    rulebase="pre",
    from_=['trust'],
    to_=['untrust']
)

# List rules with security profiles
secure_rules = security_rule.list(
    folder="Shared",
    rulebase="pre",
    profile_setting=['strict-security']
)

# Combine multiple filters
filtered_rules = security_rule.list(
    folder="Shared",
    rulebase="pre",
    action=['allow'],
    application=['web-browsing'],
    tag=['Production']
)

# Print the results
for rule in rules:
    print(f"Name: {rule.name}")
    print(f"Action: {rule.action}")
    print(f"Applications: {rule.application}")
    print("---")
```

</div>

## Fetching Security Rules

The `fetch()` method retrieves a single security rule by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
rule = security_rule.fetch(
    name="allow-web",
    folder="Shared"
)

print(f"Found rule: {rule['name']}")
print(f"Current applications: {rule['application']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a security rule:

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

# Initialize security rule object
security_rule = SecurityRule(client)

# Create new rule
create_data = {
    "name": "test-web-access",
    "description": "Test web access rule",
    "folder": "Shared",
    "from_": ["trust"],
    "to": ["untrust"],
    "source": ["internal-net"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "action": "allow",
    "log_end": True
}

new_rule = security_rule.create(create_data, rulebase="pre")
print(f"Created rule: {new_rule['name']}")

# Move rule to top
move_data = {
    "destination": "top",
    "rulebase": "pre"
}
security_rule.move(new_rule['id'], move_data)

# Fetch the rule by name
fetched_rule = security_rule.fetch(
    name="test-web-access",
    folder="Shared"
)

# Modify the fetched rule
fetched_rule["description"] = "Updated web access rule"
fetched_rule["application"].append("http2")

# Update using the modified object
updated_rule = security_rule.update(fetched_rule, rulebase="pre")
print(f"Updated rule: {updated_rule['name']}")
print(f"New description: {updated_rule['description']}")

# List all rules
rules = security_rule.list(folder="Shared", rulebase="pre")
for rule in rules:
    print(f"Listed rule: {rule['name']}")

# Clean up
security_rule.delete(new_rule['id'], rulebase="pre")
print("Rule deleted successfully")
```

</div>

## Related Models

- [SecurityRuleRequestModel](../../models/security/security_rule_models.md#securityrulerequestmodel)
- [SecurityRuleUpdateModel](../../models/security/security_rule_models.md#securityruleupdatemodel)
- [SecurityRuleResponseModel](../../models/security/security_rule_models.md#securityruleresponsemodel)