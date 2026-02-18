# DHCP Interface Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The DHCP Interface models provide a structured way to represent and validate DHCP server and relay configuration data on firewall interfaces for Palo Alto Networks' Strata Cloud Manager. These models ensure data integrity when creating and updating DHCP interface configurations, enforcing proper server/relay mutual exclusivity, lease settings, container specifications, and field validations.

### Models

The module provides the following Pydantic models:

- `DhcpInterfaceBaseModel`: Base model with fields common to all DHCP interface operations
- `DhcpInterfaceCreateModel`: Model for creating new DHCP interface configurations
- `DhcpInterfaceUpdateModel`: Model for updating existing DHCP interface configurations
- `DhcpInterfaceResponseModel`: Response model for DHCP interface operations
- `DhcpServer`: DHCP server configuration model
- `DhcpServerOption`: DHCP server option configuration model
- `DhcpRelay`: DHCP relay configuration model
- `DhcpRelayIp`: DHCP relay IP configuration model
- `DhcpDualServer`: Dual server configuration model for DNS, WINS, NIS, and NTP servers
- `DhcpLease`: DHCP lease configuration model
- `DhcpInheritance`: DHCP inheritance configuration model
- `DhcpReserved`: DHCP reserved address entry model
- `DhcpServerMode`: Enum for DHCP server operation modes

The `DhcpInterfaceBaseModel` and `DhcpInterfaceCreateModel` / `DhcpInterfaceUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `DhcpInterfaceResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### DhcpInterfaceBaseModel

This is the base model containing fields common to all DHCP interface operations.

| Attribute | Type       | Required | Default | Description                                                     |
|-----------|------------|----------|---------|-----------------------------------------------------------------|
| name      | str        | Yes      | None    | The interface name.                                             |
| server    | DhcpServer | No*      | None    | DHCP server configuration.                                     |
| relay     | DhcpRelay  | No*      | None    | DHCP relay configuration.                                      |
| folder    | str        | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet   | str        | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device    | str        | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\* `server` and `relay` are mutually exclusive. Only one may be set at a time.

\** Exactly one container (folder/snippet/device) must be provided for create operations

### DhcpInterfaceCreateModel

Inherits all fields from `DhcpInterfaceBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### DhcpInterfaceUpdateModel

Extends `DhcpInterfaceBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                          |
|-----------|------|----------|---------|------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the DHCP interface configuration |

### DhcpInterfaceResponseModel

Extends `DhcpInterfaceBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                          |
|-----------|------|----------|---------|------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the DHCP interface configuration |

> **Note:** The `DhcpInterfaceResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Enum Types

### DhcpServerMode

Defines the DHCP server operation modes:

| Value      | Description                      |
|------------|----------------------------------|
| `auto`     | Automatic DHCP server mode       |
| `enabled`  | DHCP server explicitly enabled   |
| `disabled` | DHCP server explicitly disabled  |

## Supporting Models

### DhcpServer

This model defines the DHCP server configuration.

| Attribute | Type                | Required | Default | Description                           |
|-----------|---------------------|----------|---------|---------------------------------------|
| probe_ip  | bool                | No       | None    | Enable IP probe before assignment.    |
| mode      | DhcpServerMode      | No       | None    | DHCP server mode.                     |
| option    | DhcpServerOption    | No       | None    | DHCP server options.                  |
| ip_pool   | List[str]           | No       | None    | List of IP pool ranges.               |
| reserved  | List[DhcpReserved]  | No       | None    | List of reserved address entries.     |

### DhcpServerOption

This model defines the DHCP server option configuration.

| Attribute   | Type            | Required | Default | Description                |
|-------------|-----------------|----------|---------|----------------------------|
| lease       | DhcpLease       | No       | None    | Lease configuration.       |
| inheritance | DhcpInheritance | No       | None    | Inheritance configuration. |
| gateway     | str             | No       | None    | Gateway address.           |
| subnet_mask | str             | No       | None    | Subnet mask.               |
| dns         | DhcpDualServer  | No       | None    | DNS server configuration.  |
| wins        | DhcpDualServer  | No       | None    | WINS server configuration. |
| nis         | DhcpDualServer  | No       | None    | NIS server configuration.  |
| ntp         | DhcpDualServer  | No       | None    | NTP server configuration.  |
| pop3_server | str             | No       | None    | POP3 server address.       |
| smtp_server | str             | No       | None    | SMTP server address.       |
| dns_suffix  | str             | No       | None    | DNS suffix.                |

### DhcpRelay

This model defines the DHCP relay configuration.

| Attribute | Type        | Required | Default | Description                  |
|-----------|-------------|----------|---------|------------------------------|
| ip        | DhcpRelayIp | Yes      | None    | DHCP relay IP configuration. |

### DhcpRelayIp

This model defines the DHCP relay IP configuration.

| Attribute | Type       | Required | Default | Description                           |
|-----------|------------|----------|---------|---------------------------------------|
| enabled   | bool       | No       | True    | Enable DHCP relay.                    |
| server    | List[str]  | Yes      | None    | List of DHCP relay server addresses.  |

### DhcpDualServer

Dual server configuration used for DNS, WINS, NIS, and NTP servers.

| Attribute | Type | Required | Default | Description              |
|-----------|------|----------|---------|--------------------------|
| primary   | str  | No       | None    | Primary server address.  |
| secondary | str  | No       | None    | Secondary server address.|

### DhcpLease

DHCP lease configuration. Only one of `unlimited` or `timeout` may be set.

| Attribute | Type           | Required | Default | Description                   |
|-----------|----------------|----------|---------|-------------------------------|
| unlimited | Dict[str, Any] | No*      | None    | Unlimited lease duration.     |
| timeout   | int            | No*      | None    | Lease timeout in minutes.     |

\* `unlimited` and `timeout` are mutually exclusive. Only one may be set at a time.

### DhcpInheritance

DHCP inheritance configuration.

| Attribute | Type | Required | Default | Description         |
|-----------|------|----------|---------|---------------------|
| source    | str  | No       | None    | Inheritance source. |

### DhcpReserved

DHCP reserved address entry.

| Attribute   | Type | Required | Default | Description                      |
|-------------|------|----------|---------|----------------------------------|
| name        | str  | Yes      | None    | Reserved address name.           |
| mac         | str  | Yes      | None    | MAC address for the reservation. |
| description | str  | No       | None    | Description of the reservation.  |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a DHCP interface (`DhcpInterfaceCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When both `server` and `relay` are configured on the same DHCP interface (they are mutually exclusive).
- When both `unlimited` and `timeout` are configured in a `DhcpLease` model (they are mutually exclusive).
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Field Validators in `DhcpInterfaceBaseModel`

- **validate_server_relay_exclusivity**:
  Ensures that `server` and `relay` are mutually exclusive. If both are set, it raises a `ValueError`. A DHCP interface can operate as either a DHCP server or a DHCP relay, but not both simultaneously.

### Field Validators in `DhcpLease`

- **validate_lease_type**:
  Ensures that `unlimited` and `timeout` are mutually exclusive. If both are set, it raises a `ValueError`. A lease can either be unlimited or have a specific timeout, but not both.

### Container Validation in `DhcpInterfaceCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a DHCP Server Configuration

#### Using a Dictionary

```python
from scm.models.network import DhcpInterfaceCreateModel

dhcp_data = {
    "name": "ethernet1/1",
    "server": {
        "mode": "enabled",
        "probe_ip": True,
        "ip_pool": ["192.168.1.100-192.168.1.200"],
        "option": {
            "gateway": "192.168.1.1",
            "subnet_mask": "255.255.255.0",
            "dns": {
                "primary": "8.8.8.8",
                "secondary": "8.8.4.4"
            },
            "ntp": {
                "primary": "pool.ntp.org"
            },
            "lease": {
                "timeout": 1440
            },
            "dns_suffix": "example.com"
        },
        "reserved": [
            {
                "name": "server-1",
                "mac": "00:11:22:33:44:55",
                "description": "Web server"
            }
        ]
    },
    "folder": "DHCP Interfaces"
}

# Validate and create model instance
dhcp_config = DhcpInterfaceCreateModel(**dhcp_data)
payload = dhcp_config.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly with Relay Configuration

```python
from scm.models.network import (
    DhcpInterfaceCreateModel,
    DhcpRelay,
    DhcpRelayIp,
)

# Create DHCP relay configuration
relay = DhcpRelay(
    ip=DhcpRelayIp(
        enabled=True,
        server=["10.0.0.1", "10.0.0.2"]
    )
)

# Create DHCP interface with relay
dhcp_config = DhcpInterfaceCreateModel(
    name="ethernet1/2",
    relay=relay,
    folder="DHCP Interfaces"
)
payload = dhcp_config.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a DHCP Interface Configuration

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing DHCP interface
existing = client.dhcp_interface.fetch(name="ethernet1/1", folder="DHCP Interfaces")

# Modify the IP pool
if existing.server:
    existing.server.ip_pool = ["192.168.1.50-192.168.1.250"]

# Pass modified object to update()
updated = client.dhcp_interface.update(existing)
print(f"Updated DHCP interface: {updated.name}")
```

### Creating a DHCP Server with Unlimited Lease

```python
from scm.models.network import (
    DhcpInterfaceCreateModel,
    DhcpServer,
    DhcpServerOption,
    DhcpLease,
    DhcpDualServer,
)

# Create server with unlimited lease
server = DhcpServer(
    mode="enabled",
    ip_pool=["10.0.0.100-10.0.0.200"],
    option=DhcpServerOption(
        gateway="10.0.0.1",
        subnet_mask="255.255.255.0",
        dns=DhcpDualServer(
            primary="8.8.8.8",
            secondary="8.8.4.4"
        ),
        lease=DhcpLease(unlimited={})
    )
)

dhcp_config = DhcpInterfaceCreateModel(
    name="ethernet1/3",
    server=server,
    folder="DHCP Interfaces"
)
payload = dhcp_config.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```
