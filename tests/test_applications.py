# tests/test_applications.py

from scm.config.objects import Application
from scm.models import ApplicationRequestModel, ApplicationResponseModel
from tests.factories import ApplicationFactory


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
                "risk": "5",
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
                "risk": "2",
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
                "risk": "2",
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
    mock_scm.get.return_value = mock_response

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
    mock_scm.post.return_value = mock_response

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
