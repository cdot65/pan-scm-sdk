# Schedule Models

## Overview {#Overview}

The Schedule models provide a structured way to manage time-based schedules in Palo Alto Networks' Strata Cloud Manager. These models support defining recurring schedules (weekly or daily) and non-recurring schedules. Schedules are used to specify time periods when security policies should be active, and can be defined in folders, snippets, or devices. The models handle validation of inputs and outputs when interacting with the SCM API, including format validation for time ranges and date-time specifications.

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

<div class="termy">

<!-- termynal -->

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

</div>

### Schedule Type Validation

Exactly one schedule type (recurring or non-recurring) must be specified:

<div class="termy">

<!-- termynal -->

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

</div>

### Recurring Type Validation

For recurring schedules, exactly one recurring type (weekly or daily) must be specified:

<div class="termy">

<!-- termynal -->

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

</div>

### Time Range Format Validation

Time ranges must follow the format "hh:mm-hh:mm":

<div class="termy">

<!-- termynal -->

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

</div>

### DateTime Range Format Validation

DateTime ranges for non-recurring schedules must follow the format "YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm":

<div class="termy">

<!-- termynal -->

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

</div>

## Usage Examples

### Creating a Weekly Schedule

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
weekly_schedule_dict = {
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

schedule = Schedule(api_client)
response = schedule.create(weekly_schedule_dict)

# Using model directly
from scm.models.objects import ScheduleCreateModel
from scm.models.objects.schedules import WeeklyScheduleModel

weekly_schedule = ScheduleCreateModel(
    name="BusinessHours",
    folder="Shared",
    schedule_type={
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
)

payload = weekly_schedule.model_dump(exclude_unset=True)
response = schedule.create(payload)
```

</div>

### Creating a Daily Schedule

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
daily_schedule_dict = {
    "name": "DailyBackup",
    "folder": "Shared",
    "schedule_type": {
        "recurring": {
            "daily": ["01:00-03:00"]
        }
    }
}

schedule = Schedule(api_client)
response = schedule.create(daily_schedule_dict)

# Using model directly
from scm.models.objects import ScheduleCreateModel

daily_schedule = ScheduleCreateModel(
    name="DailyBackup",
    folder="Shared",
    schedule_type={
        "recurring": {
            "daily": ["01:00-03:00"]
        }
    }
)

payload = daily_schedule.model_dump(exclude_unset=True)
response = schedule.create(payload)
```

</div>

### Creating a Non-Recurring Schedule

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
non_recurring_schedule_dict = {
    "name": "MaintenanceWindow",
    "folder": "Shared",
    "schedule_type": {
        "non_recurring": [
            "2025/06/15@01:00-2025/06/15@05:00"
        ]
    }
}

schedule = Schedule(api_client)
response = schedule.create(non_recurring_schedule_dict)

# Using model directly
from scm.models.objects import ScheduleCreateModel

non_recurring_schedule = ScheduleCreateModel(
    name="MaintenanceWindow",
    folder="Shared",
    schedule_type={
        "non_recurring": [
            "2025/06/15@01:00-2025/06/15@05:00"
        ]
    }
)

payload = non_recurring_schedule.model_dump(exclude_unset=True)
response = schedule.create(payload)
```

</div>

### Updating a Schedule

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "BusinessHours-Extended",
    "folder": "Shared",
    "schedule_type": {
        "recurring": {
            "weekly": {
                "monday": ["08:00-18:00"],
                "tuesday": ["08:00-18:00"],
                "wednesday": ["08:00-18:00"],
                "thursday": ["08:00-18:00"],
                "friday": ["08:00-18:00"],
                "saturday": ["10:00-14:00"]
            }
        }
    }
}

response = schedule.update(update_dict)

# Using model directly
from scm.models.objects import ScheduleUpdateModel

update_schedule = ScheduleUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="BusinessHours-Extended",
    folder="Shared",
    schedule_type={
        "recurring": {
            "weekly": {
                "monday": ["08:00-18:00"],
                "tuesday": ["08:00-18:00"],
                "wednesday": ["08:00-18:00"],
                "thursday": ["08:00-18:00"],
                "friday": ["08:00-18:00"],
                "saturday": ["10:00-14:00"]
            }
        }
    }
)

response = schedule.update(update_schedule)
```

</div>

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
