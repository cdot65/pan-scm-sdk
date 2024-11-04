# tests/scm/config/objects/test_application_group.py

import pytest
from unittest.mock import MagicMock
from scm.config.objects import ApplicationGroup
from scm.exceptions import ValidationError
from scm.models.objects import (
    ApplicationGroupResponseModel,
    ApplicationGroupCreateModel,
)
from tests.factories import ApplicationGroupFactory


@pytest.mark.usefixtures("load_env")
class TestApplicationGroupBase:
    """Base class for Application Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = ApplicationGroup(self.mock_scm)  # noqa


class TestApplicationGroupAPI(TestApplicationGroupBase):
    """Tests for Application Group API operations."""

    def test_list_application_groups(self):
        """
        **Objective:** Test listing all application groups.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing application groups.
            2. Calls the `list` method with a filter parameter.
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of application groups.
        """
        mock_response = {
            "data": [
                {
                    "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
                    "name": "Microsoft 365 Access",
                    "folder": "Shared",
                    "snippet": "office365",
                    "members": [
                        "office365-consumer-access",
                        "office365-enterprise-access",
                    ],
                },
                {
                    "id": "0b12a889-4220-4cdd-b95f-506e0351a5e4",
                    "name": "Microsoft 365 Services",
                    "folder": "Shared",
                    "snippet": "office365",
                    "members": [
                        "ms-office365",
                        "ms-onedrive",
                        "ms-onenote",
                        "ms-lync-base",
                        "skype",
                    ],
                },
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        application_groups = self.client.list(folder="Prisma Access")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/application-groups", params={"folder": "Prisma Access"}
        )
        assert isinstance(application_groups, list)
        assert isinstance(application_groups[0], ApplicationGroupResponseModel)
        assert len(application_groups) == 2
        assert application_groups[0].name == "Microsoft 365 Access"
        assert application_groups[0].members == [
            "office365-consumer-access",
            "office365-enterprise-access",
        ]

    def test_create_application_group(self):
        """
        **Objective:** Test creating an application group.
        **Workflow:**
            1. Uses ApplicationGroupFactory to create test data.
            2. Mocks the API response.
            3. Verifies the creation request and response.
        """
        test_application_group = ApplicationGroupFactory()
        mock_response = test_application_group.model_dump()
        mock_response["name"] = "ValidStaticApplicationGroup"
        mock_response["id"] = "0b12a889-4220-4cdd-b95f-506e0351a5e4"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_application_group.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/application-groups",
            json=test_application_group.model_dump(exclude_unset=True),
        )
        assert created_group.name == test_application_group.name
        assert created_group.members == test_application_group.members
        assert created_group.folder == test_application_group.folder

    def test_get_application_group(self):
        """
        **Objective:** Test retrieving a specific application group.
        **Workflow:**
            1. Mocks the API response for a specific group.
            2. Verifies the get request and response handling.
        """
        mock_response = {
            "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
            "name": "TestAppGroup",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        app_group_name = "TestAppGroup"
        application = self.client.get(app_group_name)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/application-groups/{app_group_name}"
        )
        assert isinstance(application, ApplicationGroupResponseModel)
        assert application.name == "TestAppGroup"
        assert application.members == [
            "office365-consumer-access",
            "office365-enterprise-access",
        ]

    def test_update_application_group(self):
        """
        **Objective:** Test updating an application group.
        **Workflow:**
            1. Prepares update data and mocks response
            2. Verifies the update request and response
            3. Ensures payload transformation is correct
        """
        from uuid import UUID

        test_uuid = UUID("123e4567-e89b-12d3-a456-426655440000")

        # Test data including ID
        update_data = {
            "id": str(test_uuid),  # Use string for input data as it would come from API
            "name": "TestAppGroup",
            "folder": "Prisma Access",
            "members": [
                "office365-consumer-access",
                "office365-enterprise-access",
                "test123",
            ],
        }

        # Expected payload should not include the ID
        expected_payload = {
            "name": "TestAppGroup",
            "folder": "Prisma Access",
            "members": [
                "office365-consumer-access",
                "office365-enterprise-access",
                "test123",
            ],
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_group = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/application-groups/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_group, ApplicationGroupResponseModel)
        assert isinstance(updated_group.id, UUID)  # Verify it's a UUID object
        assert updated_group.id == test_uuid  # Compare against UUID object
        assert (
            str(updated_group.id) == update_data["id"]
        )  # Compare string representations
        assert updated_group.name == "TestAppGroup"
        assert "test123" in updated_group.members
        assert updated_group.folder == "Prisma Access"


class TestApplicationGroupValidation(TestApplicationGroupBase):
    """Tests for Application Group validation logic."""

    def test_list_validation_error(self):
        """Test validation when multiple containers are provided."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_request_model_no_container(self):
        """Test validation when no container is provided."""
        data = {
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_request_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "Microsoft 365 Access",
            "folder": "Shared",
            "snippet": "office365",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_response_model_invalid_uuid(self):
        """Test validation of UUID format in response model."""
        invalid_data = {
            "id": "invalid-uuid",
            "name": "TestAppGroup",
            "members": ["app1", "app2"],
            "folder": "Shared",
        }
        with pytest.raises(ValueError) as exc_info:
            ApplicationGroupResponseModel(**invalid_data)
        assert "1 validation error for ApplicationGroupResponseModel" in str(
            exc_info.value
        )
        assert "Input should be a valid UUID, invalid character" in str(exc_info.value)

    def test_list_with_filters(self):
        """
        **Objective:** Test list operation with various filters.
        **Workflow:**
            1. Tests different filter combinations
            2. Verifies correct parameter handling
        """
        mock_response = {"data": [], "total": 0, "offset": 0, "limit": 200}
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with name filter
        filters = {
            "folder": "Shared",
            "names": ["app1", "app2"],
        }
        self.client.list(**filters)
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/application-groups",
            params={"folder": "Shared", "name": "app1,app2"},
        )

        # Test with types filter
        filters = {
            "folder": "Shared",
            "types": ["members", "names"],
        }
        self.client.list(**filters)
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/application-groups",
            params={"folder": "Shared", "types": ["members", "names"]},
        )


class TestApplicationGroupFetch(TestApplicationGroupBase):
    """Tests for Application Group fetch method."""

    def test_fetch_application_group_success(self):
        """
        **Objective:** Test successful fetch of an application group.
        **Workflow:**
            1. Mocks API response for a successful fetch
            2. Verifies correct parameter handling
            3. Validates response transformation
        """

        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "Microsoft Office",
            "folder": "Shared",
            "members": ["office365", "ms-office"],
            "description": None,  # Should be excluded in the result
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="Microsoft Office", folder="Shared")

        # Verify API call
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/application-groups",
            params={"folder": "Shared", "name": "Microsoft Office"},
        )

        # Verify result
        assert isinstance(result, dict)
        assert "id" in result
        assert result["name"] == "Microsoft Office"
        assert result["members"] == ["office365", "ms-office"]
        assert "description" not in result  # None values should be excluded

    def test_fetch_empty_name(self):
        """
        **Objective:** Test fetch with empty name parameter.
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
        **Objective:** Test container parameter validation in fetch.
        **Workflow:**
            1. Tests various invalid container combinations
            2. Verifies proper error handling
        """
        # Test no container provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test-group")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test-group", folder="Shared", snippet="TestSnippet")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test all containers provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(
                name="test-group",
                folder="Shared",
                snippet="TestSnippet",
                device="device1",
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_fetch_with_additional_filters(self):
        """
        **Objective:** Test fetch with additional filter parameters.
        **Workflow:**
            1. Tests handling of allowed and excluded filters
            2. Verifies correct parameter passing
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestGroup",
            "folder": "Shared",
            "members": ["app1", "app2"],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with mixed allowed and excluded filters
        result = self.client.fetch(
            name="TestGroup",
            folder="Shared",
            custom_filter="value",  # Should be included
            types=["type1"],  # Should be excluded
            values=["value1"],  # Should be excluded
            names=["name1"],  # Should be excluded
            tags=["tag1"],  # Should be excluded
        )

        # Verify only allowed filters were passed
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/application-groups",
            params={"folder": "Shared", "name": "TestGroup", "custom_filter": "value"},
        )
        assert isinstance(result, dict)

    def test_fetch_response_transformation(self):
        """
        **Objective:** Test response transformation in fetch method.
        **Workflow:**
            1. Tests handling of None values and optional fields
            2. Verifies model transformation and exclusions
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestGroup",
            "folder": "Shared",
            "members": ["app1", "app2"],
            "description": None,  # Should be excluded
            "optional_field": None,  # Should be excluded
            "snippet": None,  # Should be excluded
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="TestGroup", folder="Shared")

        # Verify None values are excluded
        assert "description" not in result
        assert "optional_field" not in result
        assert "snippet" not in result

        # Verify required fields are present
        assert "id" in result
        assert "name" in result
        assert "members" in result
        assert result["members"] == ["app1", "app2"]

    def test_fetch_with_different_containers(self):
        """
        **Objective:** Test fetch with different container types.
        **Workflow:**
            1. Tests fetch with folder, snippet, and device containers
            2. Verifies correct parameter handling for each
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestGroup",
            "members": ["app1", "app2"],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with folder
        self.client.fetch(name="TestGroup", folder="Shared")
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/application-groups",
            params={"folder": "Shared", "name": "TestGroup"},
        )

        # Test with snippet
        self.client.fetch(name="TestGroup", snippet="TestSnippet")
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/application-groups",
            params={"snippet": "TestSnippet", "name": "TestGroup"},
        )

        # Test with device
        self.client.fetch(name="TestGroup", device="TestDevice")
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/application-groups",
            params={"device": "TestDevice", "name": "TestGroup"},
        )


# Update TestSuite to include fetch tests
class TestSuite(
    TestApplicationGroupAPI,
    TestApplicationGroupValidation,
    TestApplicationGroupFetch,
):
    """Main test suite that combines all test classes."""

    pass
