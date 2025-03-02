# scm/models/objects/schedules.py

# Standard library imports
from typing import Dict, List, Optional, Union, Literal
from uuid import UUID

# External libraries
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
    constr,
)


class WeeklyScheduleModel(BaseModel):
    """
    Model representing weekly schedule time ranges.

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
            # Time range should match pattern hh:mm-hh:mm
            if not time_range or len(time_range) != 11:
                raise ValueError("Time range must be in format hh:mm-hh:mm and be exactly 11 characters")
            
            # Split into start and end times
            start_time, end_time = time_range.split("-")
            start_h, start_m = start_time.split(":")
            end_h, end_m = end_time.split(":")
            
            # Validate hours (00-23)
            if not (0 <= int(start_h) <= 23 and 0 <= int(end_h) <= 23):
                raise ValueError("Hours must be between 00 and 23")
            
            # Validate minutes (00-59)
            if not (0 <= int(start_m) <= 59 and 0 <= int(end_m) <= 59):
                raise ValueError("Minutes must be between 00 and 59")
            
        return v

    @model_validator(mode="after")
    def validate_at_least_one_day(cls, values):
        """Validate that at least one day has time ranges defined."""
        days = [
            values.sunday, values.monday, values.tuesday, 
            values.wednesday, values.thursday, values.friday, values.saturday
        ]
        
        # Check if at least one day has time ranges
        if not any(day is not None and len(day) > 0 for day in days):
            raise ValueError("Weekly schedule must define time ranges for at least one day")
        
        return values


class DailyScheduleModel(BaseModel):
    """
    Model representing daily schedule time ranges.

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
            # Time range should match pattern hh:mm-hh:mm
            if not time_range or len(time_range) != 11:
                raise ValueError("Time range must be in format hh:mm-hh:mm and be exactly 11 characters")
            
            # Split into start and end times
            start_time, end_time = time_range.split("-")
            start_h, start_m = start_time.split(":")
            end_h, end_m = end_time.split(":")
            
            # Validate hours (00-23)
            if not (0 <= int(start_h) <= 23 and 0 <= int(end_h) <= 23):
                raise ValueError("Hours must be between 00 and 23")
            
            # Validate minutes (00-59)
            if not (0 <= int(start_m) <= 59 and 0 <= int(end_m) <= 59):
                raise ValueError("Minutes must be between 00 and 59")
            
        return v


class RecurringScheduleModel(BaseModel):
    """
    Model representing recurring schedules, which can be either weekly or daily.

    Attributes:
        weekly (Optional[WeeklyScheduleModel]): Weekly schedule configuration.
        daily (Optional[DailyScheduleModel]): Daily schedule configuration.
    """

    weekly: Optional[WeeklyScheduleModel] = None
    daily: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_exactly_one_type(cls, values):
        """Validate that exactly one of weekly or daily is provided."""
        if values.weekly is not None and values.daily is not None:
            raise ValueError("Exactly one of 'weekly' or 'daily' must be provided")
        if values.weekly is None and values.daily is None:
            raise ValueError("Either 'weekly' or 'daily' must be provided")
            
        return values


class NonRecurringScheduleModel(BaseModel):
    """
    Model representing non-recurring (one-time) schedules.

    Attributes:
        non_recurring (List[str]): List of date/time ranges in format YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm.
    """

    non_recurring: List[str]

    @field_validator("non_recurring")
    def validate_datetime_ranges(cls, v):
        """Validate that datetime ranges follow the correct format."""
        if not v:
            raise ValueError("Non-recurring schedule must contain at least one datetime range")
        
        for dt_range in v:
            # Datetime range should be exactly 33 characters: YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm
            if not dt_range or len(dt_range) != 33:
                raise ValueError(
                    "Datetime range must be in format YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm and be exactly 33 characters"
                )
            
            # Split into start and end datetimes
            start_dt, end_dt = dt_range.split("-")
            
            # Validate start datetime
            start_date, start_time = start_dt.split("@")
            start_year, start_month, start_day = start_date.split("/")
            start_hour, start_minute = start_time.split(":")
            
            # Validate end datetime
            end_date, end_time = end_dt.split("@")
            end_year, end_month, end_day = end_date.split("/")
            end_hour, end_minute = end_time.split(":")
            
            # Validate years
            if not start_year.isdigit() or not end_year.isdigit():
                raise ValueError("Year must be numeric")
            
            # Validate months (01-12)
            if not (1 <= int(start_month) <= 12 and 1 <= int(end_month) <= 12):
                raise ValueError("Month must be between 01 and 12")
            
            # Validate days (01-31)
            if not (1 <= int(start_day) <= 31 and 1 <= int(end_day) <= 31):
                raise ValueError("Day must be between 01 and 31")
            
            # Validate hours (00-23)
            if not (0 <= int(start_hour) <= 23 and 0 <= int(end_hour) <= 23):
                raise ValueError("Hours must be between 00 and 23")
            
            # Validate minutes (00-59)
            if not (0 <= int(start_minute) <= 59 and 0 <= int(end_minute) <= 59):
                raise ValueError("Minutes must be between 00 and 59")
            
        return v


class ScheduleTypeModel(BaseModel):
    """
    Model representing schedule type, which can be either recurring or non-recurring.

    Attributes:
        recurring (Optional[RecurringScheduleModel]): Recurring schedule configuration.
        non_recurring (Optional[NonRecurringScheduleModel]): Non-recurring schedule configuration.
    """

    recurring: Optional[RecurringScheduleModel] = None
    non_recurring: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_exactly_one_type(cls, values):
        """Validate that exactly one of recurring or non_recurring is provided."""
        if values.recurring is not None and values.non_recurring is not None:
            raise ValueError("Exactly one of 'recurring' or 'non_recurring' must be provided")
        if values.recurring is None and values.non_recurring is None:
            raise ValueError("Either 'recurring' or 'non_recurring' must be provided")
            
        return values


class ScheduleBaseModel(BaseModel):
    """
    Base model for Schedule objects containing fields common to all CRUD operations.

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
    """
    Represents a request to create a new Schedule object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for a Schedule creation request.
    It inherits all fields from the ScheduleBaseModel class and provides additional validation
    to ensure that the creation request contains exactly one of the container types
    (folder, snippet, or device).

    Error:
        ValueError: Raised when container type validation fails.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "ScheduleCreateModel":
        """Validates that exactly one container type is provided."""
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class ScheduleUpdateModel(ScheduleBaseModel):
    """
    Represents an update to an existing Schedule object for Palo Alto Networks' Strata Cloud Manager.

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
    """
    Represents a response containing a Schedule object from Palo Alto Networks' Strata Cloud Manager.

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