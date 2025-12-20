# IKE Gateway Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The IKE Gateway models provide a structured way to manage Internet Key Exchange (IKE) gateway configurations in Palo Alto Networks' Strata Cloud Manager. These models support defining IKE configurations for establishing secure VPN connections with peer devices. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `IKEGatewayBaseModel`: Base model with fields common to all IKE gateway operations
- `IKEGatewayCreateModel`: Model for creating new IKE gateways
- `IKEGatewayUpdateModel`: Model for updating existing IKE gateways
- `IKEGatewayResponseModel`: Response model for IKE gateway operations
- `Authentication`: Authentication configuration model
- `PreSharedKey`: Pre-shared key authentication model
- `CertificateAuth`: Certificate-based authentication model
- `PeerId`: Peer identification model
- `LocalId`: Local identification model
- `Protocol`: IKE protocol configuration model
- `IKEv1`: IKEv1 protocol settings model
- `IKEv2`: IKEv2 protocol settings model
- `DeadPeerDetection`: DPD configuration model
- `ProtocolCommon`: Common protocol settings model
- `NatTraversal`: NAT traversal configuration model
- `Fragmentation`: IKE fragmentation configuration model
- `PeerAddress`: Peer address configuration model
- `PeerIdType`: Enum for peer ID types
- `LocalIdType`: Enum for local ID types
- `ProtocolVersion`: Enum for IKE protocol versions

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

| Attribute          | Type           | Required | Default              | Description                                           |
|--------------------|----------------|----------|----------------------|-------------------------------------------------------|
| `name`             | str            | Yes      | None                 | Name of IKE gateway. Max 63 chars. Pattern: `^[0-9a-zA-Z._\-]+$` |
| `id`               | UUID           | Yes*     | None                 | Unique identifier (*response/update only)             |
| `authentication`   | Authentication | Yes      | None                 | Authentication configuration                          |
| `peer_id`          | PeerId         | No       | None                 | Peer identification configuration                     |
| `local_id`         | LocalId        | No       | None                 | Local identification configuration                    |
| `protocol`         | Protocol       | Yes      | None                 | IKE protocol configuration                            |
| `protocol_common`  | ProtocolCommon | No       | None                 | Common protocol settings                              |
| `peer_address`     | PeerAddress    | Yes      | None                 | Peer address configuration                            |
| `folder`           | str            | No**     | None                 | Folder location. Max 64 chars                         |
| `snippet`          | str            | No**     | None                 | Snippet location. Max 64 chars                        |
| `device`           | str            | No**     | None                 | Device location. Max 64 chars                         |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## Enum Types

### PeerIdType

Defines the types of peer IDs supported for IKE Gateway authentication:

| Value    | Description                        |
|----------|------------------------------------|
| `ipaddr` | IP address                         |
| `keyid`  | Key ID                             |
| `fqdn`   | Fully Qualified Domain Name        |
| `ufqdn`  | User FQDN (email format)           |

### LocalIdType

Defines the types of local IDs supported for IKE Gateway authentication:

| Value    | Description                        |
|----------|------------------------------------|
| `ipaddr` | IP address                         |
| `keyid`  | Key ID                             |
| `fqdn`   | Fully Qualified Domain Name        |
| `ufqdn`  | User FQDN (email format)           |

### ProtocolVersion

Defines the IKE protocol versions supported:

| Value            | Description                                  |
|------------------|----------------------------------------------|
| `ikev2-preferred`| Prefer IKEv2, fall back to IKEv1 (default)   |
| `ikev1`          | IKEv1 only                                   |
| `ikev2`          | IKEv2 only                                   |

## Supporting Models

### Authentication Model

| Attribute       | Type           | Required | Default | Description                          |
|-----------------|----------------|----------|---------|--------------------------------------|
| `pre_shared_key`| PreSharedKey   | No*      | None    | Pre-shared key authentication        |
| `certificate`   | CertificateAuth| No*      | None    | Certificate-based authentication     |

\* Exactly one authentication type must be provided

### PreSharedKey Model

| Attribute | Type | Required | Default | Description              |
|-----------|------|----------|---------|--------------------------|
| `key`     | str  | Yes      | None    | Pre-shared key value     |

### CertificateAuth Model

| Attribute                     | Type          | Required | Default | Description                          |
|-------------------------------|---------------|----------|---------|--------------------------------------|
| `allow_id_payload_mismatch`   | bool          | No       | None    | Allow ID payload mismatch            |
| `certificate_profile`         | str           | No       | None    | Certificate profile name             |
| `local_certificate`           | Dict[str,Any] | No       | None    | Local certificate configuration      |
| `strict_validation_revocation`| bool          | No       | None    | Enable strict validation revocation  |
| `use_management_as_source`    | bool          | No       | None    | Use management interface as source   |

### PeerId Model

| Attribute | Type       | Required | Default | Description                                      |
|-----------|------------|----------|---------|--------------------------------------------------|
| `type`    | PeerIdType | Yes      | None    | Type of peer ID                                  |
| `id`      | str        | Yes      | None    | Peer ID string. Max 1024 chars                   |

### LocalId Model

| Attribute | Type        | Required | Default | Description                                     |
|-----------|-------------|----------|---------|--------------------------------------------------|
| `type`    | LocalIdType | Yes      | None    | Type of local ID                                 |
| `id`      | str         | Yes      | None    | Local ID string. Max 1024 chars                  |

### Protocol Model

| Attribute | Type            | Required | Default          | Description                    |
|-----------|-----------------|----------|------------------|--------------------------------|
| `version` | ProtocolVersion | No       | ikev2-preferred  | IKE protocol version preference|
| `ikev1`   | IKEv1           | No       | None             | IKEv1 configuration            |
| `ikev2`   | IKEv2           | No       | None             | IKEv2 configuration            |

### IKEv1 Model

| Attribute           | Type              | Required | Default | Description                  |
|---------------------|-------------------|----------|---------|------------------------------|
| `ike_crypto_profile`| str               | No       | None    | IKE Crypto Profile name      |
| `dpd`               | DeadPeerDetection | No       | None    | Dead Peer Detection config   |

### IKEv2 Model

| Attribute           | Type              | Required | Default | Description                  |
|---------------------|-------------------|----------|---------|------------------------------|
| `ike_crypto_profile`| str               | No       | None    | IKE Crypto Profile name      |
| `dpd`               | DeadPeerDetection | No       | None    | Dead Peer Detection config   |

### DeadPeerDetection Model

| Attribute | Type | Required | Default | Description                  |
|-----------|------|----------|---------|------------------------------|
| `enable`  | bool | No       | None    | Enable Dead Peer Detection   |

### ProtocolCommon Model

| Attribute      | Type          | Required | Default | Description                  |
|----------------|---------------|----------|---------|------------------------------|
| `nat_traversal`| NatTraversal  | No       | None    | NAT traversal configuration  |
| `passive_mode` | bool          | No       | None    | Enable passive mode          |
| `fragmentation`| Fragmentation | No       | None    | IKE fragmentation config     |

### NatTraversal Model

| Attribute | Type | Required | Default | Description              |
|-----------|------|----------|---------|--------------------------|
| `enable`  | bool | No       | None    | Enable NAT traversal     |

### Fragmentation Model

| Attribute | Type | Required | Default | Description                  |
|-----------|------|----------|---------|------------------------------|
| `enable`  | bool | No       | False   | Enable IKE fragmentation     |

### PeerAddress Model

| Attribute | Type          | Required | Default | Description                        |
|-----------|---------------|----------|---------|-------------------------------------|
| `ip`      | str           | No*      | None    | Static IP address of peer gateway  |
| `fqdn`    | str           | No*      | None    | FQDN of peer gateway. Max 255 chars|
| `dynamic` | Dict[str,Any] | No*      | None    | Dynamic peer address configuration |

\* Exactly one peer address type (ip/fqdn/dynamic) must be provided

## Exceptions

The IKE Gateway models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When neither or both authentication types (pre_shared_key/certificate) are provided
    - When neither or multiple peer address types (ip/fqdn/dynamic) are provided
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When protocol version is set but required config (ikev1/ikev2) is missing
    - When name pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Authentication Type Validation

The models enforce that exactly one authentication type must be specified:

```python
from scm.models.network.ike_gateway import Authentication, PreSharedKey

# This will raise a validation error - both authentication types provided
try:
    auth = Authentication(
        pre_shared_key=PreSharedKey(key="secure-key"),
        certificate={"certificate_profile": "default"}
    )
except ValueError as e:
    print(e)  # "Only one authentication method can be configured..."

# This will raise a validation error - no authentication type provided
try:
    auth = Authentication()
except ValueError as e:
    print(e)  # "At least one authentication method must be provided..."
```

### Peer Address Type Validation

Exactly one peer address type must be specified:

```python
from scm.models.network.ike_gateway import PeerAddress

# This will raise a validation error - multiple peer address types provided
try:
    peer_addr = PeerAddress(
        ip="192.168.1.1",
        fqdn="example.com"
    )
except ValueError as e:
    print(e)  # "Exactly one peer address type must be configured..."
```

### Protocol Configuration Validation

The protocol model validates that appropriate config is provided for the version:

```python
from scm.models.network.ike_gateway import Protocol

# This will raise a validation error - version is ikev2 but no ikev2 config
try:
    protocol = Protocol(
        version="ikev2"
        # Missing ikev2 configuration
    )
except ValueError as e:
    print(e)  # "IKEv2 configuration is required when version is set to ikev2"
```

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.network.ike_gateway import IKEGatewayCreateModel

# This will raise a validation error - multiple containers specified
try:
    ike_gateway = IKEGatewayCreateModel(
        name="gateway1",
        authentication={"pre_shared_key": {"key": "secure-key"}},
        protocol={"version": "ikev2", "ikev2": {"ike_crypto_profile": "default"}},
        peer_address={"ip": "192.168.1.1"},
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

## Usage Examples

### Creating an IKE Gateway with Pre-shared Key

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
psk_config = {
    "name": "site-a-gateway",
    "authentication": {
        "pre_shared_key": {
            "key": "your-secure-key"
        }
    },
    "peer_id": {
        "type": "ipaddr",
        "id": "203.0.113.1"
    },
    "protocol": {
        "version": "ikev2",
        "ikev2": {
            "ike_crypto_profile": "default",
            "dpd": {
                "enable": True
            }
        }
    },
    "peer_address": {
        "ip": "203.0.113.1"
    },
    "folder": "VPN"
}

response = client.ike_gateway.create(psk_config)
print(f"Created gateway: {response.name} (ID: {response.id})")
```

### Creating an IKE Gateway with Certificate Authentication

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
cert_config = {
    "name": "site-b-gateway",
    "authentication": {
        "certificate": {
            "certificate_profile": "default-profile",
            "local_certificate": {
                "local_certificate_name": "cert-name"
            }
        }
    },
    "protocol": {
        "version": "ikev2-preferred",
        "ikev1": {
            "ike_crypto_profile": "default"
        },
        "ikev2": {
            "ike_crypto_profile": "default"
        }
    },
    "peer_address": {
        "fqdn": "vpn.example.com"
    },
    "folder": "VPN"
}

response = client.ike_gateway.create(cert_config)
print(f"Created gateway: {response.name}")
```

### Creating an IKE Gateway with Dynamic Peer Address

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary for dynamic peer
dynamic_config = {
    "name": "dynamic-gateway",
    "authentication": {
        "pre_shared_key": {
            "key": "your-secure-key"
        }
    },
    "protocol": {
        "version": "ikev2",
        "ikev2": {
            "ike_crypto_profile": "default"
        }
    },
    "peer_address": {
        "dynamic": {}
    },
    "folder": "VPN"
}

response = client.ike_gateway.create(dynamic_config)
print(f"Created dynamic gateway: {response.name}")
```

### Updating an IKE Gateway

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing IKE gateway
existing = client.ike_gateway.fetch(name="site-a-gateway", folder="VPN")

# Modify attributes using dot notation
existing.peer_id = {
    "type": "ipaddr",
    "id": "203.0.113.2"  # Updated peer ID
}
existing.protocol_common = {
    "nat_traversal": {
        "enable": True
    }
}

# Pass modified object to update()
updated = client.ike_gateway.update(existing)
print(f"Updated gateway: {updated.name}")
```
