# Anti-Spyware Profile Models

This section covers the data models associated with the `AntiSpywareProfile` configuration object.

---

## AntiSpywareProfileRequestModel

Used when creating or updating an anti-spyware profile object.

### Attributes

- `name` (str): **Required.** The name of the anti-spyware profile.
- `description` (Optional[str]): A description of the anti-spyware profile.
- `cloud_inline_analysis` (Optional[bool]): Enable or disable cloud inline analysis. Defaults to False.
- `inline_exception_edl_url` (Optional[List[str]]): List of inline exception EDL URLs.
- `inline_exception_ip_address` (Optional[List[str]]): List of inline exception IP addresses.
- `mica_engine_spyware_enabled` (Optional[List[MicaEngineSpywareEnabledEntry]]): List of MICA engine spyware enabled
  entries.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the profile is defined.
    - `snippet` (Optional[str]): The snippet where the profile is defined.
    - `device` (Optional[str]): The device where the profile is defined.
- `rules` (List[RuleRequest]): **Required.** List of rules for the profile.
- `threat_exception` (Optional[List[ThreatExceptionRequest]]): List of threat exceptions for the profile.

### Example

<div class="termy">

<!-- termynal -->

```python
anti_spyware_profile_request = AntiSpywareProfileRequestModel(
    name="test_profile",
    description="Test anti-spyware profile",
    folder="Prisma Access",
    rules=[
        RuleRequest(
            name="rule1",
            severity=["critical", "high"],
            category="spyware",
            action=ActionRequest(root={"alert": {}})
        )
    ]
)
```

</div>

---

## AntiSpywareProfileResponseModel

Used when parsing anti-spyware profile objects retrieved from the API.

### Attributes

- `id` (str): The UUID of the anti-spyware profile object.
- `name` (str): The name of the anti-spyware profile.
- `description` (Optional[str]): A description of the anti-spyware profile.
- `cloud_inline_analysis` (Optional[bool]): Cloud inline analysis setting.
- `inline_exception_edl_url` (Optional[List[str]]): List of inline exception EDL URLs.
- `inline_exception_ip_address` (Optional[List[str]]): List of inline exception IP addresses.
- `mica_engine_spyware_enabled` (Optional[List[MicaEngineSpywareEnabledEntry]]): List of MICA engine spyware enabled
  entries.
- **Container Type Fields**:
    - `folder` (Optional[str]): The folder where the profile is defined.
    - `snippet` (Optional[str]): The snippet where the profile is defined.
    - `device` (Optional[str]): The device where the profile is defined.
- `rules` (List[RuleResponse]): List of rules for the profile.
- `threat_exception` (Optional[List[ThreatExceptionResponse]]): List of threat exceptions for the profile.

### Example

<div class="termy">

<!-- termynal -->

```python
anti_spyware_profile_response = AntiSpywareProfileResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="test_profile",
    description="Test anti-spyware profile",
    folder="Prisma Access",
    rules=[
        RuleResponse(
            name="rule1",
            severity=["critical", "high"],
            category="spyware",
            action=ActionResponse(root={"alert": {}})
        )
    ]
)
```

</div>

---

## Additional Models

### MicaEngineSpywareEnabledEntry

Represents an entry in the 'mica_engine_spyware_enabled' list.

#### Attributes

- `name` (str): Name of the MICA engine spyware detector.
- `inline_policy_action` (InlinePolicyAction): Action to be taken by the inline policy.

### Example

<div class="termy">

<!-- termynal -->

```python
mica_entry = MicaEngineSpywareEnabledEntry(
    name="mica_detector1",
    inline_policy_action=InlinePolicyAction.alert
)
```

</div>

### RuleRequest and RuleResponse

Represents a rule in the anti-spyware profile.

#### Attributes

- `name` (str): Rule name.
- `severity` (List[Severity]): List of severities.
- `category` (Category): Category of the rule.
- `threat_name` (Optional[str]): Threat name.
- `packet_capture` (Optional[PacketCapture]): Packet capture setting.
- `action` (ActionRequest or ActionResponse): Action to be taken.

### Example

<div class="termy">

<!-- termynal -->

```python
rule_request = RuleRequest(
    name="rule1",
    severity=[Severity.critical, Severity.high],
    category=Category.spyware,
    action=ActionRequest(root={"alert": {}})
)
```

</div>

### ThreatExceptionRequest and ThreatExceptionResponse

Represents a threat exception in the anti-spyware profile.

#### Attributes

- `name` (str): Threat exception name.
- `packet_capture` (PacketCapture): Packet capture setting.
- `exempt_ip` (Optional[List[ExemptIpEntry]]): Exempt IP list.
- `notes` (Optional[str]): Notes.
- `action` (ActionRequest or ActionResponse): Action to be taken.

### Example

<div class="termy">

<!-- termynal -->

```python
threat_exception_request = ThreatExceptionRequest(
    name="exception1",
    packet_capture=PacketCapture.single_packet,
    action=ActionRequest(root={"allow": {}}),
    exempt_ip=[ExemptIpEntry(name="10.0.0.1")]
)
```

</div>

### ActionRequest and ActionResponse

Represents the 'action' field in rules and threat exceptions.

#### Methods

- `get_action_name() -> str`: Returns the name of the action.

### Example

<div class="termy">

<!-- termynal -->

```python
action_request = ActionRequest(root={"block_ip": {"track_by": "source", "duration": 300}})
print(f"Action name: {action_request.get_action_name()}")
```

</div>

### Enums

- `InlinePolicyAction`: Enumeration of allowed inline policy actions.
- `PacketCapture`: Enumeration of packet capture options.
- `Severity`: Enumeration of severity levels.
- `Category`: Enumeration of threat categories.

### Example

<div class="termy">

<!-- termynal -->

```python
severity = Severity.high
category = Category.dns_security
packet_capture = PacketCapture.extended_capture
```

</div>

---

## Full Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security import (
    AntiSpywareProfileRequestModel,
    RuleRequest,
    ActionRequest,
    ThreatExceptionRequest,
    MicaEngineSpywareEnabledEntry,
    ExemptIpEntry,
    Severity,
    Category,
    PacketCapture,
    InlinePolicyAction
)

# Create a comprehensive anti-spyware profile request
profile_request = AntiSpywareProfileRequestModel(
    name="comprehensive_profile",
    description="A comprehensive anti-spyware profile",
    folder="Prisma Access",
    cloud_inline_analysis=True,
    inline_exception_edl_url=["http://example.com/edl1"],
    inline_exception_ip_address=["192.168.1.1"],
    mica_engine_spyware_enabled=[
        MicaEngineSpywareEnabledEntry(
            name="mica_detector1",
            inline_policy_action=InlinePolicyAction.alert
        )
    ],
    rules=[
        RuleRequest(
            name="rule1",
            severity=[Severity.critical, Severity.high],
            category=Category.spyware,
            action=ActionRequest(root={"alert": {}})
        ),
        RuleRequest(
            name="rule2",
            severity=[Severity.medium],
            category=Category.dns_security,
            action=ActionRequest(root={"drop": {}})
        )
    ],
    threat_exception=[
        ThreatExceptionRequest(
            name="exception1",
            packet_capture=PacketCapture.single_packet,
            action=ActionRequest(root={"allow": {}}),
            exempt_ip=[ExemptIpEntry(name="10.0.0.1")]
        )
    ]
)

# Convert the model to a dictionary
profile_dict = profile_request.model_dump(exclude_unset=True)

print("Anti-Spyware Profile Request:")
print(profile_dict)
```

</div>

This example demonstrates how to create a comprehensive `AntiSpywareProfileRequestModel` object with various settings,
including rules, threat exceptions, and MICA engine configurations. The resulting object can be used with the
`AntiSpywareProfile.create()` method to create a new anti-spyware profile in the Strata Cloud Manager.
