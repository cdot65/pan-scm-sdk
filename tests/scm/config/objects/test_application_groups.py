import pytest
from unittest.mock import MagicMock
from scm.config.objects import ApplicationGroup
from scm.exceptions import ValidationError
from scm.models.objects import (
    ApplicationGroupResponseModel,
    ApplicationGroupRequestModel,
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
            1. Prepares update data and mocks response.
            2. Verifies the update request and response.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = {
            "name": "TestAppGroup",
            "folder": "Prisma Access",
            "members": [
                "office365-consumer-access",
                "office365-enterprise-access",
                "test123",
            ],
        }
        mock_response = {"id": object_id, **update_data}

        self.mock_scm.put.return_value = mock_response  # noqa
        updated_group = self.client.update(object_id, update_data)  # noqa

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/application-groups/{object_id}",
            json=update_data,
        )
        assert isinstance(updated_group, ApplicationGroupResponseModel)
        assert updated_group.name == "TestAppGroup"
        assert "test123" in updated_group.members


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
            ApplicationGroupRequestModel(**data)
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
            ApplicationGroupRequestModel(**data)
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
        assert "Invalid UUID format for 'id'" in str(exc_info.value)

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


class TestSuite(TestApplicationGroupAPI, TestApplicationGroupValidation):
    """Main test suite that combines all test classes."""

    pass
