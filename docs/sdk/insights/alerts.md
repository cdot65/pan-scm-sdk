# Alerts Configuration Object

## Table of Contents

- [Alerts Configuration Object](#alerts-configuration-object)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Core Methods](#core-methods)
  - [Alert Model Attributes](#alert-model-attributes)
  - [Exceptions](#exceptions)
  - [Basic Configuration](#basic-configuration)
  - [Usage Examples](#usage-examples)
    - [Listing Alerts](#listing-alerts)
    - [Filtering Alerts](#filtering-alerts)
    - [Getting Alert Statistics](#getting-alert-statistics)
    - [Generating Alert Timelines](#generating-alert-timelines)
    - [Using Custom Queries](#using-custom-queries)
  - [Error Handling](#error-handling)
  - [Best Practices](#best-practices)
  - [Full Script Examples](#full-script-examples)
  - [Related Models](#related-models)

## Overview

The `Alerts` class provides functionality to access and analyze security and operational alerts from Palo Alto Networks' Prisma Access Insights API. This class inherits from `InsightsBaseObject` and provides methods for retrieving alerts, generating statistics, and creating timeline views of alert activity.

## Core Methods

| Method             | Description                  | Parameters                                                       | Return Type            |
| ------------------ | ---------------------------- | ---------------------------------------------------------------- | ---------------------- |
| `list()`           | Lists alerts with filtering  | `severity`, `status`, `start_time`, `end_time`, `category`, etc. | `List[Alert]`          |
| `query()`          | Execute custom query         | `properties`, `filter`, `group_by`, `order_by`, etc.             | `InsightsResponse`     |
| `get_statistics()` | Get alert statistics         | `time_range`, `group_by`, `exclude_notifications`                | `List[AlertStatistic]` |
| `get_timeline()`   | Get alert timeline/histogram | `time_range`, `interval`, `status`, `exclude_notifications`      | `List[AlertStatistic]` |

## Alert Model Attributes

| Attribute            | Type                     | Description                                                 |
| -------------------- | ------------------------ | ----------------------------------------------------------- |
| `id`                 | str                      | Alert ID (mapped from `alert_id`)                           |
| `name`               | Optional[str]            | Alert message/name (mapped from `message`)                  |
| `severity`           | Optional[str]            | Alert severity (Critical, High, Medium, Low, etc.)          |
| `severity_id`        | Optional[int]            | Numeric severity identifier                                 |
| `status`             | Optional[str]            | Alert state (Raised, RaisedChild, Cleared)                  |
| `timestamp`          | Optional[str]            | When alert was raised (mapped from `raised_time`)           |
| `updated_time`       | Optional[str]            | Last update timestamp                                       |
| `description`        | Optional[str]            | Detailed alert description                                  |
| `folder`             | Optional[str]            | Associated folder                                           |
| `source`             | Optional[str]            | Alert source                                                |
| `category`           | Optional[str]            | Alert category                                              |
| `code`               | Optional[str]            | Alert code                                                  |
| `impacted_resources` | Optional[List[str]]      | Affected resources (mapped from `primary_impacted_objects`) |
| `metadata`           | Optional[Dict[str, Any]] | Additional context (mapped from `resource_context`)         |
| `clear_reason`       | Optional[str]            | Reason alert was cleared                                    |
| `age`                | Optional[int]            | Alert age in days                                           |

## Exceptions

| Exception                    | HTTP Code | Description                 |
| ---------------------------- | --------- | --------------------------- |
| `InvalidObjectError`         | 400       | Invalid query parameters    |
| `MissingQueryParameterError` | 400       | Missing required parameters |
| `AuthenticationError`        | 401       | Authentication failed       |
| `ServerError`                | 500       | Internal server error       |

## Basic Configuration

The Alerts service can be accessed using the unified client interface through the Insights namespace.

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Alerts service through the insights namespace
alerts = client.insights.alerts
```

## Usage Examples

### Listing Alerts

```python
# List all alerts (default: last 30 days)
all_alerts = client.insights.alerts.list()
print(f"Found {len(all_alerts)} alerts")

# List alerts with specific severity
critical_alerts = client.insights.alerts.list(
    severity=["critical", "high"]
)
print(f"Found {len(critical_alerts)} critical/high severity alerts")

# List alerts from the last 7 days
recent_alerts = client.insights.alerts.list(
    start_time=7  # Relative days
)
print(f"Found {len(recent_alerts)} alerts from the last 7 days")
```

### Filtering Alerts

```python
# Filter by multiple criteria
filtered_alerts = client.insights.alerts.list(
    severity=["high", "critical"],
    status=["Raised"],
    category="Remote Networks",
    start_time=30,
    max_results=100
)

for alert in filtered_alerts:
    print(f"Alert: {alert.name}")
    print(f"  Severity: {alert.severity}")
    print(f"  Status: {alert.status}")
    print(f"  Category: {alert.category}")
    print(f"  Raised: {alert.timestamp}")
    if alert.impacted_resources:
        print(f"  Impacted: {', '.join(alert.impacted_resources)}")
```

### Getting Alert Statistics

```python
# Get alert statistics grouped by severity (default)
severity_stats = client.insights.alerts.get_statistics()

for stat in severity_stats:
    print(f"Severity: {stat.severity}, Count: {stat.count}")

# Get statistics grouped by category
category_stats = client.insights.alerts.get_statistics(
    time_range=90,  # Last 90 days
    group_by="category",
    exclude_notifications=True
)

for stat in category_stats:
    print(f"Category: {stat.category}, Count: {stat.count}")

# Get statistics grouped by state
state_stats = client.insights.alerts.get_statistics(
    time_range=30,
    group_by="state"
)

for stat in state_stats:
    print(f"State: {stat.state}, Count: {stat.count}")
```

### Generating Alert Timelines

```python
# Get hourly timeline for the last 7 days
hourly_timeline = client.insights.alerts.get_timeline(
    time_range=7,
    interval="hour",
    status="Raised"
)

for point in hourly_timeline:
    print(f"Time: {point.state}, Count: {point.count}")

# Get daily timeline for the last 30 days
daily_timeline = client.insights.alerts.get_timeline(
    time_range=30,
    interval="day",
    status="Raised",
    exclude_notifications=True
)

for point in daily_timeline:
    print(f"Day: {point.state}, Alerts: {point.count}")

# Get weekly timeline
weekly_timeline = client.insights.alerts.get_timeline(
    time_range=90,
    interval="week",
    status="Cleared"
)
```

### Using Custom Queries

```python
# Custom query with specific properties and filters
custom_query = client.insights.alerts.query(
    properties=[
        {"property": "alert_id"},
        {"property": "message"},
        {"property": "severity"},
        {"property": "state"},
        {"property": "raised_time"}
    ],
    filter={
        "rules": [
            {"property": "severity", "operator": "in", "values": ["Critical", "High"]},
            {"property": "state", "operator": "equals", "values": ["Raised"]},
            {"property": "updated_time", "operator": "last_n_days", "values": ["7"]}
        ]
    },
    order_by=[{"property": "raised_time", "order": "desc"}],
    limit=50
)

# Process the raw response
for item in custom_query.data:
    print(f"Alert {item.get('alert_id')}: {item.get('message')}")

# Query with grouping for aggregation
aggregated_query = client.insights.alerts.query(
    properties=[
        {"property": "severity"},
        {"property": "alert_id", "function": "distinct_count", "alias": "alert_count"}
    ],
    group_by=["severity"],
    filter={
        "rules": [
            {"property": "updated_time", "operator": "last_n_days", "values": ["30"]}
        ]
    }
)

for group in aggregated_query.data:
    print(f"Severity: {group.get('severity')}, Count: {group.get('alert_count')}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    AuthenticationError,
    ServerError
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Attempt to list alerts with invalid parameters
    alerts = client.insights.alerts.list(
        severity=["invalid_severity"]
    )

except InvalidObjectError as e:
    print(f"Invalid parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except ServerError as e:
    print(f"Server error: {e.message}")
```

## Best Practices

1. **Time Range Management**

   - Use relative time ranges (days) for consistent queries
   - Be mindful of data retention limits
   - Consider query performance with large time ranges

2. **Filtering and Performance**

   - Apply filters to reduce response size
   - Use `max_results` to limit returned data
   - Leverage server-side filtering over client-side

3. **Alert Categories**

   - Familiarize yourself with available categories
   - Use category filters to focus on specific areas
   - Consider category-specific alert handling

4. **Statistics and Trends**

   - Use `get_statistics()` for summary views
   - Leverage `get_timeline()` for trend analysis
   - Exclude notifications for security-focused analysis

5. **Error Handling**

   - Implement comprehensive error handling
   - Log errors for troubleshooting
   - Handle rate limits gracefully

6. **Data Processing**
   - Parse JSON fields in responses when needed
   - Handle optional fields appropriately
   - Consider caching frequently accessed data

## Full Script Examples

```python
from scm.client import ScmClient
from datetime import datetime
import json

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Example 1: Daily Alert Summary Report
def generate_daily_summary():
    """Generate a daily summary of alerts."""
    print("=== Daily Alert Summary ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    # Get today's alerts
    todays_alerts = client.insights.alerts.list(
        start_time=1,  # Last 24 hours
        status=["Raised"]
    )

    # Group by severity
    severity_counts = {}
    for alert in todays_alerts:
        severity = alert.severity or "Unknown"
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    print(f"\nTotal Alerts: {len(todays_alerts)}")
    print("\nBy Severity:")
    for severity, count in sorted(severity_counts.items()):
        print(f"  {severity}: {count}")

    # Get top categories
    category_counts = {}
    for alert in todays_alerts:
        category = alert.category or "Uncategorized"
        category_counts[category] = category_counts.get(category, 0) + 1

    print("\nTop Categories:")
    for category, count in sorted(
        category_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]:
        print(f"  {category}: {count}")

# Example 2: Alert Trend Analysis
def analyze_alert_trends():
    """Analyze alert trends over time."""
    print("\n=== Alert Trend Analysis ===")

    # Get 30-day statistics
    stats = client.insights.alerts.get_statistics(
        time_range=30,
        group_by="severity"
    )

    print("\n30-Day Alert Distribution:")
    total = sum(stat.count for stat in stats)
    for stat in sorted(stats, key=lambda x: x.count, reverse=True):
        percentage = (stat.count / total * 100) if total > 0 else 0
        print(f"  {stat.severity}: {stat.count} ({percentage:.1f}%)")

    # Get weekly timeline
    timeline = client.insights.alerts.get_timeline(
        time_range=30,
        interval="week",
        status="Raised"
    )

    print("\nWeekly Alert Volume:")
    for week in timeline:
        print(f"  Week {week.state}: {week.count} alerts")

# Example 3: Critical Alert Monitor
def monitor_critical_alerts():
    """Monitor and report critical alerts."""
    print("\n=== Critical Alert Monitor ===")

    # Get recent critical alerts
    critical_alerts = client.insights.alerts.list(
        severity=["critical"],
        status=["Raised"],
        start_time=7,
        max_results=10
    )

    if not critical_alerts:
        print("No critical alerts in the last 7 days")
        return

    print(f"Found {len(critical_alerts)} critical alerts:")
    for alert in critical_alerts:
        print(f"\nAlert ID: {alert.id}")
        print(f"  Message: {alert.name}")
        print(f"  Raised: {alert.timestamp}")
        print(f"  Category: {alert.category}")

        if alert.impacted_resources:
            print(f"  Impacted Resources: {', '.join(alert.impacted_resources)}")

        if alert.metadata:
            print("  Metadata:")
            for key, value in alert.metadata.items():
                print(f"    {key}: {value}")

# Run all examples
if __name__ == "__main__":
    generate_daily_summary()
    analyze_alert_trends()
    monitor_critical_alerts()
```

## Related Models

- [Alert](../models/insights/alerts_models.md#alert)
- [AlertStatistic](../models/insights/alerts_models.md#alertstatistic)
- [AlertSeverity](../models/insights/alerts_models.md#alertseverity)
- [AlertStatus](../models/insights/alerts_models.md#alertstatus)
