# tests/test_applications.py
import pytest

from scm.config.objects import Application
from scm.exceptions import ValidationError
from scm.models.objects import ApplicationResponseModel, ApplicationRequestModel
from tests.factories import ApplicationFactory
from unittest.mock import MagicMock


def test_list_applications(load_env, mock_scm):
    """
    Integration test for listing applications.
    """
    # Mock the API client's get method if you don't want to make real API calls
    mock_response = {
        "data": [
            {
                "name": "100bao",
                "description": '100bao (literally translated as "100 treasures") is a free Chinese P2P file-sharing program that supports Windows 98, 2000, and XP operating systems.',
                "ports": ["tcp/3468,6346,11300"],
                "category": "general-internet",
                "subcategory": "file-sharing",
                "technology": "peer-to-peer",
                "risk": 5,
                "evasive": True,
                "pervasive": True,
                "folder": "All",
                "snippet": "predefined-snippet",
                "excessive_bandwidth_use": True,
                "used_by_malware": True,
                "transfers_files": True,
                "has_known_vulnerabilities": True,
                "tunnels_other_apps": False,
                "prone_to_misuse": True,
                "no_certifications": False,
            },
            {
                "name": "104apci-supervisory",
                "container": "iec-60870-5-104",
                "description": "IEC 60870-5-104 enables communication between control station and substation via a standard TCP/IP network. The functional app identifies application protocol control information (APCI) for supervisory function. This control format does not contain any application service data units (ASDUs).",
                "ports": ["tcp/2404"],
                "category": "business-systems",
                "subcategory": "ics-protocols",
                "technology": "client-server",
                "risk": 2,
                "evasive": False,
                "pervasive": True,
                "folder": "All",
                "snippet": "predefined-snippet",
                "depends_on": ["iec-60870-5-104-base"],
                "excessive_bandwidth_use": False,
                "used_by_malware": False,
                "transfers_files": False,
                "has_known_vulnerabilities": True,
                "tunnels_other_apps": True,
                "prone_to_misuse": False,
                "no_certifications": False,
            },
            {
                "name": "104apci-unnumbered",
                "container": "iec-60870-5-104",
                "description": "IEC 60870-5-104 enables communication between control station and substation via a standard TCP/IP network. The functional app identifies application protocol control information (APCI) for the unnumbered control format. This control format is used as a start-stop mechanism for information flow. There are no sequence numbers. This control field may also be used where more than one connection is available between stations, and a changeover between connections is to be made without loss of data. This control format does not contain any application service data units (ASDUs).",
                "ports": ["tcp/2404"],
                "category": "business-systems",
                "subcategory": "ics-protocols",
                "technology": "client-server",
                "risk": 2,
                "evasive": False,
                "pervasive": True,
                "folder": "All",
                "snippet": "predefined-snippet",
                "depends_on": ["iec-60870-5-104-base"],
                "excessive_bandwidth_use": False,
                "used_by_malware": False,
                "transfers_files": False,
                "has_known_vulnerabilities": True,
                "tunnels_other_apps": True,
                "prone_to_misuse": False,
                "no_certifications": False,
            },
        ]
    }

    # Configure the mock_scm.get method to return the mock_response
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of AddressGroup with the mocked Scm
    applications_client = Application(mock_scm)

    # Call the list method
    applications = applications_client.list(folder="MainFolder")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/applications", params={"folder": "MainFolder"}
    )
    assert isinstance(applications, list)
    assert isinstance(applications[0], ApplicationResponseModel)
    assert len(applications) == 3
    assert applications[0].name == "100bao"
    assert applications[0].ports == ["tcp/3468,6346,11300"]


def test_create_application(load_env, mock_scm):
    # Create a test ApplicationRequestModel instance using Factory Boy
    test_application = ApplicationFactory()

    # Mock the API client's post method
    mock_response = test_application.model_dump()
    mock_response["name"] = "ValidApplication"  # Mocked name

    # Configure the mock_scm.post method to return the mock_response
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of Address with the mocked Scm
    application_client = Application(mock_scm)

    # Call the create method
    created_group = application_client.create(
        test_application.model_dump(exclude_unset=True)
    )

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/objects/v1/applications",
        json=test_application.model_dump(exclude_unset=True),
    )
    assert created_group.name == test_application.name
    assert created_group.description == test_application.description
    assert created_group.category == test_application.category
    assert created_group.technology == test_application.technology
    assert created_group.risk == test_application.risk
    assert created_group.ports == test_application.ports
    assert created_group.folder == test_application.folder
    assert created_group.evasive == test_application.evasive
    assert created_group.pervasive == test_application.pervasive
    assert (
        created_group.excessive_bandwidth_use
        == test_application.excessive_bandwidth_use
    )
    assert created_group.used_by_malware == test_application.used_by_malware
    assert created_group.transfers_files == test_application.transfers_files
    assert (
        created_group.has_known_vulnerabilities
        == test_application.has_known_vulnerabilities
    )
    assert created_group.tunnels_other_apps == test_application.tunnels_other_apps
    assert created_group.prone_to_misuse == test_application.prone_to_misuse
    assert created_group.no_certifications == test_application.no_certifications


def test_get_application(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "name": "TestApp",
        "folder": "Shared",
        "description": "A test application",
        "category": "networking",
        "subcategory": "networking",
        "technology": "client-server",
        "risk": 2,
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Application with the mocked Scm
    application_client = Application(mock_scm)

    # Call the get method
    app_name = "TestApp"
    application = application_client.get(app_name)

    # Assertions
    mock_scm.get.assert_called_once_with(f"/config/objects/v1/applications/{app_name}")
    assert isinstance(application, ApplicationResponseModel)
    assert application.name == "TestApp"
    assert application.description == "A test application"
    assert application.category == "networking"


def test_update_application(load_env, mock_scm):
    # Mock the API client's put method
    mock_response = {
        "name": "TestApp",
        "folder": "Shared",
        "description": "An updated application",
        "category": "networking",
        "subcategory": "networking",
        "technology": "client-server",
        "risk": 3,
    }
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of Application with the mocked Scm
    application_client = Application(mock_scm)

    # Prepare data for update
    app_name = "TestApp"
    update_data = {
        "name": "UpdatedApp",
        "folder": "Shared",
        "description": "An updated application",
        "category": "networking",
        "subcategory": "ics-protocols",
        "technology": "client-server",
        "risk": 3,
    }

    # Call the update method
    updated_application = application_client.update(app_name, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/objects/v1/applications/{app_name}",
        json=update_data,
    )
    assert isinstance(updated_application, ApplicationResponseModel)
    assert updated_application.name == "TestApp"
    assert updated_application.description == "An updated application"
    assert updated_application.risk == 3


def test_application_list_validation_error(load_env, mock_scm):
    # Create an instance of Application with the mocked Scm
    application_client = Application(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(ValidationError) as exc_info:
        application_client.list(folder="Shared", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_application_list_with_types_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "name": "App1",
                "folder": "Shared",
                "category": "networking",
                "type": "web",
                "description": "An updated application",
                "subcategory": "ics-protocols",
                "technology": "client-server",
                "risk": 3,
            },
            {
                "name": "App2",
                "folder": "Shared",
                "category": "database",
                "description": "An updated application",
                "subcategory": "database",
                "technology": "client-server",
                "type": "database",
                "risk": 3,
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Application with the mocked Scm
    application_client = Application(mock_scm)

    # Call the list method with 'types' filter
    filters = {
        "folder": "Shared",
        "types": ["web", "database"],
    }
    applications = application_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "type": "web,database",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/applications",
        params=expected_params,
    )
    assert len(applications) == 2


def test_application_list_with_values_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "name": "App1",
                "folder": "Shared",
                "ports": ["80"],
                "description": "An updated application",
                "category": "networking",
                "subcategory": "ics-protocols",
                "technology": "client-server",
                "risk": 3,
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Application with the mocked Scm
    application_client = Application(mock_scm)

    # Call the list method with 'values' filter
    filters = {
        "folder": "Shared",
        "values": ["80"],
    }
    applications = application_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "value": "80",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/applications",
        params=expected_params,
    )
    assert len(applications) == 1


def test_application_list_with_names_filter(load_env, mock_scm):
    # Mock the API client's get method
    mock_response = {
        "data": [
            {
                "name": "App1",
                "folder": "Shared",
                "category": "networking",
                "description": "Test application App1",
                "subcategory": "web",
                "technology": "client-server",
                "risk": 3,
            },
            {
                "name": "App2",
                "folder": "Shared",
                "category": "database",
                "description": "Test application App2",
                "subcategory": "database",
                "technology": "client-server",
                "risk": 4,
            },
        ]
    }
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of Application with the mocked Scm
    application_client = Application(mock_scm)

    # Call the list method with 'names' filter
    filters = {
        "folder": "Shared",
        "names": ["App1", "App2"],
    }
    applications = application_client.list(**filters)

    # Assertions
    expected_params = {
        "folder": "Shared",
        "name": "App1,App2",
    }
    mock_scm.get.assert_called_once_with(
        "/config/objects/v1/applications",
        params=expected_params,
    )
    assert len(applications) == 2
    assert applications[0].name == "App1"
    assert applications[1].name == "App2"


def test_application_request_model_no_container_provided():
    # No container provided
    data = {
        "name": "TestApp",
        "category": "networking",
        "subcategory": "web",
        "technology": "client-server",
        "risk": 3,
    }
    with pytest.raises(ValueError) as exc_info:
        ApplicationRequestModel(**data)
    assert "Exactly one of 'folder' or 'snippet' must be provided." in str(
        exc_info.value
    )


def test_application_request_model_multiple_containers_provided():
    # Both 'folder' and 'snippet' provided
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
        ApplicationRequestModel(**data)
    assert "Exactly one of 'folder' or 'snippet' must be provided." in str(
        exc_info.value
    )
