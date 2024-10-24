# Rule Move Configuration Object

The `SecurityRuleMoveModel` class is used to manage Security Rule movement operations in the Strata Cloud Manager.
It provides methods to reposition Security Rules within their rulebase, supporting operations such as
moving rules to the top/bottom or before/after other rules.

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

## Importing the SecurityRuleMoveModel Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.security import SecurityRuleMoveModel

rule_move = SecurityRuleMoveModel(api_client)
```

</div>

## Methods

### `move(data: Dict[str, Any]) -> None`

Moves a Security Rule to a new position within the rulebase.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the move operation parameters:
    - `source_rule` (str): UUID of the rule to move
    - `destination` (str): Where to move the rule (`top`, `bottom`, `before`, `after`)
    - `rulebase` (str): Which rulebase to use (`pre`, `post`)
    - `destination_rule` (str): UUID of reference rule (required for `before`/`after`)

**Example:**

<div class="termy">

<!-- termynal -->

```python
move_data = {
    "source_rule": "123e4567-e89b-12d3-a456-426655440000",
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}

rule_move.move(move_data)
print("Security Rule moved successfully")
```

</div>

---

## Usage Examples

### Example 1: Moving a Rule to the Top

<div class="termy">

<!-- termynal -->

```python
move_data = {
    "source_rule": "123e4567-e89b-12d3-a456-426655440000",
    "destination": "top",
    "rulebase": "pre"
}

rule_move.move(move_data)
print("Moved rule to top of pre-rulebase")
```

</div>

### Example 2: Moving a Rule to the Bottom

<div class="termy">

<!-- termynal -->

```python
move_data = {
    "source_rule": "123e4567-e89b-12d3-a456-426655440000",
    "destination": "bottom",
    "rulebase": "post"
}

rule_move.move(move_data)
print("Moved rule to bottom of post-rulebase")
```

</div>

### Example 3: Moving a Rule Before Another Rule

<div class="termy">

<!-- termynal -->

```python
move_data = {
    "source_rule": "123e4567-e89b-12d3-a456-426655440000",
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}

rule_move.move(move_data)
print("Moved rule before specified rule")
```

</div>

### Example 4: Moving a Rule After Another Rule

<div class="termy">

<!-- termynal -->

```python
move_data = {
    "source_rule": "123e4567-e89b-12d3-a456-426655440000",
    "destination": "after",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}

rule_move.move(move_data)
print("Moved rule after specified rule")
```

</div>

---

## Full Example: Creating and Reordering Security Rules

This example demonstrates creating multiple security rules and then reordering them using the SecurityRuleMoveModel
configuration
object.

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import SecurityRule, SecurityRuleMoveModel

# Initialize the SCM client
api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create SecurityRule instance
sec_rules = SecurityRule(api_client)

# Define first rule
rule_data1 = {
    "name": "Allow_HTTP_With_Profile",
    "description": "Allow HTTP traffic with security profiles",
    "folder": "Texas",
    "from": ["lan"],
    "to": ["wan"],
    "action": "allow",
    "profile_setting": {
        "group": ["best-practice"]
    },
    "log_end": True,
}

# Define second rule
rule_data2 = {
    "name": "Allow_HTTPS_With_Profile",
    "description": "Allow HTTPS traffic with security profiles",
    "folder": "Texas",
    "from": ["lan"],
    "to": ["wan"],
    "application": ["web-browsing"],
    "action": "allow",
    "profile_setting": {
        "group": ["best-practice"]
    },
    "log_end": True,
}

# Create both rules
rule1 = sec_rules.create(rule_data1)
rule2 = sec_rules.create(rule_data2)

# Create SecurityRuleMoveModel instance
move_rules = SecurityRuleMoveModel(api_client)

# Move rule2 before rule1
move_data = {
    "source_rule": rule2.id,
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": rule1.id,
}

# Perform the move operation
move_rules.move(move_data)
print("Successfully reordered security rules")
```

</div>

---

## Related Models

- [SecurityRuleMoveModel](../../models/security_services/security_rule_move_models#SecurityRuleMoveModel)
