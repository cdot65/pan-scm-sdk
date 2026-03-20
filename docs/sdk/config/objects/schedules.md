# Schedules

The `Schedule` service manages schedule objects in Strata Cloud Manager, defining time-based configurations (recurring weekly/daily or non-recurring) that specify when security policies should be active.

## Class Overview

The `Schedule` class provides CRUD operations for schedule objects. It is accessed through the `client.schedule` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Schedule service
schedules = client.schedule
```

### Key Attributes

| Attribute       | Type                | Required | Description                                       |
|-----------------|---------------------|----------|---------------------------------------------------|
| `name`          | `str`               | Yes      | Name of the schedule object (max 31 chars)        |
| `id`            | `UUID`              | Yes*     | Unique identifier (*response only)                |
| `schedule_type` | `ScheduleTypeModel` | Yes      | The type of schedule (recurring or non-recurring) |
| `folder`        | `str`               | Yes**    | Folder location (max 64 chars)                    |
| `snippet`       | `str`               | Yes**    | Snippet location (max 64 chars)                   |
| `device`        | `str`               | Yes**    | Device location (max 64 chars)                    |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Schedules

Retrieves a list of schedule objects with optional filtering.

```python
schedules = client.schedule.list(folder="Texas")

for schedule in schedules:
    print(f"Name: {schedule.name}")
```

### Fetch a Schedule

Retrieves a single schedule by name and container.

```python
schedule = client.schedule.fetch(name="WeekdayBusiness", folder="Texas")
print(f"Found schedule: {schedule.name}")
```

### Create a Schedule

Creates a new schedule object.

```python
# Weekly schedule
weekly = client.schedule.create({
    "name": "WeekdayBusiness",
    "folder": "Texas",
    "schedule_type": {
        "recurring": {
            "weekly": {
                "monday": ["09:00-17:00"],
                "tuesday": ["09:00-17:00"],
                "wednesday": ["09:00-17:00"],
                "thursday": ["09:00-17:00"],
                "friday": ["09:00-17:00"]
            }
        }
    }
})

# Non-recurring schedule
event = client.schedule.create({
    "name": "HolidayEvent",
    "folder": "Texas",
    "schedule_type": {
        "non_recurring": ["2025/12/25@00:00-2025/12/26@00:00"]
    }
})
```

### Update a Schedule

Updates an existing schedule object.

```python
existing = client.schedule.fetch(name="WeekdayBusiness", folder="Texas")

if existing.schedule_type.recurring and existing.schedule_type.recurring.weekly:
    existing.schedule_type.recurring.weekly.saturday = ["09:00-13:00"]

updated = client.schedule.update(existing)
```

### Delete a Schedule

Deletes a schedule object by ID.

```python
schedule = client.schedule.fetch(name="HolidayEvent", folder="Texas")
client.schedule.delete(schedule.id)
```

## Use Cases

### Creating Recurring Schedules

Define weekly and daily recurring schedules for policy enforcement.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Weekly business hours
client.schedule.create({
    "name": "WeekdayBusiness",
    "folder": "Texas",
    "schedule_type": {
        "recurring": {
            "weekly": {
                "monday": ["09:00-17:00"],
                "tuesday": ["09:00-17:00"],
                "wednesday": ["09:00-17:00"],
                "thursday": ["09:00-17:00"],
                "friday": ["09:00-17:00"]
            }
        }
    }
})

# Daily maintenance window
client.schedule.create({
    "name": "DailyMaintenance",
    "folder": "Texas",
    "schedule_type": {
        "recurring": {
            "daily": ["22:00-23:00"]
        }
    }
})
```

### Filtering Schedules by Type

Find schedules of a specific type.

```python
# Filter by recurring schedules
recurring = client.schedule.list(
    folder="Texas",
    schedule_type="recurring"
)

# Filter by weekly recurring
weekly = client.schedule.list(
    folder="Texas",
    recurring_type="weekly"
)

# Exact match with exclusions
filtered = client.schedule.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["Templates"]
)
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_schedule = client.schedule.create({
        "name": "test_schedule",
        "folder": "Texas",
        "schedule_type": {
            "recurring": {
                "weekly": {
                    "monday": ["09:00-17:00"],
                    "wednesday": ["09:00-17:00"],
                    "friday": ["09:00-17:00"]
                }
            }
        }
    })
except InvalidObjectError as e:
    print(f"Invalid schedule data: {e.message}")
except NameNotUniqueError as e:
    print(f"Schedule name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Schedule not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Schedule still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Schedule Models](../../models/objects/schedules_models.md#Overview)
