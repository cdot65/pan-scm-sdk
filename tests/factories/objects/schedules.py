# tests/factories/objects/schedules.py

"""Factory definitions for schedule objects."""

from typing import Dict, List, Optional
from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.schedules import (
    ScheduleBaseModel,
    ScheduleCreateModel,
    ScheduleResponseModel,
    ScheduleUpdateModel,
)

fake = Faker()


# Base factory for all schedule models
class ScheduleBaseFactory(factory.Factory):
    """Base factory for Schedule with common fields."""

    class Meta:
        model = ScheduleBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"schedule_{n}")
    description = fake.sentence()
    schedule_type: Dict = {
        "recurring": {
            "weekly": {
                "monday": ["09:00-17:00"],
                "wednesday": ["09:00-17:00"],
                "friday": ["09:00-17:00"],
            }
        }
    }

    # Container fields default to None
    folder: Optional[str] = None
    snippet: Optional[str] = None
    device: Optional[str] = None


# ----------------------------------------------------------------------------
# SDK tests against SCM API
# ----------------------------------------------------------------------------


class ScheduleCreateApiFactory(ScheduleBaseFactory):
    """Factory for creating ScheduleCreateModel instances with different schedule types."""

    class Meta:
        model = ScheduleCreateModel

    # Default to folder container
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container.

        Args:
            snippet: The snippet name to use
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleCreateModel with the snippet container

        """
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container.

        Args:
            device: The device name to use
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleCreateModel with the device container

        """
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_daily_schedule(cls, **kwargs):
        """Create an instance with daily schedule.

        Uses recurring schedule with daily time ranges.

        Args:
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleCreateModel with a daily schedule

        """
        schedule_type = {"recurring": {"daily": ["09:00-17:00", "18:00-20:00"]}}
        return cls(schedule_type=schedule_type, **kwargs)

    @classmethod
    def with_non_recurring_schedule(cls, **kwargs):
        """Create an instance with non-recurring schedule.

        Uses non-recurring schedule with specific date and time ranges.

        Args:
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleCreateModel with a non-recurring schedule

        """
        schedule_type = {
            "non_recurring": [
                "2025/01/01@09:00-2025/01/01@17:00",
                "2025/02/01@09:00-2025/02/01@17:00",
            ]
        }
        return cls(schedule_type=schedule_type, **kwargs)

    @classmethod
    def with_weekly_specific_days(cls, days: List[str], **kwargs):
        """Create an instance with weekly schedule for specific days.

        Args:
            days: List of days to include in weekly schedule (e.g., ["monday", "friday"])
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleCreateModel with a weekly schedule for specific days

        """
        weekly_schedule = {day: ["09:00-17:00"] for day in days}
        schedule_type = {"recurring": {"weekly": weekly_schedule}}
        return cls(schedule_type=schedule_type, **kwargs)

    @classmethod
    def build_invalid_time_format(cls, **kwargs):
        """Create an instance with invalid time format for testing validation errors.

        Args:
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleCreateModel with invalid time format

        """
        schedule_type = {"recurring": {"weekly": {"monday": ["0900-1700"]}}}  # Missing colons
        return cls(schedule_type=schedule_type, **kwargs)


class ScheduleUpdateApiFactory(ScheduleBaseFactory):
    """Factory for creating ScheduleUpdateModel instances with different schedule types."""

    class Meta:
        model = ScheduleUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    description = fake.sentence()
    schedule_type: Dict = {
        "recurring": {
            "weekly": {
                "monday": ["10:00-18:00"],  # Updated time range
                "wednesday": ["10:00-18:00"],
                "friday": ["10:00-18:00"],
            }
        }
    }

    @classmethod
    def with_daily_schedule(cls, **kwargs):
        """Create an instance with daily schedule.

        Uses recurring schedule with daily time ranges.

        Args:
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleUpdateModel with a daily schedule

        """
        schedule_type = {"recurring": {"daily": ["10:00-18:00"]}}  # Updated time range
        return cls(schedule_type=schedule_type, **kwargs)

    @classmethod
    def with_non_recurring_schedule(cls, **kwargs):
        """Create an instance with non-recurring schedule.

        Uses non-recurring schedule with specific date and time ranges.

        Args:
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleUpdateModel with a non-recurring schedule

        """
        schedule_type = {
            "non_recurring": [
                "2025/03/01@09:00-2025/03/01@17:00",  # Updated date range
            ]
        }
        return cls(schedule_type=schedule_type, **kwargs)

    @classmethod
    def with_weekly_specific_days(cls, days: List[str], **kwargs):
        """Create an instance with weekly schedule for specific days.

        Args:
            days: List of days to include in weekly schedule (e.g., ["monday", "friday"])
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleUpdateModel with a weekly schedule for specific days

        """
        weekly_schedule = {day: ["10:00-18:00"] for day in days}
        schedule_type = {"recurring": {"weekly": weekly_schedule}}
        return cls(schedule_type=schedule_type, **kwargs)


class ScheduleResponseFactory(ScheduleBaseFactory):
    """Factory for creating ScheduleResponseModel instances with different schedule types."""

    class Meta:
        model = ScheduleResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    description = fake.sentence()
    folder = "Shared"
    schedule_type: Dict = {
        "recurring": {
            "weekly": {
                "monday": ["09:00-17:00"],
                "wednesday": ["09:00-17:00"],
                "friday": ["09:00-17:00"],
            }
        }
    }

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container.

        Args:
            snippet: The snippet name to use
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleResponseModel with the snippet container

        """
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container.

        Args:
            device: The device name to use
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleResponseModel with the device container

        """
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_daily_schedule(cls, **kwargs):
        """Create an instance with daily schedule.

        Uses recurring schedule with daily time ranges.

        Args:
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleResponseModel with a daily schedule

        """
        schedule_type = {"recurring": {"daily": ["09:00-17:00", "18:00-20:00"]}}
        return cls(schedule_type=schedule_type, **kwargs)

    @classmethod
    def with_non_recurring_schedule(cls, **kwargs):
        """Create an instance with non-recurring schedule.

        Uses non-recurring schedule with specific date and time ranges.

        Args:
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleResponseModel with a non-recurring schedule

        """
        schedule_type = {
            "non_recurring": [
                "2025/01/01@09:00-2025/01/01@17:00",
                "2025/02/01@09:00-2025/02/01@17:00",
            ]
        }
        return cls(schedule_type=schedule_type, **kwargs)

    @classmethod
    def from_request(cls, request_model: ScheduleCreateModel, **kwargs):
        """Create a response model based on a request model.

        Args:
            request_model: The request model to base the response on
            **kwargs: Additional fields to override

        Returns:
            An instance of ScheduleResponseModel based on the request model

        """
        data = request_model.model_dump()
        data["id"] = str(uuid4())
        data.update(kwargs)
        return cls(**data)


# ----------------------------------------------------------------------------
# Pydantic modeling tests
# ----------------------------------------------------------------------------


class ScheduleCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ScheduleCreateModel validation testing."""

    class Meta:
        model = dict

    name = factory.Sequence(lambda n: f"schedule_{n}")
    description = fake.sentence()
    folder = "Shared"
    schedule_type = {
        "recurring": {
            "weekly": {
                "monday": ["09:00-17:00"],
                "wednesday": ["09:00-17:00"],
                "friday": ["09:00-17:00"],
            }
        }
    }

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes.

        Returns:
            A dictionary representing a valid ScheduleCreateModel

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            description=fake.sentence(),
            schedule_type={
                "recurring": {
                    "weekly": {
                        "monday": ["09:00-17:00"],
                        "wednesday": ["09:00-17:00"],
                        "friday": ["09:00-17:00"],
                    }
                }
            },
        )

    @classmethod
    def build_valid_daily(cls):
        """Return a valid data dict with daily schedule.

        Returns:
            A dictionary representing a valid ScheduleCreateModel with daily schedule

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            description=fake.sentence(),
            schedule_type={"recurring": {"daily": ["09:00-17:00", "18:00-20:00"]}},
        )

    @classmethod
    def build_valid_non_recurring(cls):
        """Return a valid data dict with non-recurring schedule.

        Returns:
            A dictionary representing a valid ScheduleCreateModel with non-recurring schedule

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            description=fake.sentence(),
            schedule_type={
                "non_recurring": [
                    "2025/01/01@09:00-2025/01/01@17:00",
                    "2025/02/01@09:00-2025/02/01@17:00",
                ]
            },
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern.

        Returns:
            A dictionary with an invalid name for testing validation errors

        """
        return cls(
            name="@invalid-name#",
            folder="Shared",
            schedule_type={
                "recurring": {
                    "weekly": {
                        "monday": ["09:00-17:00"],
                    }
                }
            },
        )

    @classmethod
    def build_with_invalid_time_format(cls):
        """Return a data dict with invalid time range format.

        Returns:
            A dictionary with an invalid time range for testing validation errors

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            schedule_type={
                "recurring": {
                    "weekly": {
                        "monday": ["0900-1700"]  # Missing colons
                    }
                }
            },
        )

    @classmethod
    def build_with_multiple_schedule_types(cls):
        """Return a data dict with multiple schedule types.

        Returns:
            A dictionary with both recurring and non-recurring schedules for testing validation errors

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            schedule_type={
                "recurring": {"daily": ["09:00-17:00"]},
                "non_recurring": ["2025/01/01@09:00-2025/01/01@17:00"],
            },
        )

    @classmethod
    def build_with_invalid_recurring_format(cls):
        """Return a data dict with both weekly and daily recurring schedules.

        Returns:
            A dictionary with invalid recurring structure for testing validation errors

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            schedule_type={
                "recurring": {
                    "weekly": {"monday": ["09:00-17:00"]},
                    "daily": ["09:00-17:00"],
                }
            },
        )

    @classmethod
    def build_with_both_recurring_types(cls):
        """Return a data dict with both weekly and daily recurring schedules.

        Returns:
            A dictionary with invalid recurring structure for testing validation errors

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            schedule_type={
                "recurring": {
                    "weekly": {"monday": ["09:00-17:00"]},
                    "daily": ["09:00-17:00"],
                }
            },
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers.

        Returns:
            A dictionary with multiple containers for testing validation errors

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            snippet="TestSnippet",
            schedule_type={"recurring": {"daily": ["09:00-17:00"]}},
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container.

        Returns:
            A dictionary without any container for testing validation errors

        """
        return cls(
            name="TestSchedule",
            folder=None,
            snippet=None,
            device=None,
            schedule_type={"recurring": {"daily": ["09:00-17:00"]}},
        )

    @classmethod
    def build_with_both_schedule_types(cls):
        """Return a data dict with both recurring and non-recurring schedule types.

        Returns:
            A dictionary with both schedule types for testing validation errors

        """
        return cls(
            name="TestSchedule",
            folder="Shared",
            schedule_type={
                "recurring": {"daily": ["09:00-17:00"]},
                "non_recurring": ["2025/01/01@09:00-2025/01/01@17:00"],
            },
        )


class ScheduleUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ScheduleUpdateModel validation testing."""

    class Meta:
        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"schedule_{n}")
    description = fake.sentence()
    schedule_type = {
        "recurring": {
            "weekly": {
                "monday": ["10:00-18:00"],  # Updated time range
                "wednesday": ["10:00-18:00"],
                "friday": ["10:00-18:00"],
            }
        }
    }

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a schedule.

        Returns:
            A dictionary representing a valid ScheduleUpdateModel

        """
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedSchedule",
            description=fake.sentence(),
            schedule_type={
                "recurring": {
                    "weekly": {
                        "monday": ["10:00-18:00"],
                        "wednesday": ["10:00-18:00"],
                    }
                }
            },
        )

    @classmethod
    def build_valid_daily(cls):
        """Return a valid data dict with daily schedule.

        Returns:
            A dictionary representing a valid ScheduleUpdateModel with daily schedule

        """
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedSchedule",
            description=fake.sentence(),
            schedule_type={"recurring": {"daily": ["10:00-18:00"]}},
        )

    @classmethod
    def build_valid_non_recurring(cls):
        """Return a valid data dict with non-recurring schedule.

        Returns:
            A dictionary representing a valid ScheduleUpdateModel with non-recurring schedule

        """
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedSchedule",
            description=fake.sentence(),
            schedule_type={
                "non_recurring": [
                    "2025/03/01@09:00-2025/03/01@17:00",
                ]
            },
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields.

        Returns:
            A dictionary with invalid fields for testing validation errors

        """
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            schedule_type={"recurring": {"daily": ["invalid-time-format"]}},
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields.

        Returns:
            A dictionary with only required fields for a minimal update

        """
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="MinimalUpdate",
        )
