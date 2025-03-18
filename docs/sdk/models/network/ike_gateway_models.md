# IKE Gateway Models

## Overview {#Overview}

The IKE Gateway models provide a structured way to manage Internet Key Exchange (IKE) gateway configurations in Palo Alto Networks' Strata Cloud Manager. These models support defining IKE configurations for establishing secure VPN connections with peer devices. The models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute        | Type            | Required | Default | Description                                                      |
|------------------|-----------------|----------|---------|------------------------------------------------------------------|
| name             | str             | Yes      | None    | Name of the IKE gateway. Max length: 63 chars. Pattern: ^[a-zA-Z0-9_ \.-]+$ |
| authentication   | Authentication  | Yes      | None    | Authentication configuration (pre-shared key or certificate)      |
| peer_id          | PeerID          | No       | None    | Peer identification configuration                                 |
| local_id         | LocalID         | No       | None    | Local identification configuration                                |
| protocol         | Protocol        | Yes      | None    | IKE protocol version and settings                                 |
| protocol_common  | ProtocolCommon  | No       | None    | Common protocol settings                                          |
| peer_address     | PeerAddress     | Yes      | None    | Peer address configuration                                        |
| local_address    | LocalAddress    | No       | None    | Local address configuration                                       |
| description      | str             | No       | None    | Description of the IKE gateway. Max length: 1023 chars            |
| folder           | str             | No*      | None    | Folder where IKE gateway is defined. Max length: 64 chars         |
| snippet          | str             | No*      | None    | Snippet where IKE gateway is defined. Max length: 64 chars        |
| device           | str             | No*      | None    | Device where IKE gateway is defined. Max length: 64 chars         |
| id               | UUID            | Yes**    | None    | UUID of the IKE gateway (response only)                           |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response model

### Authentication Model Attributes

| Attribute  | Type         | Required | Default | Description                                   |
|------------|--------------|----------|---------|-----------------------------------------------|
| pre_shared_key | PreSharedKey | No*     | None    | Pre-shared key authentication configuration   |
| certificate    | Certificate  | No*     | None    | Certificate-based authentication configuration|

\* Exactly one authentication type (pre_shared_key/certificate) must be provided

### Protocol Model Attributes

| Attribute | Type        | Required | Default | Description                                    |
|-----------|-------------|----------|---------|------------------------------------------------|
| version   | str         | Yes      | None    | IKE protocol version (ikev1, ikev2, ikev2-preferred) |
| ikev1     | IKEv1Config | No       | None    | IKEv1 protocol configuration                   |
| ikev2     | IKEv2Config | No       | None    | IKEv2 protocol configuration                   |

### PeerAddress Model Attributes

| Attribute | Type | Required | Default | Description                                    |
|-----------|------|----------|---------|------------------------------------------------|
| ip        | str  | No*      | None    | Peer IP address                                |
| fqdn      | str  | No*      | None    | Peer FQDN (Fully Qualified Domain Name)        |
| dynamic   | dict | No*      | None    | Dynamic peer address configuration             |

\* Exactly one peer address type (ip/fqdn/dynamic) must be provided

## Exceptions

The IKE Gateway models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When neither or multiple authentication types are provided
    - When neither or multiple peer address types are provided
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When protocol settings are missing required fields based on version
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Authentication Type Validation

The models enforce that exactly one authentication type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
from scm.models.network import Authentication

# Error: both authentication types provided
try:
    auth = Authentication(
        pre_shared_key={"key": "secure-key"},
        certificate={"certificate_profile": "default"}
    )
except ValueError as e:
    print(e)  # "Exactly one of 'pre_shared_key' or 'certificate' must be provided."

# Error: no authentication type provided
try:
    auth = Authentication()
except ValueError as e:
    print(e)  # "Exactly one of 'pre_shared_key' or 'certificate' must be provided."
```

</div>

### Peer Address Type Validation

Exactly one peer address type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
from scm.models.network import PeerAddress

# Error: multiple peer address types provided
try:
    peer_addr = PeerAddress(
        ip="192.168.1.1",
        fqdn="example.com"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'ip', 'fqdn', or 'dynamic' must be provided."

# Error: no peer address type provided
try:
    peer_addr = PeerAddress()
except ValueError as e:
    print(e)  # "Exactly one of 'ip', 'fqdn', or 'dynamic' must be provided."
```

</div>

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
from scm.models.network import IKEGatewayCreateModel

# Error: multiple containers specified
try:
    ike_gateway = IKEGatewayCreateModel(
        name="gateway1",
        authentication={"pre_shared_key": {"key": "secure-key"}},
        protocol={"version": "ikev2"},
        peer_address={"ip": "192.168.1.1"},
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

## Usage Examples

### Creating an IKE Gateway with Pre-shared Key

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.network import IKEGateway

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

ike_gateway = IKEGateway(api_client)
response = ike_gateway.create(psk_config)

# Using model directly
from scm.models.network import (
    IKEGatewayCreateModel, 
    Authentication, 
    PreSharedKey,
    PeerID,
    Protocol,
    IKEv2Config,
    DPD,
    PeerAddress
)

psk_gateway = IKEGatewayCreateModel(
    name="site-a-gateway",
    authentication=Authentication(
        pre_shared_key=PreSharedKey(
            key="your-secure-key"
        )
    ),
    peer_id=PeerID(
        type="ipaddr",
        id="203.0.113.1"
    ),
    protocol=Protocol(
        version="ikev2",
        ikev2=IKEv2Config(
            ike_crypto_profile="default",
            dpd=DPD(
                enable=True
            )
        )
    ),
    peer_address=PeerAddress(
        ip="203.0.113.1"
    ),
    folder="VPN"
)

payload = psk_gateway.model_dump(exclude_unset=True)
response = ike_gateway.create(payload)
```

</div>

### Creating an IKE Gateway with Certificate Authentication

<div class="termy">

<!-- termynal -->

```python
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

response = ike_gateway.create(cert_config)

# Using model directly
from scm.models.network import (
    IKEGatewayCreateModel, 
    Authentication, 
    Certificate,
    LocalCertificate,
    Protocol,
    IKEv1Config,
    IKEv2Config,
    PeerAddress
)

cert_gateway = IKEGatewayCreateModel(
    name="site-b-gateway",
    authentication=Authentication(
        certificate=Certificate(
            certificate_profile="default-profile",
            local_certificate=LocalCertificate(
                local_certificate_name="cert-name"
            )
        )
    ),
    protocol=Protocol(
        version="ikev2-preferred",
        ikev1=IKEv1Config(
            ike_crypto_profile="default"
        ),
        ikev2=IKEv2Config(
            ike_crypto_profile="default"
        )
    ),
    peer_address=PeerAddress(
        fqdn="vpn.example.com"
    ),
    folder="VPN"
)

payload = cert_gateway.model_dump(exclude_unset=True)
response = ike_gateway.create(payload)
```

</div>

### Creating an IKE Gateway with Dynamic Peer Address

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
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
    "local_address": {
        "interface": "ethernet1/1"
    },
    "folder": "VPN"
}

response = ike_gateway.create(dynamic_config)

# Using model directly
from scm.models.network import (
    IKEGatewayCreateModel, 
    Authentication, 
    PreSharedKey,
    Protocol,
    IKEv2Config,
    PeerAddress,
    LocalAddress
)

dynamic_gateway = IKEGatewayCreateModel(
    name="dynamic-gateway",
    authentication=Authentication(
        pre_shared_key=PreSharedKey(
            key="your-secure-key"
        )
    ),
    protocol=Protocol(
        version="ikev2",
        ikev2=IKEv2Config(
            ike_crypto_profile="default"
        )
    ),
    peer_address=PeerAddress(
        dynamic={}
    ),
    local_address=LocalAddress(
        interface="ethernet1/1"
    ),
    folder="VPN"
)

payload = dynamic_gateway.model_dump(exclude_unset=True)
response = ike_gateway.create(payload)
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

response = ike_gateway.update(update_dict)

# Using model directly
from scm.models.network import (
    IKEGatewayUpdateModel, 
    PeerID,
    ProtocolCommon,
    NatTraversal
)

update_gateway = IKEGatewayUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="site-a-gateway",
    peer_id=PeerID(
        type="ipaddr",
        id="203.0.113.2"
    ),
    protocol_common=ProtocolCommon(
        nat_traversal=NatTraversal(
            enable=True
        )
    )
)

payload = update_gateway.model_dump(exclude_unset=True)
response = ike_gateway.update(payload)
```

</div>
