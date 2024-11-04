# tests/scm/config/objects/test_service.py

import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError as PydanticValidationError
from scm.exceptions import ValidationError as SCMValidationError, ValidationError

from scm.config.objects import Service
from scm.models.objects import ServiceCreateModel, ServiceResponseModel
from tests.factories import ServiceFactory


@pytest.mark.usefixtures("load_env")
class TestServiceBase:
    """Base class for Service tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Service(self.mock_scm)  # noqa


class TestServiceAPI(TestServiceBase):
    """Tests for Service API operations."""

    def test_list_services(self):
        """
        Test listing services.

        **Objective:** Test listing all services.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing services.
            2. Calls the `list` method of `self.client` with a filter parameter.
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of services, checking their types and attributes.
        """
        mock_response = {
            "data": [
                {
                    "name": "service-http",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "protocol": {"tcp": {"port": "80,8080"}},
                },
                {
                    "name": "service-https",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "protocol": {"tcp": {"port": "443"}},
                },
                {
                    "id": "5e7600f1-8681-4048-973b-4117da7e446c",
                    "name": "Test",
                    "folder": "Shared",
                    "description": "This is just a test",
                    "protocol": {
                        "tcp": {
                            "port": "4433,4333,4999,9443",
                            "override": {
                                "timeout": 10,
                                "halfclose_timeout": 10,
                                "timewait_timeout": 10,
                            },
                        }
                    },
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        services = self.client.list(folder="Prisma Access")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params={"folder": "Prisma Access"},
        )
        assert isinstance(services, list)
        assert isinstance(services[0], ServiceResponseModel)
        assert len(services) == 3
        assert services[0].name == "service-http"

    def test_create_service(self):
        """
        Test creating a service.

        **Objective:** Test creating a new service.
        **Workflow:**
            1. Creates test data using ServiceFactory.
            2. Mocks the API response.
            3. Calls create method and validates the result.
        """
        test_service = ServiceFactory()
        mock_response = test_service.model_dump()
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_service = self.client.create(
            test_service.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            json=test_service.model_dump(exclude_unset=True),
        )
        assert created_service.name == test_service.name
        assert created_service.description == test_service.description
        assert created_service.protocol == test_service.protocol
        assert created_service.folder == test_service.folder

    def test_get_service(self):
        """
        Test retrieving a service by ID.

        **Objective:** Test fetching a specific service.
        **Workflow:**
            1. Mocks the API response for a specific service.
            2. Calls get method and validates the result.
        """
        service_id = "5e7600f1-8681-4048-973b-4117da7e446c"
        mock_response = {
            "id": service_id,
            "name": "Test",
            "folder": "Shared",
            "description": "This is just a test",
            "protocol": {
                "tcp": {
                    "port": "4433,4333,4999,9443",
                },
            },
            "tag": ["Automation"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        service = self.client.get(service_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/services/{service_id}"
        )
        assert isinstance(service, ServiceResponseModel)
        assert service.name == "Test"
        assert service.protocol.tcp.port == "4433,4333,4999,9443"

    def test_update_service(self):
        """
        Test updating a service.

        **Objective:** Test updating an existing service.
        **Workflow:**
            1. Sets up the update data for the service.
            2. Sets up a mock response that includes the updated data.
            3. Calls the `update` method and verifies payload transformation.
            4. Validates the updated service's attributes.
        """
        from uuid import UUID

        # Test data including ID
        update_data = {
            "id": "5e7600f1-8681-4048-973b-4117da7e446c",
            "name": "UpdatedService",
            "folder": "Shared",
            "description": "An updated service",
            "protocol": {
                "tcp": {
                    "port": "4433,4333,4999,9443",
                }
            },
        }

        # Expected payload should not include the ID
        expected_payload = {
            "name": "UpdatedService",
            "folder": "Shared",
            "description": "An updated service",
            "protocol": {
                "tcp": {
                    "port": "4433,4333,4999,9443",
                }
            },
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_service = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/services/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_service, ServiceResponseModel)
        assert isinstance(updated_service.id, UUID)
        assert str(updated_service.id) == update_data["id"]
        assert updated_service.name == "UpdatedService"
        assert updated_service.description == "An updated service"
        assert updated_service.protocol.tcp.port == "4433,4333,4999,9443"

    def test_fetch_service_success(self):
        """
        **Objective:** Test successful fetch of a service.
        **Workflow:**
            1. Mocks API response for a successful fetch
            2. Verifies correct parameter handling
            3. Validates response transformation
        """

        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "web-browsing",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80,443"}},
            "description": None,  # Should be excluded in the result
            "tag": ["web"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="web-browsing", folder="Shared")

        # Verify API call
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params={"folder": "Shared", "name": "web-browsing"},
        )

        # Verify result
        assert isinstance(result, dict)
        assert "id" in result
        assert result["name"] == "web-browsing"
        assert result["protocol"]["tcp"]["port"] == "80,443"
        assert "description" not in result  # None values should be excluded
        assert result["tag"] == ["web"]

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
            self.client.fetch(name="test-service")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(
                name="test-service", folder="Shared", snippet="TestSnippet"
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test all containers provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(
                name="test-service",
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
            "name": "TestService",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80"}},
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with mixed allowed and excluded filters
        result = self.client.fetch(
            name="TestService",
            folder="Shared",
            custom_filter="value",  # Should be included
            types=["type1"],  # Should be excluded
            values=["value1"],  # Should be excluded
            names=["name1"],  # Should be excluded
            tags=["tag1"],  # Should be excluded
        )

        # Verify only allowed filters were passed
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params={
                "folder": "Shared",
                "name": "TestService",
                "custom_filter": "value",
            },
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
            "name": "TestService",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80", "override": None}},  # Should be excluded
            "description": None,  # Should be excluded
            "tag": None,  # Should be excluded
            "snippet": None,  # Should be excluded
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="TestService", folder="Shared")

        # Verify None values are excluded
        assert "description" not in result
        assert "tag" not in result
        assert "snippet" not in result
        assert "override" not in result["protocol"]["tcp"]

        # Verify required fields are present
        assert "id" in result
        assert "name" in result
        assert "protocol" in result
        assert result["protocol"]["tcp"]["port"] == "80"

    def test_fetch_with_different_containers(self):
        """
        **Objective:** Test fetch with different container types.
        **Workflow:**
            1. Tests fetch with folder, snippet, and device containers
            2. Verifies correct parameter handling for each
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestService",
            "protocol": {"tcp": {"port": "80"}},
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with folder
        self.client.fetch(name="TestService", folder="Shared")
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/services",
            params={"folder": "Shared", "name": "TestService"},
        )

        # Test with snippet
        self.client.fetch(name="TestService", snippet="TestSnippet")
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/services",
            params={"snippet": "TestSnippet", "name": "TestService"},
        )

        # Test with device
        self.client.fetch(name="TestService", device="TestDevice")
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/services",
            params={"device": "TestDevice", "name": "TestService"},
        )

    def test_fetch_udp_protocol(self):
        """
        **Objective:** Test fetch of a service with UDP protocol.
        **Workflow:**
            1. Tests fetch of a UDP service
            2. Verifies protocol structure handling
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "dns-service",
            "folder": "Shared",
            "protocol": {
                "udp": {
                    "port": "53",
                }
            },
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="dns-service", folder="Shared")

        assert result["protocol"]["udp"]["port"] == "53"
        assert "tcp" not in result["protocol"]


class TestServiceValidation(TestServiceBase):
    """Tests for Service validation."""

    def test_service_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(SCMValidationError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_service_request_model_invalid_uuid(self):
        """Test UUID validation in ServiceResponseModel."""
        invalid_data = {
            "id": "invalid-uuid",
            "name": "TestService",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80"}},
        }
        with pytest.raises(ValueError) as exc_info:
            ServiceResponseModel(**invalid_data)
        assert "1 validation error for ServiceResponseModel" in str(exc_info.value)
        assert "Input should be a valid UUID, invalid character" in str(exc_info.value)

    def test_service_request_model_no_protocol_provided(self):
        """Test validation when no protocol is provided."""
        data = {
            "name": "TestService",
            "folder": "Shared",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert "Field required" in str(exc_info.value)

    def test_service_request_model_multiple_protocols_provided(self):
        """Test validation when multiple protocols are provided."""
        data = {
            "name": "TestService",
            "folder": "Shared",
            "protocol": {
                "tcp": {"port": "80"},
                "udp": {"port": "53"},
            },
        }
        with pytest.raises(ValueError) as exc_info:
            ServiceCreateModel(**data)
        assert "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'." in str(
            exc_info.value
        )

    def test_service_request_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "TestService",
            "protocol": {"tcp": {"port": "80"}},
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_service_request_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "TestService",
            "protocol": {"tcp": {"port": "80"}},
            "folder": "Shared",
            "snippet": "TestSnippet",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_service_request_model_with_device_container(self):
        """Test service creation with device container."""
        data = {
            "name": "TestService",
            "protocol": {"tcp": {"port": "80"}},
            "device": "Device1",
        }
        model = ServiceCreateModel(**data)
        assert model.device == "Device1"

    def test_service_request_model_multiple_containers_with_device(self):
        """Test validation when multiple containers including device are provided."""
        data = {
            "name": "TestService",
            "protocol": {"tcp": {"port": "80"}},
            "folder": "Shared",
            "device": "Device1",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestServiceFilters(TestServiceBase):
    """Tests for Service filtering functionality."""

    def test_service_list_with_filters(self):
        """Test listing services with filters."""
        mock_response = {
            "data": [
                {
                    "name": "service-http",
                    "folder": "Shared",
                    "protocol": {"tcp": {"port": "80,8080"}},
                },
                {
                    "name": "service-https",
                    "folder": "Shared",
                    "protocol": {"tcp": {"port": "443"}},
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {
            "folder": "Shared",
            "names": ["service-http", "service-https"],
            "tags": ["Tag1", "Tag2"],
        }
        services = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "name": "service-http,service-https",
            "tag": "Tag1,Tag2",
        }
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params=expected_params,
        )
        assert len(services) == 2


class TestSuite(
    TestServiceAPI,
    TestServiceValidation,
    TestServiceFilters,
):
    """Main test suite that combines all test classes."""

    pass
