# IPsec Tunnel Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The IPsec Tunnel models provide a structured way to represent and validate IPsec tunnel configuration data for Palo Alto Networks' Strata Cloud Manager. These models ensure data integrity when creating and updating IPsec tunnels, enforcing proper auto key settings, proxy ID configurations, tunnel monitoring, container specifications, and field validations.

### Models

The module provides the following Pydantic models:

- `IPsecTunnelBaseModel`: Base model with fields common to all IPsec tunnel operations
- `IPsecTunnelCreateModel`: Model for creating new IPsec tunnels
- `IPsecTunnelUpdateModel`: Model for updating existing IPsec tunnels
- `IPsecTunnelResponseModel`: Response model for IPsec tunnel operations
- `AutoKey`: Auto key configuration model for IPsec tunnel
- `IkeGatewayRef`: Reference model for IKE gateways
- `ProxyId`: Proxy ID configuration model
- `ProxyIdProtocol`: Protocol configuration model for proxy ID
- `PortPair`: Local and remote port pair model
- `TunnelMonitor`: Tunnel monitor configuration model

The `IPsecTunnelBaseModel` and `IPsecTunnelCreateModel` / `IPsecTunnelUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `IPsecTunnelResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### IPsecTunnelBaseModel

This is the base model containing fields common to all IPsec tunnel operations.

| Attribute                 | Type          | Required | Default | Description                                                     |
|---------------------------|---------------|----------|---------|-----------------------------------------------------------------|
| name                      | str           | Yes      | None    | Name of the IPsec tunnel. Max 63 chars.                         |
| auto_key                  | AutoKey       | Yes      | None    | Auto key configuration.                                        |
| anti_replay               | bool          | No       | None    | Enable anti-replay protection.                                 |
| copy_tos                  | bool          | No       | False   | Copy TOS header.                                               |
| enable_gre_encapsulation  | bool          | No       | False   | Enable GRE encapsulation.                                      |
| tunnel_monitor            | TunnelMonitor | No       | None    | Tunnel monitor configuration.                                  |
| folder                    | str           | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet                   | str           | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device                    | str           | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### IPsecTunnelCreateModel

Inherits all fields from `IPsecTunnelBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### IPsecTunnelUpdateModel

Extends `IPsecTunnelBaseModel` by adding:

| Attribute | Type | Required | Default | Description                              |
|-----------|------|----------|---------|------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the IPsec tunnel |

### IPsecTunnelResponseModel

Extends `IPsecTunnelBaseModel` by adding:

| Attribute | Type | Required | Default | Description                              |
|-----------|------|----------|---------|------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the IPsec tunnel |

> **Note:** The `IPsecTunnelResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### AutoKey

This model defines the auto key configuration for IPsec tunnels.

| Attribute          | Type             | Required | Default | Description                    |
|--------------------|------------------|----------|---------|--------------------------------|
| ike_gateway        | List[IkeGatewayRef] | Yes   | None    | List of IKE gateway references.|
| ipsec_crypto_profile | str            | Yes      | None    | IPsec crypto profile name.     |
| proxy_id           | List[ProxyId]    | No       | None    | List of proxy IDs.             |
| proxy_id_v6        | List[ProxyId]    | No       | None    | List of IPv6 proxy IDs.        |

### IkeGatewayRef

This model defines a reference to an IKE gateway.

| Attribute | Type | Required | Default | Description               |
|-----------|------|----------|---------|---------------------------|
| name      | str  | Yes      | None    | The name of the IKE gateway.|

### ProxyId

This model defines the proxy ID configuration for IPsec tunnels.

| Attribute | Type            | Required | Default | Description              |
|-----------|-----------------|----------|---------|--------------------------|
| name      | str             | Yes      | None    | The name of the proxy ID.|
| local     | str             | No       | None    | Local address or subnet. |
| remote    | str             | No       | None    | Remote address or subnet.|
| protocol  | ProxyIdProtocol | No       | None    | Protocol configuration.  |

### ProxyIdProtocol

This model defines the protocol configuration for proxy ID. At most one protocol type may be set.

| Attribute | Type     | Required | Default | Description                           |
|-----------|----------|----------|---------|---------------------------------------|
| number    | int      | No*      | None    | IP protocol number. Range: 1-254.     |
| tcp       | PortPair | No*      | None    | TCP port pair.                        |
| udp       | PortPair | No*      | None    | UDP port pair.                        |

\* At most one of `number`, `tcp`, or `udp` may be set.

### PortPair

This model defines local and remote port pairs for proxy ID protocol configuration.

| Attribute   | Type | Required | Default | Description                        |
|-------------|------|----------|---------|------------------------------------|
| local_port  | int  | No       | 0       | Local port number. Range: 0-65535. |
| remote_port | int  | No       | 0       | Remote port number. Range: 0-65535.|

### TunnelMonitor

This model defines tunnel monitor configuration for IPsec tunnels.

| Attribute      | Type | Required | Default | Description                                     |
|----------------|------|----------|---------|-------------------------------------------------|
| enable         | bool | No       | True    | Enable tunnel monitoring.                       |
| destination_ip | str  | Yes      | None    | Destination IP address for tunnel monitoring.   |
| proxy_id       | str  | No       | None    | Proxy ID for tunnel monitoring.                 |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating an IPsec tunnel (`IPsecTunnelCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When more than one protocol type (`number`, `tcp`, or `udp`) is configured in a `ProxyIdProtocol` model (at most one is allowed).
- When the tunnel name exceeds the maximum length.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Field Validators in `ProxyIdProtocol`

- **validate_single_protocol**:
  Ensures that at most one protocol type is set. If more than one of `number`, `tcp`, or `udp` is configured, it raises a `ValueError`. This enforces that a proxy ID can only match a single protocol type.

### Container Validation in `IPsecTunnelCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating an IPsec Tunnel

#### Using a Dictionary

```python
from scm.models.network import IPsecTunnelCreateModel

tunnel_data = {
    "name": "ipsec-tunnel-1",
    "auto_key": {
        "ike_gateway": [{"name": "ike-gw-1"}],
        "ipsec_crypto_profile": "ipsec-crypto-1",
        "proxy_id": [
            {
                "name": "proxy-1",
                "local": "10.0.0.0/24",
                "remote": "192.168.1.0/24",
                "protocol": {
                    "tcp": {
                        "local_port": 0,
                        "remote_port": 0
                    }
                }
            }
        ]
    },
    "anti_replay": True,
    "tunnel_monitor": {
        "enable": True,
        "destination_ip": "192.168.1.1"
    },
    "folder": "VPN Tunnels"
}

# Validate and create model instance
tunnel = IPsecTunnelCreateModel(**tunnel_data)
payload = tunnel.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import (
    IPsecTunnelCreateModel,
    AutoKey,
    IkeGatewayRef,
    ProxyId,
    ProxyIdProtocol,
    PortPair,
    TunnelMonitor,
)

# Create auto key configuration
auto_key = AutoKey(
    ike_gateway=[IkeGatewayRef(name="ike-gw-1")],
    ipsec_crypto_profile="ipsec-crypto-1",
    proxy_id=[
        ProxyId(
            name="proxy-1",
            local="10.0.0.0/24",
            remote="192.168.1.0/24",
            protocol=ProxyIdProtocol(
                tcp=PortPair(local_port=443, remote_port=443)
            )
        )
    ]
)

# Create tunnel monitor
monitor = TunnelMonitor(
    enable=True,
    destination_ip="192.168.1.1"
)

# Create IPsec tunnel
tunnel = IPsecTunnelCreateModel(
    name="ipsec-tunnel-2",
    auto_key=auto_key,
    anti_replay=True,
    copy_tos=True,
    tunnel_monitor=monitor,
    folder="VPN Tunnels"
)
payload = tunnel.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating an IPsec Tunnel

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing tunnel
existing = client.ipsec_tunnel.fetch(name="ipsec-tunnel-1", folder="VPN Tunnels")

# Modify attributes using dot notation
existing.anti_replay = True
existing.copy_tos = True

# Update tunnel monitor
if existing.tunnel_monitor:
    existing.tunnel_monitor.destination_ip = "10.0.0.1"

# Pass modified object to update()
updated = client.ipsec_tunnel.update(existing)
print(f"Updated IPsec tunnel: {updated.name}")
```

### Creating an IPsec Tunnel with Protocol Number Proxy ID

```python
from scm.models.network import (
    IPsecTunnelCreateModel,
    AutoKey,
    IkeGatewayRef,
    ProxyId,
    ProxyIdProtocol,
)

# Create tunnel with protocol number-based proxy ID (e.g., GRE = 47)
tunnel = IPsecTunnelCreateModel(
    name="gre-over-ipsec",
    auto_key=AutoKey(
        ike_gateway=[IkeGatewayRef(name="ike-gw-2")],
        ipsec_crypto_profile="ipsec-crypto-2",
        proxy_id=[
            ProxyId(
                name="gre-proxy",
                local="10.1.0.0/16",
                remote="172.16.0.0/16",
                protocol=ProxyIdProtocol(number=47)
            )
        ]
    ),
    folder="VPN Tunnels"
)
payload = tunnel.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```
