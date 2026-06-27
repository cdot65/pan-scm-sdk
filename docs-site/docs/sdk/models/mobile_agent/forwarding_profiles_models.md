# GlobalProtect Forwarding Profile Models

Pydantic models for GlobalProtect forwarding profiles in Palo Alto Networks Strata Cloud Manager.

## Model Hierarchy

| Model                             | Purpose                                              |
|-----------------------------------|------------------------------------------------------|
| `ForwardingProfileBaseModel`      | Common fields shared across all CRUD operations      |
| `ForwardingProfileCreateModel`    | Fields for creating new forwarding profiles          |
| `ForwardingProfileUpdateModel`    | Fields for updating profiles (adds optional `id`)    |
| `ForwardingProfileResponseModel`  | Fields returned by the API (adds `id`)               |

## Base Model Attributes

| Attribute           | Type             | Required | Default | Description                                                  |
|---------------------|------------------|----------|---------|--------------------------------------------------------------|
| `name`              | str              | Yes      | None    | Profile name (max 64 chars, pattern `^[0-9a-zA-Z._-]+$`)     |
| `description`       | str              | No       | None    | Description (max 1023 chars)                                  |
| `definition_method` | DefinitionMethod | No       | rules   | `rules` or `pac-file`                                         |
| `type`              | Union            | No       | None    | One of the three profile type models below                   |

## Profile Type Models

The `type` field accepts exactly one of three wrapper models, matching the API's `oneOf` schema:

| Model                                  | Wrapper key            | Config model            |
|----------------------------------------|------------------------|-------------------------|
| `ForwardingProfilePacFile`             | `pac_file`             | `BasicForwardingConfig` |
| `ForwardingProfileGlobalProtectProxy`  | `global_protect_proxy` | `BasicForwardingConfig` |
| `ForwardingProfileZtnaAgent`           | `ztna_agent`           | `ZtnaForwardingConfig`  |

### BasicForwardingConfig / ZtnaForwardingConfig

| Attribute          | Type                      | Required | Default | Description               |
|--------------------|---------------------------|----------|---------|---------------------------|
| `pac_upload`       | bool                      | No       | False   | User upload PAC file      |
| `forwarding_rules` | List[ForwardingRule*]     | No       | None    | The forwarding rules      |
| `block_rule`       | BlockRule*                | No       | None    | The block rule            |

`BasicForwardingConfig` uses `ForwardingRuleBasic`/`BlockRuleBasic`; `ZtnaForwardingConfig` uses `ForwardingRuleZtna`/`BlockRuleZtna`.

### ForwardingRuleBasic

| Attribute        | Type | Required | Default  | Description                                |
|------------------|------|----------|----------|--------------------------------------------|
| `name`           | str  | Yes      | None     | Rule name (max 64 chars, `[0-9a-zA-Z._-]`) |
| `enabled`        | bool | No       | True     | Enable the rule                            |
| `user_locations` | str  | No       | "Any"    | User locations (max 64 chars)              |
| `destinations`   | str  | No       | "Any"    | Destinations (max 64 chars)                |
| `connectivity`   | str  | No       | "direct" | Connectivity method (max 64 chars)         |

### ForwardingRuleZtna

Adds to the basic rule fields:

| Attribute             | Type            | Required | Default | Description                                          |
|-----------------------|-----------------|----------|---------|------------------------------------------------------|
| `traffic_type`        | ZtnaTrafficType | No       | dns     | `dns`, `dns-and-network-traffic`, or `network-traffic` |
| `source_applications` | str             | No       | "Any"   | Source applications                                  |

### BlockRuleBasic

| Attribute   | Type                   | Required | Default | Description               |
|-------------|------------------------|----------|---------|---------------------------|
| `enable`    | bool                   | No       | None    | Enable block rule         |
| `allow_tcp` | BlockRuleBasicAllowTcp | No       | None    | Allow-TCP settings        |
| `allow_udp` | BlockRuleBasicAllowUdp | No       | None    | Allow-UDP settings        |

### BlockRuleZtna

All fields are optional booleans controlling tunnel traffic blocking behavior, e.g.
`block_all_other_unmatched_outbound_connections` (default False),
`allow_icmp_for_troubleshooting` (default False),
`enforcer_fqdn_dns_resolution_via_dns_servers` (default True).

## Enums

| Enum               | Values                                              |
|--------------------|-----------------------------------------------------|
| `DefinitionMethod` | `rules`, `pac-file`                                 |
| `ZtnaTrafficType`  | `dns`, `dns-and-network-traffic`, `network-traffic` |

## Usage Example

```python
from scm.models.mobile_agent.forwarding_profiles import (
    ForwardingProfileCreateModel,
    ForwardingProfileZtnaAgent,
    ForwardingRuleZtna,
    ZtnaForwardingConfig,
    ZtnaTrafficType,
)

profile = ForwardingProfileCreateModel(
    name="corp-forwarding",
    description="Corporate ZTNA forwarding profile",
    type=ForwardingProfileZtnaAgent(
        ztna_agent=ZtnaForwardingConfig(
            forwarding_rules=[
                ForwardingRuleZtna(
                    name="internal-apps",
                    traffic_type=ZtnaTrafficType.DNS_AND_NETWORK_TRAFFIC,
                    destinations="internal-destinations",
                )
            ]
        )
    ),
)

payload = profile.model_dump(exclude_unset=True)
```

## Related Documentation

- [Forwarding Profiles Configuration](../../config/mobile_agent/forwarding_profiles.md)
- [Forwarding Profile Destination Models](forwarding_profile_destinations_models.md)
