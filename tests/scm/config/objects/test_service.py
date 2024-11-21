# tests/scm/config/objects/test_service.py

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError as PydanticValidationError

from scm.config.objects import Service
from scm.exceptions import (
    APIError,
    BadRequestError,
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
)
from scm.models.objects import (
    ServiceCreateModel,
    ServiceResponseModel,
)
from tests.factories import (
    ServiceResponseFactory,
    ServiceCreateApiFactory,
    ServiceUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


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


# -------------------- Test Classes Grouped by Functionality --------------------


class TestServiceList(TestServiceBase):
    """Tests for listing Service objects."""

    def test_list_objects(self):
        """
        **Objective:** Test listing all objects using factories.
        """
        mock_response = {
            "data": [
                ServiceResponseFactory.with_tcp(
                    name="service-http",
                    folder="All",
                    snippet="predefined-snippet",
                    protocol={"tcp": {"port": "80,8080"}},
                ).model_dump(),
                ServiceResponseFactory.with_tcp(
                    name="service-https",
                    folder="All",
                    snippet="predefined-snippet",
                    protocol={"tcp": {"port": "443"}},
                ).model_dump(),
                ServiceResponseFactory.with_tcp(
                    id="5e7600f1-8681-4048-973b-4117da7e446c",
                    name="Test",
                    folder="Shared",
                    description="This is just a test",
                    protocol={
                        "tcp": {
                            "port": "4433,4333,4999,9443",
                            "override": {
                                "timeout": 10,
                                "halfclose_timeout": 10,
                                "timewait_timeout": 10,
                            },
                        }
                    },
                ).model_dump(),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Prisma Access")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params={
                "limit": 10000,
                "folder": "Prisma Access",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], ServiceResponseModel)
        assert len(existing_objects) == 3
        assert existing_objects[0].name == "service-http"


class TestServiceCreate(TestServiceBase):
    """Tests for creating Service objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new object using factories.
        """
        test_object = ServiceCreateApiFactory.with_tcp()
        mock_response = ServiceResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert created_object.name == test_object.name
        assert created_object.description == test_object.description
        assert created_object.protocol == test_object.protocol
        assert created_object.folder == test_object.folder

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        """
        test_data = ServiceCreateApiFactory.with_tcp()

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Object creation failed",
            error_type="Object Already Exists",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data.model_dump())

        error = exc_info.value
        assert error.error_code == "API_I00013"
        assert "Object creation failed" in str(error)

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        """
        test_data = ServiceCreateApiFactory.with_tcp()

        # Mock a generic exception without response
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data.model_dump())
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"

    def test_create_malformed_response_handling(self):
        """
        **Objective:** Test handling of malformed response in create method.
        """
        test_data = ServiceCreateApiFactory.with_tcp()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data.model_dump())
        assert "Invalid response format" in str(exc_info.value)


class TestServiceGet(TestServiceBase):
    """Tests for retrieving a specific Service object."""

    def test_get_object(self):
        """
        **Objective:** Test retrieving a specific object using factories.
        """
        object_id = "5e7600f1-8681-4048-973b-4117da7e446c"
        mock_response = ServiceResponseFactory.with_tcp(
            id=object_id,
            name="Test",
            folder="Shared",
            description="This is just a test",
            protocol={
                "tcp": {
                    "port": "4433,4333,4999,9443",
                }
            },
            tag=["Automation"],
        ).model_dump()

        self.mock_scm.get.return_value = mock_response  # noqa
        get_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/services/{object_id}"
        )
        assert isinstance(get_object, ServiceResponseModel)
        assert get_object.name == "Test"
        assert get_object.protocol.tcp.port == "4433,4333,4999,9443"

    def test_get_object_error_handling(self):
        """
        **Objective:** Test error handling during object retrieval.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.get(object_id)

        error = exc_info.value
        assert error.error_code == "API_I00013"
        assert "Object not found" in str(error)

    def test_get_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in get method.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.get(object_id)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestServiceUpdate(TestServiceBase):
    """Tests for updating Service objects."""

    def test_update_object(self):
        """
        **Objective:** Test updating an object using factories.
        """

        update_data = ServiceUpdateApiFactory.with_tcp(
            id="5e7600f1-8681-4048-973b-4117da7e446c",
            name="UpdatedService",
            folder="Shared",
            description="An updated service",
            protocol={"tcp": {"port": "4433,4333,4999,9443"}},
        )

        expected_payload = update_data.model_dump(exclude={"id"})

        mock_response = ServiceResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        # Perform update
        updated_object = self.client.update(update_data.model_dump())

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/services/{update_data.id}",
            json=expected_payload,
        )

        # Verify response model
        assert isinstance(updated_object, ServiceResponseModel)
        assert str(updated_object.id) == update_data.id
        assert updated_object.name == "UpdatedService"
        assert updated_object.description == "An updated service"
        assert updated_object.protocol.tcp.port == "4433,4333,4999,9443"

    def test_update_object_error_handling(self):
        """
        **Objective:** Test error handling during object update.
        """
        update_data = ServiceUpdateApiFactory.with_tcp(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-service",
            folder="Shared",
            protocol={"tcp": {"port": "80"}},
        )

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.update(update_data.model_dump())

        error = exc_info.value
        assert error.error_code == "API_I00013"
        assert "Update failed" in str(error)

    def test_update_with_invalid_data(self):
        """
        **Objective:** Test update method with invalid data structure.
        """
        invalid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "invalid_field": "test",
        }

        with pytest.raises(APIError):
            self.client.update(invalid_data)

    def test_update_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in update method.
        """
        update_data = ServiceUpdateApiFactory.with_tcp(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-service",
            folder="Shared",
            protocol={"tcp": {"port": "80"}},
        )

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.update(update_data.model_dump())
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestServiceDelete(TestServiceBase):
    """Tests for deleting Service objects."""

    def test_delete_referenced_object(self):
        """
        **Objective:** Test deleting an application that is referenced by another group.
        """
        application_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        # Configure mock to raise HTTPError with our custom error response
        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Your configuration is not valid. Please review the error message for more details.",
            error_type="Reference Not Zero",
        )

        # Attempt to delete the application and expect ConflictError
        with pytest.raises(APIError) as exc_info:
            self.client.delete(application_id)

        error = exc_info.value

        # Verify the error contains the expected information
        assert error.error_code == "API_I00013"
        assert "Your configuration is not valid" in str(error)

    def test_delete_error_handling(self):
        """
        **Objective:** Test error handling during object deletion.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.delete(object_id)

    def test_delete_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in delete method.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.delete(object_id)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestServiceFetch(TestServiceBase):
    """Tests for fetching Service objects by name."""

    def test_fetch_object(self):
        """
        **Objective:** Test successful fetch of an object using factories.
        """
        mock_response = ServiceResponseFactory.with_tcp(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="web-browsing",
            folder="Shared",
            protocol={"tcp": {"port": "80,443"}},
            description=None,
            tag=["web"],
        ).model_dump(exclude_unset=True)

        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(name="web-browsing", folder="Shared")

        # Verify API call
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params={
                "folder": "Shared",
                "name": "web-browsing",
            },
        )

        # Verify result
        assert isinstance(result, dict)
        assert "id" in result
        assert result["name"] == "web-browsing"
        assert result["protocol"]["tcp"]["port"] == "80,443"
        assert "description" not in result  # None values should be excluded
        assert result["tag"] == ["web"]

    def test_fetch_object_not_found(self):
        """
        **Objective:** Test that fetching a non-existent object raises NotFoundError.
        """
        service_name = "NonExistent"
        folder_name = "Shared"

        # Configure mock to raise HTTPError with the mock response
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Your configuration is not valid. Please review the error message for more details.",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.fetch(name=service_name, folder=folder_name)

    def test_fetch_empty_name(self):
        """
        **Objective:** Test fetch with empty name parameter.
        **Workflow:**
            1. Attempts to fetch with empty name
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")
        assert "Field 'name' cannot be empty" in str(exc_info.value)

    def test_fetch_container_validation(self):
        """
        **Objective:** Test container parameter validation in fetch.
        **Workflow:**
            1. Tests various invalid container combinations
            2. Verifies proper error handling
        """
        # Test empty folder
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test no container
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-service")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-service", folder="Shared", snippet="TestSnippet"
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_fetch_response_handling(self):
        """
        **Objective:** Test fetch method's response handling using factories.
        """
        mock_response = ServiceResponseFactory.with_tcp(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestService",
            folder="Shared",
            protocol={"tcp": {"port": "80", "override": None}},
            description=None,
            tag=None,
            snippet=None,
        ).model_dump(exclude_unset=True)

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

    def test_fetch_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in fetch method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"

    def test_fetch_unexpected_response_format(self):
        """
        **Objective:** Ensure that the fetch method raises APIError when the response format is not as expected.
        """
        service_name = "TestService"
        folder_name = "Shared"

        # Mocking an unexpected response format
        self.mock_scm.get.return_value = {"unexpected_key": "unexpected_value"}  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name=service_name, folder=folder_name)
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

    def test_fetch_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in fetch method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response without expected fields
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

        # Test response with both id and data fields (invalid format)
        self.mock_scm.get.return_value = {  # noqa
            "id": "some-id",
            "data": [{"some": "data"}],
        }  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "An unexpected error occurred: 3 validation errors" in str(
            exc_info.value
        )

        # Test malformed response in list format
        self.mock_scm.get.return_value = [{"unexpected": "format"}]  # noqa
        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

    def test_fetch_error_handler_json_error(self):
        """
        **Objective:** Test fetch method error handling when json() raises an error.
        **Workflow:**
            1. Mocks an exception with a response that raises error on json()
            2. Verifies the original exception is re-raised
        """

        class MockResponse:
            @property
            def response(self):
                return self

            def json(self):
                raise ValueError("Original error")

        # Create mock exception with our special response
        mock_exception = Exception("Original error")
        mock_exception.response = MockResponse()

        # Configure mock to raise our custom exception
        self.mock_scm.get.side_effect = mock_exception  # noqa

        # The original exception should be raised since json() failed
        with pytest.raises(ValueError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Original error" in str(exc_info.value)


class TestServiceValidation(TestServiceBase):
    """Tests for Service validation."""

    def test_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_request_model_no_protocol_provided(self):
        """Test validation when no protocol is provided."""
        data = ServiceCreateApiFactory.build_without_protocol()
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert "Field required" in str(exc_info.value)

    def test_request_model_multiple_protocols_provided(self):
        """Test validation when multiple protocols are provided."""
        data = ServiceCreateApiFactory.build_with_multiple_protocols()
        with pytest.raises(ValueError) as exc_info:
            ServiceCreateModel(**data)
        assert "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'." in str(
            exc_info.value
        )

    def test_request_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = ServiceCreateApiFactory.build_with_no_containers()
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_request_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = ServiceCreateApiFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            ServiceCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_response_model_invalid_uuid(self):
        """Test validation of UUID format in response model."""
        invalid_data = {
            "id": "invalid-uuid",
            "name": "TestService",
            "folder": "Shared",
            "protocol": {"tcp": {"port": "80"}},
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            ServiceResponseModel(**invalid_data)
        assert "1 validation error for ServiceResponseModel" in str(exc_info.value)
        assert "Input should be a valid UUID, invalid character" in str(exc_info.value)


class TestServiceListFilters(TestServiceBase):
    """Tests for filtering during listing Service objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
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
            "folder": "Shared",  # Added this
            "protocols": ["tcp", "udp"],
            "tags": ["Tag1", "Tag2"],
        }
        filtered_objects = self.client.list(**filters)

        expected_params = {
            "limit": 10000,
            "folder": "Shared",
        }
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/services",
            params=expected_params,
        )
        assert len(filtered_objects) == 2

    def test_list_filters_protocol_validation(self):
        """
        **Objective:** Test validation of filter protocol in list method.
        """
        mock_response = {
            "data": [
                ServiceResponseFactory.with_tcp(
                    name="service-http",
                    folder="All",
                    snippet="predefined-snippet",
                    protocol={"tcp": {"port": "80,8080"}},
                ).model_dump(),
                ServiceResponseFactory.with_tcp(
                    name="service-https",
                    folder="All",
                    snippet="predefined-snippet",
                    protocol={"tcp": {"port": "443"}},
                ).model_dump(),
                ServiceResponseFactory.with_tcp(
                    id="7242be61-ba51-4862-95b1-b24b20acf9b4",
                    name="web-service",
                    folder="Texas",
                    description="Web service for HTTP/HTTPS",
                    protocol={
                        "tcp": {
                            "port": "80,443",
                            "override": {
                                "timeout": 60,
                                "halfclose_timeout": 30,
                            },
                        }
                    },
                    tag=["Automation"],
                ).model_dump(),
                ServiceResponseFactory.with_udp(
                    id="28832824-2775-4eb7-bd38-ca70ad6d9ba5",
                    name="dns-service",
                    folder="Texas",
                    description="DNS service",
                    protocol={"udp": {"port": "53"}},
                ).model_dump(),
            ],
            "offset": 0,
            "total": 4,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid protocol filter (string instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", protocol="tcp")
        assert str(exc_info.value) == "'protocol' filter must be a list"

        # Test invalid protocol filter (dict instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", protocol={"value": "tcp"})
        assert str(exc_info.value) == "'protocol' filter must be a list"

        # Test invalid tag filter (string instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", tag="database")
        assert str(exc_info.value) == "'tag' filter must be a list"

        # Test invalid tag filter (dict instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", tag={"value": "database"})
        assert str(exc_info.value) == "'tag' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                tag=["database"],
            )
        except BadRequestError:
            pytest.fail("Unexpected BadRequestError raised with valid list filters")

    def test_list_protocol_filtering(self):
        """
        **Objective:** Test filtering objects by protocol type.
        """
        mock_response = {
            "data": [
                ServiceResponseFactory.with_tcp(
                    id="123e4567-e89b-12d3-a456-426655440000",
                    name="http-service",
                    folder="Shared",
                    protocol={"tcp": {"port": "80,8080"}},
                ).model_dump(),
                ServiceResponseFactory.with_udp(
                    id="123e4567-e89b-12d3-a456-426655440001",
                    name="dns-service",
                    folder="Shared",
                    protocol={"udp": {"port": "53"}},
                ).model_dump(),
                ServiceResponseFactory.with_tcp(
                    id="123e4567-e89b-12d3-a456-426655440002",
                    name="https-service",
                    folder="Shared",
                    protocol={"tcp": {"port": "443"}},
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test TCP protocol filter
        tcp_objects = self.client.list(folder="Shared", protocol=["tcp"])
        assert len(tcp_objects) == 2
        assert all(svc.protocol.tcp is not None for svc in tcp_objects)
        assert all(svc.name in ["http-service", "https-service"] for svc in tcp_objects)

        # Test UDP protocol filter
        udp_objects = self.client.list(folder="Shared", protocol=["udp"])
        assert len(udp_objects) == 1
        assert all(svc.protocol.udp is not None for svc in udp_objects)
        assert udp_objects[0].name == "dns-service"

        # Test multiple protocol filter
        all_objects = self.client.list(folder="Shared", protocol=["tcp", "udp"])
        assert len(all_objects) == 3
        assert any(svc.protocol.tcp is not None for svc in all_objects)
        assert any(svc.protocol.udp is not None for svc in all_objects)

        # Verify API was called correctly
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/objects/v1/services",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )

    def test_list_empty_folder_error(self):
        """
        **Objective:** Test that empty folder raises appropriate error.
        **Workflow:**
            1. Attempts to list objects with empty folder
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

    def test_list_multiple_containers_error(self):
        """
        **Objective:** Test validation of container parameters.
        **Workflow:**
            1. Attempts to list with multiple containers
            2. Verifies InvalidObjectError is raised
        """
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_list_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in list method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response
        self.mock_scm.get.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(APIError):
            self.client.list(folder="Shared")

        # Test invalid data format
        self.mock_scm.get.return_value = {"data": "not-a-list"}  # noqa

        with pytest.raises(APIError):
            self.client.list(folder="Shared")

    def test_list_non_dict_response(self):
        """
        **Objective:** Test list method handling of non-dictionary response.
        **Workflow:**
            1. Mocks a non-dictionary response from the API
            2. Verifies that APIError is raised with correct message
            3. Tests different non-dict response types
        """
        # Test with list response
        self.mock_scm.get.return_value = ["not", "a", "dict"]  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with string response
        self.mock_scm.get.return_value = "string response"  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with None response
        self.mock_scm.get.return_value = None  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

    def test_list_error_handling(self):
        """
        **Objective:** Test error handling in list operation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to list objects
            3. Verifies proper error handling
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Listing failed",
                    "details": {"errorType": "Operation Impossible"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.get.side_effect = Exception()  # noqa
        self.mock_scm.get.side_effect.response = MagicMock()  # noqa
        self.mock_scm.get.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="NonexistentFolder")
        assert str(exc_info.value) == "An unexpected error occurred"

    def test_list_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in list method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert str(exc_info.value) == "An unexpected error occurred"


# -------------------- End of Test Classes --------------------
