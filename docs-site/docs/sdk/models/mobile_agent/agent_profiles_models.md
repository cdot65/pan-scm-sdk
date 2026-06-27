# GlobalProtect Agent Profiles (Application Settings) Models

Pydantic models for GlobalProtect agent profiles in Palo Alto Networks Strata Cloud Manager.

:::note
The Strata Cloud Manager UI refers to this resource as **App Settings** / **Application Settings**. The underlying API resource is `agent-profiles`.
:::

## Model Hierarchy

| Model                        | Purpose                                                  |
|------------------------------|----------------------------------------------------------|
| `AgentProfilesBaseModel`     | Common fields shared across all operations               |
| `AgentProfilesCreateModel`   | Creating new profiles (requires `folder="Mobile Users"`) |
| `AgentProfilesUpdateModel`   | Updating profiles by name (requires `folder`)            |
| `AgentProfilesResponseModel` | API responses (ignores unknown fields)                   |

Agent profiles are addressed by `name` within the `Mobile Users` folder — there is no `id` field on any of these models.

## Enums

| Enum                          | Values                                                                  |
|-------------------------------|-------------------------------------------------------------------------|
| `AgentProfileOperatingSystem` | `Android`, `Chrome`, `IoT`, `Linux`, `Mac`, `Windows`, `WindowsUWP`, `iOS` |
| `SaveUserCredentials`         | `"0"` (no), `"1"` (yes), `"2"` (username only), `"3"` (with fingerprint) |
| `ThirdPartyVpnClient`         | `PAN Virtual Ethernet Adapter`, `Juniper Network Virtual Adapter`, `Cisco Systems VPN Adapter` |
| `ConnectMethodValue`          | `user-logon`, `pre-logon`, `on-demand`, `pre-logon-then-on-demand`      |
| `GatewayPriority`             | `"0"` (highest) through `"4"` (lowest), `"5"` (manual only)             |

## Nested Models

| Model                                | Description                                                       |
|--------------------------------------|-------------------------------------------------------------------|
| `AgentUI` / `WelcomePage`            | Agent UI options: override timeout/count, passcode, uninstall password, welcome page |
| `AuthenticationOverride` / `AcceptCookie` / `CookieLifetime` | Authentication override cookie generation and lifetime |
| `AgentProfileCertificate` / `CertificateCriteria` | Certificate profile matching criteria                |
| `ClientCertificate`                  | Local or SCEP client certificate                                  |
| `CustomChecks` / `CustomChecksCriteria` / `PlistEntry` / `PlistKeyEntry` / `RegistryKeyEntry` / `RegistryValueEntry` | Custom plist (macOS) and registry (Windows) matching criteria |
| `Gateways` / `ExternalGateways` / `ExternalGatewayEntry` / `InternalGateways` / `InternalGatewayEntry` / `GatewayChoice` / `GatewayAddress` / `GatewayPriorityRule` | External and internal gateway configuration |
| `GPAppConfig` / `ConnectMethodAppConfig` / `TunnelMtuAppConfig` | App configuration entries (discriminated union on `name`) |
| `HipCollection` / `HipCustomChecks` / `HipExclusion` (+ per-OS models) | HIP data collection, custom checks, and exclusions |
| `InternalHostDetection` / `InternalHostDetectionV6` | Internal host detection by IPv4/IPv6 address and hostname |
| `MachineAccountExistsWithSerialno`   | Machine account exists with serial number setting (`yes`/`no` empty objects) |

### Validation Highlights

- `folder` must be `"Mobile Users"` on all models; create and update additionally require it to be set.
- `GatewayChoice` enforces exactly one of `fqdn` or `ip` (mirrors the API's `oneOf`).
- `GPAppConfig.config` is a discriminated union: entries with `name="connect-method"` accept a single `ConnectMethodValue`; entries with `name="tunnel-mtu"` accept a single number between 1000 and 1420.
- `AgentUI`: `agent_user_override_timeout` 0–65535, `max_agent_user_overrides` 0–25, `passcode` 6–64 chars, `uninstall_password` 6–32 chars.
- `CookieLifetime`: days 1–365, hours 1–72, minutes 1–59.
- `HipCollection.max_wait_time`: 10–60 seconds; macOS plist and Windows registry key entries require `name`.

## Usage Example

```python
from scm.client import Scm
from scm.models.mobile_agent.agent_profiles import (
    AgentProfilesCreateModel,
    AgentProfileOperatingSystem,
)

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

profile = AgentProfilesCreateModel(
    name="windows-profile",
    folder="Mobile Users",
    os=[AgentProfileOperatingSystem.WINDOWS],
    gp_app_config={
        "config": [
            {"name": "connect-method", "value": ["user-logon"]},
            {"name": "tunnel-mtu", "value": [1400]},
        ]
    },
)

result = client.agent_profile.create(profile.model_dump(exclude_unset=True))
print(f"Created: {result.name}")
```

## Related Documentation

- [Agent Profiles Configuration](../../config/mobile_agent/agent_profiles.md)
- [Mobile Agent Models Overview](index.md)
