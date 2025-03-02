# Schedule Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Schedule Model Attributes](#schedule-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
   - [Creating Schedules](#creating-schedules)
   - [Retrieving Schedules](#retrieving-schedules)
   - [Updating Schedules](#updating-schedules)
   - [Listing Schedules](#listing-schedules)
   - [Filtering Responses](#filtering-responses)
   - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
   - [Deleting Schedules](#deleting-schedules)
7. [Managing Configuration Changes](#managing-configuration-changes)
   - [Performing Commits](#performing-commits)
   - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Schedule` class provides functionality to manage schedule objects in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting schedules with specific time configurations. Schedules can be configured as recurring (weekly or daily) or non-recurring, and are used to specify when security policies should be active. The class offers flexible filtering capabilities when listing schedules, enabling you to filter by schedule type, limit results to exact matches of a configuration container, and exclude certain folders, snippets, or devices as needed.

## Core Methods

| Method     | Description                                          | Parameters                                                                                                              | Return Type                   |
|------------|------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| `create()` | Creates a new schedule                               | `data: Dict[str, Any]`                                                                                                  | `ScheduleResponseModel`       |
| `get()`    | Retrieves a schedule by ID                           | `object_id: str`                                                                                                        | `ScheduleResponseModel`       |
| `update()` | Updates an existing schedule                         | `schedule: ScheduleUpdateModel`                                                                                         | `ScheduleResponseModel`       |
| `delete()` | Deletes a schedule                                   | `object_id: str`                                                                                                        | `None`                        |
| `list()`   | Lists schedules with comprehensive filtering options | `folder` or `snippet` or `device`, `exact_match`, `exclude_folders`, `exclude_snippets`, `exclude_devices`, `**filters` | `List[ScheduleResponseModel]` |
| `fetch()`  | Gets schedule by name and container                  | `name: str` and one container (`folder`, `snippet`, or `device`)                                                        | `ScheduleResponseModel`       |

## Schedule Model Attributes

| Attribute       | Type            | Required | Description                                               |
|-----------------|-----------------|----------|-----------------------------------------------------------|
| `name`          | str             | Yes      | Name of the schedule object (max 31 chars)                |
| `id`            | UUID            | Yes*     | Unique identifier (*response only)                        |
| `schedule_type` | ScheduleTypeModel | Yes      | The type of schedule (recurring or non-recurring)         |
| `folder`        | str             | Yes**    | Folder location (**one container required**)              |
| `snippet`       | str             | Yes**    | Snippet location (**one container required**)             |
| `device`        | str             | Yes**    | Device location (**one container required**)              |

## Exceptions

| Exception                    | HTTP Code | Description                      |
|------------------------------|-----------|----------------------------------|
| `InvalidObjectError`         | 400       | Invalid schedule data or format  |
| `MissingQueryParameterError` | 400       | Missing required parameters      |
| `NameNotUniqueError`         | 409       | Schedule name already exists     |
| `ObjectNotPresentError`      | 404       | Schedule not found               |
| `ReferenceNotZeroError`      | 409       | Schedule still referenced        |
| `AuthenticationError`        | 401       | Authentication failed            |
| `ServerError`                | 500       | Internal server error            |

## Basic Configuration

The Schedule service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Schedule service directly through the client
# No need to create a separate Schedule instance
schedules = client.schedule
```

</div>

### Traditional Service Instantiation (Legacy)

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Schedule

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Schedule object explicitly
schedules = Schedule(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Schedules

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Weekly schedule configuration
weekly_schedule = {
    "name": "WeekdayBusiness",
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

# Create weekly schedule
weekly_schedule_obj = client.schedule.create(weekly_schedule)

# Daily schedule configuration
daily_schedule = {
    "name": "DailyMaintenance",
    "folder": "Shared",
    "schedule_type": {
        "recurring": {
            "daily": ["22:00-23:00"]
        }
    }
}

# Create daily schedule
daily_schedule_obj = client.schedule.create(daily_schedule)

# Non-recurring schedule for a special event
special_event = {
    "name": "HolidayEvent",
    "folder": "Shared",
    "schedule_type": {
        "non_recurring": [
            "2025/12/25@00:00-2025/12/26@00:00"
        ]
    }
}

# Create non-recurring schedule
special_event_obj = client.schedule.create(special_event)
```

</div>

### Retrieving Schedules

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
schedule = client.schedule.fetch(name="WeekdayBusiness", folder="Shared")
print(f"Found schedule: {schedule.name}")

# Get the schedule_type details
if schedule.schedule_type.recurring:
    if schedule.schedule_type.recurring.weekly:
        for day, times in schedule.schedule_type.recurring.weekly.__dict__.items():
            if times:  # Only show days that have time ranges
                print(f"{day.capitalize()}: {', '.join(times)}")
    elif schedule.schedule_type.recurring.daily:
        print(f"Daily: {', '.join(schedule.schedule_type.recurring.daily)}")
elif schedule.schedule_type.non_recurring:
    print(f"Non-recurring: {', '.join(schedule.schedule_type.non_recurring)}")

# Get by ID
schedule_by_id = client.schedule.get(schedule.id)
print(f"Retrieved schedule: {schedule_by_id.name}")
```

</div>

### Updating Schedules

<div class="termy">

<!-- termynal -->

```python
# Fetch existing schedule
existing_schedule = client.schedule.fetch(name="WeekdayBusiness", folder="Shared")

# Update time ranges - add early morning hours
if existing_schedule.schedule_type.recurring and existing_schedule.schedule_type.recurring.weekly:
    weekly = existing_schedule.schedule_type.recurring.weekly
    
    # Add early morning hours to Monday through Friday
    if weekly.monday:
        weekly.monday.append("07:00-09:00")
    if weekly.tuesday:
        weekly.tuesday.append("07:00-09:00")
    if weekly.wednesday:
        weekly.wednesday.append("07:00-09:00")
    if weekly.thursday:
        weekly.thursday.append("07:00-09:00")
    if weekly.friday:
        weekly.friday.append("07:00-09:00")
    
    # Add Saturday (half day)
    weekly.saturday = ["09:00-13:00"]

# Perform update
updated_schedule = client.schedule.update(existing_schedule)

# Verify the update
for day, times in updated_schedule.schedule_type.recurring.weekly.__dict__.items():
    if times:  # Only show days that have time ranges
        print(f"{day.capitalize()}: {', '.join(times)}")
```

</div>

### Listing Schedules

<div class="termy">

<!-- termynal -->

```python
# List all schedules from a specific folder
schedules = client.schedule.list(
    folder='Shared'
)

for schedule in schedules:
    print(f"Name: {schedule.name}, ID: {schedule.id}")
    
    # Display schedule details based on type
    if schedule.schedule_type.recurring:
        if schedule.schedule_type.recurring.weekly:
            print("  Type: Weekly recurring")
            for day, times in schedule.schedule_type.recurring.weekly.__dict__.items():
                if times:  # Only show days that have time ranges
                    print(f"    {day.capitalize()}: {', '.join(times)}")
        elif schedule.schedule_type.recurring.daily:
            print("  Type: Daily recurring")
            print(f"    Times: {', '.join(schedule.schedule_type.recurring.daily)}")
    elif schedule.schedule_type.non_recurring:
        print("  Type: Non-recurring")
        print(f"    Time ranges: {', '.join(schedule.schedule_type.non_recurring)}")
    print("---")
```

</div>

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. You can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Additional Filter Parameters:**

- `schedule_type (str)`: Filter by schedule type ('recurring' or 'non_recurring').
- `recurring_type (str)`: Filter by recurring type ('weekly' or 'daily').

**Examples:**

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Only return schedules defined exactly in 'Shared'
exact_schedules = client.schedule.list(
    folder='Shared',
    exact_match=True
)

for schedule in exact_schedules:
    print(f"Exact match: {schedule.name} in {schedule.folder}")

# Filter by recurring schedules only
recurring_schedules = client.schedule.list(
    folder='Shared',
    schedule_type='recurring'
)

print(f"Found {len(recurring_schedules)} recurring schedules")

# Filter by non-recurring schedules only
non_recurring_schedules = client.schedule.list(
    folder='Shared',
    schedule_type='non_recurring'
)

print(f"Found {len(non_recurring_schedules)} non-recurring schedules")

# Filter by weekly recurring schedules
weekly_schedules = client.schedule.list(
    folder='Shared',
    recurring_type='weekly'
)

print(f"Found {len(weekly_schedules)} weekly schedules")

# Filter by daily recurring schedules
daily_schedules = client.schedule.list(
    folder='Shared',
    recurring_type='daily'
)

print(f"Found {len(daily_schedules)} daily schedules")

# Exclude schedules from specific folders
filtered_schedules = client.schedule.list(
    folder='Shared',
    exclude_folders=['Templates']
)

for schedule in filtered_schedules:
    assert schedule.folder != 'Templates'
    print(f"Schedule: {schedule.name}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 200. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved.

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.config.objects import Schedule

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom Schedule instance with max_limit
schedule_service = Schedule(client, max_limit=1000)
all_schedules1 = schedule_service.list(folder='Shared')

# Option 2: Use the unified client interface directly
# This will use the default max_limit (200)
all_schedules2 = client.schedule.list(folder='Shared')

# Both options will auto-paginate through all available objects.
# The schedules are fetched in chunks according to the max_limit.
```

</div>

### Deleting Schedules

<div class="termy">

<!-- termynal -->

```python
# Get schedule to delete
schedule_to_delete = client.schedule.fetch(name="HolidayEvent", folder="Shared")

# Delete by ID
client.schedule.delete(schedule_to_delete.id)
print(f"Deleted schedule: {schedule_to_delete.name}")
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Shared"],
    "description": "Updated schedule definitions",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly using the client
# Note: Commits should always be performed on the client object directly, not on service objects
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Create schedule configuration
    schedule_config = {
        "name": "test_schedule",
        "folder": "Shared",
        "schedule_type": {
            "recurring": {
                "weekly": {
                    "monday": ["09:00-17:00"],
                    "wednesday": ["09:00-17:00"],
                    "friday": ["09:00-17:00"]
                }
            }
        }
    }

    # Create the schedule
    new_schedule = client.schedule.create(schedule_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Shared"],
        description="Added test schedule",
        sync=True
    )

    # Check job status directly from the client
    status = client.get_job_status(result.job_id)

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

</div>

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.schedule`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Schedule Type Configuration**
   - Use appropriate schedule type (recurring vs. non-recurring) based on your needs
   - For recurring schedules, choose weekly or daily patterns as appropriate
   - Ensure time ranges follow the correct format (e.g., "09:00-17:00")
   - For non-recurring schedules, use the correct date-time format (e.g., "2025/01/01@09:00-2025/01/01@17:00")
   - Define time ranges in chronological order

3. **Container Management**
   - Always specify exactly one container (folder, snippet, or device)
   - Use consistent container names
   - Validate container existence
   - Group related schedules

4. **Naming Conventions**
   - Use descriptive names that indicate the schedule's purpose
   - Follow consistent patterns
   - Avoid special characters
   - Document naming standards
   - Consider hierarchical naming (e.g., "BusinessHours_Standard", "BusinessHours_Extended")

5. **Performance**
   - Create a single client instance and reuse it
   - Use appropriate pagination
   - Implement proper retry logic
   - Monitor API limits
   - Batch operations when possible

6. **Error Handling**
   - Validate input data
   - Handle specific exceptions
   - Log error details
   - Monitor commit status
   - Track job completion

## Full Script Examples

A complete example including various schedule types and management operations will be available in the examples directory.

## Related Models

- [ScheduleCreateModel](../../models/objects/schedules_models.md#Overview)
- [ScheduleUpdateModel](../../models/objects/schedules_models.md#Overview)
- [ScheduleResponseModel](../../models/objects/schedules_models.md#Overview)