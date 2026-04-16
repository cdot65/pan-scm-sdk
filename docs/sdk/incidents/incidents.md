# Incidents

Search and retrieve security incident details from the Unified Incident Framework in Strata Cloud Manager.

## Class Overview

The `Incidents` class inherits from `ServiceBase` and provides methods for searching incidents with filtering and pagination, and retrieving detailed incident information including alerts and remediation steps.

!!! note
    The Incidents API requires the `X-PANW-Region` header. The SDK sets this automatically from the `region` parameter passed to the `Scm` client (default: `"americas"`).

### Methods

| Method | Description | Parameters | Return Type |
| --- | --- | --- | --- |
| `search()` | Search incidents with filters | `status`, `severity`, `product`, `filter_rules`, `page_size`, `page_number`, `order_by` | `IncidentSearchResponseModel` |
| `get_details()` | Get full incident details | `incident_id` | `IncidentDetailModel` |

### Exceptions

| Exception | HTTP Code | Description |
| --- | --- | --- |
| `AuthenticationError` | 401 | Authentication failed |
| `ObjectNotPresentError` | 404 | Incident not found |
| `ServerError` | 500 | Internal server error |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    region="americas"  # Sets X-PANW-Region header
)
```

## Methods

### Search Incidents

Search for incidents using convenience filters or raw filter rules.

```python
# Search all incidents (default pagination: 50 per page)
result = client.incidents.search()
print(f"Found {len(result.data)} incidents")

# Filter by status
result = client.incidents.search(status=["Raised"])

# Filter by severity and product
result = client.incidents.search(
    severity=["Critical", "High"],
    product=["Prisma Access", "NGFW"]
)

# Custom pagination
result = client.incidents.search(
    page_size=25,
    page_number=2,
    order_by=[{"property": "updated_time", "order": "desc"}]
)
```

**Using raw filter rules for full control:**

```python
# Raw filter rules bypass convenience kwargs
result = client.incidents.search(
    filter_rules=[
        {"property": "release_state", "operator": "in", "values": ["Released"]},
        {"property": "status", "operator": "in", "values": ["Raised"]},
        {"property": "product", "operator": "in", "values": ["NGFW"]},
    ]
)
```

### Get Incident Details

Retrieve comprehensive information about a specific incident, including alerts and remediation steps.

```python
# Get detailed incident information
detail = client.incidents.get_details("21818c4a-8353-4d9c-ae3e-ae90004d4662")

print(f"Title: {detail.title}")
print(f"Severity: {detail.severity}")
print(f"Status: {detail.status}")
print(f"Description: {detail.description}")

# Access associated alerts
if detail.alerts:
    for alert in detail.alerts:
        print(f"  Alert: {alert.title} ({alert.severity})")
```

## Use Cases

### Monitor Critical Incidents

```python
# Find all critical raised incidents
result = client.incidents.search(
    status=["Raised"],
    severity=["Critical"],
    order_by=[{"property": "updated_time", "order": "desc"}]
)

for incident in result.data:
    print(f"[{incident.severity}] {incident.title}")
    print(f"  Product: {incident.product}")
    print(f"  ID: {incident.incident_id}")
    print()
```

### Paginate Through All Incidents

```python
page = 1
all_incidents = []

while True:
    result = client.incidents.search(
        status=["Raised"],
        page_size=50,
        page_number=page
    )
    all_incidents.extend(result.data)

    if len(result.data) < 50:
        break
    page += 1

print(f"Total incidents: {len(all_incidents)}")
```

### Incident Detail Drill-Down

```python
# Search for incidents, then get details on each
result = client.incidents.search(
    severity=["Critical"],
    page_size=5
)

for incident in result.data:
    detail = client.incidents.get_details(incident.incident_id)
    print(f"\n{'='*60}")
    print(f"Title: {detail.title}")
    print(f"Product: {detail.product}")
    print(f"Category: {detail.category}")

    if detail.description:
        print(f"Description: {detail.description}")

    if detail.remediations:
        print(f"Remediations: {detail.remediations}")

    if detail.alerts:
        print(f"Alerts ({len(detail.alerts)}):")
        for alert in detail.alerts:
            print(f"  - {alert.title} [{alert.severity}]")
```

## Error Handling

```python
from scm.exceptions import (
    AuthenticationError,
    ObjectNotPresentError,
    ServerError,
)

try:
    result = client.incidents.search(
        severity=["Critical"],
        status=["Raised"]
    )
except AuthenticationError:
    print("Authentication failed. Check your credentials.")
except ServerError as e:
    print(f"Server error: {e.message}")

try:
    detail = client.incidents.get_details("nonexistent-id")
except ObjectNotPresentError:
    print("Incident not found.")
```

## Related Topics

- [Incidents Models](../../models/incidents/index.md)
- [Client Module](../../client.md)
- [Exceptions](../../exceptions.md)
