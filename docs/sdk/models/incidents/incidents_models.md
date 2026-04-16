# Incidents Models

Pydantic models for incident search, filtering, pagination, and detail retrieval in Strata Cloud Manager.

## Overview

The Incidents models provide data validation for:

- Building search queries with filter rules and pagination
- Parsing incident search responses with metadata
- Representing individual incidents with severity, status, and impacted objects
- Detailed incident information with alerts and remediation steps

## Request Models

### FilterRuleModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `property` | `str` | Yes | The property to filter on |
| `operator` | `str` | Yes | The filter operator (e.g., `in`, `equals`) |
| `values` | `List[Any]` | Yes | The values to filter by |

### PaginationModel

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `page_size` | `int` | No | `50` | Number of results per page |
| `page_number` | `int` | No | `1` | Page number to retrieve |
| `order_by` | `Optional[List[Dict]]` | No | `None` | Ordering specification |

### IncidentSearchRequestModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `filter` | `Optional[FilterObjectModel]` | No | Filter rules container |
| `pagination` | `Optional[PaginationModel]` | No | Pagination parameters |

## Response Models

### IncidentSearchResponseModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `header` | `IncidentSearchResponseHeaderModel` | Yes | Response metadata (pagination, counts) |
| `data` | `List[IncidentModel]` | No | List of matching incidents |

### IncidentModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `incident_id` | `str` | Yes | Unique incident identifier |
| `title` | `str` | Yes | Incident title |
| `severity` | `str` | Yes | Severity level (Critical, High, etc.) |
| `severity_id` | `Optional[int]` | No | Numeric severity identifier |
| `status` | `str` | Yes | Incident status (Raised, Cleared) |
| `priority` | `Optional[str]` | No | Priority level |
| `product` | `str` | Yes | Product (NGFW, Prisma Access, etc.) |
| `category` | `Optional[str]` | No | Incident category |
| `sub_category` | `Optional[str]` | No | Incident sub-category |
| `code` | `Optional[str]` | No | Incident code identifier |
| `raised_time` | `Optional[int]` | No | Epoch timestamp when raised |
| `updated_time` | `Optional[int]` | No | Epoch timestamp of last update |
| `cleared_time` | `Optional[int]` | No | Epoch timestamp when cleared |
| `incident_type` | `Optional[str]` | No | Type classification |
| `acknowledged` | `Optional[bool]` | No | Whether incident is acknowledged |
| `primary_impacted_objects` | `Optional[ImpactedObjectsModel]` | No | Primary impacted resources |
| `related_impacted_objects` | `Optional[ImpactedObjectsModel]` | No | Related impacted resources |
| `snow_ticket_id` | `Optional[str]` | No | ServiceNow ticket ID |

### IncidentDetailModel

Extends `IncidentModel` with additional fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `description` | `Optional[str]` | No | Detailed incident description |
| `remediations` | `Optional[str]` | No | JSON string with remediation steps |
| `detail` | `Optional[str]` | No | JSON string with detailed alert info |
| `alerts` | `Optional[List[AlertModel]]` | No | Associated alerts |
| `resource_keys` | `Optional[str]` | No | JSON string with resource identifiers |
| `resource_context` | `Optional[str]` | No | JSON string with contextual info |
| `incident_code` | `Optional[str]` | No | Incident code |
| `incident_settings_id` | `Optional[str]` | No | Incident settings identifier |

## Component Models

### AlertModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `alert_id` | `str` | Yes | Unique alert identifier |
| `severity` | `Optional[str]` | No | Alert severity |
| `state` | `Optional[str]` | No | Alert state |
| `title` | `Optional[str]` | No | Alert title |
| `updated_time` | `Optional[int]` | No | Last update timestamp |
| `domain` | `Optional[str]` | No | Alert domain |
| `code` | `Optional[str]` | No | Alert code |

### ImpactedObjectsModel

All fields are `Optional[List[str]]` and default to `None`. Key fields include:

| Field | Description |
| --- | --- |
| `device_ids` | Impacted device identifiers |
| `host_names` | Impacted host names |
| `interfaces` | Impacted network interfaces |
| `locations` | Impacted locations |
| `zones` | Impacted security zones |
| `site_names` | Impacted site names |
| `tunnel_names` | Impacted tunnel names |
| `certificate_names` | Impacted certificates |
| `cves` | Related CVE identifiers |

## Usage Examples

### Creating a Search Request

```python
from scm.models.incidents.incidents import (
    FilterRuleModel,
    PaginationModel,
    IncidentSearchRequestModel,
)

# Build a search request
request = IncidentSearchRequestModel(
    filter={"rules": [
        {"property": "status", "operator": "in", "values": ["Raised"]},
        {"property": "severity", "operator": "in", "values": ["Critical"]},
    ]},
    pagination={"page_size": 25, "page_number": 1}
)
```

### Parsing a Search Response

```python
from scm.models.incidents.incidents import IncidentSearchResponseModel

response = IncidentSearchResponseModel(**api_response)
for incident in response.data:
    print(f"{incident.severity}: {incident.title} ({incident.status})")
```

### Working with Incident Details

```python
from scm.models.incidents.incidents import IncidentDetailModel

detail = IncidentDetailModel(**api_response)
print(f"Title: {detail.title}")
if detail.alerts:
    for alert in detail.alerts:
        print(f"  Alert: {alert.title}")
```

## Related Documentation

- [Incidents Service](../../incidents/incidents.md)
- [API Client](../../client.md)
