# tests/scm/config/objects/test_schedules.py

# Standard library imports
import pytest
import uuid
from unittest.mock import MagicMock

# External libraries
from pydantic import ValidationError

# Local SDK imports
from scm.config.objects import Schedule
from scm.models.objects import (
    ScheduleResponseModel,
    ScheduleUpdateModel,
)
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    MissingQueryParameterError,
)
from tests.factories import (
    ScheduleResponseFactory,
)


@pytest.mark.usefixtures("load_env")
class TestScheduleBase:
    """Base test class for Schedule object tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.schedule = Schedule(self.mock_scm, max_limit=200)


class TestScheduleInit(TestScheduleBase):
    """Tests for Schedule object initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        assert self.schedule.api_client == self.mock_scm
        assert self.schedule.max_limit == 200  # Custom value from setup_method

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        custom_limit = 500
        schedule = Schedule(self.mock_scm, max_limit=custom_limit)
        assert schedule.max_limit == custom_limit

    def test_max_limit_property(self):
        """Test the max_limit property getter and setter."""
        new_limit = 300
        self.schedule.max_limit = new_limit
        assert self.schedule.max_limit == new_limit

    def test_validate_max_limit_none(self):
        """Test _validate_max_limit with None value."""
        result = self.schedule._validate_max_limit(None)
        assert result == Schedule.DEFAULT_MAX_LIMIT

    def test_validate_max_limit_valid(self):
        """Test _validate_max_limit with valid value."""
        valid_limit = 1000
        result = self.schedule._validate_max_limit(valid_limit)
        assert result == valid_limit

    def test_validate_max_limit_not_int(self):
        """Test _validate_max_limit with non-integer value."""
        with pytest.raises(InvalidObjectError):
            self.schedule._validate_max_limit("not_an_int")

    def test_validate_max_limit_less_than_one(self):
        """Test _validate_max_limit with value less than 1."""
        with pytest.raises(InvalidObjectError):
            self.schedule._validate_max_limit(0)

    def test_validate_max_limit_exceeds_max(self):
        """Test _validate_max_limit with value exceeding maximum."""
        with pytest.raises(InvalidObjectError):
            self.schedule._validate_max_limit(Schedule.ABSOLUTE_MAX_LIMIT + 1)


class TestScheduleCreate(TestScheduleBase):
    """Tests for Schedule.create method."""

    def test_create_valid_schedule(self):
        """Test creating a schedule with valid data."""
        # Test data
        schedule_data = {
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

        # Mock API response
        mock_response = {"id": str(uuid.uuid4()), **schedule_data}
        self.mock_scm.post.return_value = mock_response

        # Call the method
        result = self.schedule.create(schedule_data)

        # Verify the result
        assert isinstance(result, ScheduleResponseModel)
        assert result.id == uuid.UUID(mock_response["id"])
        assert result.name == schedule_data["name"]

        # Verify API call
        self.mock_scm.post.assert_called_once_with(
            self.schedule.ENDPOINT,
            json=schedule_data,
        )

    def test_create_with_validation_error(self):
        """Test creating a schedule with invalid data that fails validation."""
        # Test data with invalid name (contains special characters)
        invalid_data = {
            "name": "Test@Schedule",  # Invalid name with @ character
            "folder": "Shared",
            "schedule_type": {
                "recurring": {
                    "weekly": {
                        "monday": ["09:00-17:00"],
                    }
                }
            },
        }

        # Expect ValidationError from Pydantic
        with pytest.raises(ValidationError):
            self.schedule.create(invalid_data)

        # Verify API call was not made
        self.mock_scm.post.assert_not_called()


class TestScheduleGet(TestScheduleBase):
    """Tests for Schedule.get method."""

    def test_get_schedule_by_id(self):
        """Test getting a schedule by ID."""
        # Test data
        object_id = str(uuid.uuid4())
        mock_response = {
            "id": object_id,
            "name": "TestSchedule",
            "folder": "Shared",
            "schedule_type": {
                "recurring": {
                    "weekly": {
                        "monday": ["09:00-17:00"],
                    }
                }
            },
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method
        result = self.schedule.get(object_id)

        # Verify the result
        assert isinstance(result, ScheduleResponseModel)
        assert str(result.id) == object_id
        assert result.name == mock_response["name"]

        # Verify API call
        self.mock_scm.get.assert_called_once_with(
            f"{self.schedule.ENDPOINT}/{object_id}",
        )

    def test_get_with_api_error(self):
        """Test getting a schedule with API error."""
        # Test data
        object_id = str(uuid.uuid4())
        error_details = {"error": "Object not found"}

        self.mock_scm.get.side_effect = APIError(
            message="Object Not Present",
            error_code="E005",
            http_status_code=404,
            details=error_details,
        )

        # Call the method and expect APIError
        with pytest.raises(APIError) as exc_info:
            self.schedule.get(object_id)

        # Verify error details
        assert exc_info.value.message == "Object Not Present"
        assert exc_info.value.http_status_code == 404
        assert exc_info.value.error_code == "E005"

        # Verify API call
        self.mock_scm.get.assert_called_once_with(
            f"{self.schedule.ENDPOINT}/{object_id}",
        )


class TestScheduleUpdate(TestScheduleBase):
    """Tests for Schedule.update method."""

    def test_update_schedule(self):
        """Test updating a schedule."""
        # Test data
        object_id = str(uuid.uuid4())
        update_data = ScheduleUpdateModel(
            id=object_id,
            name="UpdatedSchedule",
            folder="Shared",
            schedule_type={
                "recurring": {
                    "weekly": {
                        "tuesday": ["10:00-18:00"],
                    }
                }
            },
        )

        mock_response = {
            "id": object_id,
            "name": "UpdatedSchedule",
            "folder": "Shared",
            "schedule_type": {
                "recurring": {
                    "weekly": {
                        "tuesday": ["10:00-18:00"],
                    }
                }
            },
        }
        self.mock_scm.put.return_value = mock_response

        # Call the method
        result = self.schedule.update(update_data)

        # Verify the result
        assert isinstance(result, ScheduleResponseModel)
        assert str(result.id) == object_id
        assert result.name == "UpdatedSchedule"

        # Verify API call - should not include ID in payload
        expected_payload = update_data.model_dump(exclude_unset=True)
        expected_payload.pop("id")
        self.mock_scm.put.assert_called_once_with(
            f"{self.schedule.ENDPOINT}/{object_id}",
            json=expected_payload,
        )


class TestScheduleDelete(TestScheduleBase):
    """Tests for Schedule.delete method."""

    def test_delete_schedule(self):
        """Test deleting a schedule."""
        # Test data
        object_id = str(uuid.uuid4())
        self.mock_scm.delete.return_value = None

        # Call the method
        result = self.schedule.delete(object_id)

        # Verify the result
        assert result is None

        # Verify API call
        self.mock_scm.delete.assert_called_once_with(
            f"{self.schedule.ENDPOINT}/{object_id}",
        )

    def test_delete_with_api_error(self):
        """Test deleting a schedule with API error."""
        # Test data
        object_id = str(uuid.uuid4())
        error_details = {"error": "Object not found"}

        self.mock_scm.delete.side_effect = APIError(
            message="Object Not Present",
            error_code="E005",
            http_status_code=404,
            details=error_details,
        )

        # Call the method and expect APIError
        with pytest.raises(APIError) as exc_info:
            self.schedule.delete(object_id)

        # Verify error details
        assert exc_info.value.message == "Object Not Present"
        assert exc_info.value.http_status_code == 404
        assert exc_info.value.error_code == "E005"

        # Verify API call
        self.mock_scm.delete.assert_called_once_with(
            f"{self.schedule.ENDPOINT}/{object_id}",
        )


class TestScheduleList(TestScheduleBase):
    """Tests for Schedule.list method."""

    def test_list_schedules_empty_folder(self):
        """Test listing schedules with empty folder name."""
        with pytest.raises(MissingQueryParameterError):
            self.schedule.list(folder="")

    def test_list_schedules_no_container(self):
        """Test listing schedules with no container provided."""
        with pytest.raises(InvalidObjectError):
            self.schedule.list()

    def test_list_schedules_single_page(self):
        """Test listing schedules with a single page of results."""
        # Test data
        folder = "Shared"
        object_count = 3

        # Create test objects
        mock_objects = [ScheduleResponseFactory.build(folder=folder) for _ in range(object_count)]

        # Create API response
        mock_response = {
            "data": [obj.model_dump() for obj in mock_objects],
            "limit": self.schedule.max_limit,
            "offset": 0,
            "total": object_count,
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method
        result = self.schedule.list(folder=folder)

        # Verify the result
        assert len(result) == object_count
        assert all(isinstance(obj, ScheduleResponseModel) for obj in result)

        # Verify API call
        self.mock_scm.get.assert_called_once_with(
            self.schedule.ENDPOINT,
            params={
                "folder": folder,
                "limit": self.schedule.max_limit,
                "offset": 0,
            },
        )

    def test_list_schedules_multiple_pages(self):
        """Test listing schedules with multiple pages of results."""
        # Test data
        folder = "Shared"
        page_size = self.schedule.max_limit
        total_objects = page_size + 5  # More than one page

        # Create first page response
        first_page_objects = [
            ScheduleResponseFactory.build(folder=folder).model_dump() for _ in range(page_size)
        ]
        first_page_response = {
            "data": first_page_objects,
            "limit": page_size,
            "offset": 0,
            "total": total_objects,
        }

        # Create second page response
        second_page_objects = [
            ScheduleResponseFactory.build(folder=folder).model_dump()
            for _ in range(total_objects - page_size)
        ]
        second_page_response = {
            "data": second_page_objects,
            "limit": page_size,
            "offset": page_size,
            "total": total_objects,
        }

        # Configure mock to return different responses for each call
        self.mock_scm.get.side_effect = [first_page_response, second_page_response]

        # Call the method
        result = self.schedule.list(folder=folder)

        # Verify the result
        assert len(result) == total_objects
        assert all(isinstance(obj, ScheduleResponseModel) for obj in result)

        # Verify API calls
        assert self.mock_scm.get.call_count == 2
        self.mock_scm.get.assert_any_call(
            self.schedule.ENDPOINT,
            params={
                "folder": folder,
                "limit": page_size,
                "offset": 0,
            },
        )
        self.mock_scm.get.assert_any_call(
            self.schedule.ENDPOINT,
            params={
                "folder": folder,
                "limit": page_size,
                "offset": page_size,
            },
        )

    def test_list_schedules_invalid_response_not_dict(self):
        """Test listing schedules with invalid response (not a dict)."""
        self.mock_scm.get.return_value = "not a dict"

        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule.list(folder="Shared")

        assert exc_info.value.message == "Invalid response format: expected dictionary"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_list_schedules_invalid_response_no_data(self):
        """Test listing schedules with invalid response (no data field)."""
        self.mock_scm.get.return_value = {"not_data": []}

        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule.list(folder="Shared")

        assert exc_info.value.message == "Invalid response format: missing 'data' field"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_list_schedules_invalid_response_data_not_list(self):
        """Test listing schedules with invalid response (data is not a list)."""
        self.mock_scm.get.return_value = {"data": "not a list"}

        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule.list(folder="Shared")

        assert exc_info.value.message == "Invalid response format: 'data' field must be a list"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_list_with_exact_match(self):
        """Test listing schedules with exact_match=True."""
        # Test data
        folder = "Shared"
        exact_match_folder = folder
        different_folder = "DifferentFolder"

        # Create test objects with different folders
        object1 = ScheduleResponseFactory.build(folder=exact_match_folder)
        object2 = ScheduleResponseFactory.build(folder=different_folder)
        object3 = ScheduleResponseFactory.build(folder=exact_match_folder)

        # Create API response containing mixed folders
        mock_response = {
            "data": [
                object1.model_dump(),
                object2.model_dump(),
                object3.model_dump(),
            ],
            "limit": self.schedule.max_limit,
            "offset": 0,
            "total": 3,
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method with exact_match=True
        result = self.schedule.list(folder=folder, exact_match=True)

        # Verify the result - should only include objects with matching folder
        assert len(result) == 2
        assert all(obj.folder == exact_match_folder for obj in result)

    def test_list_with_exclude_folders(self):
        """Test listing schedules with exclude_folders filter."""
        # Test data
        folder = "Shared"
        exclude_folder = "ExcludeMe"

        # Create test objects
        object1 = ScheduleResponseFactory.build(folder=folder)
        object2 = ScheduleResponseFactory.build(folder=exclude_folder)
        object3 = ScheduleResponseFactory.build(folder=folder)

        # Create API response
        mock_response = {
            "data": [
                object1.model_dump(),
                object2.model_dump(),
                object3.model_dump(),
            ],
            "limit": self.schedule.max_limit,
            "offset": 0,
            "total": 3,
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method with exclude_folders
        result = self.schedule.list(
            folder=folder,
            exclude_folders=[exclude_folder],
        )

        # Verify the result - should exclude objects with excluded folder
        assert len(result) == 2
        assert all(obj.folder != exclude_folder for obj in result)

    def test_list_with_exclude_snippets(self):
        """Test listing schedules with exclude_snippets filter."""
        # Test data
        folder = "Shared"
        exclude_snippet = "ExcludeSnippet"

        # Create test objects
        object1 = ScheduleResponseFactory.build(folder=folder)
        object1.snippet = exclude_snippet  # Add snippet attribute
        object2 = ScheduleResponseFactory.build(folder=folder)
        object2.snippet = None
        object3 = ScheduleResponseFactory.build(folder=folder)
        object3.snippet = "OtherSnippet"

        # Create API response
        mock_response = {
            "data": [
                object1.model_dump(),
                object2.model_dump(),
                object3.model_dump(),
            ],
            "limit": self.schedule.max_limit,
            "offset": 0,
            "total": 3,
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method with exclude_snippets
        result = self.schedule.list(
            folder=folder,
            exclude_snippets=[exclude_snippet],
        )

        # Verify the result - should exclude objects with excluded snippet
        assert len(result) == 2
        assert all(obj.snippet != exclude_snippet for obj in result)

    def test_list_with_exclude_devices(self):
        """Test listing schedules with exclude_devices filter."""
        # Test data
        folder = "Shared"
        exclude_device = "ExcludeDevice"

        # Create test objects
        object1 = ScheduleResponseFactory.build(folder=folder)
        object1.device = exclude_device  # Add device attribute
        object2 = ScheduleResponseFactory.build(folder=folder)
        object2.device = None
        object3 = ScheduleResponseFactory.build(folder=folder)
        object3.device = "OtherDevice"

        # Create API response
        mock_response = {
            "data": [
                object1.model_dump(),
                object2.model_dump(),
                object3.model_dump(),
            ],
            "limit": self.schedule.max_limit,
            "offset": 0,
            "total": 3,
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method with exclude_devices
        result = self.schedule.list(
            folder=folder,
            exclude_devices=[exclude_device],
        )

        # Verify the result - should exclude objects with excluded device
        assert len(result) == 2
        assert all(obj.device != exclude_device for obj in result)


class TestScheduleFilters(TestScheduleBase):
    """Tests for Schedule filtering functionality."""

    def test_apply_filters_empty(self):
        """Test _apply_filters with empty filters."""
        # Create test schedules
        schedules = [
            ScheduleResponseFactory.build(),
            ScheduleResponseFactory.build(),
        ]

        # Apply filters
        result = self.schedule._apply_filters(schedules, {})

        # Verify no filtering occurred
        assert len(result) == len(schedules)
        assert result == schedules

    def test_apply_filters_schedule_type_recurring(self):
        """Test _apply_filters with schedule_type=recurring filter."""
        # Create test schedules with different types
        recurring_schedule = ScheduleResponseFactory.build()
        non_recurring_schedule = ScheduleResponseFactory.with_non_recurring_schedule()
        schedules = [recurring_schedule, non_recurring_schedule]

        # Apply filter for recurring schedules
        result = self.schedule._apply_filters(schedules, {"schedule_type": "recurring"})

        # Verify filtering
        assert len(result) == 1
        assert result[0].schedule_type.recurring is not None
        assert result[0].schedule_type.non_recurring is None

    def test_apply_filters_schedule_type_non_recurring(self):
        """Test _apply_filters with schedule_type=non_recurring filter."""
        # Create test schedules with different types
        recurring_schedule = ScheduleResponseFactory.build()
        non_recurring_schedule = ScheduleResponseFactory.with_non_recurring_schedule()
        schedules = [recurring_schedule, non_recurring_schedule]

        # Apply filter for non-recurring schedules
        result = self.schedule._apply_filters(schedules, {"schedule_type": "non_recurring"})

        # Verify filtering
        assert len(result) == 1
        assert result[0].schedule_type.non_recurring is not None
        assert result[0].schedule_type.recurring is None

    def test_apply_filters_schedule_type_invalid(self):
        """Test _apply_filters with invalid schedule_type value."""
        # Create test schedules
        schedules = [ScheduleResponseFactory.build()]

        # Apply filter with invalid value
        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule._apply_filters(schedules, {"schedule_type": "invalid_type"})

        # Verify error
        assert (
            exc_info.value.message
            == "'schedule_type' filter must be 'recurring' or 'non_recurring'"
        )
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_apply_filters_recurring_type_weekly(self):
        """Test _apply_filters with recurring_type=weekly filter."""
        # Create test schedules with different recurring types
        weekly_schedule = ScheduleResponseFactory.build()  # Default is weekly
        daily_schedule = ScheduleResponseFactory.with_daily_schedule()
        non_recurring_schedule = ScheduleResponseFactory.with_non_recurring_schedule()
        schedules = [weekly_schedule, daily_schedule, non_recurring_schedule]

        # Apply filter for weekly schedules
        result = self.schedule._apply_filters(schedules, {"recurring_type": "weekly"})

        # Verify filtering
        assert len(result) == 1
        assert result[0].schedule_type.recurring is not None
        assert result[0].schedule_type.recurring.weekly is not None

    def test_apply_filters_recurring_type_daily(self):
        """Test _apply_filters with recurring_type=daily filter."""
        # Create test schedules with different recurring types
        weekly_schedule = ScheduleResponseFactory.build()  # Default is weekly
        daily_schedule = ScheduleResponseFactory.with_daily_schedule()
        non_recurring_schedule = ScheduleResponseFactory.with_non_recurring_schedule()
        schedules = [weekly_schedule, daily_schedule, non_recurring_schedule]

        # Apply filter for daily schedules
        result = self.schedule._apply_filters(schedules, {"recurring_type": "daily"})

        # Verify filtering
        assert len(result) == 1
        assert result[0].schedule_type.recurring is not None
        assert result[0].schedule_type.recurring.daily is not None

    def test_apply_filters_recurring_type_invalid(self):
        """Test _apply_filters with invalid recurring_type value."""
        # Create test schedules
        schedules = [ScheduleResponseFactory.build()]

        # Apply filter with invalid value
        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule._apply_filters(schedules, {"recurring_type": "invalid_type"})

        # Verify error
        assert exc_info.value.message == "'recurring_type' filter must be 'weekly' or 'daily'"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400


class TestScheduleFetch(TestScheduleBase):
    """Tests for Schedule.fetch method."""

    def test_fetch_by_name_empty_name(self):
        """Test fetching a schedule with empty name."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.schedule.fetch(name="")

        assert exc_info.value.message == "Field 'name' cannot be empty"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_by_name_empty_folder(self):
        """Test fetching a schedule with empty folder."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.schedule.fetch(name="TestSchedule", folder="")

        assert exc_info.value.message == "Field 'folder' cannot be empty"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_by_name_no_container(self):
        """Test fetching a schedule with no container."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule.fetch(name="TestSchedule")

        assert (
            exc_info.value.message
            == "At least one of 'folder', 'snippet', or 'device' must be provided."
        )
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_by_name_valid_response_data_list(self):
        """Test fetching a schedule by name with data list response."""
        # Test data
        name = "TestSchedule"
        folder = "Shared"
        object_id = str(uuid.uuid4())

        # Create API response
        mock_response = {
            "data": [
                {
                    "id": object_id,
                    "name": name,
                    "folder": folder,
                    "schedule_type": {
                        "recurring": {
                            "weekly": {
                                "monday": ["09:00-17:00"],
                            }
                        }
                    },
                }
            ],
            "limit": 1,
            "offset": 0,
            "total": 1,
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method
        result = self.schedule.fetch(name=name, folder=folder)

        # Verify the result
        assert isinstance(result, ScheduleResponseModel)
        assert str(result.id) == object_id
        assert result.name == name
        assert result.folder == folder

        # Verify API call
        self.mock_scm.get.assert_called_once_with(
            self.schedule.ENDPOINT,
            params={
                "name": name,
                "folder": folder,
            },
        )

    def test_fetch_by_name_valid_response_direct_object(self):
        """Test fetching a schedule by name with direct object response."""
        # Test data
        name = "TestSchedule"
        folder = "Shared"
        object_id = str(uuid.uuid4())

        # Create API response (direct object)
        mock_response = {
            "id": object_id,
            "name": name,
            "folder": folder,
            "schedule_type": {
                "recurring": {
                    "weekly": {
                        "monday": ["09:00-17:00"],
                    }
                }
            },
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method
        result = self.schedule.fetch(name=name, folder=folder)

        # Verify the result
        assert isinstance(result, ScheduleResponseModel)
        assert str(result.id) == object_id
        assert result.name == name
        assert result.folder == folder

    def test_fetch_by_name_empty_data_list(self):
        """Test fetching a schedule by name with empty data list."""
        # Test data
        name = "NonExistentSchedule"
        folder = "Shared"

        # Create API response with empty data list
        mock_response = {
            "data": [],
            "limit": 1,
            "offset": 0,
            "total": 0,
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method and expect error
        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule.fetch(name=name, folder=folder)

        # Verify error
        assert exc_info.value.message == f"No schedule found with name '{name}'"
        assert exc_info.value.error_code == "E005"
        assert exc_info.value.http_status_code == 404

    def test_fetch_by_name_invalid_response_format(self):
        """Test fetching a schedule by name with invalid response format."""
        # Test data
        name = "TestSchedule"
        folder = "Shared"

        # Create API response with invalid format
        mock_response = {
            "some_other_field": "value",
            # Missing both 'data' and 'id'
        }
        self.mock_scm.get.return_value = mock_response

        # Call the method and expect error
        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule.fetch(name=name, folder=folder)

        # Verify error
        assert exc_info.value.message == "Invalid response format"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_by_name_response_not_dict(self):
        """Test fetching a schedule by name with non-dict response."""
        # Test data
        name = "TestSchedule"
        folder = "Shared"

        # Create invalid API response
        self.mock_scm.get.return_value = "not a dict"

        # Call the method and expect error
        with pytest.raises(InvalidObjectError) as exc_info:
            self.schedule.fetch(name=name, folder=folder)

        # Verify error
        assert exc_info.value.message == "Invalid response format: expected dictionary"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500


class TestScheduleUtilityMethods(TestScheduleBase):
    """Tests for Schedule utility methods."""

    def test_build_container_params_folder(self):
        """Test _build_container_params with folder."""
        result = self.schedule._build_container_params(
            folder="Shared",
            snippet=None,
            device=None,
        )
        assert result == {"folder": "Shared"}

    def test_build_container_params_snippet(self):
        """Test _build_container_params with snippet."""
        result = self.schedule._build_container_params(
            folder=None,
            snippet="TestSnippet",
            device=None,
        )
        assert result == {"snippet": "TestSnippet"}

    def test_build_container_params_device(self):
        """Test _build_container_params with device."""
        result = self.schedule._build_container_params(
            folder=None,
            snippet=None,
            device="TestDevice",
        )
        assert result == {"device": "TestDevice"}

    def test_build_container_params_multiple(self):
        """Test _build_container_params with multiple containers."""
        result = self.schedule._build_container_params(
            folder="Shared",
            snippet="TestSnippet",
            device=None,
        )
        assert result == {"folder": "Shared", "snippet": "TestSnippet"}

    def test_build_container_params_none(self):
        """Test _build_container_params with no containers."""
        result = self.schedule._build_container_params(
            folder=None,
            snippet=None,
            device=None,
        )
        assert result == {}
