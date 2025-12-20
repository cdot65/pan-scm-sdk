# NAT Rules Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [NAT Rule Model Attributes](#nat-rule-model-attributes)
4. [Source Translation Types](#source-translation-types)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating NAT Rules](#creating-nat-rules)
    - [Retrieving NAT Rules](#retrieving-nat-rules)
    - [Updating NAT Rules](#updating-nat-rules)
    - [Listing NAT Rules](#listing-nat-rules)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting NAT Rules](#deleting-nat-rules)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Full Script Examples](#full-script-examples)
12. [Related Models](#related-models)

## Overview

The `NatRule` class manages NAT rule objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete NAT rules. Additionally, it provides client-side filtering for listing operations and enforces container requirements using the `folder`, `snippet`, or `device` parameters.

## Core Methods

| Method     | Description                                                   | Parameters                                                                                                                                                | Return Type                  |
|------------|---------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| `create()` | Creates a new NAT rule object                                 | `data: Dict[str, Any]`, `position: str = "pre"`                                                                                                           | `NatRuleResponseModel`       |
| `get()`    | Retrieves a NAT rule object by its unique ID                  | `object_id: str`                                                                                                                                          | `NatRuleResponseModel`       |
| `update()` | Updates an existing NAT rule object                           | `rule: NatRuleUpdateModel`, `position: str = "pre"`                                                                                                       | `NatRuleResponseModel`       |
| `list()`   | Lists NAT rule objects with optional filtering and containers | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `position: str = "pre"`, `exact_match: bool = False`, plus additional filters | `List[NatRuleResponseModel]` |
| `fetch()`  | Fetches a single NAT rule by its name within a container      | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `position: str = "pre"`                                          | `NatRuleResponseModel`       |
| `delete()` | Deletes a NAT rule object by its ID                           | `object_id: str`                                                                                                                                          | `None`                       |

## NAT Rule Model Attributes

| Attribute                    | Type                   | Required | Default   | Description                                              |
|------------------------------|------------------------|----------|-----------|----------------------------------------------------------|
| `name`                       | str                    | Yes      | None      | The name of the NAT rule. Pattern: `^[a-zA-Z0-9_ \.-]+$` |
| `id`                         | UUID                   | Yes*     | None      | Unique identifier (*response/update only)                |
| `description`                | str                    | No       | None      | Description of the NAT rule                              |
| `nat_type`                   | NatType                | No       | ipv4      | The type of NAT rule (`ipv4`, `nat64`, `nptv6`)          |
| `from_`                      | List[str]              | No       | ["any"]   | Source zone(s) (alias: `from`)                           |
| `to_`                        | List[str]              | No       | ["any"]   | Destination zone(s) (alias: `to`)                        |
| `to_interface`               | str                    | No       | None      | Destination interface of the original packet             |
| `source`                     | List[str]              | No       | ["any"]   | Source addresses for the NAT rule                        |
| `destination`                | List[str]              | No       | ["any"]   | Destination addresses for the NAT rule                   |
| `service`                    | str                    | No       | "any"     | The TCP/UDP service associated with the NAT translation  |
| `tag`                        | List[str]              | No       | []        | Tags associated with the NAT rule                        |
| `disabled`                   | bool                   | No       | False     | Indicates whether the NAT rule is disabled               |
| `source_translation`         | SourceTranslation      | No       | None      | Source translation configuration                         |
| `destination_translation`    | DestinationTranslation | No       | None      | Destination translation configuration                    |
| `active_active_device_binding` | str                  | No       | None      | Active/Active device binding                             |
| `folder`                     | str                    | No**     | None      | The folder container. Max 64 chars                       |
| `snippet`                    | str                    | No**     | None      | The snippet container. Max 64 chars                      |
| `device`                     | str                    | No**     | None      | The device container. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## Source Translation Types

The NAT rules model supports three different types of source translation methods, following a discriminated union pattern where exactly one type must be provided:

### 1. Dynamic IP and Port (PAT)

This is the most common NAT type, where multiple internal IP addresses are translated to use a single external IP with dynamic ports.

```python
nat_rule_data = {
    "name": "dynamic-ip-port-rule",
    "source_translation": {
        "dynamic_ip_and_port": {
            "type": "dynamic_ip_and_port",
            "translated_address": ["192.168.1.100"]  # Single or multiple IP addresses
        }
    },
    "folder": "NAT Rules"
}
```

Alternatively, you can use an interface for translation:

```python
nat_rule_data = {
    "name": "interface-translation-rule",
    "source_translation": {
        "dynamic_ip_and_port": {
            "type": "dynamic_ip_and_port",
            "interface_address": {
                "interface": "ethernet1/1",
                "ip": "192.168.1.1",
                "floating_ip": "192.168.1.100"  # Optional
            }
        }
    },
    "folder": "NAT Rules"
}
```

### 2. Dynamic IP (NAT)

Dynamic IP NAT allows multiple internal IPs to be translated to a pool of external IPs without port translation.

```python
nat_rule_data = {
    "name": "dynamic-ip-rule",
    "source_translation": {
        "dynamic_ip": {
            "translated_address": ["192.168.1.100", "192.168.1.101"],
            "fallback_type": "translated_address",  # Optional
            "fallback_address": ["10.0.0.100"]  # Optional
        }
    },
    "folder": "NAT Rules"
}
```

### 3. Static IP

This provides a one-to-one mapping between internal and external IPs, optionally with bi-directional support.

```python
nat_rule_data = {
    "name": "static-ip-rule",
    "source_translation": {
        "static_ip": {
            "translated_address": "192.168.1.100",
            "bi_directional": "yes"  # Optional, must be string "yes" or "no"
        }
    },
    "folder": "NAT Rules"
}
```

## Exceptions

| Exception                    | HTTP Code | Description                                                                  |
|------------------------------|-----------|------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                          |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing |
| `NameNotUniqueError`         | 409       | NAT rule name already exists in the container                                |
| `ObjectNotPresentError`      | 404       | NAT rule not found                                                           |
| `AuthenticationError`        | 401       | Authentication failed                                                        |
| `ServerError`                | 500       | Internal server error                                                        |

In addition to these HTTP exceptions, the model validation may raise `ValueError` for various validation issues, such as:

- Using tags other than strings
- Using DNS rewrite with NAT64 rule type
- Using bi-directional static NAT with destination translation
- Providing invalid source translation configurations
- Violating the container requirements

## Basic Configuration

The NAT Rule service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the NAT Rule service directly through the client
nat_rules = client.nat_rule
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import NatRule

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize NatRule object explicitly
nat_rules = NatRule(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating NAT Rules

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Define NAT rule configuration data with dynamic IP and port translation
nat_rule_data = {
    "name": "nat-rule-1",
    "nat_type": "ipv4",
    "service": "any",
    "destination": ["any"],
    "source": ["10.0.0.0/24"],
    "tag": ["Automation"],
    "disabled": False,
    "source_translation": {
        "dynamic_ip_and_port": {
            "type": "dynamic_ip_and_port",
            "translated_address": ["192.168.1.100"]
        }
    },
    "folder": "Texas"
}

# Create a new NAT rule (default position is 'pre')
new_nat_rule = client.nat_rule.create(nat_rule_data)
print(f"Created NAT rule with ID: {new_nat_rule.id}")

# Create a static NAT rule with bi-directional translation
static_nat_data = {
    "name": "static-nat-rule",
    "nat_type": "ipv4",
    "service": "any",
    "destination": ["any"],
    "source": ["10.0.0.10"],
    "source_translation": {
        "static_ip": {
            "translated_address": "192.168.1.100",
            "bi_directional": "yes"
        }
    },
    "folder": "Texas"
}

static_nat_rule = client.nat_rule.create(static_nat_data)
print(f"Created static NAT rule with ID: {static_nat_rule.id}")
```

### Retrieving NAT Rules

```python
# Fetch by name and folder
fetched_rule = client.nat_rule.fetch(
    name="nat-rule-1",
    folder="Texas"
)
print(f"Fetched NAT Rule: {fetched_rule.name}")

# Retrieve a NAT rule by its unique ID
rule_by_id = client.nat_rule.get(fetched_rule.id)
print(f"NAT Rule ID: {rule_by_id.id}, Name: {rule_by_id.name}")
```

### Updating NAT Rules

```python
# Fetch existing NAT rule
existing_rule = client.nat_rule.fetch(
    name="nat-rule-1",
    folder="Texas"
)

# Modify attributes using dot notation
existing_rule.disabled = True
existing_rule.description = "Updated NAT rule"
existing_rule.source = ["10.0.0.0/24", "10.0.1.0/24"]
existing_rule.source_translation = {
    "dynamic_ip": {
        "translated_address": ["192.168.1.100", "192.168.1.101"]
    }
}

# Perform update
updated_rule = client.nat_rule.update(existing_rule)
print(f"Updated NAT Rule: {updated_rule.name}")
```

### Listing NAT Rules

```python
# List all NAT rules in a folder
nat_rules_list = client.nat_rule.list(folder="Texas")

# Process results
for rule in nat_rules_list:
    print(f"Name: {rule.name}, Service: {rule.service}")

    # Check source translation type
    if rule.source_translation:
        if rule.source_translation.dynamic_ip_and_port:
            print("  Translation: Dynamic IP and Port (PAT)")
        elif rule.source_translation.dynamic_ip:
            print("  Translation: Dynamic IP (NAT)")
        elif rule.source_translation.static_ip:
            print("  Translation: Static IP")

# List with position parameter
pre_rules = client.nat_rule.list(folder="Texas", position="pre")
post_rules = client.nat_rule.list(folder="Texas", position="post")
```

### Filtering Responses

The `list()` method supports additional filtering parameters:

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container are returned
- `exclude_folders (List[str])`: List of folder names to exclude from results
- `exclude_snippets (List[str])`: List of snippet values to exclude from results
- `exclude_devices (List[str])`: List of device values to exclude from results
- `nat_type (List[str])`: Filter by NAT types (e.g., `["ipv4", "nat64"]`)
- `service (List[str])`: Filter by services
- `destination (List[str])`: Filter by destination addresses
- `source (List[str])`: Filter by source addresses
- `tag (List[str])`: Filter by tags
- `disabled (bool)`: Filter by disabled status

**Examples:**

```python
# List with exact match on container
exact_rules = client.nat_rule.list(
    folder="Texas",
    exact_match=True
)

# Filter by NAT type
ipv4_rules = client.nat_rule.list(
    folder="Texas",
    nat_type=["ipv4"]
)

# Filter by disabled status
enabled_rules = client.nat_rule.list(
    folder="Texas",
    disabled=False
)

# Filter by tags
tagged_rules = client.nat_rule.list(
    folder="Texas",
    tag=["Automation", "Production"]
)

# Exclude specific folders from results
no_shared_rules = client.nat_rule.list(
    folder="Texas",
    exclude_folders=["Shared"]
)

# Combine multiple filters
filtered_rules = client.nat_rule.list(
    folder="Texas",
    position="pre",
    nat_type=["ipv4"],
    disabled=False,
    tag=["Automation"]
)
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000.

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.nat_rule.max_limit = 1000

# List all NAT rules - auto-paginates through results
all_rules = client.nat_rule.list(folder="Texas")
```

### Deleting NAT Rules

```python
# Get the rule to delete
rule = client.nat_rule.fetch(name="nat-rule-1", folder="Texas")

# Delete by ID
client.nat_rule.delete(str(rule.id))
print(f"Deleted NAT rule: {rule.name}")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated NAT rules",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Create NAT rule
    nat_rule_data = {
        "name": "test-nat-rule",
        "source": ["10.0.0.0/24"],
        "source_translation": {
            "dynamic_ip_and_port": {
                "type": "dynamic_ip_and_port",
                "translated_address": ["192.168.1.100"]
            }
        },
        "folder": "Texas"
    }

    new_rule = client.nat_rule.create(nat_rule_data)

    # Commit changes
    result = client.commit(
        folders=["Texas"],
        description="Added NAT rule",
        sync=True
    )

    # Check job status
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid rule data: {e.message}")
except NameNotUniqueError as e:
    print(f"Rule name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Rule not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified `ScmClient` approach for simpler code
    - Access NAT rule operations via `client.nat_rule` property
    - Perform commit operations directly on the client (`client.commit()`)
    - Monitor jobs directly on the client (`client.get_job_status()`)

2. **NAT Rule Configuration**
    - Use clear and descriptive names for NAT rules
    - Validate IP addresses and subnets for both source and destination
    - Use the appropriate source translation type for your use case
    - Be aware that bi-directional static NAT cannot be used with destination translation

3. **Source Translation Selection**
    - Use **Dynamic IP and Port** for most outbound traffic to the internet
    - Use **Dynamic IP** when preserving the source port is important
    - Use **Static IP** for one-to-one mapping, especially for inbound connections
    - Enable bi-directional mode for static NAT when two-way connections are needed

4. **Container Management**
    - Always provide exactly one container parameter: `folder`, `snippet`, or `device`
    - Use the `exact_match` parameter if strict container matching is required
    - Validate container existence before creating rules

5. **Filtering and Listing**
    - Leverage additional filters (e.g., `nat_type`, `service`, `tag`) for precise listings
    - Use `position` parameter to target pre or post rulebases
    - Use exclusion filters to remove unwanted results

6. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Handle model validation errors for source translation configurations
    - Log responses and exceptions to troubleshoot API issues effectively

7. **Performance**
    - Use the `max_limit` property setter to control pagination
    - Utilize pagination effectively when working with large numbers of NAT rules

## Full Script Examples

Refer to the [nat_rule.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/network/nat_rule.py) for a complete implementation.

## Related Models

- [NatRuleBaseModel](../../models/network/nat_rule_models.md#Overview)
- [NatRuleCreateModel](../../models/network/nat_rule_models.md#Overview)
- [NatRuleUpdateModel](../../models/network/nat_rule_models.md#Overview)
- [NatRuleResponseModel](../../models/network/nat_rule_models.md#Overview)
- [NatRuleMoveModel](../../models/network/nat_rule_models.md#Overview)
- [SourceTranslation](../../models/network/nat_rule_models.md#Overview)
- [DynamicIpAndPort](../../models/network/nat_rule_models.md#Overview)
- [DynamicIp](../../models/network/nat_rule_models.md#Overview)
- [StaticIp](../../models/network/nat_rule_models.md#Overview)
- [DestinationTranslation](../../models/network/nat_rule_models.md#Overview)
- [DnsRewrite](../../models/network/nat_rule_models.md#Overview)
- [InterfaceAddress](../../models/network/nat_rule_models.md#Overview)
- [NatType](../../models/network/nat_rule_models.md#Overview)
- [NatMoveDestination](../../models/network/nat_rule_models.md#Overview)
- [NatRulebase](../../models/network/nat_rule_models.md#Overview)
- [BiDirectional](../../models/network/nat_rule_models.md#Overview)
- [DnsRewriteDirection](../../models/network/nat_rule_models.md#Overview)
