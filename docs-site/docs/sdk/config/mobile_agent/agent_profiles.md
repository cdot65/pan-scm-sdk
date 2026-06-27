# GlobalProtect Agent Profiles (Application Settings) Configuration Object

Manages GlobalProtect agent profiles in Palo Alto Networks Strata Cloud Manager. Agent profiles control the GlobalProtect app behavior for mobile users: agent UI options, authentication overrides, gateways, app configuration (connect method, tunnel MTU), HIP collection, and more.

:::note
The Strata Cloud Manager UI refers to this resource as **App Settings** / **Application Settings** (under Workflows → GlobalProtect App). The underlying API resource is `agent-profiles`.
:::

## Class Overview

The `AgentProfiles` class inherits from `BaseObject` and provides CRUD operations for GlobalProtect agent profile objects.

Unlike most SDK resources, the agent-profiles API exposes **no `/{id}` paths**: objects are addressed by `name` within the `Mobile Users` folder. Updates are sent to the collection endpoint and deletes are performed by name.

### Methods

| Method     | Description                          | Parameters                                | Return Type                              |
|------------|--------------------------------------|-------------------------------------------|------------------------------------------|
| `create()` | Creates a new agent profile          | `data: Dict[str, Any]`                    | `AgentProfilesResponseModel`             |
| `update()` | Updates an existing profile by name  | `data: Dict[str, Any]`                    | `Optional[AgentProfilesResponseModel]`   |
| `delete()` | Deletes an agent profile by name     | `name: str`, `folder: str`                | `None`                                   |
| `list()`   | Lists profiles with filtering        | `folder: str`, `name: Optional[str]`, `**filters` | `List[AgentProfilesResponseModel]` |
| `fetch()`  | Gets a profile by name and folder    | `name: str`, `folder: str`                | `AgentProfilesResponseModel`             |

:::note
`update()` returns `None` when the API responds with `200 OK` and no body (the documented behavior); use `fetch()` afterwards if you need the updated object.
:::

### Model Attributes

| Attribute                              | Type                                  | Required | Description                                              |
|----------------------------------------|---------------------------------------|----------|----------------------------------------------------------|
| `name`                                 | str                                   | Yes      | Name of the agent profile                                |
| `folder`                               | str                                   | Yes*     | Must be "Mobile Users" for all operations                |
| `agent_ui`                             | AgentUI                               | No       | Agent UI options (passcode, overrides, welcome page)     |
| `authentication_override`              | AuthenticationOverride                | No       | Authentication override cookie settings                  |
| `certificate`                          | AgentProfileCertificate               | No       | Certificate profile matching criteria                    |
| `client_certificate`                   | ClientCertificate                     | No       | Local or SCEP client certificate                         |
| `custom_checks`                        | CustomChecks                          | No       | Custom plist/registry matching criteria                  |
| `gateways`                             | Gateways                              | No       | External and internal gateway configuration              |
| `gp_app_config`                        | GPAppConfig                           | No       | App config (connect-method, tunnel-mtu)                  |
| `hip_collection`                       | HipCollection                         | No       | HIP data collection settings                             |
| `internal_host_detection`              | InternalHostDetection                 | No       | Internal host detection (IPv4)                           |
| `internal_host_detection_v6`           | InternalHostDetectionV6               | No       | Internal host detection (IPv6)                           |
| `machine_account_exists_with_serialno` | MachineAccountExistsWithSerialno      | No       | Machine account exists with serial number setting        |
| `os`                                   | List[AgentProfileOperatingSystem]     | No       | Operating systems the profile applies to                 |
| `save_user_credentials`                | SaveUserCredentials                   | No       | Save user credentials behavior ("0"–"3")                 |
| `source_user`                          | List[str]                             | No       | Source users the profile applies to                      |
| `third_party_vpn_clients`              | List[ThirdPartyVpnClient]             | No       | Supported third party VPN clients                        |

\* Required for create and update operations (sent as a query parameter)

### Exceptions

| Exception                    | HTTP Code | Description                          |
|------------------------------|-----------|--------------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or folder value |
| `MissingQueryParameterError` | 400       | Missing required parameters          |
| `ObjectNotPresentError`      | 404       | Agent profile not found              |
| `AuthenticationError`        | 401       | Authentication failed                |
| `ServerError`                | 500       | Internal server error                |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

agent_profiles = client.agent_profile
```

## Methods

### List Agent Profiles

```python
profiles = client.agent_profile.list(folder="Mobile Users")

for profile in profiles:
    print(f"{profile.name}: os={profile.os}")
```

### Fetch an Agent Profile

```python
profile = client.agent_profile.fetch(name="windows-profile", folder="Mobile Users")
print(profile.model_dump(exclude_unset=True))
```

### Create an Agent Profile

```python
profile_data = {
    "name": "windows-profile",
    "folder": "Mobile Users",
    "os": ["Windows"],
    "source_user": ["any"],
    "agent_ui": {
        "agent_user_override_timeout": 30,
        "max_agent_user_overrides": 5,
        "passcode": "secret-passcode",
    },
    "gp_app_config": {
        "config": [
            {"name": "connect-method", "value": ["user-logon"]},
            {"name": "tunnel-mtu", "value": [1400]},
        ]
    },
    "gateways": {
        "external": {
            "list": [
                {
                    "name": "us-east-gateway",
                    "choice": {"fqdn": "gw.example.com"},
                    "manual": True,
                    "priority_rule": [{"name": "rule-1", "priority": "1"}],
                }
            ]
        }
    },
}

new_profile = client.agent_profile.create(profile_data)
print(f"Created: {new_profile.name}")
```

### Update an Agent Profile

```python
update_data = {
    "name": "windows-profile",   # addressed by name, no id
    "folder": "Mobile Users",
    "os": ["Windows", "Mac"],
    "save_user_credentials": "1",
}

result = client.agent_profile.update(update_data)
# The API returns 200 OK with no body; re-fetch if you need the updated object
updated = client.agent_profile.fetch(name="windows-profile")
```

### Delete an Agent Profile

```python
client.agent_profile.delete(name="windows-profile", folder="Mobile Users")
```

## Related Documentation

- [Agent Profiles Models](../../models/mobile_agent/agent_profiles_models.md)
- [Mobile Agent Configuration Overview](index.md)
