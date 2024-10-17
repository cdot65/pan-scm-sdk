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

---

## Additional Models

### MicaEngineSpywareEnabledEntry

Represents an entry in the 'mica_engine_spyware_enabled' list.

#### Attributes

- `name` (str): Name of the MICA engine spyware detector.
- `inline_policy_action` (InlinePolicyAction): Action to be taken by the inline policy.

### RuleRequest and RuleResponse

Represents a rule in the anti-spyware profile.

#### Attributes

- `name` (str): Rule name.
- `severity` (List[Severity]): List of severities.
- `category` (Category): Category of the rule.
- `threat_name` (Optional[str]): Threat name.
- `packet_capture` (Optional[PacketCapture]): Packet capture setting.
- `action` (ActionRequest or ActionResponse): Action to be taken.

### ThreatExceptionRequest and ThreatExceptionResponse

Represents a threat exception in the anti-spyware profile.

#### Attributes

- `name` (str): Threat exception name.
- `packet_capture` (PacketCapture): Packet capture setting.
- `exempt_ip` (Optional[List[ExemptIpEntry]]): Exempt IP list.
- `notes` (Optional[str]): Notes.
- `action` (ActionRequest or ActionResponse): Action to be taken.

### ActionRequest and ActionResponse

Represents the 'action' field in rules and threat exceptions.

#### Methods

- `get_action_name() -> str`: Returns the name of the action.

### Enums

- `InlinePolicyAction`: Enumeration of allowed inline policy actions.
- `PacketCapture`: Enumeration of packet capture options.
- `Severity`: Enumeration of severity levels.
- `Category`: Enumeration of threat categories.
