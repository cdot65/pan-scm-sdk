# tests/test_services.py

import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError as PydanticValidationError
from scm.exceptions import ValidationError as SCMValidationError

from scm.config.objects import Service
from scm.models import ServiceRequestModel, ServiceResponseModel
from tests.factories import ServiceFactory


def test_list_services(load_env, mock_scm):
    """
    Test for listing services.
    """
    # Mock the API client's get method to prevent from making real API calls
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
            {
                "id": "5a3d6182-c5f1-4b1e-8ec9-e984ae5247fb",
                "name": "Test123UDP",
                "folder": "Shared",
                "description": "UDP test",
                "protocol": {"udp": {"port": "5444,5432"}},
                "tag": ["Automation"],
            },
        ],
        "offset": 0,
        "total": 4,
        "limit": 200,
    }

    # Configure the mock_scm.get method to return the mock_response
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Service with the mocked Scm
    services_client = Service(mock_scm)

    # Call the list method
    services = services_client.list(folder="Prisma Access")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/services", params={"folder": "Prisma Access"}
    )
    assert isinstance(services, list)
    assert isinstance(services[0], ServiceResponseModel)
    assert len(services) == 4
    assert services[0].name == "service-http"
    assert services[3].id == "5a3d6182-c5f1-4b1e-8ec9-e984ae5247fb"
    assert services[3].name == "Test123UDP"


def test_create_services(load_env, mock_scm):
    # Create a new ServiceRequestModel instance using Factory Boy
    test_service = ServiceFactory()

    # Mock the API client's post method
    mock_response = test_service.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID

    # Configure the mock_scm.post method to return the mock_response
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of Service with the mocked Scm
    service_client = Service(mock_scm)

    # Call the create method
    created_service = service_client.create(test_service.model_dump(exclude_unset=True))

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/objects/v1/services",
        json=test_service.model_dump(exclude_unset=True),
    )
    assert created_service.name == test_service.name
    assert created_service.description == test_service.description
    assert created_service.protocol == test_service.protocol
    assert created_service.folder == test_service.folder


def test_get_service(load_env, mock_scm):
    mock_response = {
        "id": "5e7600f1-8681-4048-973b-4117da7e446c",
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
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Service with the mocked Scm
    service_client = Service(mock_scm)

    # Call the get method
    service_id = "5e7600f1-8681-4048-973b-4117da7e446c"
    service = service_client.get(service_id)

    # Assertions
    mock_scm.get.assert_called_once_with(f"/config/objects/v1/services/{service_id}")
    assert isinstance(service, ServiceResponseModel)
    assert service.id == service_id
    assert service.name == "Test"
    assert service.folder == "Shared"
    assert service.description == "This is just a test"
    assert service.protocol.tcp.port == "4433,4333,4999,9443"
    assert service.tag == ["Automation"]


def test_update_service(load_env, mock_scm):
    # Mock the API client's put method
    mock_response = {
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
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of Service with the mocked Scm
    service_client = Service(mock_scm)

    # Prepare data for update
    service_id = "5e7600f1-8681-4048-973b-4117da7e446c"
    update_data = {
        "name": "UpdatedService",
        "folder": "Shared",
        "description": "An updated service",
        "protocol": {
            "tcp": {
                "port": "4433,4333,4999,9443",
            }
        },
    }

    # Call the update method
    updated_service = service_client.update(service_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/objects/v1/services/{service_id}",
        json=update_data,
    )
    assert isinstance(updated_service, ServiceResponseModel)
    assert updated_service.id == service_id
    assert updated_service.name == "UpdatedService"
    assert updated_service.folder == "Shared"
    assert updated_service.description == "An updated service"


def test_service_list_validation_error(load_env, mock_scm):
    # Create an instance of Service with the mocked Scm
    service_client = Service(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(SCMValidationError) as exc_info:
        service_client.list(folder="Shared", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_service_list_with_filters(load_env, mock_scm):
    # Mock the API client's get method
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
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Service with the mocked Scm
    service_client = Service(mock_scm)

    # Call the list method with filters
    filters = {
        "folder": "Shared",
        "names": ["service-http", "service-https"],
        "tags": ["Tag1", "Tag2"],
    }
    services = service_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "name": "service-http,service-https",
        "tag": "Tag1,Tag2",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/services",
        params=expected_params,
    )
    assert len(services) == 2


def test_service_request_model_invalid_uuid():
    # Invalid UUID
    invalid_data = {
        "id": "invalid-uuid",
        "name": "TestService",
        "folder": "Shared",
        "protocol": {"tcp": {"port": "80"}},
    }
    with pytest.raises(ValueError) as exc_info:
        ServiceResponseModel(**invalid_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_service_request_model_no_protocol_provided():
    data = {
        "name": "TestService",
        "folder": "Shared",
        # No protocol provided
    }
    with pytest.raises(PydanticValidationError) as exc_info:
        ServiceRequestModel(**data)
    assert "Field required" in str(exc_info.value)


def test_service_request_model_multiple_protocols_provided():
    data = {
        "name": "TestService",
        "folder": "Shared",
        "protocol": {
            "tcp": {"port": "80"},
            "udp": {"port": "53"},
        },
    }
    with pytest.raises(ValueError) as exc_info:
        ServiceRequestModel(**data)
    assert "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'." in str(
        exc_info.value
    )


def test_service_request_model_no_container_provided():
    data = {
        "name": "TestService",
        "protocol": {"tcp": {"port": "80"}},
        # No container provided
    }
    with pytest.raises(PydanticValidationError) as exc_info:
        ServiceRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_service_request_model_multiple_containers_provided():
    data = {
        "name": "TestService",
        "protocol": {"tcp": {"port": "80"}},
        "folder": "Shared",
        "snippet": "TestSnippet",
        # Multiple containers provided
    }
    with pytest.raises(PydanticValidationError) as exc_info:
        ServiceRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_service_response_model_invalid_uuid():
    # Invalid UUID in response model
    invalid_data = {
        "id": "invalid-uuid",
        "name": "TestService",
        "folder": "Shared",
        "protocol": {"tcp": {"port": "80"}},
    }
    with pytest.raises(ValueError) as exc_info:
        ServiceResponseModel(**invalid_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_service_request_model_with_device_container():
    # 'device' provided as the container
    data = {
        "name": "TestService",
        "protocol": {"tcp": {"port": "80"}},
        "device": "Device1",
    }
    model = ServiceRequestModel(**data)
    assert model.device == "Device1"


def test_service_request_model_multiple_containers_with_device():
    # Multiple containers including 'device' provided
    data = {
        "name": "TestService",
        "protocol": {"tcp": {"port": "80"}},
        "folder": "Shared",
        "device": "Device1",
    }
    with pytest.raises(PydanticValidationError) as exc_info:
        ServiceRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )
