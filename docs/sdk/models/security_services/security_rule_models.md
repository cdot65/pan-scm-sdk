# Security Rule Models

This section covers the data models associated with the `SecurityRule` configuration object.

---

## SecurityRuleRequestModel

Used when creating or updating a Security Rule object.

### Attributes

- `name` (str): **Required.** The name of the Security Rule.
- `disabled` (bool): Whether the rule is disabled. Defaults to `False`.
- `description` (Optional[str]): A description of the Security Rule.
- `tag` (List[str]): Tags associated with the Security Rule.
- `from_` (List[str]): Source security zones.
- `source` (List[str]): Source addresses.
- `negate_source` (bool): Whether to negate the source addresses. Defaults to `False`.
- `source_user` (List[str]): Source users or groups.
- `source_hip` (List[str]): Source Host Integrity Profiles.
- `to_` (List[str]): Destination security zones.
- `destination` (List[str]): Destination addresses.
- `negate_destination` (bool): Whether to negate the destination addresses. Defaults to `False`.
- `destination_hip` (List[str]): Destination Host Integrity Profiles.
- `application` (List[str]): Applications.
- `service` (List[str]): Services.
- `category` (List[str]): URL categories.
- `action` (Action): Action to be taken when the rule is matched.
- `profile_setting` (Optional[ProfileSetting]): Security profile settings.
- `log_setting` (Optional[str]): Log forwarding profile.
- `schedule` (Optional[str]): Schedule for the rule.
- `log_start` (Optional[bool]): Log at session start.
- `log_end` (Optional[bool]): Log at session end.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the rule is defined.
    - `snippet` (Optional[str]): The snippet where the rule is defined.
    - `device` (Optional[str]): The device where the rule is defined.

### Example with Python Dictionary

<div class="termy">

<!-- termynal -->

```python
rule_data = {
    "name": "Block_Telnet",
    "folder": "Shared",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["telnet"],
    "action": "deny",
    "log_end": True,
}
```

</div>

### Example with Pydantic Model

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rules import SecurityRuleRequestModel

rule_request = SecurityRuleRequestModel(
    name="Block_Telnet",
    folder="Shared",
    from_=["trust"],
    to_=["untrust"],
    source=["any"],
    destination=["any"],
    application=["telnet"],
    action="deny",
    log_end=True,
)

print(rule_request.model_dump_json(indent=2))
```

</div>

---

## SecurityRuleResponseModel

Used when parsing Security Rule objects retrieved from the API.

### Attributes

- `id` (str): The UUID of the Security Rule.
- All attributes from `SecurityRuleRequestModel`.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rules import SecurityRuleResponseModel

rule_response = SecurityRuleResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="Allow_HTTP",
    folder="Shared",
    from_=["trust"],
    to_=["untrust"],
    source=["any"],
    destination=["any"],
    application=["web-browsing"],
    action="allow",
    log_end=True,
)

print(rule_response.model_dump_json(indent=2))
```

</div>

---

## ProfileSetting

Represents the `profile_setting` for a Security Rule.

### Attributes

- `group` (Optional[List[str]]): Security profile groups.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rules import ProfileSetting

profile_setting = ProfileSetting(
    group=["best-practice"]
)

print(profile_setting.model_dump_json(indent=2))
```

</div>

---

## Enums

### Action

Enumeration of allowed actions for Security Rules:

- `allow`
- `deny`
- `drop`
- `reset-client`
- `reset-server`
- `reset-both`

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rules import Action

print(f"Available Actions: {[action.value for action in Action]}")
```

</div>

---

## Validators

The models include validators to ensure data integrity:

- Fields like `from_`, `to_`, `source`, `destination`, etc., are validated to be lists of unique strings.
- Single strings are converted to lists.
- Duplicate items in lists raise a `ValueError`.

### Example: Single String Converted to List

<div class="termy">

<!-- termynal -->

```python
rule_request = SecurityRuleRequestModel(
    name="Single_String_Test",
    folder="Shared",
    from_="trust",
    to_="untrust",
    source="any",
    destination="any",
    application="ssh",
    action="allow",
    log_end=True,
)

print(rule_request.from_)  # Output: ['trust']
```

</div>

### Example: Duplicate Items Raise Error

<div class="termy">

<!-- termynal -->

```python
try:
    rule_request = SecurityRuleRequestModel(
        name="Duplicate_Test",
        folder="Shared",
        from_=["trust", "trust"],
        to_=["untrust"],
        source=["any"],
        destination=["any"],
        application=["ssh"],
        action="allow",
        log_end=True,
    )
except ValueError as e:
    print(f"Validation Error: {e}")
```

</div>

---

## Full Example: Creating a Comprehensive Security Rule Model

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rules import (
    SecurityRuleRequestModel,
    ProfileSetting,
    Action,
)

# Create a comprehensive Security Rule model
comprehensive_rule = SecurityRuleRequestModel(
    name="Comprehensive_Rule",
    description="A comprehensive security rule example",
    folder="Shared",
    from_=["trust", "vpn-zone"],
    to_=["datacenter-zone"],
    source=["10.0.0.0/8", "192.168.1.0/24"],
    destination=["192.168.2.0/24"],
    application=["ssh", "ms-rdp", "web-browsing"],
    service=["application-default"],
    category=["any"],
    action=Action.allow,
    profile_setting=ProfileSetting(
        group=["best-practice"]
    ),
    log_setting="Send_to_SIEM",
    log_start=True,
    log_end=True,
)

# Print the JSON representation of the model
print(comprehensive_rule.model_dump_json(indent=2))

# Validate the model
comprehensive_rule.model_validate(comprehensive_rule.model_dump())
print("Model validation successful")
```

</div>

This example demonstrates how to create a comprehensive Security Rule model using the provided classes and enums.
It includes multiple source zones, destinations, applications, profile settings, and logging options to showcase the
full capabilities of the model.

---

## SecurityRulesResponse

Represents the response for a Security Rules query.

### Attributes

- `data` (List[SecurityRuleResponseModel]): List of Security Rule objects.
- `offset` (int): Pagination offset.
- `total` (int): Total number of Security Rules available.
- `limit` (int): Pagination limit.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.security_rules import SecurityRulesResponse, SecurityRuleResponseModel

rules_response = SecurityRulesResponse(
    data=[
        SecurityRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="Allow_HTTP",
            folder="Shared",
            action="allow",
        ),
        SecurityRuleResponseModel(
            id="223e4567-e89b-12d3-a456-426655440001",
            name="Block_Telnet",
            folder="Shared",
            action="deny",
        ),
    ],
    offset=0,
    total=2,
    limit=100,
)

print(rules_response.model_dump_json(indent=2))
```

</div>
```