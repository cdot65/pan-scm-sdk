"""Alerts module for Insights API integration."""

from typing import Any, Dict, List, Optional

from scm.config.insights import InsightsBaseObject
from scm.models.insights.alerts import Alert, AlertStatistic


class Alerts(InsightsBaseObject):
    """Alerts service for Prisma Access Insights API.

    This service provides access to security and system alerts from the
    Prisma Access environment. Alerts can be filtered by severity, status,
    time range, and other criteria.

    Example:
        ```python
        # List recent critical alerts
        alerts = client.alerts.list(
            severity=["critical", "high"],
            start_time=7,  # last 7 days
            status=["Raised"]
        )

        # Get alert statistics
        stats = client.alerts.query(
            properties=[
                {"property": "severity"},
                {"property": "alert_id", "function": "distinct_count", "alias": "count"}
            ],
            filter={
                "rules": [
                    {"property": "state", "operator": "in", "values": ["Raised"]},
                    {"property": "updated_time", "operator": "last_n_days", "values": [30]}
                ]
            }
        )
        ```
    """

    def get_resource_endpoint(self) -> str:
        """Get the alerts resource endpoint.

        Returns:
            str: The alerts endpoint path
        """
        return "resource/query/prisma_sase_external_alerts_current"

    def list(
        self,
        *,
        folder: Optional[str] = None,
        severity: Optional[List[str]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        status: Optional[List[str]] = None,
        category: Optional[str] = None,
        max_results: Optional[int] = 100,
        **kwargs,
    ) -> List[Alert]:
        """List alerts with filtering options.

        Args:
            folder: Filter by folder name
            severity: Filter by severity levels (critical, high, medium, low)
            start_time: Filter alerts from this time (days ago or unix timestamp)
            end_time: Filter alerts up to this time
            status: Filter by status (Raised, Cleared, etc.)
            category: Filter by alert category
            max_results: Maximum number of results (default: 100)
            **kwargs: Additional query parameters

        Returns:
            List[Alert]: List of alert objects
        """
        # Build filter rules
        filter_rules: List[Dict[str, Any]] = []

        # Add severity filter
        if severity:
            filter_rules.append({"property": "severity", "operator": "in", "values": severity})

        # Add status filter
        if status:
            filter_rules.append({"property": "state", "operator": "in", "values": status})

        # Add time filters
        if start_time is not None:
            if isinstance(start_time, int) and start_time < 365:
                # Treat as relative days
                filter_rules.append(
                    {
                        "property": "updated_time",
                        "operator": "last_n_days",
                        "values": [start_time],
                    }
                )
            else:
                # Treat as timestamp
                filter_rules.append(
                    {
                        "property": "updated_time",
                        "operator": "greater_or_equal",
                        "values": [start_time],
                    }
                )

        if end_time is not None:
            filter_rules.append(
                {"property": "updated_time", "operator": "less_or_equal", "values": [end_time]}
            )

        # Add category filter
        if category:
            filter_rules.append(
                {"property": "category", "operator": "equals", "values": [category]}
            )

        # Build properties list for detailed alert info
        properties = [
            {"property": "alert_id"},
            {"property": "severity"},
            {"property": "severity_id"},
            {"property": "message", "alias": "name"},
            {"property": "raised_time"},
            {"property": "updated_time"},
            {"property": "state"},
            {"property": "category"},
            {"property": "code"},
            {"property": "primary_impacted_objects", "function": "to_json_string"},
            {"property": "resource_context", "function": "to_json_string"},
            {"property": "clear_reason"},
            {"property": "age"},
        ]

        # Build query
        query_params = {"properties": properties, "count": max_results}

        if filter_rules:
            query_params["filter"] = {"rules": filter_rules}

        # Add any additional parameters
        query_params.update(kwargs)

        # Execute query
        response = self.query(**query_params)

        # Parse response into Alert objects
        # response is now an InsightsResponse object
        alerts_data = response.data

        # Convert to Alert objects
        alerts = []
        for alert_data in alerts_data:
            try:
                alert = Alert(**alert_data)
                alerts.append(alert)
            except Exception:
                # If parsing fails due to missing fields, create partial object
                # This handles cases where some fields might be None/missing
                if isinstance(alert_data, dict):
                    alerts.append(Alert(**{k: v for k, v in alert_data.items() if v is not None}))
                else:
                    alerts.append(alert_data)

        return alerts

    def get(self, alert_id: str, **kwargs) -> Alert:
        """Get a specific alert by ID.

        Args:
            alert_id: The alert ID to retrieve
            **kwargs: Additional query parameters

        Returns:
            Alert: The alert object

        Raises:
            ValueError: If alert not found
        """
        # Query for specific alert
        query_params = {
            "properties": [
                {"property": "alert_id"},
                {"property": "severity"},
                {"property": "severity_id"},
                {"property": "message", "alias": "name"},
                {"property": "raised_time"},
                {"property": "updated_time"},
                {"property": "state"},
                {"property": "category"},
                {"property": "code"},
                {"property": "primary_impacted_objects", "function": "to_json_string"},
                {"property": "resource_context", "function": "to_json_string"},
                {"property": "clear_reason"},
                {"property": "age"},
            ],
            "filter": {
                "rules": [{"property": "alert_id", "operator": "equals", "values": [alert_id]}]
            },
            "count": 1,
        }

        query_params.update(kwargs)

        response = self.query(**query_params)

        # Extract alert data
        # response is now an InsightsResponse object
        if response.data:
            alert_data = response.data[0]
        else:
            raise ValueError(f"Alert with ID '{alert_id}' not found")

        # Convert to Alert object
        return Alert(**alert_data)

    def get_statistics(
        self,
        *,
        time_range: int = 30,
        group_by: str = "severity",
        exclude_notifications: bool = True,
        **kwargs,
    ) -> List[AlertStatistic]:
        """Get alert statistics.

        Args:
            time_range: Number of days to look back (default: 30)
            group_by: Field to group by (severity, category, state)
            exclude_notifications: Whether to exclude notification-level alerts
            **kwargs: Additional query parameters

        Returns:
            List[AlertStatistic]: Alert statistics grouped by the specified field
        """
        # Build filter
        filter_rules = [
            {"property": "updated_time", "operator": "last_n_days", "values": [time_range]}
        ]

        if exclude_notifications:
            filter_rules.append(
                {"property": "severity", "operator": "not_in", "values": ["Notification"]}
            )

        # Build query
        query_params = {
            "properties": [
                {"property": group_by},
                {"property": "alert_id", "function": "distinct_count", "alias": "count"},
            ],
            "filter": {"rules": filter_rules},
        }

        query_params.update(kwargs)

        response = self.query(**query_params)

        # Extract and convert data to AlertStatistic objects
        # response is now an InsightsResponse object
        return [AlertStatistic(**item) for item in response.data]

    def get_timeline(
        self,
        *,
        time_range: int = 7,
        interval: str = "hour",
        status: str = "Raised",
        exclude_notifications: bool = True,
        **kwargs,
    ) -> List[AlertStatistic]:
        """Get alert timeline/histogram data.

        Args:
            time_range: Number of days to look back (default: 7)
            interval: Time interval (hour, day, week)
            status: Alert status to track (Raised, Cleared)
            exclude_notifications: Whether to exclude notification-level alerts
            **kwargs: Additional query parameters

        Returns:
            Dict[str, Any]: Timeline data with counts per interval
        """
        # Determine which time field to use
        time_field = "raised_time" if status == "Raised" else "updated_time"

        # Build filter
        filter_rules = [{"property": time_field, "operator": "last_n_days", "values": [time_range]}]

        if status:
            filter_rules.append({"property": "state", "operator": "equals", "values": [status]})

        if exclude_notifications:
            filter_rules.append(
                {"property": "severity", "operator": "not_in", "values": ["Notification"]}
            )

        # Build query with histogram
        query_params = {
            "properties": [
                {"property": "alert_id", "function": "distinct_count", "alias": "count"}
            ],
            "histogram": {
                "property": time_field,
                "enableEmptyInterval": True,
                "range": interval,
                "value": "1",
            },
            "filter": {"rules": filter_rules},
        }

        query_params.update(kwargs)

        response = self.query(**query_params)

        # Extract and convert data to AlertStatistic objects
        # response is now an InsightsResponse object
        return [AlertStatistic(**item) for item in response.data]
