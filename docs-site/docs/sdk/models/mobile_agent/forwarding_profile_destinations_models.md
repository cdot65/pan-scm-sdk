# GlobalProtect Forwarding Profile Destination Models

Pydantic models for GlobalProtect forwarding profile destinations in Palo Alto Networks Strata Cloud Manager.

## Model Hierarchy

| Model                                          | Purpose                                            |
|------------------------------------------------|----------------------------------------------------|
| `ForwardingProfileDestinationBaseModel`        | Common fields shared across all CRUD operations    |
| `ForwardingProfileDestinationCreateModel`      | Fields for creating new destinations               |
| `ForwardingProfileDestinationUpdateModel`      | Fields for updating destinations (adds optional `id`) |
| `ForwardingProfileDestinationResponseModel`    | Fields returned by the API (adds `id`)             |

## Base Model Attributes

| Attribute      | Type                       | Required | Default | Description                                                |
|----------------|----------------------------|----------|---------|------------------------------------------------------------|
| `name`         | str                        | Yes      | None    | Destination name (max 64 chars, pattern `^[0-9a-zA-Z._-]+$`) |
| `description`  | str                        | No       | None    | Description (max 1023 chars)                                |
| `fqdn`         | List[DestinationFqdnEntry] | No       | None    | FQDN entries                                                |
| `ip_addresses` | List[DestinationIpEntry]   | No       | None    | IP address entries                                          |

## Supporting Models

### DestinationFqdnEntry

| Attribute | Type | Required | Default | Description                                                               |
|-----------|------|----------|---------|---------------------------------------------------------------------------|
| `name`    | str  | Yes      | None    | FQDN (max 255 chars, wildcards `*` and at most one trailing `$` supported) |
| `port`    | int  | No       | None    | Port number (1-65535)                                                      |

### DestinationIpEntry

| Attribute | Type | Required | Default | Description                                              |
|-----------|------|----------|---------|----------------------------------------------------------|
| `name`    | str  | Yes      | None    | IP address with wildcards and CIDR notation support      |
| `port`    | int  | No       | None    | Port number (1-65535)                                    |

## Usage Example

```python
from scm.models.mobile_agent.forwarding_profile_destinations import (
    DestinationFqdnEntry,
    DestinationIpEntry,
    ForwardingProfileDestinationCreateModel,
)

destination = ForwardingProfileDestinationCreateModel(
    name="internal-destinations",
    description="Internal corporate destinations",
    fqdn=[
        DestinationFqdnEntry(name="*.example.com"),
        DestinationFqdnEntry(name="intranet.example.com", port=8443),
    ],
    ip_addresses=[
        DestinationIpEntry(name="10.0.0.0/8"),
        DestinationIpEntry(name="192.168.1.*", port=443),
    ],
)

payload = destination.model_dump(exclude_unset=True)
```

## Related Documentation

- [Forwarding Profile Destinations Configuration](../../config/mobile_agent/forwarding_profile_destinations.md)
- [Forwarding Profile Models](forwarding_profiles_models.md)
