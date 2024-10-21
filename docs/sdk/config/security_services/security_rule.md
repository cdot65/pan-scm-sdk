# Security Rule Configuration Object

The `SecurityRule` class is used to manage Security Rules in the Strata Cloud Manager.
It provides methods to create, retrieve, update, delete, and list Security Rule objects.

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

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the Security Rule object data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Allow_HTTP",
    "description": "Allow HTTP traffic",
    "folder": "Shared",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["web-browsing"],
    "service": ["application-default"],
    "action": "allow",
    "log_setting": "Send_to_SIEM",
    "log_end": True,
}

new_rule = security_rule.create(rule_data)
print(f"Created Security Rule with ID: {new_rule.id}")
```

</div>

### `get(object_id: str) -> SecurityRuleResponseModel`

Retrieves a Security Rule object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the Security Rule object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
rule_id = "123e4567-e89b-12d3-a456-426655440000"
rule_object = security_rule.get(rule_id)
print(f"Rule Name: {rule_object.name}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> SecurityRuleResponseModel`

Updates an existing Security Rule object.

**Parameters:**

- `object_id` (str): The UUID of the Security Rule object.
- `data` (Dict[str, Any]): A dictionary containing the updated Security Rule data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Allow HTTP and HTTPS traffic",
    "application": ["web-browsing", "ssl"],
}

updated_rule = security_rule.update(rule_id, update_data)
print(f"Updated Security Rule with ID: {updated_rule.id}")
```

</div>

### `delete(object_id: str) -> None`

Deletes a Security Rule object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the Security Rule object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
security_rule.delete(rule_id)
print(f"Deleted Security Rule with ID: {rule_id}")
```

</div>

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, offset: Optional[int] = None, limit: Optional[int] = None, name: Optional[str] = None, **filters) -> List[SecurityRuleResponseModel]`

Lists Security Rule objects, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list rules from.
- `snippet` (Optional[str]): The snippet to list rules from.
- `device` (Optional[str]): The device to list rules from.
- `offset` (Optional[int]): The pagination offset.
- `limit` (Optional[int]): The pagination limit.
- `name` (Optional[str]): Filter rules by name.
- `**filters`: Additional filters.

**Example:**

<div class="termy">

<!-- termynal -->

```python
rules = security_rule.list(folder='Shared', limit=10)

for rule in rules:
    print(f"Rule Name: {rule.name}, ID: {rule.id}")
```

</div>

---

## Usage Examples

### Example 1: Creating a Basic Allow Rule

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Allow_DNS",
    "description": "Allow DNS traffic",
    "folder": "Shared",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["dns"],
    "service": ["application-default"],
    "action": "allow",
    "log_end": True,
}

new_rule = security_rule.create(rule_data)
print(f"Created Security Rule: {new_rule.name}")
```

</div>

### Example 2: Creating a Deny Rule for Specific Application

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Deny_FTP",
    "description": "Block FTP traffic",
    "folder": "Shared",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["ftp"],
    "service": ["application-default"],
    "action": "deny",
    "log_end": True,
}

new_rule = security_rule.create(rule_data)
print(f"Created Security Rule: {new_rule.name}")
```

</div>

### Example 3: Updating a Rule to Add Tags

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "tag": ["PCI", "Critical"],
}

updated_rule = security_rule.update(rule_id, update_data)
print(f"Updated Rule Tags: {updated_rule.tag}")
```

</div>

### Example 4: Listing Rules with a Name Filter

<div class="termy">

<!-- termynal -->

```python
rules = security_rule.list(folder='Shared', name='Allow_DNS')

for rule in rules:
    print(f"Found Rule: {rule.name}")
```

</div>

### Example 5: Deleting a Security Rule

<div class="termy">

<!-- termynal -->

```python
security_rule.delete(new_rule.id)
print(f"Deleted Security Rule: {new_rule.name}")
```

</div>

### Example 6: Creating a Rule with Profile Settings

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Allow_HTTP_With_Profile",
    "description": "Allow HTTP traffic with security profiles",
    "folder": "Shared",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["web-browsing"],
    "service": ["application-default"],
    "action": "allow",
    "profile_setting": {
        "group": ["best-practice"]
    },
    "log_end": True,
}

new_rule = security_rule.create(rule_data)
print(f"Created Security Rule with Profiles: {new_rule.name}")
```

</div>

### Example 7: Creating a Rule with User and HIP Profiles

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Allow_VPN_Users",
    "description": "Allow traffic for VPN users with specific HIP profiles",
    "folder": "Shared",
    "from": ["vpn-zone"],
    "to": ["datacenter-zone"],
    "source": ["any"],
    "destination": ["datacenter-subnet"],
    "source_user": ["domain\\vpn-users"],
    "source_hip": ["corporate-laptop"],
    "application": ["any"],
    "service": ["any"],
    "action": "allow",
    "log_end": True,
}

new_rule = security_rule.create(rule_data)
print(f"Created Security Rule for VPN Users: {new_rule.name}")
```

</div>

### Example 8: Updating a Rule's Action

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "action": "drop",
}

updated_rule = security_rule.update(rule_id, update_data)
print(f"Updated Rule Action: {updated_rule.action}")
```

</div>

### Example 9: Listing Rules with Offset and Limit

<div class="termy">

<!-- termynal -->

```python
rules = security_rule.list(folder='Shared', offset=10, limit=5)

for rule in rules:
    print(f"Rule Name: {rule.name}")
```

</div>

### Example 10: Creating a Rule with Negated Source

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Block_Not_Internal",
    "description": "Block traffic not from internal network",
    "folder": "Shared",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["10.0.0.0/8"],
    "negate_source": True,
    "destination": ["any"],
    "application": ["any"],
    "service": ["any"],
    "action": "deny",
    "log_end": True,
}

new_rule = security_rule.create(rule_data)
print(f"Created Security Rule with Negated Source: {new_rule.name}")
```

</div>

---

## Full Example: Creating and Managing a Security Rule

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import SecurityRule

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create a SecurityRule instance
security_rule = SecurityRule(scm)

# Create a new Security Rule
rule_data = {
    "name": "Allow_SSH",
    "description": "Allow SSH traffic from management subnet",
    "folder": "Shared",
    "from": ["mgmt-zone"],
    "to": ["servers-zone"],
    "source": ["192.168.1.0/24"],
    "destination": ["192.168.2.0/24"],
    "application": ["ssh"],
    "service": ["application-default"],
    "action": "allow",
    "log_setting": "Send_to_SIEM",
    "log_end": True,
}

new_rule = security_rule.create(rule_data)
print(f"Created Security Rule: {new_rule.name} with ID: {new_rule.id}")

# Retrieve the created rule
retrieved_rule = security_rule.get(new_rule.id)
print(f"Retrieved Rule: {retrieved_rule.name}")

# Update the rule
update_data = {
    "description": "Allow SSH and RDP traffic from management subnet",
    "application": ["ssh", "ms-rdp"],
}

updated_rule = security_rule.update(new_rule.id, update_data)
print(f"Updated Rule: {updated_rule.name}")

# List rules in the folder
rules = security_rule.list(folder='Shared', limit=5)
print("List of Security Rules:")
for rule in rules:
    print(f"- {rule.name} (ID: {rule.id})")

# Delete the rule
security_rule.delete(new_rule.id)
print(f"Deleted Security Rule: {new_rule.name}")
```

</div>

---

## Related Models

- [SecurityRuleRequestModel](../../models/security/security_rules.md#SecurityRuleRequestModel)
- [SecurityRuleResponseModel](../../models/security/security_rules.md#SecurityRuleResponseModel)

