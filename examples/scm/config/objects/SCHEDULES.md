# Schedules

This guide provides examples of using the Strata Cloud Manager SDK to manage Schedule objects.

## Overview

Schedule objects in SCM define time periods when security policies should be active. They can be used to control when rules are enforced, limiting their effect to specific time windows. There are three main types of schedules:

- **Daily Schedule**: Defines the same time window for every day
- **Weekly Schedule**: Defines different time windows for specific days of the week
- **Non-recurring Schedule**: Defines a one-time date and time range for special events

The example script demonstrates how to:
- Create different types of schedules
- Update existing schedules
- List and filter schedules
- Generate comprehensive CSV reports
- Delete schedules when they're no longer needed

## Usage

The example script can be executed directly:

```bash
python examples/scm/config/objects/schedules.py
```

### Authentication

The script supports authentication via environment variables or command-line arguments:

```bash
export SCM_CLIENT_ID="your-client-id"
export SCM_CLIENT_SECRET="your-client-secret"
export SCM_API_SCOPE="tsg_id:all"
```

Or provide them as arguments:

```bash
python examples/scm/config/objects/schedules.py \
  --client-id="your-client-id" \
  --client-secret="your-client-secret" \
  --scope="tsg_id:all"
```

### Additional Options

The script supports these additional options:

- `--skip-delete`: Prevent deletion of created objects
- `--debug`: Enable debug logging
- `--api-url`: Override the default API URL
- `--token-url`: Override the default token URL

## Schedule Types and Examples

### Daily Schedule

Daily schedules apply the same time window for every day of the week.

```python
schedule = schedule_client.create(
    name="Daily-WorkHours",
    description="Daily schedule for standard work hours",
    schedule_type="recurring",
    recurring_type="daily",
    daily_time_ranges=["08:00-17:00"]
)
```

### Weekly Schedule

Weekly schedules allow different time windows for specific days of the week.

```python
schedule = schedule_client.create(
    name="Weekly-WorkDays",
    description="Weekly schedule for Mon, Wed, Fri work days",
    schedule_type="recurring", 
    recurring_type="weekly",
    weekly_time_ranges={
        "monday": ["09:00-17:00"],
        "wednesday": ["09:00-17:00"],
        "friday": ["09:00-13:00"]
    }
)
```

### Non-recurring Schedule

Non-recurring schedules define one-time date and time ranges for special events.

```python
schedule = schedule_client.create(
    name="NonRecurring-Event",
    description="Schedule for a special one-time event",
    schedule_type="non-recurring",
    non_recurring_date_time_ranges=[
        {
            "start_date": "2025-04-05",
            "start_time": "08:00",
            "end_date": "2025-04-10", 
            "end_time": "17:00"
        }
    ]
)
```

## Filtering Schedules

You can filter schedules based on their type:

```python
# List all schedules
all_schedules = schedule_client.list()

# List only recurring schedules
recurring_schedules = schedule_client.list(schedule_type="recurring")

# List only non-recurring schedules
non_recurring_schedules = schedule_client.list(schedule_type="non-recurring")
```

## Updating Schedules

Update an existing schedule by specifying its ID and the attributes to change:

```python
updated_schedule = schedule_client.update(
    id="schedule-id",
    description="Updated description"
)
```

## Deleting Schedules

Delete a schedule when it's no longer needed:

```python
schedule_client.delete(id="schedule-id")
```

## Report Generation

The example script demonstrates generating CSV reports of all schedules, which is useful for auditing and documentation purposes.