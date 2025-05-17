"""Schedules models for Strata Cloud Manager SDK.

Contains Pydantic models for representing schedule objects and related data.
"""

# scm/models/objects/schedules.py

# Standard library imports
import re
from typing import List, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Regular expression to validate time range in format hh:mm-hh:mm
# This pattern ensures:
# - Hours from 00-23 (first digit can only be 0, 1, or 2)
# - Minutes from 00-59
# - Proper format with a hyphen between times
TIME_RANGE_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$")


class WeeklyScheduleModel(BaseModel):
    """Model representing weekly schedule time ranges.

    Attributes:
        sunday (Optional[List[str]]): List of time ranges for Sunday.
        monday (Optional[List[str]]): List of time ranges for Monday.
        tuesday (Optional[List[str]]): List of time ranges for Tuesday.
        wednesday (Optional[List[str]]): List of time ranges for Wednesday.
        thursday (Optional[List[str]]): List of time ranges for Thursday.
        friday (Optional[List[str]]): List of time ranges for Friday.
        saturday (Optional[List[str]]): List of time ranges for Saturday.

    """

    sunday: Optional[List[str]] = None
    monday: Optional[List[str]] = None
    tuesday: Optional[List[str]] = None
    wednesday: Optional[List[str]] = None
    thursday: Optional[List[str]] = None
    friday: Optional[List[str]] = None
    saturday: Optional[List[str]] = None

    @field_validator("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
    def validate_time_ranges(cls, v):
        """Validate that time ranges follow the correct format."""
        if v is None:
            return v

        for time_range in v:
            if not TIME_RANGE_PATTERN.match(time_range):
                raise ValueError("Time range must be in format hh:mm-hh:mm (00:00-23:59)")

        return v

    @model_validator(mode="after")
    def ensure_at_least_one_day(cls, values):
        """Validate that at least one day has time ranges defined."""
        days = [
            values.sunday,
            values.monday,
            values.tuesday,
            values.wednesday,
            values.thursday,
            values.friday,
            values.saturday,
        ]

        # Check if at least one day has time ranges
        if not any(day is not None and len(day) > 0 for day in days):
            raise ValueError("Weekly schedule must define time ranges for at least one day")

        return values


class DailyScheduleModel(BaseModel):
    """Model representing daily schedule time ranges.

    Attributes:
        daily (List[str]): List of time ranges for every day.

    """

    daily: List[str]

    @field_validator("daily")
    def validate_time_ranges(cls, v):
        """Validate that time ranges follow the correct format."""
        if not v:
            raise ValueError("Daily schedule must contain at least one time range")

        for time_range in v:
            if not TIME_RANGE_PATTERN.match(time_range):
                raise ValueError("Time range must be in format hh:mm-hh:mm (00:00-23:59)")

        return v


class RecurringScheduleModel(BaseModel):
    """Model representing recurring schedules, which can be either weekly or daily.

    Attributes:
        weekly (Optional[WeeklyScheduleModel]): Weekly schedule configuration.
        daily (Optional[DailyScheduleModel]): Daily schedule configuration.

    """

    weekly: Optional[WeeklyScheduleModel] = None
    daily: Optional[List[str]] = None

    @model_validator(mode="after")
    def ensure_exactly_one_type(cls, values):
        """Validate that exactly one of weekly or daily is provided."""
        if values.weekly is not None and values.daily is not None:
            raise ValueError("Exactly one of 'weekly' or 'daily' must be provided")
        if values.weekly is None and values.daily is None:
            raise ValueError("Either 'weekly' or 'daily' must be provided")

        return values


class NonRecurringScheduleModel(BaseModel):
    """Model representing non-recurring (one-time) schedules.

    Attributes:
        non_recurring (List[str]): List of date/time ranges in format YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm.

    """

    non_recurring: List[str]

    @field_validator("non_recurring")
    def validate_time_ranges(cls, v):
        """Validate that datetime ranges follow the correct format."""
        if not v:
            raise ValueError("Non-recurring schedule must contain at least one datetime range")

        for dt_range in v:
            # Check for the format YYYY/M/D@HH:MM - detecting missing leading zeros
            dt_parts = dt_range.split("-")
            if len(dt_parts) != 2:
                raise ValueError("Invalid datetime range format - must contain a single hyphen")

            # Process start date/time
            start_dt = dt_parts[0]
            if "@" not in start_dt:
                raise ValueError("Start datetime must contain @ to separate date and time")

            start_date, start_time = start_dt.split("@")
            start_parts = start_date.split("/")
            if len(start_parts) != 3:
                raise ValueError("Start date must be in format YYYY/MM/DD")

            start_year, start_month, start_day = start_parts

            # Validate that year is numeric
            if not start_year.isdigit():
                raise ValueError("Year must be numeric")

            start_time_parts = start_time.split(":")
            if len(start_time_parts) != 2:
                raise ValueError("Start time must be in format HH:MM")

            start_hour, start_minute = start_time_parts

            # Process end date/time
            end_dt = dt_parts[1]
            if "@" not in end_dt:
                raise ValueError("End datetime must contain @ to separate date and time")

            end_date, end_time = end_dt.split("@")
            end_parts = end_date.split("/")
            if len(end_parts) != 3:
                raise ValueError("End date must be in format YYYY/MM/DD")

            end_year, end_month, end_day = end_parts

            # Validate that year is numeric
            if not end_year.isdigit():
                raise ValueError("Year must be numeric")

            end_time_parts = end_time.split(":")
            if len(end_time_parts) != 2:
                raise ValueError("End time must be in format HH:MM")

            end_hour, end_minute = end_time_parts

            # Validate leading zeros for months
            if len(start_month) != 2 or not start_month.startswith("0") and int(start_month) < 10:
                raise ValueError("Month must use leading zeros (01-12)")

            if len(end_month) != 2 or not end_month.startswith("0") and int(end_month) < 10:
                raise ValueError("Month must use leading zeros (01-12)")

            # Validate leading zeros for days
            if len(start_day) != 2 or not start_day.startswith("0") and int(start_day) < 10:
                raise ValueError("Day must use leading zeros (01-31)")

            if len(end_day) != 2 or not end_day.startswith("0") and int(end_day) < 10:
                raise ValueError("Day must use leading zeros (01-31)")

            # Validate leading zeros for hours
            if len(start_hour) != 2 or not start_hour.startswith("0") and int(start_hour) < 10:
                raise ValueError("Hours must use leading zeros (00-23)")

            if len(end_hour) != 2 or not end_hour.startswith("0") and int(end_hour) < 10:
                raise ValueError("Hours must use leading zeros (00-23)")

            # Validate leading zeros for minutes
            if (
                len(start_minute) != 2
                or not start_minute.startswith("0")
                and int(start_minute) < 10
            ):
                raise ValueError("Minutes must use leading zeros (00-59)")

            if len(end_minute) != 2 or not end_minute.startswith("0") and int(end_minute) < 10:
                raise ValueError("Minutes must use leading zeros (00-59)")

            # Validate numeric ranges
            if not (0 <= int(start_hour) <= 23 and 0 <= int(end_hour) <= 23):
                raise ValueError("Hours must be between 00 and 23")

            if not (0 <= int(start_minute) <= 59 and 0 <= int(end_minute) <= 59):
                raise ValueError("Minutes must be between 00 and 59")

            if not (1 <= int(start_month) <= 12 and 1 <= int(end_month) <= 12):
                raise ValueError("Month must be between 01 and 12")

            if not (1 <= int(start_day) <= 31 and 1 <= int(end_day) <= 31):
                raise ValueError("Day must be between 01 and 31")

        return v


class ScheduleTypeModel(BaseModel):
    """Model representing schedule type, which can be either recurring or non-recurring.

    Attributes:
        recurring (Optional[RecurringScheduleModel]): Recurring schedule configuration.
        non_recurring (Optional[NonRecurringScheduleModel]): Non-recurring schedule configuration.

    """

    recurring: Optional[RecurringScheduleModel] = None
    non_recurring: Optional[List[str]] = None

    @model_validator(mode="after")
    def ensure_exactly_one_type(cls, values):
        """Validate that exactly one of recurring or non_recurring is provided."""
        if values.recurring is not None and values.non_recurring is not None:
            raise ValueError("Exactly one of 'recurring' or 'non_recurring' must be provided")
        if values.recurring is None and values.non_recurring is None:
            raise ValueError("Either 'recurring' or 'non_recurring' must be provided")

        return values


class ScheduleBaseModel(BaseModel):
    """Base model for Schedule objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the schedule.
        schedule_type (Dict): The type of schedule (recurring or non-recurring).
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    """

    # Required fields
    name: str = Field(
        ...,
        max_length=31,
        pattern=r"^[ a-zA-Z\d._-]+$",
        description="The name of the schedule",
    )
    schedule_type: ScheduleTypeModel = Field(
        ...,
        description="The type of schedule (recurring or non-recurring)",
    )

    # Container Types - Exactly one must be provided
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_\. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["Shared"],
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_\. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
        examples=["My Snippet"],
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9\-_\. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
        examples=["My Device"],
    )

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class ScheduleCreateModel(ScheduleBaseModel):
    """Represents a request to create a new Schedule object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a Schedule creation request.
    It inherits all fields from the ScheduleBaseModel class and provides additional validation
    to ensure that the creation request contains exactly one of the container types
    (folder, snippet, or device).

    Error:
        ValueError: Raised when container type validation fails.

    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "ScheduleCreateModel":
        """Validate that exactly one container type is provided."""
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class ScheduleUpdateModel(ScheduleBaseModel):
    """Represents an update to an existing Schedule object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a Schedule update request.
    It inherits all fields from the ScheduleBaseModel class and adds the id field which is required
    for updates.

    Attributes:
        id (UUID): The UUID of the schedule object.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the schedule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ScheduleResponseModel(ScheduleBaseModel):
    """Represents a response containing a Schedule object from Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a Schedule response model.
    It inherits all fields from the ScheduleBaseModel class and adds the required id field.

    Attributes:
        id (UUID): The UUID of the schedule object.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the schedule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
