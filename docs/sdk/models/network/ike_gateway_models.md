# IKE Gateway Models

## Overview

The IKE Gateway models provide a structured way to manage Internet Key Exchange (IKE) gateway configurations in Palo Alto Networks' Strata Cloud Manager. These models handle validation of inputs and outputs when interacting with the SCM API, ensuring that configurations for VPN tunnel endpoints are properly formatted and validated.

## Attributes

| Attribute         | Type              | Required | Default | Description                                                                          |
|-------------------|-------------------|----------|---------|--------------------------------------------------------------------------------------|
| name              | str               | Yes      | None    | Name of the IKE gateway. Max length: 63 chars. Must match pattern: ^[0-9a-zA-Z._\-]+$ |
| authentication    | Authentication    | Yes      | None    | Authentication configuration (pre-shared key or certificate)                          |
| peer_id           | PeerId            | No       | None    | Peer identification configuration                                                     |
| local_id          | LocalId           | No       | None    | Local identification configuration                                                    |
| protocol          | Protocol          | Yes      | None    | IKE protocol configuration                                                            |
| protocol_common   | ProtocolCommon    | No       | None    | Common protocol settings like NAT traversal and fragmentation                         |
| peer_address      | PeerAddress       | Yes      | None    | Peer address configuration (IP, FQDN, or dynamic)                                     |
| folder            | str               | No*      | None    | Folder where IKE gateway is defined. Max length: 64 chars                             |
| snippet           | str               | No*      | None    | Snippet where IKE gateway is defined. Max length: 64 chars                            |
| device            | str               | No*      | None    | Device where IKE gateway is defined. Max length: 64 chars                             |
| id                | UUID              | Yes**    | None    | UUID of the IKE gateway (response only)                                               |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response and update models

## Authentication Models

IKE Gateway authentication supports either pre-shared key or certificate-based authentication.

### PreSharedKey Model

| Attribute | Type | Required | Default | Description                      |
|-----------|------|----------|---------|----------------------------------|
| key       | str  | Yes      | None    | Pre-shared key for authentication |

### CertificateAuth Model

| Attribute                      | Type    | Required | Default | Description                                 |
|--------------------------------|---------|----------|---------|---------------------------------------------|
| allow_id_payload_mismatch      | bool    | No       | None    | Allow ID payload mismatch                   |
| certificate_profile            | str     | No       | None    | Certificate profile name                    |
| local_certificate              | dict    | No       | None    | Local certificate configuration             |
| strict_validation_revocation   | bool    | No       | None    | Enable strict validation revocation         |
| use_management_as_source       | bool    | No       | None    | Use management interface as source          |

## Protocol Models

### Protocol Model

| Attribute | Type             | Required | Default            | Description                     |
|-----------|------------------|---------|--------------------|----------------------------------|
| ikev1     | IKEv1            | No*      | None               | IKEv1 protocol configuration    |
| ikev2     | IKEv2            | No*      | None               | IKEv2 protocol configuration    |
| version   | ProtocolVersion  | No       | ikev2-preferred    | IKE protocol version preference |

\* At least one protocol configuration (ikev1 or ikev2) must be provided based on the version

### ProtocolVersion Enum

- `ikev2-preferred`: Prefer IKEv2 but fall back to IKEv1 if needed
- `ikev1`: Use only IKEv1
- `ikev2`: Use only IKEv2

## Peer Address Models

The `PeerAddress` model supports three types of peer address configurations:

- `ip`: Static IP address of the peer gateway
- `fqdn`: Fully qualified domain name of the peer gateway
- `dynamic`: Dynamic peer gateway configuration (for dynamic IP addresses)

## Exceptions

The IKE Gateway models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When no authentication method or multiple authentication methods are provided
    - When multiple peer address types are specified
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When protocol configuration does not match the selected version
    - When name pattern validation fails

## Model Validators

### Authentication Method Validation

The models enforce that exactly one authentication method must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
from scm.models.network import IKEGatewayCreateModel

# Error: multiple authentication methods provided
try:
    gateway = IKEGatewayCreateModel(
        name="invalid-gateway",
        authentication={
            "pre_shared_key": {"key": "secret-key"},
            "certificate": {"certificate_profile": "default"}
        },
        protocol={
            "version": "ikev2",
            "ikev2": {"ike_crypto_profile": "default"}
        },
        peer_address={"ip": "203.0.113.1"},
        folder="VPN"
    )
except ValueError as e:
    print(e)  # "Only one authentication method can be configured: pre_shared_key or certificate"

# Error: no authentication method provided
try:
    gateway = IKEGatewayCreateModel(
        name="invalid-gateway",
        authentication={},
        protocol={
            "version": "ikev2",
            "ikev2": {"ike_crypto_profile": "default"}
        },
        peer_address={"ip": "203.0.113.1"},
        folder="VPN"
    )
except ValueError as e:
    print(e)  # "At least one authentication method must be provided: pre_shared_key or certificate"
```

</div>

### Peer Address Type Validation

The models enforce that exactly one peer address type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
try:
    gateway = IKEGatewayCreateModel(
        name="invalid-gateway",
        authentication={"pre_shared_key": {"key": "secret-key"}},
        protocol={
            "version": "ikev2",
            "ikev2": {"ike_crypto_profile": "default"}
        },
        peer_address={
            "ip": "203.0.113.1",
            "fqdn": "vpn.example.com"  # Can't specify both IP and FQDN
        },
        folder="VPN"
    )
except ValueError as e:
    print(e)  # "Exactly one peer address type must be configured: ip, fqdn, or dynamic"
```

</div>

### Protocol Configuration Validation

The models ensure that the protocol configuration matches the version selected:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error for mismatched protocol version and configuration
try:
    gateway = IKEGatewayCreateModel(
        name="invalid-gateway",
        authentication={"pre_shared_key": {"key": "secret-key"}},
        protocol={
            "version": "ikev1",  # Specified IKEv1
            "ikev2": {"ike_crypto_profile": "default"}  # But only provided IKEv2 config
        },
        peer_address={"ip": "203.0.113.1"},
        folder="VPN"
    )
except ValueError as e:
    print(e)  # "IKEv1 configuration is required when version is set to ikev1"
```

</div>

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
try:
    gateway = IKEGatewayCreateModel(
        name="invalid-gateway",
        authentication={"pre_shared_key": {"key": "secret-key"}},
        protocol={
            "version": "ikev2",
            "ikev2": {"ike_crypto_profile": "default"}
        },
        peer_address={"ip": "203.0.113.1"},
        folder="VPN",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

## Usage Examples

### Creating a Pre-Shared Key IKE Gateway

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.network import IKEGateway

psk_dict = {
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

gateway = IKEGateway(api_client)
response = gateway.create(psk_dict)

# Using model directly
from scm.models.network import IKEGatewayCreateModel

psk_gateway = IKEGatewayCreateModel(
    name="site-a-gateway",
    authentication={
        "pre_shared_key": {
            "key": "your-secure-key"
        }
    },
    peer_id={
        "type": "ipaddr",
        "id": "203.0.113.1"
    },
    protocol={
        "version": "ikev2",
        "ikev2": {
            "ike_crypto_profile": "default",
            "dpd": {
                "enable": True
            }
        }
    },
    peer_address={
        "ip": "203.0.113.1"
    },
    folder="VPN"
)

payload = psk_gateway.model_dump(exclude_unset=True)
response = gateway.create(payload)
```

</div>

### Creating a Certificate-Based IKE Gateway

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
cert_dict = {
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

response = gateway.create(cert_dict)

# Using model directly
from scm.models.network import IKEGatewayCreateModel

cert_gateway = IKEGatewayCreateModel(
    name="site-b-gateway",
    authentication={
        "certificate": {
            "certificate_profile": "default-profile",
            "local_certificate": {
                "local_certificate_name": "cert-name"
            }
        }
    },
    protocol={
        "version": "ikev2-preferred",
        "ikev1": {
            "ike_crypto_profile": "default"
        },
        "ikev2": {
            "ike_crypto_profile": "default"
        }
    },
    peer_address={
        "fqdn": "vpn.example.com"
    },
    folder="VPN"
)

payload = cert_gateway.model_dump(exclude_unset=True)
response = gateway.create(payload)
```

</div>

### Updating an IKE Gateway

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "site-a-gateway",
    "peer_id": {
        "type": "ipaddr",
        "id": "203.0.113.2"  # Updated peer ID
    },
    "protocol_common": {
        "nat_traversal": {
            "enable": True
        }
    }
}

response = gateway.update(update_dict)

# Using model directly
from scm.models.network import IKEGatewayUpdateModel

update_gateway = IKEGatewayUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="site-a-gateway",
    peer_id={
        "type": "ipaddr",
        "id": "203.0.113.2"  # Updated peer ID
    },
    protocol_common={
        "nat_traversal": {
            "enable": True
        }
    }
)

payload = update_gateway.model_dump(exclude_unset=True)
response = gateway.update(payload)
```

</div>
