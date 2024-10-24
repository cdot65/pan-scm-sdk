# Rule Based Move Models

This section covers the data models associated with moving Security Rules within their rulebase.

---

## SecurityRuleMoveModel

Used when moving a Security Rule to a new position within the rulebase.

### Attributes

- `source_rule` (str): **Required.** UUID of the security rule to be moved.
- `destination` (Destination): **Required.** Where to move the rule (`top`, `bottom`, `before`, `after`).
- `rulebase` (Rulebase): **Required.** Which rulebase to use (`pre`, `post`).
- `destination_rule` (Optional[str]): UUID of the reference rule. Required only when `destination` is `before` or
  `after`.

### Example with Python Dictionary

<div class="termy">

<!-- termynal -->

```python
move_data = {
    "source_rule": "123e4567-e89b-12d3-a456-426655440000",
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}
```

</div>

### Example with Pydantic Model

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rule_move import SecurityRuleMoveModel

move_request = SecurityRuleMoveModel(
    source_rule="123e4567-e89b-12d3-a456-426655440000",
    destination="before",
    rulebase="pre",
    destination_rule="987fcdeb-51d3-a456-426655440000"
)

print(move_request.model_dump_json(indent=2))
```

</div>

---

## Enums

### Destination

Enumeration of allowed destinations for rule movement:

- `top`: Move rule to the top of the rulebase
- `bottom`: Move rule to the bottom of the rulebase
- `before`: Move rule before a specified rule
- `after`: Move rule after a specified rule

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rule_move import Destination

print(f"Available Destinations: {[dest.value for dest in Destination]}")
```

</div>

### Rulebase

Enumeration of allowed rulebase values:

- `pre`: Pre-rulebase
- `post`: Post-rulebase

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rule_move import Rulebase

print(f"Available Rulebases: {[base.value for base in Rulebase]}")
```

</div>

---

## Validators

The model includes validators to ensure data integrity:

- UUID fields (`source_rule` and `destination_rule`) are validated to ensure they contain valid UUIDs
- `destination_rule` is required when `destination` is `before` or `after`
- `destination_rule` must not be provided when `destination` is `top` or `bottom`

### Example: Moving to Top (No destination_rule needed)

<div class="termy">

<!-- termynal -->

```python
move_top = SecurityRuleMoveModel(
    source_rule="123e4567-e89b-12d3-a456-426655440000",
    destination="top",
    rulebase="pre"
)

print(move_top.model_dump_json(indent=2))
```

</div>

### Example: Invalid UUID Raises Error

<div class="termy">

<!-- termynal -->

```python
try:
    move_invalid = SecurityRuleMoveModel(
        source_rule="invalid-uuid",
        destination="top",
        rulebase="pre"
    )
except ValueError as e:
    print(f"Validation Error: {e}")
```

</div>

### Example: Missing Required destination_rule Raises Error

<div class="termy">

<!-- termynal -->

```python
try:
    move_invalid = SecurityRuleMoveModel(
        source_rule="123e4567-e89b-12d3-a456-426655440000",
        destination="before",
        rulebase="pre"
        # Missing required destination_rule
    )
except ValueError as e:
    print(f"Validation Error: {e}")
```

</div>

---

## Full Example: Moving a Security Rule

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rule_move import SecurityRuleMoveModel, Destination, Rulebase

# Create a move request to place a rule before another rule
move_request = SecurityRuleMoveModel(
    source_rule="123e4567-e89b-12d3-a456-426655440000",
    destination=Destination.BEFORE,
    rulebase=Rulebase.PRE,
    destination_rule="987fcdeb-51d3-a456-426655440000"
)

# Print the JSON representation of the model
print(move_request.model_dump_json(indent=2))

# Validate the model
move_request.model_validate(move_request.model_dump())
print("Model validation successful")
```

</div>

This example demonstrates how to create a complete rule move request using the provided classes and enums.
It includes all required fields and shows how to properly structure a request to move a security rule
before another rule in the pre-rulebase.
