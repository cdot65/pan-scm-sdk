# InsightsBaseObject Developer Guide

## Table of Contents

- [InsightsBaseObject Developer Guide](#insightsbaseobject-developer-guide)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
    - [Class Hierarchy](#class-hierarchy)
    - [Key Differences from Config Services](#key-differences-from-config-services)
  - [InsightsBaseObject Reference](#insightsbaseobject-reference)
    - [Class Attributes](#class-attributes)
    - [Core Methods](#core-methods)
    - [Abstract Methods](#abstract-methods)
  - [Query API Reference](#query-api-reference)
    - [Query Structure](#query-structure)
    - [Properties Configuration](#properties-configuration)
      - [Basic Properties](#basic-properties)
      - [Property Functions](#property-functions)
      - [Property Aliases](#property-aliases)
    - [Filter Rules](#filter-rules)
      - [Filter Structure](#filter-structure)
      - [Available Operators](#available-operators)
      - [Comparison Operators](#comparison-operators)
      - [Time-Based Operators](#time-based-operators)
      - [String Operators](#string-operators)
      - [Set Operators](#set-operators)
      - [Null Operators](#null-operators)
      - [Combining Filter Rules](#combining-filter-rules)
    - [Histogram Configuration](#histogram-configuration)
      - [Histogram Structure](#histogram-structure)
      - [Interval Options](#interval-options)
    - [Grouping and Ordering](#grouping-and-ordering)
  - [Response Handling](#response-handling)
    - [InsightsResponse Structure](#insightsresponse-structure)
    - [Response Header Fields](#response-header-fields)
  - [Extending InsightsBaseObject](#extending-insightsbaseobject)
    - [Creating a Custom Insights Service](#creating-a-custom-insights-service)
    - [Step-by-Step Guide](#step-by-step-guide)
    - [Complete Example: Custom Tunnel Insights Service](#complete-example-custom-tunnel-insights-service)
    - [Registering Custom Services with the Client](#registering-custom-services-with-the-client)
  - [Best Practices](#best-practices)
    - [Query Optimization](#query-optimization)
    - [Error Handling](#error-handling)
    - [Data Processing](#data-processing)
  - [Common Patterns](#common-patterns)
    - [Pagination Pattern](#pagination-pattern)
    - [Time-Series Analysis Pattern](#time-series-analysis-pattern)
    - [Aggregation Pattern](#aggregation-pattern)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
  - [Related Documentation](#related-documentation)

## Overview

The `InsightsBaseObject` class is an abstract base class that provides the foundation for all Prisma Access Insights API services. Unlike the standard configuration services that use CRUD operations, Insights services use a **query-based API pattern** designed for analytics, reporting, and read-only data access.

This guide provides comprehensive documentation for:

- Understanding the InsightsBaseObject architecture
- Mastering the Query API syntax
- Creating custom Insights services
- Best practices for Insights API integration

## Architecture

### Class Hierarchy

```
InsightsBaseObject (ABC)
    │
    ├── Alerts          # Security and operational alerts
    │
    └── [Custom Services] # User-defined Insights services
```

### Key Differences from Config Services

| Aspect | Config Services (BaseObject) | Insights Services (InsightsBaseObject) |
|--------|------------------------------|---------------------------------------|
| Operations | Full CRUD (Create, Read, Update, Delete) | Read-only (Query, List, Get) |
| API Pattern | RESTful endpoints | Query-based POST requests |
| Base URL | `api.strata.paloaltonetworks.com` | `api.strata.paloaltonetworks.com/insights/v3.0` |
| Data Nature | Configuration objects | Telemetry and analytics data |
| Filtering | URL parameters | JSON query body |
| Aggregation | Not supported | Built-in (group_by, functions) |
| Time-series | Not supported | Histogram support |

## InsightsBaseObject Reference

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `INSIGHTS_BASE_URL` | str | Base URL for Insights API (`https://api.strata.paloaltonetworks.com/insights/v3.0`) |
| `REGION_HEADER` | str | Fixed region header for API requests (`americas`) |
| `_client` | Scm | Reference to the API client for authentication |

### Core Methods

| Method | Description | Return Type |
|--------|-------------|-------------|
| `query(**kwargs)` | Execute a raw query against the Insights API | `InsightsResponse` |
| `list(**kwargs)` | List resources with optional filtering | `List[Dict[str, Any]]` |
| `get(resource_id)` | Get a specific resource by ID | `Dict[str, Any]` |

### Abstract Methods

| Method | Description |
|--------|-------------|
| `get_resource_endpoint()` | Returns the resource-specific endpoint path (must be implemented by subclasses) |

## Query API Reference

### Query Structure

The Insights API uses a JSON-based query structure sent via POST requests:

```python
query_payload = {
    "properties": [...],    # Required: Fields to retrieve
    "filter": {...},        # Optional: Filter criteria
    "count": 100,           # Optional: Maximum results
    "histogram": {...},     # Optional: Time-series bucketing
    "group_by": [...],      # Optional: Grouping fields
    "order_by": [...],      # Optional: Sorting configuration
}
```

### Properties Configuration

#### Basic Properties

Properties define which fields to include in the response:

```python
properties = [
    {"property": "alert_id"},
    {"property": "severity"},
    {"property": "message"},
    {"property": "raised_time"},
]
```

#### Property Functions

Apply aggregation or transformation functions to properties:

| Function | Description | Example Use Case |
|----------|-------------|------------------|
| `distinct_count` | Count unique values | Count unique alerts |
| `count` | Count all values | Total occurrences |
| `sum` | Sum numeric values | Total data transfer |
| `avg` | Average numeric values | Average response time |
| `min` | Minimum value | Earliest timestamp |
| `max` | Maximum value | Latest timestamp |
| `to_json_string` | Convert complex objects to JSON | Serialize nested data |

```python
properties = [
    # Count unique alerts
    {"property": "alert_id", "function": "distinct_count", "alias": "total_alerts"},

    # Get average severity score
    {"property": "severity_id", "function": "avg", "alias": "avg_severity"},

    # Serialize complex nested data
    {"property": "resource_context", "function": "to_json_string"},
]
```

#### Property Aliases

Use aliases to rename fields in the response:

```python
properties = [
    {"property": "message", "alias": "alert_name"},
    {"property": "raised_time", "alias": "timestamp"},
    {"property": "alert_id", "function": "distinct_count", "alias": "count"},
]
```

### Filter Rules

#### Filter Structure

Filters use a rules-based structure:

```python
filter = {
    "rules": [
        {"property": "field_name", "operator": "operator_type", "values": ["value1", "value2"]},
        # Additional rules...
    ]
}
```

#### Available Operators

The Insights API supports a comprehensive set of filter operators:

#### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `equals` | Exact match (single value) | `{"property": "state", "operator": "equals", "values": ["Raised"]}` |
| `not_equals` | Not equal to | `{"property": "severity", "operator": "not_equals", "values": ["Low"]}` |
| `greater_than` | Greater than | `{"property": "severity_id", "operator": "greater_than", "values": [2]}` |
| `greater_or_equal` | Greater than or equal | `{"property": "age", "operator": "greater_or_equal", "values": [7]}` |
| `less_than` | Less than | `{"property": "severity_id", "operator": "less_than", "values": [4]}` |
| `less_or_equal` | Less than or equal | `{"property": "age", "operator": "less_or_equal", "values": [30]}` |

#### Time-Based Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `last_n_days` | Within last N days | `{"property": "updated_time", "operator": "last_n_days", "values": [7]}` |
| `last_n_hours` | Within last N hours | `{"property": "raised_time", "operator": "last_n_hours", "values": [24]}` |
| `last_n_minutes` | Within last N minutes | `{"property": "updated_time", "operator": "last_n_minutes", "values": [30]}` |
| `between` | Between two timestamps | `{"property": "raised_time", "operator": "between", "values": [start_ts, end_ts]}` |

#### String Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `contains` | Contains substring | `{"property": "message", "operator": "contains", "values": ["tunnel"]}` |
| `not_contains` | Does not contain | `{"property": "message", "operator": "not_contains", "values": ["test"]}` |
| `starts_with` | Starts with prefix | `{"property": "category", "operator": "starts_with", "values": ["Remote"]}` |
| `ends_with` | Ends with suffix | `{"property": "code", "operator": "ends_with", "values": ["_ERROR"]}` |
| `like` | SQL-like pattern matching | `{"property": "message", "operator": "like", "values": ["%connection%"]}` |

#### Set Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `in` | Value is in list | `{"property": "severity", "operator": "in", "values": ["Critical", "High"]}` |
| `not_in` | Value is not in list | `{"property": "severity", "operator": "not_in", "values": ["Notification"]}` |

#### Null Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `is_null` | Field is null | `{"property": "clear_reason", "operator": "is_null", "values": []}` |
| `is_not_null` | Field is not null | `{"property": "metadata", "operator": "is_not_null", "values": []}` |

#### Combining Filter Rules

Multiple rules are combined with implicit AND logic:

```python
# All rules must match (AND)
filter = {
    "rules": [
        {"property": "severity", "operator": "in", "values": ["Critical", "High"]},
        {"property": "state", "operator": "equals", "values": ["Raised"]},
        {"property": "updated_time", "operator": "last_n_days", "values": [7]},
    ]
}
```

### Histogram Configuration

Histograms enable time-series analysis by bucketing data into time intervals.

#### Histogram Structure

```python
histogram = {
    "property": "raised_time",        # Time field to bucket
    "range": "hour",                  # Interval type
    "value": "1",                     # Interval value
    "enableEmptyInterval": True,      # Include intervals with zero count
}
```

#### Interval Options

| Range | Description | Use Case |
|-------|-------------|----------|
| `minute` | Per-minute buckets | Real-time monitoring |
| `hour` | Hourly buckets | Daily trend analysis |
| `day` | Daily buckets | Weekly/monthly trends |
| `week` | Weekly buckets | Long-term analysis |
| `month` | Monthly buckets | Historical reporting |

**Example: Hourly Alert Timeline**

```python
response = alerts.query(
    properties=[
        {"property": "alert_id", "function": "distinct_count", "alias": "count"}
    ],
    filter={
        "rules": [
            {"property": "raised_time", "operator": "last_n_days", "values": [7]},
            {"property": "state", "operator": "equals", "values": ["Raised"]}
        ]
    },
    histogram={
        "property": "raised_time",
        "range": "hour",
        "value": "1",
        "enableEmptyInterval": True
    }
)

for bucket in response.data:
    print(f"Time: {bucket.get('raised_time')}, Count: {bucket.get('count')}")
```

### Grouping and Ordering

**Group By**

Group results by one or more fields for aggregation:

```python
response = alerts.query(
    properties=[
        {"property": "severity"},
        {"property": "category"},
        {"property": "alert_id", "function": "distinct_count", "alias": "count"}
    ],
    group_by=["severity", "category"],
    filter={
        "rules": [
            {"property": "updated_time", "operator": "last_n_days", "values": [30]}
        ]
    }
)
```

**Order By**

Sort results by field(s):

```python
response = alerts.query(
    properties=[...],
    order_by=[
        {"property": "raised_time", "order": "desc"},
        {"property": "severity_id", "order": "asc"}
    ]
)
```

## Response Handling

### InsightsResponse Structure

All Insights API queries return an `InsightsResponse` object:

```python
class InsightsResponse(BaseModel):
    header: InsightsResponseHeader  # Metadata about the response
    data: List[Dict[str, Any]]      # Actual query results
```

### Response Header Fields

| Field | Type | Description |
|-------|------|-------------|
| `createdAt` | str | Response timestamp |
| `dataCount` | int | Number of records returned |
| `requestId` | str | Unique request identifier for debugging |
| `queryInput` | Dict | Echo of the query that was executed |
| `isResourceDataOverridden` | bool | Whether data was overridden |
| `fieldList` | List[Dict] | Metadata about returned fields |
| `status` | Dict | Success/failure status |
| `name` | str | Resource name |
| `cache_operation` | Optional[str] | Cache hit/miss information |

**Accessing Response Data**

```python
response = alerts.query(...)

# Check response metadata
print(f"Total records: {response.header.dataCount}")
print(f"Request ID: {response.header.requestId}")
print(f"Success: {response.header.status.get('success')}")

# Process data
for record in response.data:
    print(record)
```

## Extending InsightsBaseObject

### Creating a Custom Insights Service

To create a custom Insights service, extend `InsightsBaseObject` and implement the required abstract method.

### Step-by-Step Guide

1. **Import the base class**
2. **Create your service class**
3. **Implement `get_resource_endpoint()`**
4. **Add custom methods for your use case**

### Complete Example: Custom Tunnel Insights Service

```python
"""Custom Tunnel Insights service example."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from scm.insights import InsightsBaseObject
from scm.models.insights.common import InsightsResponse


# Step 1: Define your data models
class TunnelStatus(BaseModel):
    """Model for tunnel status data."""
    tunnel_id: str
    tunnel_name: Optional[str] = None
    status: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    uptime: Optional[int] = None
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None
    last_updated: Optional[str] = None


class TunnelStatistic(BaseModel):
    """Model for tunnel statistics."""
    status: Optional[str] = None
    count: Optional[int] = None
    total_bytes: Optional[int] = None


# Step 2: Create your service class
class TunnelInsights(InsightsBaseObject):
    """Tunnel Insights service for monitoring IPsec/GRE tunnel status.

    This service provides access to tunnel telemetry data from the
    Prisma Access environment including connection status, throughput,
    and performance metrics.

    Example:
        ```python
        # List active tunnels
        tunnels = client.tunnel_insights.list(
            status=["up"],
            max_results=100
        )

        # Get tunnel statistics
        stats = client.tunnel_insights.get_statistics(
            time_range=7,
            group_by="status"
        )
        ```
    """

    # Step 3: Implement the abstract method
    def get_resource_endpoint(self) -> str:
        """Get the tunnel resource endpoint.

        Returns:
            str: The tunnel insights endpoint path
        """
        # Replace with actual endpoint for your resource
        return "resource/query/tunnel_status"

    # Step 4: Add custom methods
    def list(
        self,
        *,
        status: Optional[List[str]] = None,
        source_ip: Optional[str] = None,
        destination_ip: Optional[str] = None,
        min_uptime: Optional[int] = None,
        max_results: int = 100,
        **kwargs,
    ) -> List[TunnelStatus]:
        """List tunnels with filtering options.

        Args:
            status: Filter by tunnel status (up, down, degraded)
            source_ip: Filter by source IP address
            destination_ip: Filter by destination IP address
            min_uptime: Minimum uptime in seconds
            max_results: Maximum number of results (default: 100)
            **kwargs: Additional query parameters

        Returns:
            List[TunnelStatus]: List of tunnel status objects
        """
        # Build filter rules
        filter_rules: List[Dict[str, Any]] = []

        if status:
            filter_rules.append({
                "property": "status",
                "operator": "in",
                "values": status
            })

        if source_ip:
            filter_rules.append({
                "property": "source_ip",
                "operator": "equals",
                "values": [source_ip]
            })

        if destination_ip:
            filter_rules.append({
                "property": "destination_ip",
                "operator": "equals",
                "values": [destination_ip]
            })

        if min_uptime is not None:
            filter_rules.append({
                "property": "uptime",
                "operator": "greater_or_equal",
                "values": [min_uptime]
            })

        # Define properties to retrieve
        properties = [
            {"property": "tunnel_id"},
            {"property": "tunnel_name"},
            {"property": "status"},
            {"property": "source_ip"},
            {"property": "destination_ip"},
            {"property": "uptime"},
            {"property": "bytes_sent"},
            {"property": "bytes_received"},
            {"property": "last_updated"},
        ]

        # Build query
        query_params = {
            "properties": properties,
            "count": max_results,
        }

        if filter_rules:
            query_params["filter"] = {"rules": filter_rules}

        query_params.update(kwargs)

        # Execute query
        response = self.query(**query_params)

        # Convert to model objects
        return [TunnelStatus(**item) for item in response.data]

    def get(self, tunnel_id: str, **kwargs) -> TunnelStatus:
        """Get a specific tunnel by ID.

        Args:
            tunnel_id: The tunnel ID to retrieve
            **kwargs: Additional query parameters

        Returns:
            TunnelStatus: The tunnel status object

        Raises:
            ValueError: If tunnel not found
        """
        query_params = {
            "properties": [
                {"property": "tunnel_id"},
                {"property": "tunnel_name"},
                {"property": "status"},
                {"property": "source_ip"},
                {"property": "destination_ip"},
                {"property": "uptime"},
                {"property": "bytes_sent"},
                {"property": "bytes_received"},
                {"property": "last_updated"},
            ],
            "filter": {
                "rules": [
                    {"property": "tunnel_id", "operator": "equals", "values": [tunnel_id]}
                ]
            },
            "count": 1,
        }

        query_params.update(kwargs)
        response = self.query(**query_params)

        if not response.data:
            raise ValueError(f"Tunnel with ID '{tunnel_id}' not found")

        return TunnelStatus(**response.data[0])

    def get_statistics(
        self,
        *,
        time_range: int = 30,
        group_by: str = "status",
        **kwargs,
    ) -> List[TunnelStatistic]:
        """Get tunnel statistics.

        Args:
            time_range: Number of days to look back (default: 30)
            group_by: Field to group by (status, source_ip, destination_ip)
            **kwargs: Additional query parameters

        Returns:
            List[TunnelStatistic]: Tunnel statistics grouped by the specified field
        """
        query_params = {
            "properties": [
                {"property": group_by},
                {"property": "tunnel_id", "function": "distinct_count", "alias": "count"},
                {"property": "bytes_sent", "function": "sum", "alias": "total_bytes"},
            ],
            "filter": {
                "rules": [
                    {"property": "last_updated", "operator": "last_n_days", "values": [time_range]}
                ]
            },
        }

        query_params.update(kwargs)
        response = self.query(**query_params)

        return [TunnelStatistic(**item) for item in response.data]

    def get_throughput_timeline(
        self,
        *,
        tunnel_id: Optional[str] = None,
        time_range: int = 7,
        interval: str = "hour",
        **kwargs,
    ) -> InsightsResponse:
        """Get tunnel throughput over time.

        Args:
            tunnel_id: Optional specific tunnel to monitor
            time_range: Number of days to look back (default: 7)
            interval: Time interval (hour, day, week)
            **kwargs: Additional query parameters

        Returns:
            InsightsResponse: Timeline data with throughput per interval
        """
        filter_rules = [
            {"property": "last_updated", "operator": "last_n_days", "values": [time_range]}
        ]

        if tunnel_id:
            filter_rules.append({
                "property": "tunnel_id",
                "operator": "equals",
                "values": [tunnel_id]
            })

        query_params = {
            "properties": [
                {"property": "bytes_sent", "function": "sum", "alias": "total_sent"},
                {"property": "bytes_received", "function": "sum", "alias": "total_received"},
            ],
            "histogram": {
                "property": "last_updated",
                "range": interval,
                "value": "1",
                "enableEmptyInterval": True,
            },
            "filter": {"rules": filter_rules},
        }

        query_params.update(kwargs)
        return self.query(**query_params)
```

### Registering Custom Services with the Client

To use your custom service with the SCM client, you can manually instantiate it:

```python
from scm.client import ScmClient
from my_insights.tunnel import TunnelInsights

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create custom service instance
tunnel_insights = TunnelInsights(client)

# Use the service
tunnels = tunnel_insights.list(status=["up"], max_results=50)
for tunnel in tunnels:
    print(f"Tunnel: {tunnel.tunnel_name} - Status: {tunnel.status}")
```

## Best Practices

### Query Optimization

1. **Limit Properties**: Only request the fields you need

   ```python
   # Good: Specific properties
   properties = [
       {"property": "alert_id"},
       {"property": "severity"},
       {"property": "message"}
   ]

   # Avoid: Requesting all fields when you only need a few
   ```

2. **Use Server-Side Filtering**: Filter on the server, not in your code

   ```python
   # Good: Server-side filtering
   alerts = client.alerts.list(severity=["Critical"], status=["Raised"])

   # Avoid: Fetching all and filtering client-side
   all_alerts = client.alerts.list()
   critical = [a for a in all_alerts if a.severity == "Critical"]
   ```

3. **Set Reasonable Limits**: Use `count` to limit results

   ```python
   # Good: Limit results
   response = alerts.query(properties=[...], count=100)

   # Avoid: Unbounded queries on large datasets
   ```

### Error Handling

```python
from scm.exceptions import APIError, AuthenticationError

try:
    response = custom_service.query(
        properties=[{"property": "field_name"}],
        filter={"rules": [...]}
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Handle re-authentication
except APIError as e:
    print(f"API error: {e}")
    # Handle API errors (rate limits, invalid queries, etc.)
except ValueError as e:
    print(f"Resource not found: {e}")
    # Handle not found errors
```

### Data Processing

1. **Handle Optional Fields**: Insights data may have null values

   ```python
   for alert in alerts:
       severity = alert.severity or "Unknown"
       category = alert.category or "Uncategorized"
   ```

2. **Parse JSON Fields**: Some fields contain serialized JSON

   ```python
   import json

   for alert in alerts:
       if alert.metadata:
           try:
               metadata = json.loads(alert.metadata) if isinstance(alert.metadata, str) else alert.metadata
           except json.JSONDecodeError:
               metadata = {}
   ```

## Common Patterns

### Pagination Pattern

For large datasets, implement pagination:

```python
def fetch_all_alerts(client, batch_size=1000):
    """Fetch all alerts with pagination."""
    all_alerts = []
    offset = 0

    while True:
        batch = client.alerts.list(
            max_results=batch_size,
            # Note: Implement offset handling based on your needs
        )

        if not batch:
            break

        all_alerts.extend(batch)

        if len(batch) < batch_size:
            break

        offset += batch_size

    return all_alerts
```

### Time-Series Analysis Pattern

```python
def analyze_alert_trends(client, days=30, interval="day"):
    """Analyze alert trends over time."""
    timeline = client.alerts.get_timeline(
        time_range=days,
        interval=interval,
        status="Raised"
    )

    # Calculate statistics
    counts = [point.count for point in timeline if point.count]

    if counts:
        avg_daily = sum(counts) / len(counts)
        max_daily = max(counts)
        min_daily = min(counts)

        print(f"Average {interval}ly alerts: {avg_daily:.1f}")
        print(f"Max {interval}ly alerts: {max_daily}")
        print(f"Min {interval}ly alerts: {min_daily}")
```

### Aggregation Pattern

```python
def get_alert_breakdown(client, group_fields):
    """Get alert breakdown by multiple dimensions."""
    results = {}

    for field in group_fields:
        stats = client.alerts.get_statistics(
            time_range=30,
            group_by=field
        )

        results[field] = {
            stat.get(field, "Unknown"): stat.count
            for stat in stats
        }

    return results

# Usage
breakdown = get_alert_breakdown(client, ["severity", "category", "state"])
```

## Troubleshooting

### Common Issues

1. **Empty Results**

   - Verify your filter rules are correct
   - Check the time range - data may not exist for the specified period
   - Ensure property names match the API schema

2. **Authentication Errors**

   - Verify your credentials are valid
   - Check that your TSG ID has access to Insights API
   - Ensure your token hasn't expired

3. **Invalid Query Errors**

   - Check property names are spelled correctly
   - Verify operator names are valid
   - Ensure value types match the property type (string vs int)

4. **Rate Limiting**

   - Implement exponential backoff
   - Reduce query frequency
   - Use caching for frequently accessed data

## Related Documentation

- [Alerts Service](alerts.md) - Detailed documentation for the Alerts Insights service
- [Alerts Models](../models/insights/alerts_models.md) - Data models for alert responses
- [Authentication](../auth.md) - Authentication configuration
- [Error Handling](../exceptions.md) - Exception types and error handling
