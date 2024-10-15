# tests/test_application_groups.py

import pytest

from scm.config.objects import ApplicationGroup
from scm.exceptions import ValidationError
from scm.models import ApplicationGroupResponseModel, ApplicationGroupRequestModel
from tests.factories import ApplicationGroupFactory
from unittest.mock import MagicMock


def test_list_application_groups(load_env, mock_scm):
    """
    Integration test for listing application groups.
    """
    # Mock the API client's get method if you don't want to make real API calls
    mock_response = {
        "data": [
            {
                "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
                "name": "Microsoft 365 Access",
                "folder": "Shared",
                "snippet": "office365",
                "members": ["office365-consumer-access", "office365-enterprise-access"],
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
            {
                "id": "67e962f5-280b-40ac-a26c-d330f1c1baf6",
                "name": "Microsoft 365 Mail Clients",
                "folder": "Shared",
                "snippet": "office365",
                "members": [
                    "mapi-over-http",
                    "ms-exchange",
                    "rpc-over-http",
                    "activesync",
                ],
            },
            {
                "id": "c75509c1-edc3-4d7d-be92-591f415edb48",
                "name": "Microsoft Real Time Protocols",
                "folder": "Shared",
                "snippet": "office365",
                "members": ["rtcp", "stun", "rtp"],
            },
            {
                "id": "25633a36-cfff-4be9-a0cf-53b3a9880418",
                "name": "Microsoft 365 - Dependent Apps",
                "folder": "Shared",
                "snippet": "office365",
                "members": [
                    "http-audio",
                    "http-video",
                    "ocsp",
                    "soap",
                    "ssl",
                    "web-browsing",
                    "websocket",
                    "windows-azure-base",
                ],
            },
            {
                "id": "7d29b9b2-7f18-4860-b986-0a9838f3ab69",
                "name": "tewstasdfasdf",
                "folder": "Shared",
                "members": ["20-twenty", "flashtalking"],
            },
            {
                "id": "65d16b65-b3e2-4d8f-9dce-a3af7f6b1d0b",
                "name": "adfsasdfsaf",
                "folder": "Shared",
                "members": ["tewstasdfasdf"],
            },
            {
                "id": "00bb9992-e28c-4306-8c17-c1da03750b3b",
                "name": "asdfasdfasdfasdfasdfasdfasdf",
                "folder": "Shared",
                "members": ["High Risk Applications"],
            },
        ],
        "offset": 0,
        "total": 8,
        "limit": 200,
    }

    # Configure the mock_scm.get method to return the mock_response
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of ApplicationGroup with the mocked Scm
    application_groups_client = ApplicationGroup(mock_scm)

    # Call the list method
    application_groups = application_groups_client.list(folder="Prisma Access")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/application-groups", params={"folder": "Prisma Access"}
    )
    assert isinstance(application_groups, list)
    assert isinstance(application_groups[0], ApplicationGroupResponseModel)
    assert len(application_groups) == 8
    assert application_groups[0].id == "b44a8c00-7555-4021-96f0-d59deecd54e8"
    assert application_groups[0].name == "Microsoft 365 Access"
    assert application_groups[0].folder == "Shared"
    assert application_groups[0].snippet == "office365"
    assert application_groups[0].members == [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]


def test_create_application_group(load_env, mock_scm):
    # Create a test ApplicationGroupRequestModel instance using Factory Boy
    test_application_group = ApplicationGroupFactory()

    # Mock the API client's post method
    mock_response = test_application_group.model_dump()
    mock_response["name"] = "ValidStaticApplicationGroup"  # Mocked name

    # Configure the mock_scm.post method to return the mock_response
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroup with the mocked Scm
    application_group_client = ApplicationGroup(mock_scm)

    # Call the create method
    created_group = application_group_client.create(
        test_application_group.model_dump(exclude_unset=True)
    )

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/objects/v1/application-groups",
        json=test_application_group.model_dump(exclude_unset=True),
    )
    assert created_group.name == test_application_group.name
    assert created_group.members == test_application_group.members
    assert created_group.folder == test_application_group.folder


def test_get_application_group(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
        "name": "TestAppGroup",
        "members": [
            "office365-consumer-access",
            "office365-enterprise-access",
        ],
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Application with the mocked Scm
    application_group_client = ApplicationGroup(mock_scm)

    # Call the get method
    app_group_name = "TestAppGroup"
    application = application_group_client.get(app_group_name)

    # Assertions
    mock_scm.get.assert_called_once_with(
        f"/config/objects/v1/application-groups/{app_group_name}"
    )
    assert isinstance(application, ApplicationGroupResponseModel)
    assert application.name == "TestAppGroup"
    assert application.members == [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    assert application.id == "b44a8c00-7555-4021-96f0-d59deecd54e8"


def test_update_application_group(load_env, mock_scm):
    # Mock the API client's put method with the updated members list
    mock_response = {
        "id": "123e4567-e89b-12d3-a456-426655440000",
        "name": "TestAppGroup",
        "folder": "Prisma Access",
        "members": [
            "office365-consumer-access",
            "office365-enterprise-access",
            "test123",  # New member added
        ],
    }
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of ApplicationGroup with the mocked Scm
    application_group_client = ApplicationGroup(mock_scm)

    # Prepare data for update
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

    # Call the update method
    updated_application_group = application_group_client.update(object_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/objects/v1/application-groups/{object_id}",
        json=update_data,
    )
    assert isinstance(updated_application_group, ApplicationGroupResponseModel)
    assert updated_application_group.name == "TestAppGroup"
    assert updated_application_group.members == [
        "office365-consumer-access",
        "office365-enterprise-access",
        "test123",
    ]
    assert updated_application_group.folder == "Prisma Access"


def test_application_group_list_validation_error(load_env, mock_scm):
    # Create an instance of ApplicationGroup with the mocked Scm
    application_group_client = ApplicationGroup(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(ValidationError) as exc_info:
        application_group_client.list(folder="Prisma Access", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_application_group_list_with_types_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
                "name": "Microsoft 365 Access",
                "folder": "Shared",
                "snippet": "office365",
                "members": ["office365-consumer-access", "office365-enterprise-access"],
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
            {
                "id": "67e962f5-280b-40ac-a26c-d330f1c1baf6",
                "name": "Microsoft 365 Mail Clients",
                "folder": "Shared",
                "snippet": "office365",
                "members": [
                    "mapi-over-http",
                    "ms-exchange",
                    "rpc-over-http",
                    "activesync",
                ],
            },
            {
                "id": "c75509c1-edc3-4d7d-be92-591f415edb48",
                "name": "Microsoft Real Time Protocols",
                "folder": "Shared",
                "snippet": "office365",
                "members": ["rtcp", "stun", "rtp"],
            },
            {
                "id": "25633a36-cfff-4be9-a0cf-53b3a9880418",
                "name": "Microsoft 365 - Dependent Apps",
                "folder": "Shared",
                "snippet": "office365",
                "members": [
                    "http-audio",
                    "http-video",
                    "ocsp",
                    "soap",
                    "ssl",
                    "web-browsing",
                    "websocket",
                    "windows-azure-base",
                ],
            },
            {
                "id": "7d29b9b2-7f18-4860-b986-0a9838f3ab69",
                "name": "tewstasdfasdf",
                "folder": "Shared",
                "members": ["20-twenty", "flashtalking"],
            },
            {
                "id": "65d16b65-b3e2-4d8f-9dce-a3af7f6b1d0b",
                "name": "adfsasdfsaf",
                "folder": "Shared",
                "members": ["tewstasdfasdf"],
            },
            {
                "id": "00bb9992-e28c-4306-8c17-c1da03750b3b",
                "name": "asdfasdfasdfasdfasdfasdfasdf",
                "folder": "Shared",
                "members": ["High Risk Applications"],
            },
        ],
        "offset": 0,
        "total": 8,
        "limit": 200,
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of ApplicationGroup with the mocked Scm
    application_group_client = ApplicationGroup(mock_scm)

    # Call the list method with 'types' filter
    filters = {
        "folder": "Shared",
        "types": ["members", "names"],
    }
    application_groups = application_group_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "types": ["members", "names"],
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/application-groups",
        params=expected_params,
    )
    assert len(application_groups) == 8


def test_application_group_list_with_values_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
                "name": "Microsoft 365 Access",
                "folder": "Shared",
                "snippet": "office365",
                "members": ["office365-consumer-access", "office365-enterprise-access"],
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
            {
                "id": "67e962f5-280b-40ac-a26c-d330f1c1baf6",
                "name": "Microsoft 365 Mail Clients",
                "folder": "Shared",
                "snippet": "office365",
                "members": [
                    "mapi-over-http",
                    "ms-exchange",
                    "rpc-over-http",
                    "activesync",
                ],
            },
            {
                "id": "c75509c1-edc3-4d7d-be92-591f415edb48",
                "name": "Microsoft Real Time Protocols",
                "folder": "Shared",
                "snippet": "office365",
                "members": ["rtcp", "stun", "rtp"],
            },
            {
                "id": "25633a36-cfff-4be9-a0cf-53b3a9880418",
                "name": "Microsoft 365 - Dependent Apps",
                "folder": "Shared",
                "snippet": "office365",
                "members": [
                    "http-audio",
                    "http-video",
                    "ocsp",
                    "soap",
                    "ssl",
                    "web-browsing",
                    "websocket",
                    "windows-azure-base",
                ],
            },
            {
                "id": "7d29b9b2-7f18-4860-b986-0a9838f3ab69",
                "name": "tewstasdfasdf",
                "folder": "Shared",
                "members": ["20-twenty", "flashtalking"],
            },
            {
                "id": "65d16b65-b3e2-4d8f-9dce-a3af7f6b1d0b",
                "name": "adfsasdfsaf",
                "folder": "Shared",
                "members": ["tewstasdfasdf"],
            },
            {
                "id": "00bb9992-e28c-4306-8c17-c1da03750b3b",
                "name": "asdfasdfasdfasdfasdfasdfasdf",
                "folder": "Shared",
                "members": ["High Risk Applications"],
            },
        ],
        "offset": 0,
        "total": 8,
        "limit": 200,
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Application with the mocked Scm
    application_group_client = ApplicationGroup(mock_scm)

    # Call the list method with 'values' filter
    filters = {
        "folder": "Shared",
        "names": ["adfsasdfsaf"],
    }
    application_groups = application_group_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "name": "adfsasdfsaf",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/application-groups",
        params=expected_params,
    )
    assert len(application_groups) == 8


def test_application_group_list_with_names_filter(load_env, mock_scm):
    # Mock the API client's get method with filtered data
    mock_response = {
        "data": [
            {
                "id": "65d16b65-b3e2-4d8f-9dce-a3af7f6b1d0b",
                "name": "adfsasdfsaf",
                "folder": "Shared",
                "members": ["tewstasdfasdf"],
            },
            {
                "id": "00bb9992-e28c-4306-8c17-c1da03750b3b",
                "name": "asdfasdfasdfasdfasdfasdfasdf",
                "folder": "Shared",
                "members": ["High Risk Applications"],
            },
        ],
        "offset": 0,
        "total": 2,
        "limit": 200,
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of ApplicationGroup with the mocked Scm
    application_group_client = ApplicationGroup(mock_scm)

    # Call the list method with 'names' filter
    filters = {
        "folder": "Shared",
        "names": [
            "adfsasdfsaf",
            "asdfasdfasdfasdfasdfasdfasdf",
        ],
    }
    application_groups = application_group_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "name": "adfsasdfsaf,asdfasdfasdfasdfasdfasdfasdf",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/application-groups",
        params=expected_params,
    )
    assert len(application_groups) == 2
    assert application_groups[0].name == "adfsasdfsaf"
    assert application_groups[1].name == "asdfasdfasdfasdfasdfasdfasdf"


def test_application_group_request_model_no_container_provided():
    # No container provided
    data = {
        "name": "Microsoft 365 Access",
        "members": ["office365-consumer-access", "office365-enterprise-access"],
    }

    with pytest.raises(ValueError) as exc_info:
        ApplicationGroupRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_application_request_model_multiple_containers_provided():
    # Both 'folder' and 'snippet' provided
    data = {
        "name": "Microsoft 365 Access",
        "folder": "Shared",
        "snippet": "office365",
        "members": ["office365-consumer-access", "office365-enterprise-access"],
    }

    with pytest.raises(ValueError) as exc_info:
        ApplicationGroupRequestModel(**data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_application_group_response_model_invalid_uuid():
    # Invalid UUID in 'id' field
    invalid_data = {
        "id": "invalid-uuid",  # This should trigger the ValueError
        "name": "TestAppGroup",
        "members": ["app1", "app2"],
        "folder": "Shared",
    }

    with pytest.raises(ValueError) as exc_info:
        ApplicationGroupResponseModel(**invalid_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)
