# Schedule Models

## Overview {#Overview}

The Schedule models provide a structured way to manage time-based schedules in Palo Alto Networks' Strata Cloud Manager. These models support defining recurring schedules (weekly or daily) and non-recurring schedules. Schedules are used to specify time periods when security policies should be active, and can be defined in folders, snippets, or devices. The models handle validation of inputs and outputs when interacting with the SCM API, including format validation for time ranges and date-time specifications.

### Models

The module provides the following Pydantic models:

- `ScheduleBaseModel`: Base model with fields common to all schedule operations
- `ScheduleCreateModel`: Model for creating new schedules
- `ScheduleUpdateModel`: Model for updating existing schedules
- `ScheduleResponseModel`: Response model for schedule operations
- `ScheduleTypeModel`: Container for recurring or non-recurring schedule types
- `RecurringScheduleModel`: Container for weekly or daily schedule configurations
- `WeeklyScheduleModel`: Weekly time ranges for each day of the week
- `NonRecurringScheduleModel`: One-time schedules with date-time ranges

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Hierarchy

The Schedule models use a hierarchical structure to represent different schedule types:

1. **Base Models**:
   - `ScheduleBaseModel`: Common fields for all schedule objects
   - `ScheduleCreateModel`: For creating new schedules
   - `ScheduleUpdateModel`: For updating existing schedules
   - `ScheduleResponseModel`: For API responses

2. **Schedule Type Models**:
   - `ScheduleTypeModel`: Container for either recurring or non-recurring schedules
   - `RecurringScheduleModel`: Container for either weekly or daily schedules
   - `WeeklyScheduleModel`: Weekly time ranges for each day of the week
   - `DailyScheduleModel`: Daily time ranges
   - `NonRecurringScheduleModel`: One-time schedules with date-time ranges

## Attributes

### Schedule Base Model Attributes

| Attribute       | Type                | Required | Default | Description                                                         |
|-----------------|---------------------|----------|---------|---------------------------------------------------------------------|
| name            | str                 | Yes      | None    | Name of the schedule. Max length: 31 chars. Pattern: `^[ a-zA-Z\d._-]+$` |
| schedule_type   | ScheduleTypeModel   | Yes      | None    | The type of schedule (recurring or non-recurring)                   |
| folder          | str                 | No*      | None    | Folder where schedule is defined. Max length: 64 chars              |
| snippet         | str                 | No*      | None    | Snippet where schedule is defined. Max length: 64 chars             |
| device          | str                 | No*      | None    | Device where schedule is defined. Max length: 64 chars              |
| id              | UUID                | Yes**    | None    | UUID of the schedule (required only for update and response models) |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for update and response models

### Schedule Type Model Attributes

| Model                     | Attributes                                                            | Format                                             |
|---------------------------|-----------------------------------------------------------------------|---------------------------------------------------|
| WeeklyScheduleModel       | sunday, monday, tuesday, wednesday, thursday, friday, saturday        | List of time ranges ("hh:mm-hh:mm")               |
| DailyScheduleModel        | daily                                                                 | List of time ranges ("hh:mm-hh:mm")               |
| NonRecurringScheduleModel | non_recurring                                                         | List of datetime ranges ("YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm") |

## Exceptions

The Schedule models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When multiple schedule types (recurring/non-recurring) are specified
    - When multiple recurring types (weekly/daily) are specified
    - When time range format validation fails
    - When datetime range format validation fails
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# Using dictionary
from scm.config.objects import Schedule

# Error: multiple containers specified
try:
    schedule_dict = {
        "name": "invalid-schedule",
        "folder": "Shared",
        "device": "fw01",  # Can't specify both folder and device
        "schedule_type": {
            "recurring": {
                "weekly": {
                    "monday": ["09:00-17:00"]
                }
            }
        }
    }
    schedule = Schedule(api_client)
    response = schedule.create(schedule_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
from scm.models.objects import ScheduleCreateModel

try:
    schedule = ScheduleCreateModel(
        name="invalid-schedule",
        folder="Shared",
        device="fw01",
        schedule_type={
            "recurring": {
                "weekly": {
                    "monday": ["09:00-17:00"]
                }
            }
        }
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Schedule Type Validation

Exactly one schedule type (recurring or non-recurring) must be specified:

```python
# Using dictionary
try:
    schedule_dict = {
        "name": "invalid-schedule",
        "folder": "Shared",
        "schedule_type": {
            "recurring": {
                "weekly": {
                    "monday": ["09:00-17:00"]
                }
            },
            "non_recurring": [
                "2025/01/01@09:00-2025/01/01@17:00"
            ]
        }
    }
    response = schedule.create(schedule_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'recurring' or 'non_recurring' must be provided."

# Using model directly
try:
    from scm.models.objects.schedules import ScheduleTypeModel

    schedule_type = ScheduleTypeModel(
        recurring={
            "weekly": {
                "monday": ["09:00-17:00"]
            }
        },
        non_recurring=["2025/01/01@09:00-2025/01/01@17:00"]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'recurring' or 'non_recurring' must be provided."
```

### Recurring Type Validation

For recurring schedules, exactly one recurring type (weekly or daily) must be specified:

```python
# Using dictionary
try:
    schedule_dict = {
        "name": "invalid-schedule",
        "folder": "Shared",
        "schedule_type": {
            "recurring": {
                "weekly": {
                    "monday": ["09:00-17:00"]
                },
                "daily": ["09:00-17:00"]
            }
        }
    }
    response = schedule.create(schedule_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'weekly' or 'daily' must be provided."

# Using model directly
try:
    from scm.models.objects.schedules import RecurringScheduleModel

    recurring_schedule = RecurringScheduleModel(
        weekly={
            "monday": ["09:00-17:00"]
        },
        daily=["09:00-17:00"]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'weekly' or 'daily' must be provided."
```

### Time Range Format Validation

Time ranges must follow the format "hh:mm-hh:mm":

```python
# Using dictionary
try:
    schedule_dict = {
        "name": "invalid-schedule",
        "folder": "Shared",
        "schedule_type": {
            "recurring": {
                "weekly": {
                    "monday": ["9:00-17:00"]  # Missing leading zero
                }
            }
        }
    }
    response = schedule.create(schedule_dict)
except ValueError as e:
    print(e)  # "Time range must be in format hh:mm-hh:mm and be exactly 11 characters"

# Using model directly
try:
    from scm.models.objects.schedules import WeeklyScheduleModel

    weekly_schedule = WeeklyScheduleModel(
        monday=["9:00-17:00"]  # Missing leading zero
    )
except ValueError as e:
    print(e)  # "Time range must be in format hh:mm-hh:mm and be exactly 11 characters"
```

### DateTime Range Format Validation

DateTime ranges for non-recurring schedules must follow the format "YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm":

```python
# Using dictionary
try:
    schedule_dict = {
        "name": "invalid-schedule",
        "folder": "Shared",
        "schedule_type": {
            "non_recurring": [
                "2025/1/1@09:00-2025/01/01@17:00"  # Missing leading zeros in month and day
            ]
        }
    }
    response = schedule.create(schedule_dict)
except ValueError as e:
    print(e)  # "Datetime range must be in format YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm and be exactly 33 characters"

# Using model directly
try:
    from scm.models.objects.schedules import NonRecurringScheduleModel

    non_recurring_schedule = NonRecurringScheduleModel(
        non_recurring=["2025/1/1@09:00-2025/01/01@17:00"]  # Missing leading zeros
    )
except ValueError as e:
    print(e)  # "Datetime range must be in format YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm and be exactly 33 characters"
```

## Usage Examples

### Creating a Weekly Schedule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
weekly_schedule_data = {
    "name": "BusinessHours",
    "folder": "Shared",
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
}

response = client.schedule.create(weekly_schedule_data)
print(f"Created schedule: {response.name} (ID: {response.id})")
```

### Creating a Daily Schedule

```python
# Using dictionary
daily_schedule_data = {
    "name": "DailyBackup",
    "folder": "Shared",
    "schedule_type": {
        "recurring": {
            "daily": ["01:00-03:00"]
        }
    }
}

response = client.schedule.create(daily_schedule_data)
print(f"Created daily schedule: {response.name}")
```

### Creating a Non-Recurring Schedule

```python
# Using dictionary
non_recurring_data = {
    "name": "MaintenanceWindow",
    "folder": "Shared",
    "schedule_type": {
        "non_recurring": [
            "2025/06/15@01:00-2025/06/15@05:00"
        ]
    }
}

response = client.schedule.create(non_recurring_data)
print(f"Created non-recurring schedule: {response.name}")
```

### Updating a Schedule

```python
# Fetch existing schedule
existing = client.schedule.fetch(name="BusinessHours", folder="Shared")

# Modify attributes using dot notation
existing.name = "BusinessHours-Extended"

# Update weekly schedule to include Saturday
if existing.schedule_type.recurring and existing.schedule_type.recurring.weekly:
    existing.schedule_type.recurring.weekly.saturday = ["10:00-14:00"]
    # Extend weekday hours
    existing.schedule_type.recurring.weekly.monday = ["08:00-18:00"]
    existing.schedule_type.recurring.weekly.tuesday = ["08:00-18:00"]
    existing.schedule_type.recurring.weekly.wednesday = ["08:00-18:00"]
    existing.schedule_type.recurring.weekly.thursday = ["08:00-18:00"]
    existing.schedule_type.recurring.weekly.friday = ["08:00-18:00"]

# Pass modified object to update()
updated = client.schedule.update(existing)
print(f"Updated schedule: {updated.name}")
```

## Best Practices

1. **Time Formatting**
   - Always use the correct format for time ranges ("hh:mm-hh:mm")
   - Always use the correct format for datetime ranges ("YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm")
   - Include leading zeros for hours, minutes, months, and days
   - Validate time ranges before submission

2. **Schedule Types**
   - Use weekly schedules for time patterns that vary by day of the week
   - Use daily schedules for consistent daily time patterns
   - Use non-recurring schedules for one-time events

3. **Naming Conventions**
   - Use descriptive names that indicate the schedule's purpose
   - Consider including time or frequency information in the name
   - Use consistent naming patterns
   - Avoid special characters
   - Document naming standards

4. **Multiple Time Ranges**
   - For complex time patterns (like split shifts), use multiple time ranges within a day
   - Order time ranges chronologically
   - Avoid overlapping time ranges
   - Consider using separate schedules for very different patterns
