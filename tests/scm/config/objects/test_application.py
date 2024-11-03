# tests/scm/config/objects/test_application.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import Application
from scm.exceptions import ValidationError
from scm.models.objects import ApplicationResponseModel, ApplicationCreateModel
from tests.factories import ApplicationFactory

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestApplicationBase:
    """Base class for Application tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Application(self.mock_scm)  # noqa


class TestApplicationAPI(TestApplicationBase):
    """Tests for Application API operations."""

    def test_list_applications(self):
        """
        Test listing applications.

        **Objective:** Test listing all applications.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing applications.
            2. Calls the `list` method of `self.client` with a filter parameter.
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of applications, checking their types and attributes.
        """
        mock_response = {
            "data": [
                {
                    "name": "100bao",
                    "description": "100bao is a free Chinese P2P file-sharing program",
                    "ports": ["tcp/3468,6346,11300"],
                    "category": "general-internet",
                    "subcategory": "file-sharing",
                    "technology": "peer-to-peer",
                    "risk": 5,
                    "evasive": True,
                    "pervasive": True,
                    "folder": "All",
                    "snippet": "predefined-snippet",
                },
                {
                    "name": "104apci-supervisory",
                    "container": "iec-60870-5-104",
                    "description": "IEC 60870-5-104 protocol",
                    "ports": ["tcp/2404"],
                    "category": "business-systems",
                    "subcategory": "ics-protocols",
                    "technology": "client-server",
                    "risk": 2,
                    "folder": "All",
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        applications = self.client.list(folder="MainFolder")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications", params={"folder": "MainFolder"}
        )
        assert isinstance(applications, list)
        assert isinstance(applications[0], ApplicationResponseModel)
        assert len(applications) == 2
        assert applications[0].name == "100bao"
        assert applications[0].ports == ["tcp/3468,6346,11300"]

    def test_create_application(self):
        """
        Test creating an application.

        **Objective:** Test creating a new application.
        **Workflow:**
            1. Creates test data using ApplicationFactory.
            2. Mocks the API response.
            3. Calls create method and validates the result.
        """
        test_application = ApplicationFactory()
        mock_response = test_application.model_dump()
        mock_response["name"] = "ValidApplication"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_app = self.client.create(
            test_application.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            json=test_application.model_dump(exclude_unset=True),
        )
        assert created_app.name == test_application.name
        assert created_app.description == test_application.description
        assert created_app.category == test_application.category

    def test_get_application(self):
        """
        Test retrieving an application by name.

        **Objective:** Test fetching a specific application.
        **Workflow:**
            1. Mocks the API response for a specific application.
            2. Calls get method and validates the result.
        """
        mock_response = {
            "name": "TestApp",
            "folder": "Shared",
            "description": "A test application",
            "category": "networking",
            "subcategory": "networking",
            "technology": "client-server",
            "risk": 2,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        app_name = "TestApp"
        application = self.client.get(app_name)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/applications/{app_name}"
        )
        assert isinstance(application, ApplicationResponseModel)
        assert application.name == "TestApp"
        assert application.category == "networking"

    def test_update_with_invalid_data(self):
        """
        **Objective:** Test update method with invalid data structure.
        **Workflow:**
            1. Attempts to update with invalid data
            2. Verifies proper validation error handling
        """
        invalid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "invalid_field": "test",
        }

        with pytest.raises(PydanticValidationError):
            self.client.update(invalid_data)

    def test_fetch_empty_name(self):
        """
        **Objective:** Test fetch method with empty name parameter.
        **Workflow:**
            1. Attempts to fetch with empty name
            2. Verifies ValidationError is raised
        """
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="", folder="Shared")
        assert "Parameter 'name' must be provided for fetch method." in str(
            exc_info.value
        )

    def test_fetch_container_validation(self):
        """
        **Objective:** Test container parameter validation in fetch method.
        **Workflow:**
            1. Tests various invalid container combinations
            2. Verifies proper error handling
        """
        # Test no container
        with pytest.raises(ValidationError):
            self.client.fetch(name="test")

        # Test multiple containers
        with pytest.raises(ValidationError):
            self.client.fetch(name="test", folder="Shared", snippet="TestSnippet")

        # Test with device container
        with pytest.raises(ValidationError):
            self.client.fetch(name="test", folder="Shared", device="device1")

    def test_fetch_response_handling(self):
        """
        **Objective:** Test fetch method's response handling.
        **Workflow:**
            1. Tests various response scenarios
            2. Verifies proper response transformation
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestApp",
            "folder": "Shared",
            "description": None,  # Should be excluded
            "category": "networking",
            "subcategory": "web",
            "technology": "client-server",
            "risk": 2,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="TestApp", folder="Shared")

        # Verify None values are excluded
        assert "description" not in result
        assert result["name"] == mock_response["name"]
        assert result["folder"] == mock_response["folder"]

    def test_payload_construction(self):
        """
        **Objective:** Test payload construction using model_dump (line 50)
        **Workflow:**
            1. Tests that unset values are properly excluded
            2. Verifies the payload matches expected structure
        """
        test_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedApp",
            "folder": "Shared",
            "members": ["app1", "app2"],
            "undefined_field": None,  # Should be excluded
            "category": "networking",
            "subcategory": "web",
            "technology": "client-server",
            "risk": 2,
        }

        # Mock response to prevent actual API call
        mock_response = {
            "id": test_data["id"],
            "name": test_data["name"],
            "folder": test_data["folder"],
            "members": test_data["members"],
            "category": test_data["category"],
            "subcategory": test_data["subcategory"],
            "technology": test_data["technology"],
            "risk": test_data["risk"],
        }
        self.mock_scm.put.return_value = mock_response  # noqa

        # Call update method
        self.client.update(test_data)

        # Verify the payload sent to put() has excluded None values
        actual_payload = self.mock_scm.put.call_args[1]["json"]  # noqa
        expected_payload = {
            "name": "UpdatedApp",
            "folder": "Shared",
            "category": "networking",
            "subcategory": "web",
            "technology": "client-server",
            "risk": 2,
        }
        assert actual_payload == expected_payload
        assert "description" not in actual_payload
        assert "undefined_field" not in actual_payload
        assert "id" not in actual_payload  # ID should not be in payload


class TestApplicationValidation(TestApplicationBase):
    """Tests for Application validation."""

    def test_application_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_application_request_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "TestApp",
            "category": "networking",
            "subcategory": "web",
            "technology": "client-server",
            "risk": 3,
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided." in str(
            exc_info.value
        )

    def test_application_request_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "TestApp",
            "category": "networking",
            "subcategory": "web",
            "technology": "client-server",
            "risk": 3,
            "folder": "Shared",
            "snippet": "Snippet1",
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided." in str(
            exc_info.value
        )

    def test_application_model_required_fields(self):
        """Test validation of required fields."""
        # Test missing required fields
        data = {
            "name": "TestApp",
            "folder": "Shared",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert "category" in str(exc_info.value)
        assert "technology" in str(exc_info.value)


class TestApplicationFilters(TestApplicationBase):
    """Tests for Application filtering functionality."""

    def test_application_list_with_types_filter(self):
        """Test listing applications with types filter."""
        mock_response = {
            "data": [
                {
                    "name": "App1",
                    "folder": "Shared",
                    "category": "networking",
                    "subcategory": "web",
                    "technology": "client-server",
                    "risk": 10,  # Invalid risk level
                    "type": "web",
                },
                {
                    "name": "App2",
                    "folder": "Shared",
                    "category": "database",
                    "subcategory": "web",
                    "technology": "client-server",
                    "risk": 10,  # Invalid risk level
                    "type": "database",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {
            "folder": "Shared",
            "types": ["web", "database"],
        }
        applications = self.client.list(**filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={"folder": "Shared", "type": "web,database"},
        )
        assert len(applications) == 2

    def test_application_list_with_values_filter(self):
        """Test listing applications with values filter."""
        mock_response = {
            "data": [
                {
                    "name": "App1",
                    "folder": "Shared",
                    "ports": ["80"],
                    "category": "web",
                    "subcategory": "web",
                    "technology": "client-server",
                    "risk": 10,  # Invalid risk level
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {
            "folder": "Shared",
            "values": ["80"],
        }
        applications = self.client.list(**filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/applications",
            params={"folder": "Shared", "value": "80"},
        )
        assert len(applications) == 1


class TestSuite(
    TestApplicationAPI,
    TestApplicationValidation,
    TestApplicationFilters,
):
    """Main test suite that combines all test classes."""

    pass
