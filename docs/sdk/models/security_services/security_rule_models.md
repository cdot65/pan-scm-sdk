# Security Rule Models

This section covers the data models used for Security Rule configuration in the Strata Cloud Manager SDK.

---

## SecurityRuleRequestModel

Model used for creating and updating Security Rules.

### Key Attributes

- `name` (str): **Required.** Name of the Security Rule (pattern: `^[a-zA-Z0-9_ \.-]+$`)
- `disabled` (bool): Whether the rule is disabled (default: `False`)
- `description` (Optional[str]): Rule description
- `tag` (List[str]): Tags associated with the rule
- `from_` (List[str]): Source security zones (aliased as "from" in API)
- `to_` (List[str]): Destination security zones (aliased as "to" in API)
- `action` (Action): Rule action (allow, deny, drop, reset-client, reset-server, reset-both)

### Important Field Aliases

- `from_` → `from`: Source zones field is aliased in the API
- `to_` → `to`: Destination zones field is aliased in the API

### Example with Dictionary

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Allow_Web_Traffic",
    "folder": "Shared",
    "from": ["trust"],  # Note: Using "from" instead of "from_"
    "to": ["untrust"],  # Note: Using "to" instead of "to_"
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "application": ["web-browsing"],
    "action": "allow"
}
```

</div>

### Example with Pydantic Model

<div class="termy">

<!-- termynal -->

```python
from scm.models.security import SecurityRuleRequestModel

rule = SecurityRuleRequestModel(
    name="Allow_Web_Traffic",
    folder="Shared",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/8"],
    destination=["any"],
    application=["web-browsing"],
    action="allow"
)
```

</div>

## SecurityRuleResponseModel

Model used for Security Rule responses from the API.

### Additional Attributes

- `id` (str): UUID of the Security Rule
- All attributes from SecurityRuleRequestModel

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security import SecurityRuleResponseModel

response = SecurityRuleResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="Allow_Web_Traffic",
    folder="Shared",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/8"],
    destination=["any"],
    application=["web-browsing"],
    action="allow"
)
```

</div>

## ProfileSetting

Model for security profile settings within a rule.

### Attributes

- `group` (Optional[List[str]]): Security profile groups

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security import ProfileSetting

profile = ProfileSetting(
    group=["strict-security", "best-practice"]
)
```

</div>

## SecurityRuleMoveModel

Model for rule movement operations.

### Attributes

- `source_rule` (str): UUID of rule to move
- `destination` (RuleMoveDestination): Move destination (top, bottom, before, after)
- `rulebase` (Rulebase): Target rulebase (pre, post)
- `destination_rule` (Optional[str]): Reference rule UUID for before/after moves

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security import SecurityRuleMoveModel

move_config = SecurityRuleMoveModel(
    source_rule="123e4567-e89b-12d3-a456-426655440000",
    destination="before",
    rulebase="pre",
    destination_rule="987fcdeb-51d3-a456-426655440000"
)
```

</div>

## Enums

### Action

- `allow`
- `deny`
- `drop`
- `reset_client`
- `reset_server`
- `reset_both`

### RuleMoveDestination

- `TOP`
- `BOTTOM`
- `BEFORE`
- `AFTER`

### Rulebase

- `PRE`
- `POST`

## Complete Example: Building a Comprehensive Security Rule Model

<div class="termy">

<!-- termynal -->

```python
from scm.models.security import (
    SecurityRuleRequestModel,
    ProfileSetting,
    Action
)

# Create a comprehensive security rule
rule = SecurityRuleRequestModel(
    name="Comprehensive_Security_Rule",
    description="Complete example of security rule configuration",
    folder="Shared",
    from_=["trust", "internal"],
    to_=["untrust"],
    source=["10.0.0.0/8", "192.168.0.0/16"],
    negate_source=False,
    source_user=["domain\\vpn-users"],
    source_hip=["host-profile"],
    destination=["any"],
    negate_destination=False,
    application=["web-browsing", "ssl", "http2"],
    service=["application-default"],
    category=["any"],
    action=Action.allow,
    profile_setting=ProfileSetting(
        group=["strict-security"]
    ),
    log_setting="default-logging",
    log_start=True,
    log_end=True,
    tag=["production", "web-traffic"],
    disabled=False
)

# Validate and export the model
validated_data = rule.model_dump(exclude_none=True, by_alias=True)
print("Validated Rule Configuration:")
print(validated_data)
```

</div>