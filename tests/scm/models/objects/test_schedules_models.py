# tests/scm/models/objects/test_schedules_models.py

"""Tests for schedule models."""

# External libraries
from uuid import UUID

from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.objects import (
    ScheduleCreateModel,
    ScheduleResponseModel,
    ScheduleUpdateModel,
)
from scm.models.objects.schedules import (
    DailyScheduleModel,
    NonRecurringScheduleModel,
    RecurringScheduleModel,
    ScheduleTypeModel,
    WeeklyScheduleModel,
)
from tests.factories.objects.schedules import (
    ScheduleCreateModelFactory,
    ScheduleUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestWeeklyScheduleModel:
    """Tests for weekly schedule model validation."""

    def test_validate_time_ranges(self):
        """Test validation of time ranges."""
        # Test with valid time ranges
        model = WeeklyScheduleModel(
            monday=["09:00-17:00"], wednesday=["09:00-17:00"], friday=["09:00-17:00"]
        )
        assert model.monday == ["09:00-17:00"]
        assert model.wednesday == ["09:00-17:00"]
        assert model.friday == ["09:00-17:00"]

        # Test with None value for a day
        model = WeeklyScheduleModel(monday=None, wednesday=["09:00-17:00"])
        assert model.monday is None
        assert model.wednesday == ["09:00-17:00"]

        # Test with invalid time format (missing leading zero)
        with pytest.raises(ValidationError):
            WeeklyScheduleModel(monday=["9:00-17:00"])

        # Test with invalid time format (wrong length)
        with pytest.raises(ValidationError):
            WeeklyScheduleModel(monday=["9:00-5:00"])

        # Test with invalid hours
        with pytest.raises(ValidationError):
            WeeklyScheduleModel(monday=["25:00-17:00"])

        # Test with invalid minutes
        with pytest.raises(ValidationError):
            WeeklyScheduleModel(monday=["09:60-17:00"])

    def test_validate_at_least_one_day(self):
        """Test validation that at least one day has time ranges."""
        # Test with valid model (has time ranges for at least one day)
        model = WeeklyScheduleModel(monday=["09:00-17:00"])
        assert model.monday == ["09:00-17:00"]

        # Test with invalid model (no days have time ranges)
        with pytest.raises(ValueError):
            WeeklyScheduleModel()


class TestDailyScheduleModel:
    """Tests for daily schedule model validation."""

    def test_validate_time_ranges(self):
        """Test validation of time ranges."""
        # Test with valid time ranges
        model = DailyScheduleModel(daily=["09:00-17:00", "18:00-20:00"])
        assert model.daily == ["09:00-17:00", "18:00-20:00"]

        # Test with empty daily list
        with pytest.raises(ValueError):
            DailyScheduleModel(daily=[])

        # Test with invalid time format
        with pytest.raises(ValidationError):
            DailyScheduleModel(daily=["9:00-17:00"])

        # Test with invalid hours
        with pytest.raises(ValueError):
            DailyScheduleModel(daily=["24:00-17:00"])

        # Test with invalid minutes
        with pytest.raises(ValueError):
            DailyScheduleModel(daily=["09:60-17:00"])


class TestRecurringScheduleModel:
    """Tests for recurring schedule model validation."""

    def test_validate_exactly_one_type(self):
        """Test validation that exactly one of weekly or daily is provided."""
        # Test with weekly schedule
        model = RecurringScheduleModel(weekly={"monday": ["09:00-17:00"]})
        assert model.weekly is not None
        assert model.weekly.monday == ["09:00-17:00"]

        # Test with daily schedule
        model = RecurringScheduleModel(daily=["09:00-17:00"])
        assert model.daily == ["09:00-17:00"]

        # Test with neither type
        with pytest.raises(ValueError):
            RecurringScheduleModel()

        # Test with both types
        with pytest.raises(ValueError):
            RecurringScheduleModel(weekly={"monday": ["09:00-17:00"]}, daily=["09:00-17:00"])


class TestNonRecurringScheduleModel:
    """Tests for non-recurring schedule model validation."""

    def test_validate_datetime_ranges(self):
        """Test validation of datetime ranges."""
        # Test with valid datetime ranges
        model = NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025/01/01@17:00"])
        assert model.non_recurring == ["2025/01/01@09:00-2025/01/01@17:00"]

        # Test with multiple valid datetime ranges
        model = NonRecurringScheduleModel(
            non_recurring=["2025/01/01@09:00-2025/01/01@17:00", "2025/02/15@10:30-2025/02/15@15:45"]
        )
        assert len(model.non_recurring) == 2

        # Test with empty non_recurring list
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=[])

        # Test with invalid datetime format (missing leading zero in hour)
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025/01/01@9:00-2025/01/01@17:00"])

        # Test with invalid year format (non-numeric)
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["ABCD/01/01@09:00-2025/01/01@17:00"])

        # Test with invalid month (out of range)
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025/13/01@09:00-2025/01/01@17:00"])

        # Test with invalid day (out of range)
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025/01/32@09:00-2025/01/01@17:00"])

        # Test with invalid hours (out of range)
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025/01/01@24:00-2025/01/01@17:00"])

        # Test with invalid minutes (out of range)
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:60-2025/01/01@17:00"])

        # Test with missing leading zero in month
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/1/01@09:00-2025/01/01@17:00"])
        assert "Month must use leading zeros" in str(exc_info.value)

        # Test with missing leading zero in day
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/1@09:00-2025/01/01@17:00"])
        assert "Day must use leading zeros" in str(exc_info.value)

        # Test with missing leading zero in hours
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@9:00-2025/01/01@17:00"])
        assert "Hours must use leading zeros" in str(exc_info.value)

        # Test with missing leading zero in minutes
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:0-2025/01/01@17:00"])
        assert "Minutes must use leading zeros" in str(exc_info.value)

        # Test with invalid separator (using - instead of /)
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025-01-01@09:00-2025/01/01@17:00"])

        # Test with missing @ separator
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025/01/01 09:00-2025/01/01@17:00"])

        # Test with only one side of the range
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00"])

        # Test with invalid range format (missing hyphen)
        with pytest.raises(ValueError):
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00=2025/01/01@17:00"])

    def test_start_date_format_validation(self):
        """Test validation of the start date format."""
        # Test invalid start date parts count (covers line 171)
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(
                non_recurring=["2025/01@09:00-2025/01/01@17:00"]  # Missing day in start date
            )
        assert "Start date must be in format YYYY/MM/DD" in str(exc_info.value)

        # Test invalid time format in start time (covers line 181)
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(
                non_recurring=["2025/01/01@09-2025/01/01@17:00"]  # Missing minutes in start time
            )
        assert "Start time must be in format HH:MM" in str(exc_info.value)

    def test_end_date_format_validation(self):
        """Test validation of the end date format."""
        # Test missing @ separator in end date (covers line 188)
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(
                non_recurring=[
                    "2025/01/01@09:00-2025/01/01 17:00"
                ]  # Space instead of @ in end time
            )
        assert "End datetime must contain @ to separate date and time" in str(exc_info.value)

        # Test invalid parts count in end date (covers line 193)
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(
                non_recurring=["2025/01/01@09:00-2025@17:00"]  # Missing month/day in end date
            )
        assert "End date must be in format YYYY/MM/DD" in str(exc_info.value)


class TestScheduleTypeModel:
    """Tests for schedule type model validation."""

    def test_validate_exactly_one_type(self):
        """Test validation that exactly one schedule type is provided."""
        # Test with recurring schedule
        model = ScheduleTypeModel(recurring={"weekly": {"monday": ["09:00-17:00"]}})
        assert model.recurring is not None
        assert model.recurring.weekly is not None
        assert model.recurring.weekly.monday == ["09:00-17:00"]

        # Test with non-recurring schedule
        model = ScheduleTypeModel(non_recurring=["2025/01/01@09:00-2025/01/01@17:00"])
        assert model.non_recurring == ["2025/01/01@09:00-2025/01/01@17:00"]

        # Test with neither type
        with pytest.raises(ValueError):
            ScheduleTypeModel()

        # Test with both types
        with pytest.raises(ValueError):
            ScheduleTypeModel(
                recurring={"weekly": {"monday": ["09:00-17:00"]}},
                non_recurring=["2025/01/01@09:00-2025/01/01@17:00"],
            )


class TestScheduleCreateModel:
    """Tests for schedule model validation."""

    def test_schedule_create_model_valid_weekly(self):
        """Test validation with valid weekly schedule data."""
        data = ScheduleCreateModelFactory.build_valid()
        model = ScheduleCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.schedule_type.recurring is not None
        assert model.schedule_type.recurring.weekly is not None
        assert "monday" in model.schedule_type.recurring.weekly.__dict__

    def test_schedule_create_model_valid_daily(self):
        """Test validation with valid daily schedule data."""
        data = ScheduleCreateModelFactory.build_valid_daily()
        model = ScheduleCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.schedule_type.recurring is not None
        assert model.schedule_type.recurring.daily is not None
        assert "09:00-17:00" in model.schedule_type.recurring.daily

    def test_schedule_create_model_valid_non_recurring(self):
        """Test validation with valid non-recurring schedule data."""
        data = ScheduleCreateModelFactory.build_valid_non_recurring()
        model = ScheduleCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.schedule_type.non_recurring is not None
        assert "2025/01/01@09:00-2025/01/01@17:00" in model.schedule_type.non_recurring

    def test_schedule_create_model_invalid_name(self):
        """Test validation when invalid name is provided."""
        data = ScheduleCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateModel(**data)
        assert "name" in str(exc_info.value)
        assert "pattern" in str(exc_info.value)

    def test_schedule_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = ScheduleCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            ScheduleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_schedule_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = ScheduleCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            ScheduleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_schedule_create_model_invalid_time_format(self):
        """Test validation when invalid time format is provided."""
        data = ScheduleCreateModelFactory.build_with_invalid_time_format()
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateModel(**data)
        assert "Time range must be in format hh:mm-hh:mm" in str(exc_info.value)

    def test_schedule_create_model_invalid_date_format(self):
        """Test validation when invalid date format is provided in a composed model."""
        # Testing validation via the NonRecurringScheduleModel directly
        # This is the proper way to ensure the validation is applied correctly
        data = NonRecurringScheduleModel(
            non_recurring=["2025/01/01@09:00-2025/01/01@17:00"]  # Valid format
        )
        assert len(data.non_recurring) == 1

        # Now test invalid format with direct model
        with pytest.raises(
            ValueError
        ) as exc_info:  # Note: Using ValueError, not ValidationError here
            NonRecurringScheduleModel(
                non_recurring=["2025/1/01@09:00-2025/01/01@17:00"]  # Missing leading zero in month
            )
        assert "Month must use leading zeros" in str(exc_info.value)

    def test_non_recurring_date_format_validation(self):
        """Test validation of the date format for non-recurring schedules."""
        # Test with various invalid formats directly using the NonRecurringScheduleModel

        # Test missing leading zero in month
        with pytest.raises(ValueError) as exc_info:  # Using ValueError directly
            NonRecurringScheduleModel(non_recurring=["2025/1/01@09:00-2025/01/01@17:00"])
        assert "Month must use leading zeros" in str(exc_info.value)

        # Test missing leading zero in day
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/1@09:00-2025/01/01@17:00"])
        assert "Day must use leading zeros" in str(exc_info.value)

        # Test missing leading zero in hours
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@9:00-2025/01/01@17:00"])
        assert "Hours must use leading zeros" in str(exc_info.value)

        # Test missing leading zero in minutes
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:0-2025/01/01@17:00"])
        assert "Minutes must use leading zeros" in str(exc_info.value)

    def test_non_recurring_end_date_format_validation(self):
        """Test validation of the end date format for non-recurring schedules."""
        # Test various invalid end date formats

        # Test missing leading zero in end month
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025/1/01@17:00"])
        assert "Month must use leading zeros" in str(exc_info.value)

        # Test missing leading zero in end day
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025/01/1@17:00"])
        assert "Day must use leading zeros" in str(exc_info.value)

        # Test missing leading zero in end hours
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025/01/01@9:00"])
        assert "Hours must use leading zeros" in str(exc_info.value)

        # Test missing leading zero in end minutes
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025/01/01@17:0"])
        assert "Minutes must use leading zeros" in str(exc_info.value)

        # Test invalid end date separator
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025-01-01@17:00"])
        assert "Invalid datetime range format" in str(exc_info.value)

        # Test invalid end time separator
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025/01/01@17.00"])
        assert "End time must be in format HH:MM" in str(exc_info.value)

        # Test invalid end year format
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-ABCD/01/01@17:00"])
        assert "Year must be numeric" in str(exc_info.value)

        # Test out of range end values
        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025/13/01@17:00"])
        assert "Month must be between 01 and 12" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            NonRecurringScheduleModel(non_recurring=["2025/01/01@09:00-2025/01/32@17:00"])
        assert "Day must be between 01 and 31" in str(exc_info.value)

    def test_schedule_create_model_both_recurring_types(self):
        """Test validation when both weekly and daily schedules are provided."""
        data = ScheduleCreateModelFactory.build_with_both_recurring_types()
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateModel(**data)
        assert "Exactly one of 'weekly' or 'daily' must be provided" in str(exc_info.value)

    def test_schedule_create_model_both_schedule_types(self):
        """Test validation when both recurring and non-recurring schedules are provided."""
        data = ScheduleCreateModelFactory.build_with_both_schedule_types()
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateModel(**data)
        assert "Exactly one of 'recurring' or 'non_recurring' must be provided" in str(
            exc_info.value
        )

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateModel(name="Test")
        # In newer pydantic versions, the error message is slightly different
        assert "required" in str(exc_info.value)


class TestScheduleUpdateModel:
    """Tests for schedule update model validation."""

    def test_schedule_update_model_valid(self):
        """Test validation with valid update data."""
        data = ScheduleUpdateModelFactory.build_valid()
        model = ScheduleUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.schedule_type.recurring is not None
        assert model.schedule_type.recurring.weekly is not None
        assert "monday" in model.schedule_type.recurring.weekly.__dict__
        assert "tuesday" in model.schedule_type.recurring.weekly.__dict__

    def test_schedule_update_model_valid_daily(self):
        """Test validation with valid daily schedule update data."""
        data = ScheduleUpdateModelFactory.build_valid_daily()
        model = ScheduleUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.schedule_type.recurring is not None
        assert model.schedule_type.recurring.daily is not None
        assert "10:00-18:00" in model.schedule_type.recurring.daily

    def test_schedule_update_model_valid_non_recurring(self):
        """Test validation with valid non-recurring schedule update data."""
        data = ScheduleUpdateModelFactory.build_valid_non_recurring()
        model = ScheduleUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.schedule_type.non_recurring is not None
        assert "2025/03/01@09:00-2025/03/01@17:00" in model.schedule_type.non_recurring

    def test_schedule_update_model_invalid_fields(self):
        """Test validation when invalid fields are provided."""
        data = ScheduleUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            ScheduleUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "id" in error_msg or "name" in error_msg or "schedule_type" in error_msg

    def test_schedule_update_model_minimal_update(self):
        """Test validation with minimal update data."""
        # Create a model manually to ensure validation runs
        with pytest.raises(ValidationError) as exc_info:
            ScheduleUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="MinimalUpdate",
                # Missing schedule_type which is required
            )
        assert "required" in str(exc_info.value)
        assert "schedule_type" in str(exc_info.value)


class TestModelConfig:
    """Tests for Pydantic model configuration options."""

    def test_populate_by_name(self):
        """Test that populate_by_name works correctly in ScheduleBaseModel."""
        # Creating a model with an alias
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestSchedule",
            "folder": "Shared",
            "schedule_type": {"recurring": {"weekly": {"monday": ["09:00-17:00"]}}},
        }

        # Test with update model (inherits from ScheduleBaseModel)
        model = ScheduleUpdateModel(**data)

        # Verify model_config settings are applied
        assert model.model_config["populate_by_name"] is True
        assert model.model_config["validate_assignment"] is True
        assert model.model_config["arbitrary_types_allowed"] is True

    def test_validate_assignment(self):
        """Test that validate_assignment works correctly."""
        # Create a model
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestSchedule",
            "folder": "Shared",
            "schedule_type": {"recurring": {"weekly": {"monday": ["09:00-17:00"]}}},
        }
        model = ScheduleUpdateModel(**data)

        # Test that assignment is validated
        with pytest.raises(ValueError):
            # Name has a pattern validation that only allows certain characters
            model.name = "$Invalid~Name"


class TestScheduleResponseModel:
    """Tests for schedule response model validation."""

    def test_schedule_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestSchedule",
            "folder": "Shared",
            "schedule_type": {
                "recurring": {
                    "weekly": {
                        "monday": ["09:00-17:00"],
                        "wednesday": ["09:00-17:00"],
                        "friday": ["09:00-17:00"],
                    }
                }
            },
        }
        model = ScheduleResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.schedule_type.recurring is not None
        assert model.schedule_type.recurring.weekly is not None

    def test_schedule_response_model_with_snippet(self):
        """Test validation with snippet container."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestSchedule",
            "snippet": "TestSnippet",
            "schedule_type": {"recurring": {"daily": ["09:00-17:00"]}},
        }
        model = ScheduleResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_schedule_response_model_with_device(self):
        """Test validation with device container."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestSchedule",
            "device": "TestDevice",
            "schedule_type": {"non_recurring": ["2025/01/01@09:00-2025/01/01@17:00"]},
        }
        model = ScheduleResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None

    def test_schedule_response_model_missing_id(self):
        """Test validation when id is missing."""
        data = {
            "name": "TestSchedule",
            "folder": "Shared",
            "schedule_type": {"recurring": {"weekly": {"monday": ["09:00-17:00"]}}},
        }
        with pytest.raises(ValidationError) as exc_info:
            ScheduleResponseModel(**data)
        assert "id" in str(exc_info.value)
        assert "required" in str(exc_info.value)


class TestExtraFieldsForbidden:
    """Test that extra fields are rejected by all models."""

    def test_weekly_schedule_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in WeeklyScheduleModel."""
        with pytest.raises(ValidationError) as exc_info:
            WeeklyScheduleModel(monday=["09:00-17:00"], unknown_field="should fail")
        assert "extra" in str(exc_info.value).lower()

    def test_daily_schedule_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in DailyScheduleModel."""
        with pytest.raises(ValidationError) as exc_info:
            DailyScheduleModel(daily=["09:00-17:00"], unknown_field="should fail")
        assert "extra" in str(exc_info.value).lower()

    def test_recurring_schedule_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in RecurringScheduleModel."""
        with pytest.raises(ValidationError) as exc_info:
            RecurringScheduleModel(daily=["09:00-17:00"], unknown_field="should fail")
        assert "extra" in str(exc_info.value).lower()

    def test_non_recurring_schedule_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in NonRecurringScheduleModel."""
        with pytest.raises(ValidationError) as exc_info:
            NonRecurringScheduleModel(
                non_recurring=["2025/01/01@09:00-2025/01/01@17:00"],
                unknown_field="should fail",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_schedule_type_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ScheduleTypeModel."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleTypeModel(
                recurring={"daily": ["09:00-17:00"]},
                unknown_field="should fail",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_schedule_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ScheduleCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreateModel(
                name="TestSchedule",
                folder="Shared",
                schedule_type={"recurring": {"daily": ["09:00-17:00"]}},
                unknown_field="should fail",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_schedule_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ScheduleUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="TestSchedule",
                schedule_type={"recurring": {"daily": ["09:00-17:00"]}},
                unknown_field="should fail",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_schedule_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored in ScheduleResponseModel."""
        model = ScheduleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestSchedule",
            folder="Shared",
            schedule_type={"recurring": {"daily": ["09:00-17:00"]}},
            unknown_field="should be ignored",
        )
        assert not hasattr(model, "unknown_field")


# -------------------- End of Test Classes --------------------
