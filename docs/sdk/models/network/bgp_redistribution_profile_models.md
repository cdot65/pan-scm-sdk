# BGP Redistribution Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The BGP Redistribution Profile models provide a structured way to represent and validate BGP redistribution profile configuration data for Palo Alto Networks' Strata Cloud Manager. These models control which routing protocols' routes are redistributed into BGP, with per-protocol enable/disable, metric, and route map settings.

> **Important:** Unlike many other BGP configuration models that use oneOf (mutually exclusive) semantics, the protocols in a redistribution profile are **NOT mutually exclusive**. All three protocols (static, OSPF, and connected) can be configured simultaneously under the unicast container.

### Models

The module provides the following Pydantic models:

- `BgpRedistributionProfileBaseModel`: Base model with fields common to all BGP redistribution profile operations
- `BgpRedistributionProfileCreateModel`: Model for creating new BGP redistribution profiles
- `BgpRedistributionProfileUpdateModel`: Model for updating existing BGP redistribution profiles
- `BgpRedistributionProfileResponseModel`: Response model for BGP redistribution profile operations
- `BgpRedistributionIpv4`: IPv4 container for redistribution
- `BgpRedistributionUnicast`: Unicast redistribution containing static, OSPF, and connected protocols
- `BgpRedistributionProtocol`: Configuration for a single redistribution protocol

The `BgpRedistributionProfileBaseModel` and `BgpRedistributionProfileCreateModel` / `BgpRedistributionProfileUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `BgpRedistributionProfileResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### BgpRedistributionProfileBaseModel

This is the base model containing fields common to all BGP redistribution profile operations.

| Attribute | Type                   | Required | Default | Description                                                     |
|-----------|------------------------|----------|---------|-----------------------------------------------------------------|
| name      | str                    | Yes      | None    | Profile name.                                                   |
| ipv4      | BgpRedistributionIpv4  | No       | None    | IPv4 redistribution configuration.                              |
| folder    | str                    | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet   | str                    | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device    | str                    | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### BgpRedistributionProfileCreateModel

Inherits all fields from `BgpRedistributionProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### BgpRedistributionProfileUpdateModel

Extends `BgpRedistributionProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                               |
|-----------|------|----------|---------|-----------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP redistribution profile   |

### BgpRedistributionProfileResponseModel

Extends `BgpRedistributionProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                               |
|-----------|------|----------|---------|-----------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP redistribution profile   |

> **Note:** The `BgpRedistributionProfileResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### BgpRedistributionIpv4

IPv4 container for redistribution profiles.

| Attribute | Type                     | Required | Default | Description                          |
|-----------|--------------------------|----------|---------|--------------------------------------|
| unicast   | BgpRedistributionUnicast | No       | None    | Unicast redistribution configuration.|

### BgpRedistributionUnicast

Unicast redistribution containing static, OSPF, and connected protocol configurations. All three protocols can coexist -- they are NOT mutually exclusive.

| Attribute | Type                       | Required | Default | Description                     |
|-----------|----------------------------|----------|---------|---------------------------------|
| static    | BgpRedistributionProtocol  | No       | None    | Static route redistribution.    |
| ospf      | BgpRedistributionProtocol  | No       | None    | OSPF route redistribution.      |
| connected | BgpRedistributionProtocol  | No       | None    | Connected route redistribution. |

### BgpRedistributionProtocol

Configuration for a single redistribution protocol (static, OSPF, or connected).

| Attribute | Type | Required | Default | Description                         |
|-----------|------|----------|---------|-------------------------------------|
| enable    | bool | No       | None    | Enable redistribution for protocol. |
| metric    | int  | No       | None    | Metric value (1-65535).             |
| route_map | str  | No       | None    | Route map name to apply.            |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a profile (`BgpRedistributionProfileCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When a metric value is outside the valid range (1-65535).
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Container Validation in `BgpRedistributionProfileCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a BGP Redistribution Profile

#### Using a Dictionary

```python
from scm.models.network import BgpRedistributionProfileCreateModel

profile_data = {
    "name": "redist-profile-1",
    "ipv4": {
        "unicast": {
            "static": {
                "enable": True,
                "metric": 100,
                "route_map": "static-to-bgp-map",
            },
            "ospf": {
                "enable": True,
                "metric": 200,
                "route_map": "ospf-to-bgp-map",
            },
            "connected": {
                "enable": True,
                "metric": 50,
            },
        },
    },
    "folder": "Routing",
}

# Validate and create model instance
profile = BgpRedistributionProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import (
    BgpRedistributionProfileCreateModel,
    BgpRedistributionIpv4,
    BgpRedistributionUnicast,
    BgpRedistributionProtocol,
)

# All three protocols can be configured simultaneously
profile = BgpRedistributionProfileCreateModel(
    name="redist-profile-2",
    ipv4=BgpRedistributionIpv4(
        unicast=BgpRedistributionUnicast(
            static=BgpRedistributionProtocol(
                enable=True,
                metric=100,
                route_map="static-rm",
            ),
            ospf=BgpRedistributionProtocol(
                enable=True,
                metric=200,
            ),
            connected=BgpRedistributionProtocol(
                enable=True,
            ),
        ),
    ),
    folder="Routing",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Profile with Only Static Redistribution

```python
from scm.models.network import (
    BgpRedistributionProfileCreateModel,
    BgpRedistributionIpv4,
    BgpRedistributionUnicast,
    BgpRedistributionProtocol,
)

# Only redistribute static routes
profile = BgpRedistributionProfileCreateModel(
    name="redist-static-only",
    ipv4=BgpRedistributionIpv4(
        unicast=BgpRedistributionUnicast(
            static=BgpRedistributionProtocol(
                enable=True,
                metric=100,
                route_map="static-filter",
            ),
        ),
    ),
    folder="Routing",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a BGP Redistribution Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing profile
existing = client.bgp_redistribution_profile.fetch(
    name="redist-profile-1", folder="Routing"
)

# Modify metric for static redistribution
existing.ipv4.unicast.static.metric = 150

# Disable OSPF redistribution
existing.ipv4.unicast.ospf.enable = False

# Pass modified object to update()
updated = client.bgp_redistribution_profile.update(existing)
print(f"Updated profile: {updated.name}")
```
