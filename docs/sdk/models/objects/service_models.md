# Service Models

This section covers the data models associated with the `Service` configuration object.

---

## ServiceRequestModel

Used when creating or updating a service object.

### Attributes

- `name` (str): **Required.** The name of the service object.
- `protocol` (Protocol): **Required.** The protocol configuration for the service.
    - **Exactly one of:**
        - `tcp` (TCPProtocol): Configuration for TCP protocol.
        - `udp` (UDPProtocol): Configuration for UDP protocol.
- `description` (Optional[str]): A description of the service object.
- `tag` (Optional[List[str]]): Tags associated with the service object.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the service is defined.
    - `snippet` (Optional[str]): The snippet where the service is defined.
    - `device` (Optional[str]): The device where the service is defined.

#### Protocol

- `tcp` (Optional[TCPProtocol]): TCP protocol configuration.
- `udp` (Optional[UDPProtocol]): UDP protocol configuration.

#### TCPProtocol

- `port` (str): **Required.** TCP port(s) associated with the service (e.g., `"80"` or `"80,8080"`).
- `override` (Optional[Override]): Override settings for the TCP protocol.

#### UDPProtocol

- `port` (str): **Required.** UDP port(s) associated with the service (e.g., `"53"` or `"67,68"`).
- `override` (Optional[Override]): Override settings for the UDP protocol.

#### Override

- `timeout` (Optional[int]): Timeout in seconds.
- `halfclose_timeout` (Optional[int]): Half-close timeout in seconds.
- `timewait_timeout` (Optional[int]): Time-wait timeout in seconds.

### Examples

#### Example 1: TCP Service

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ServiceRequestModel, Protocol, TCPProtocol, Override

tcp_service = ServiceRequestModel(
    name="web-service",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="80,443",
            override=Override(
                timeout=30,
                halfclose_timeout=15,
            )
        )
    ),
    description="HTTP and HTTPS service",
    folder="Web Services",
    tag=["web", "production"]
)

print(tcp_service.model_dump_json(indent=2))
```

</div>

#### Example 2: UDP Service

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ServiceRequestModel, Protocol, UDPProtocol

udp_service = ServiceRequestModel(
    name="dns-service",
    protocol=Protocol(
        udp=UDPProtocol(
            port="53"
        )
    ),
    description="DNS service",
    snippet="network-services",
    tag=["dns", "network"]
)

print(udp_service.model_dump_json(indent=2))
```

</div>

#### Example 3: Service with Multiple Ports

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ServiceRequestModel, Protocol, TCPProtocol

multi_port_service = ServiceRequestModel(
    name="app-service",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="8080-8090,9000"
        )
    ),
    description="Application service with multiple ports",
    device="firewall-01",
    tag=["app", "custom"]
)

print(multi_port_service.model_dump_json(indent=2))
```

</div>

---

## ServiceResponseModel

Used when parsing service objects retrieved from the API.

### Attributes

- `id` (Optional[str]): The UUID of the service object.
- `name` (str): The name of the service object.
- `protocol` (Protocol): The protocol configuration for the service.
    - **Exactly one of:**
        - `tcp` (TCPProtocol): Configuration for TCP protocol.
        - `udp` (UDPProtocol): Configuration for UDP protocol.
- `folder` (str): The folder where the service is defined.
- `description` (Optional[str]): A description of the service object.
- `tag` (Optional[List[str]]): Tags associated with the service object.
- `snippet` (Optional[str]): The snippet where the service is defined.

### Examples

#### Example 4: TCP Service Response

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ServiceResponseModel, Protocol, TCPProtocol, Override

tcp_response = ServiceResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="web-service",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="80,443",
            override=Override(
                timeout=30,
                halfclose_timeout=15,
            )
        )
    ),
    folder="Web Services",
    description="HTTP and HTTPS service",
    tag=["web", "production"]
)

print(tcp_response.model_dump_json(indent=2))
```

</div>

#### Example 5: UDP Service Response

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ServiceResponseModel, Protocol, UDPProtocol

udp_response = ServiceResponseModel(
    id="987e6543-e21b-43d3-b456-987655440000",
    name="dns-service",
    protocol=Protocol(
        udp=UDPProtocol(
            port="53"
        )
    ),
    folder="Network Services",
    description="DNS service",
    tag=["dns", "network"]
)

print(udp_response.model_dump_json(indent=2))
```

</div>

#### Example 6: Service Response with Snippet

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ServiceResponseModel, Protocol, TCPProtocol

snippet_response = ServiceResponseModel(
    id="456e7890-a12b-34c5-d678-123455440000",
    name="custom-app-service",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="9000-9100"
        )
    ),
    folder="Shared",
    description="Custom application service",
    snippet="app-services",
    tag=["custom", "application"]
)

print(snippet_response.model_dump_json(indent=2))
```

</div>

---

## Full Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import (
    ServiceRequestModel,
    ServiceResponseModel,
    Protocol,
    TCPProtocol,
    UDPProtocol,
    Override
)

# Create a complex service request
complex_service_request = ServiceRequestModel(
    name="complex-service",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="80,443,8080-8090",
            override=Override(
                timeout=300,
                halfclose_timeout=60,
                timewait_timeout=30
            )
        )
    ),
    description="Complex service with multiple TCP ports and overrides",
    folder="Advanced Services",
    tag=["complex", "multi-port", "custom"]
)

print("Service Request:")
print(complex_service_request.model_dump_json(indent=2))

# Simulate a service response
complex_service_response = ServiceResponseModel(
    id="abcde123-4567-89fg-hijk-lmnopqrstuv",
    name=complex_service_request.name,
    protocol=complex_service_request.protocol,
    folder=complex_service_request.folder,
    description=complex_service_request.description,
    tag=complex_service_request.tag
)

print("\nService Response:")
print(complex_service_response.model_dump_json(indent=2))

# Create a UDP service
udp_service_request = ServiceRequestModel(
    name="voip-service",
    protocol=Protocol(
        udp=UDPProtocol(
            port="5060-5061"
        )
    ),
    description="VoIP service using UDP",
    snippet="voice-services",
    tag=["voip", "udp"]
)

print("\nUDP Service Request:")
print(udp_service_request.model_dump_json(indent=2))
```

</div>

---
