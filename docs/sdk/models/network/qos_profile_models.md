# QoS Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Exceptions](#exceptions)
4. [Model Validators](#model-validators)
5. [Usage Examples](#usage-examples)

## Overview {#Overview}

The QoS Profile models provide a structured way to represent and validate QoS profile configuration data for Palo Alto Networks' Strata Cloud Manager. These models manage bandwidth allocation settings including aggregate bandwidth limits and per-class bandwidth type configurations used for traffic prioritization.

### Models

The module provides the following Pydantic models:

- `QosProfileBaseModel`: Base model with fields common to all QoS profile operations
- `QosProfileCreateModel`: Model for creating new QoS profiles
- `QosProfileUpdateModel`: Model for updating existing QoS profiles
- `QosProfileResponseModel`: Response model for QoS profile operations

The `QosProfileBaseModel` and `QosProfileCreateModel` / `QosProfileUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `QosProfileResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### QosProfileBaseModel

This is the base model containing fields common to all QoS profile operations.

| Attribute              | Type              | Required | Default | Description                                                                |
|------------------------|-------------------|----------|---------|----------------------------------------------------------------------------|
| name                   | str               | Yes      | None    | Profile name. Max 31 chars. Pattern: `[0-9a-zA-Z._-]`                     |
| aggregate_bandwidth    | Dict[str, Any]    | No       | None    | Aggregate bandwidth settings (egress_max, egress_guaranteed).              |
| class_bandwidth_type   | Dict[str, Any]    | No       | None    | Class bandwidth type configuration (mbps or percentage).                   |
| folder                 | str               | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.             |
| snippet                | str               | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.            |
| device                 | str               | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.             |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### QosProfileCreateModel

Inherits all fields from `QosProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### QosProfileUpdateModel

Extends `QosProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the QoS profile           |

### QosProfileResponseModel

Extends `QosProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the QoS profile           |

> **Note:** The `QosProfileResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a profile (`QosProfileCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.
- When the `name` field exceeds the maximum length of 31 characters.

## Model Validators

### Container Validation in `QosProfileCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a QoS Profile

#### Using a Dictionary

```python
from scm.models.network import QosProfileCreateModel

profile_data = {
    "name": "high-priority-qos",
    "aggregate_bandwidth": {
        "egress_max": 1000,
        "egress_guaranteed": 500
    },
    "folder": "Networking",
}

# Validate and create model instance
profile = QosProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import QosProfileCreateModel

# Create QoS profile with class bandwidth type
profile = QosProfileCreateModel(
    name="class-based-qos",
    aggregate_bandwidth={
        "egress_max": 2000,
        "egress_guaranteed": 1000
    },
    class_bandwidth_type={
        "percentage": {
            "class1": 30,
            "class2": 20,
            "class3": 15
        }
    },
    folder="Networking",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a QoS Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing profile
existing = client.qos_profile.fetch(name="high-priority-qos", folder="Networking")

# Modify the bandwidth settings
existing.aggregate_bandwidth = {
    "egress_max": 1500,
    "egress_guaranteed": 750
}

# Pass modified object to update()
updated = client.qos_profile.update(existing)
print(f"Updated profile: {updated.name}")
```
