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

### Example

```python
from scm.models.service import ServiceRequestModel, Protocol, TCPProtocol, Override

service_request = ServiceRequestModel(
    name="web-service",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="80,8080",
            override=Override(
                timeout=30,
                halfclose_timeout=15,
            )
        )
    ),
    description="HTTP service",
    folder="Prisma Access",
)
```

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

### Example

```python
from scm.models.service import ServiceResponseModel, Protocol, TCPProtocol

service_response = ServiceResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="web-service",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="80,8080",
            override=None,
        )
    ),
    folder="Prisma Access",
    description="HTTP service",
)
```

---
