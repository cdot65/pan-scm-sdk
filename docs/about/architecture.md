# Architecture

## Overview

The `pan-scm-sdk` follows a layered architecture with clear separation between the client entry point,
service classes, Pydantic data models, and operational utilities. Every service class inherits from
`BaseObject` and exposes a consistent CRUD interface, while models enforce validation through a
four-tier hierarchy.

## Architecture Diagram

<figure markdown="span">
  ![pan-scm-sdk Architecture](../images/architecture.svg){ width="100%" }
  <figcaption>High-level architecture of the pan-scm-sdk package</figcaption>
</figure>

## Layers

### Entry Point

The `Scm` client in `client.py` is the single entry point for all SDK operations. It authenticates
via OAuth2 client credentials (`auth.py`), registers every service class as a property, and delegates
HTTP methods to the underlying session. Errors from the SCM API are caught and mapped to SDK-specific
exceptions through `ErrorHandler`.

```python
from scm.client import Scm

client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tsg-id",
)
```

### Service Classes (`config/`)

Service classes are organized by category and inherit from `BaseObject`. Each service defines an
`ENDPOINT` constant and implements six standard methods: `create()`, `get()`, `update()`, `delete()`,
`list()`, and `fetch()`. Container validation ensures exactly one of `folder`, `snippet`, or `device`
is provided. The `list()` method handles auto-pagination with a configurable `max_limit` (default 2500).

| Category       | Services | Description                                          |
|----------------|----------|------------------------------------------------------|
| `objects/`     | 19       | Addresses, tags, applications, services, HIP, etc.   |
| `security/`    | 12       | Security rules, decryption, antivirus profiles       |
| `network/`     | 30       | Interfaces, routing, NAT, VPN, QoS, zones            |
| `deployment/`  | 6        | Bandwidth, BGP routing, remote networks              |
| `setup/`       | 5        | Folders, labels, snippets, devices, variables         |
| `identity/`    | 6        | Authentication and server profiles                    |
| `mobile_agent/`| 2        | Agent versions and auth settings                      |

### Pydantic Models (`models/`)

Every resource has a parallel model module that defines four model classes:

- **`BaseModel`** — shared fields and validators
- **`CreateModel`** — `extra="forbid"`, container validation
- **`UpdateModel`** — includes `id: UUID`
- **`ResponseModel`** — `extra="ignore"`, includes `id: UUID`

Service classes use `.model_dump(exclude_unset=True)` for API payloads, and `False` values are
omitted to comply with SCM API requirements.

### Operations & Insights

The `operations/` package provides `Jobs` (async job tracking) and `CandidatePush` (configuration
deployment), while `insights/` provides the `Alerts` service for monitoring.

## Test Architecture

The test suite mirrors the source structure exactly, with 81 config tests, 91 model tests, and 92
factory files providing comprehensive coverage. All 6,020 tests pass with 100% code coverage.
