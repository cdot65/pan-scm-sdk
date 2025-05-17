"""Test module for Remote Networks configuration service.

This module contains unit tests for the Remote Networks configuration service and its related models.
"""
# tests/scm/config/deployment/test_remote_networks.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.deployment import RemoteNetworks
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import RemoteNetworkResponseModel
from tests.factories.deployment.remote_networks import (
    RemoteNetworkCreateApiFactory,
    RemoteNetworkResponseFactory,
    RemoteNetworkUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestRemoteNetworkBase:
    """Base class for RemoteNetwork tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = RemoteNetworks(self.mock_scm, max_limit=5000)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestRemoteNetworkMaxLimit(TestRemoteNetworkBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = RemoteNetworks(self.mock_scm)  # noqa
        assert client.max_limit == RemoteNetworks.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = RemoteNetworks(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = RemoteNetworks(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            RemoteNetworks(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            RemoteNetworks(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            RemoteNetworks(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestRemoteNetworkList(TestRemoteNetworkBase):
    """Tests for listing RemoteNetwork objects."""

    def test_list_valid(self):
        """**Objective:** Test listing all objects."""
        mock_response = {
            "data": [
                RemoteNetworkResponseFactory.with_ecmp_enabled().model_dump(),
                RemoteNetworkResponseFactory.with_ecmp_enabled().model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/sse/config/v1/remote-networks",
            params={
                "folder": "All",
                "limit": 5000,
                "offset": 0,
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], RemoteNetworkResponseModel)
        assert len(existing_objects) == 2

    def test_list_folder_empty_error(self):
        """Test that empty folder raises appropriate error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_list_folder_nonexistent_error(self):
        """Test error handling in list operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

    def test_list_container_missing_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()
        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_filters_valid(self):
        """Test that filters are properly added to parameters."""
        filters = {
            "regions": ["type1", "type2"],
            "license_types": ["value1", "value2"],
            "subnets": ["tag1", "tag2"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Remote Networks", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/sse/config/v1/remote-networks",
            params={
                "folder": "Remote Networks",
                "limit": 5000,
                "offset": 0,
            },
        )

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                RemoteNetworkResponseFactory.with_ecmp_enabled().model_dump(),
                RemoteNetworkResponseFactory.with_ecmp_enabled().model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches (since filters remove results)
        filtered_objects = self.client.list(
            folder="Remote Networks",
            regions=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Remote Networks",
            license_types=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Remote Networks",
            spn_names=[],
        )
        assert len(filtered_objects) == 0

    def test_list_filters_types(self):
        """Test validation of filter types in list method."""
        # Mock response for successful case
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-remote-network0",
                    "folder": "Remote Networks",
                    "region": "us-east-1",
                    "license_type": "FWAAS-AGGREGATE",
                    "spn_name": "spn-response",
                    "ecmp_load_balancing": "disable",
                    "ipsec_tunnel": "ipsec-tunnel-response",
                    "subnets": ["10.0.0.0/8", "10.1.0.0/8", "10.2.0.0/8"],
                    "protocol": {
                        "bgp": {
                            "enable": True,
                            "peer_ip_address": "10.11.0.254",
                            "peer_as": "65515",
                            "local_ip_address": "192.168.11.11",
                        }
                    },
                },
                {
                    "id": "123e4567-e89b-12d3-a456-426655440001",
                    "name": "test-remote-network1",
                    "folder": "Remote Networks",
                    "region": "us-east-2",
                    "license_type": "FWAAS-AGGREGATE",
                    "spn_name": "spn-response",
                    "ecmp_load_balancing": "disable",
                    "ipsec_tunnel": "ipsec-tunnel-response",
                    "subnets": ["192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"],
                    "protocol": {
                        "bgp": {
                            "enable": False,
                            "peer_ip_address": "10.11.0.254",
                            "peer_as": "65515",
                            "local_ip_address": "192.168.11.11",
                        }
                    },
                },
                {
                    "id": "123e4567-e89b-12d3-a456-426655440002",
                    "name": "test-remote-network2",
                    "folder": "Remote Networks",
                    "region": "us-east-2",
                    "license_type": "FWAAS-AGGREGATE",
                    "spn_name": "spn-response",
                    "ecmp_load_balancing": "disable",
                    "ipsec_tunnel": "ipsec-tunnel-response",
                    "subnets": ["172.16.1.0/24", "172.16.2.0/24", "172.16.3.0/24"],
                },
            ]
        }

        # Test invalid regions filter (string instead of list)
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'regions' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Remote Networks", regions="test123")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "'regions' filter must be a list"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Query Parameter"

        # Reset side effect for next test
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'license_types' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Remote Networks", license_types="test123")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "'license_types' filter must be a list"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Query Parameter"

        # Reset side effect for next test
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'subnets' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Remote Networks", subnets="1.1.1.1/24")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "'subnets' filter must be a list"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Query Parameter"

        # Reset side effect for successful case
        self.mock_scm.get.side_effect = None  # noqa
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Remote Networks",
                regions=["us-east-1"],
                license_types=["FWAAS-AGGREGATE"],
                subnets=["172.16.1.0/24"],
            )
        except HTTPError:
            pytest.fail("Unexpected HTTPError raised with valid list filters")

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when API returns response with missing data field."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when API returns non-list data field."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500

    def test_list_response_no_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None  # Simulate no content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")

    def test_list_server_error(self):
        """Test generic exception handling in list method."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_list_pagination_multiple_pages(self):
        """Test that the list method correctly aggregates data from multiple pages.
        Using a custom client with max_limit=2500 to test pagination.
        """
        client = RemoteNetworks(self.mock_scm, max_limit=2500)  # noqa

        # Create test data
        total_objects = 7500  # Three pages worth
        first_batch = [RemoteNetworkResponseFactory.build() for i in range(2500)]
        second_batch = [RemoteNetworkResponseFactory.build() for i in range(2500)]
        third_batch = [RemoteNetworkResponseFactory.build() for i in range(2500)]

        # Set up mock responses
        mock_responses = [
            {"data": [obj.model_dump() for obj in first_batch]},
            {"data": [obj.model_dump() for obj in second_batch]},
            {"data": [obj.model_dump() for obj in third_batch]},
            {"data": []},  # Empty response to end pagination
        ]
        self.mock_scm.get.side_effect = mock_responses  # noqa

        # Get results
        results = client.list(folder="Remote Networks")

        # Verify results
        assert len(results) == total_objects
        assert isinstance(results[0], RemoteNetworkResponseModel)
        assert all(isinstance(r, RemoteNetworkResponseModel) for r in results)

        # Verify the number of API calls
        assert self.mock_scm.get.call_count == 4  # noqa # Three pages + one final check

        # Verify first API call used correct parameters
        self.mock_scm.get.assert_any_call(  # noqa
            "/sse/config/v1/remote-networks",
            params={
                "folder": "Remote Networks",
                "limit": 2500,
                "offset": 0,
            },
        )

    # -------------------- New Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """Test that exact_match=True returns only objects that match the container exactly."""
        mock_response = {
            "data": [
                RemoteNetworkResponseFactory.build().model_dump(),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # exact_match should exclude the one from "All"
        filtered = self.client.list(folder="Remote Networks", exact_match=True)
        assert len(filtered) == 0

    def test_list_exclude_folders(self):
        """Test that exclude_folders removes objects from those folders."""
        mock_response = {
            "data": [
                RemoteNetworkResponseFactory.build().model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Remote Networks", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """Test combining exact_match with exclusions."""
        mock_response = {
            "data": [
                {
                    "id": "920508c1-143d-47dc-b3d0-4c1b75dfff3e",
                    "name": "RN-Branch-01",
                    "folder": "Remote Networks",
                    "license_type": "FWAAS-AGGREGATE",
                    "region": "us-east-1",
                    "spn_name": "us-east-gingko",
                    "ecmp_load_balancing": "disable",
                    "subnets": ["10.11.0.0/16"],
                    "ipsec_tunnel": "RN-Tunnel-01",
                    "protocol": {
                        "bgp": {
                            "enable": None,
                            "peer_ip_address": "10.11.0.254",
                            "peer_as": "65515",
                            "local_ip_address": "192.168.11.11",
                        }
                    },
                    "details": {
                        "branch_as_and_router": [
                            {"AS": "65515 | 10.11.0.254", "tunnel": "RN-Tunnel-01"}
                        ],
                        "branch_as_and_router_ecmp": None,
                        "ebgp_router": ["192.168.11.11"],
                        "ebgp_router_ecmp": None,
                        "inbound_access_apps": [],
                        "local_ip_address": "RN-Tunnel-01",
                        "loopback_ip_address": "192.168.255.7",
                        "static_subnet": ["10.11.0.0/16"],
                        "name": "RN-Branch-01",
                        "service_ip_address": "165.1.203.22",
                        "fqdn": "",
                    },
                },
                {
                    "id": "8214e181-f16a-406e-a2f8-4938cd619b9e",
                    "name": "RN-Branch-02",
                    "folder": "Remote Networks",
                    "license_type": "FWAAS-AGGREGATE",
                    "region": "us-east-2",
                    "spn_name": "us-central-redbud",
                    "ipsec_tunnel": "RN-Tunnel-02",
                    "subnets": ["10.12.0.0/16"],
                    "ecmp_load_balancing": "disable",
                    "details": {
                        "branch_as_and_router": [],
                        "branch_as_and_router_ecmp": None,
                        "ebgp_router": ["192.168.255.9"],
                        "ebgp_router_ecmp": None,
                        "inbound_access_apps": [],
                        "local_ip_address": "RN-Tunnel-02",
                        "loopback_ip_address": "192.168.255.9",
                        "static_subnet": ["10.12.0.0/16"],
                        "name": "RN-Branch-02",
                        "service_ip_address": "134.238.214.129",
                        "fqdn": "",
                    },
                },
                {
                    "id": "5e05c2c6-5316-4322-8579-0d7fa7aea98e",
                    "name": "RN-oreiter-azureSC",
                    "folder": "Remote Networks",
                    "license_type": "FWAAS-AGGREGATE",
                    "region": "us-east-2",
                    "spn_name": "us-central-redbud",
                    "ipsec_tunnel": "oreiter-azure-ngfw-RN",
                    "subnets": ["172.17.3.0/24", "172.17.2.0/24", "172.20.0.0/24"],
                    "ecmp_load_balancing": "disable",
                    "details": {
                        "branch_as_and_router": [],
                        "branch_as_and_router_ecmp": None,
                        "ebgp_router": ["192.168.255.9"],
                        "ebgp_router_ecmp": None,
                        "inbound_access_apps": None,
                        "local_ip_address": "oreiter-azure-ngfw-RN",
                        "loopback_ip_address": "192.168.255.9",
                        "static_subnet": [
                            "172.17.2.0/24",
                            "172.20.0.0/24",
                            "172.17.3.0/24",
                        ],
                        "name": "RN-oreiter-azureSC",
                        "service_ip_address": "134.238.214.129",
                        "fqdn": "",
                    },
                },
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(
            folder="Remote Networks",
            exact_match=True,
            exclude_folders=["All"],
        )
        # Only those in Remote Networks should remain
        assert len(filtered) == 3
        obj = filtered[0]
        assert obj.folder == "Remote Networks"


class TestRemoteNetworkCreate(TestRemoteNetworkBase):
    """Tests for creating RemoteNetwork objects."""

    def test_create_valid_type(self):
        """Test creating an object with ip_netmask."""
        test_object = RemoteNetworkCreateApiFactory.build()
        mock_response = RemoteNetworkResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/sse/config/v1/remote-networks",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.folder == test_object.folder

    def test_create_valid_type_ecmp_enabled(self):
        """Test creating an object with ip_netmask."""
        test_object = RemoteNetworkCreateApiFactory.with_ecmp_enabled()
        mock_response = RemoteNetworkResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/sse/config/v1/remote-networks",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.folder == test_object.folder

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {
                    "name": "test",
                    "region": "us-west-2",
                    "folder": "Remote Networks",
                    "license_type": "FWAAS-AGGREGATE",
                    "spn_name": "spn-test",
                    "ecmp_load_balancing": "disable",
                    "ipsec_tunnel": "ipsec-tunnel-default",
                    "ecmp_tunnels": None,
                }
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test",
            "region": "us-west-2",
            "folder": "Remote Networks",
            "license_type": "FWAAS-AGGREGATE",
            "spn_name": "spn-test",
            "ecmp_load_balancing": "disable",
            "ipsec_tunnel": "ipsec-tunnel-default",
            "ecmp_tunnels": None,
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Create failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Create failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(
                {
                    "name": "test",
                    "region": "us-west-2",
                    "folder": "Remote Networks",
                    "license_type": "FWAAS-AGGREGATE",
                    "spn_name": "spn-test",
                    "ecmp_load_balancing": "disable",
                    "ipsec_tunnel": "ipsec-tunnel-default",
                    "ecmp_tunnels": None,
                }
            )
        assert str(exc_info.value) == "Generic error"


class TestRemoteNetworkGet(TestRemoteNetworkBase):
    """Tests for retrieving a specific RemoteNetwork object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = RemoteNetworkResponseFactory.build()

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        object_id = mock_response.id

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/sse/config/v1/remote-networks/{object_id}"
        )
        assert isinstance(retrieved_object, RemoteNetworkResponseModel)
        assert retrieved_object.id == mock_response.id
        assert retrieved_object.name == mock_response.name
        assert retrieved_object.folder == mock_response.folder

    def test_get_object_not_present_error(self):
        """Test error handling when the object is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_get_generic_exception_handling(self):
        """Test generic exception handling in get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get(object_id)

        assert str(exc_info.value) == "Generic error"

    def test_get_http_error_no_response_content(self):
        """Test get method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.get(object_id)

    def test_get_server_error(self):
        """Test handling of server errors during get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestRemoteNetworkUpdate(TestRemoteNetworkBase):
    """Tests for updating RemoteNetwork objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = RemoteNetworkUpdateApiFactory.build(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestRemoteNetwork",
            region="us-west-2",
            license_type="FWAAS-AGGREGATE",
            spn_name="spn-test",
            ecmp_load_balancing="disable",
            ipsec_tunnel="ipsec-tunnel-default",
            folder="Remote Networks",
        )

        mock_response = RemoteNetworkResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa
        call_args = self.mock_scm.put.call_args  # noqa
        assert call_args[0][0] == f"/sse/config/v1/remote-networks/{update_data.id}"

        payload = call_args[1]["json"]
        assert payload["name"] == "TestRemoteNetwork"
        assert payload["region"] == "us-west-2"
        assert payload["license_type"] == "FWAAS-AGGREGATE"
        assert payload["spn_name"] == "spn-test"
        assert payload["ecmp_load_balancing"] == "disable"
        assert payload["ipsec_tunnel"] == "ipsec-tunnel-default"
        assert payload["folder"] == "Remote Networks"

        assert isinstance(updated_object, RemoteNetworkResponseModel)
        assert str(updated_object.id) == str(mock_response.id)
        assert updated_object.name == mock_response.name
        assert updated_object.description == mock_response.description
        assert updated_object.folder == mock_response.folder

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = RemoteNetworkUpdateApiFactory.build()

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Update failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = RemoteNetworkUpdateApiFactory.build()

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = RemoteNetworkUpdateApiFactory.build()

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        update_data = RemoteNetworkUpdateApiFactory.build()

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = RemoteNetworkUpdateApiFactory.build()

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestRemoteNetworkDelete(TestRemoteNetworkBase):
    """Tests for deleting RemoteNetwork objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        # Should not raise any exception
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/sse/config/v1/remote-networks/{object_id}"
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced elsewhere."""
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=409,
            error_code="E009",
            message="Your configuration is not valid.",
            error_type="Reference Not Zero",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Your configuration is not valid."
        assert error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_delete_http_error_no_response_content(self):
        """Test delete method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.delete(object_id)

    def test_delete_generic_exception_handling(self):
        """Test handling of a generic exception during delete."""
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdefg")

        assert str(exc_info.value) == "Generic error"

    def test_delete_server_error(self):
        """Test handling of server errors during delete."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestRemoteNetworkFetch(TestRemoteNetworkBase):
    """Tests for fetching RemoteNetwork objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = RemoteNetworkResponseFactory.build()
        mock_response_data = mock_response_model.model_dump()

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/sse/config/v1/remote-networks",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        assert isinstance(fetched_object, RemoteNetworkResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.description == mock_response_model.description
        assert fetched_object.folder == mock_response_model.folder

    def test_fetch_object_not_present_error(self):
        """Test fetching an object that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"name" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Texas")

        error_msg = str(exc_info.value)
        assert '"name" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")

        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_invalid_response_format_error(self):
        """Test fetching an object when the API returns an unexpected format."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="Invalid response format",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Invalid response format"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Texas")

        assert str(exc_info.value) == "Generic error"

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-address", folder="Texas")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-rn",
            "folder": "Remote Networks",
            "region": "test",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-rn", folder="Remote Networks")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-rn")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500


class TestRemoteNetworkFilters(TestRemoteNetworkBase):
    """Tests for Remote Network filtering functionality."""

    def test_single_string_filter_match(self):
        """Test filtering with single string value."""
        networks = [
            RemoteNetworkResponseFactory(region="us-east-1"),
            RemoteNetworkResponseFactory(region="us-west-2"),
        ]
        filtered = self.client._apply_filters(networks, {"regions": "us-east-1"})
        assert len(filtered) == 1
        assert filtered[0].region == "us-east-1"

    def test_subnet_filtering_list(self):
        """Test subnet filtering with list of values."""
        networks = [
            RemoteNetworkResponseFactory(subnets=["10.0.0.0/24", "192.168.1.0/24"]),
            RemoteNetworkResponseFactory(subnets=["172.16.0.0/24"]),
        ]
        filtered = self.client._apply_filters(networks, {"subnets": ["10.0.0.0/24"]})
        assert len(filtered) == 1
        assert "10.0.0.0/24" in filtered[0].subnets

    def test_subnet_filtering_single_value(self):
        """Test subnet filtering with single string value."""
        networks = [
            RemoteNetworkResponseFactory(subnets=["10.0.0.0/24", "192.168.1.0/24"]),
            RemoteNetworkResponseFactory(subnets=["172.16.0.0/24"]),
        ]
        filtered = self.client._apply_filters(networks, {"subnets": "10.0.0.0/24"})
        assert len(filtered) == 1
        assert "10.0.0.0/24" in filtered[0].subnets

    def test_subnet_filtering_empty_subnets(self):
        """Test subnet filtering with empty subnets list."""
        networks = [
            RemoteNetworkResponseFactory(subnets=[]),
            RemoteNetworkResponseFactory(subnets=None),
        ]
        filtered = self.client._apply_filters(networks, {"subnets": ["10.0.0.0/24"]})
        assert len(filtered) == 0

    def test_spn_name_filtering(self):
        """Test SPN name filtering."""
        networks = [
            RemoteNetworkResponseFactory(spn_name="spn1"),
            RemoteNetworkResponseFactory(spn_name="spn2"),
        ]
        filtered = self.client._apply_filters(networks, {"spn_names": ["spn1"]})
        assert len(filtered) == 1
        assert filtered[0].spn_name == "spn1"

    def test_ecmp_load_balancing_filtering(self):
        """Test ECMP load balancing filtering."""
        networks = [
            RemoteNetworkResponseFactory(ecmp_load_balancing="disable"),
            RemoteNetworkResponseFactory(ecmp_load_balancing="disable"),
        ]
        filtered = self.client._apply_filters(networks, {"ecmp_load_balancing": "enable"})
        assert len(filtered) == 0

    def test_protocol_filtering_list(self):
        """Test protocol filtering with list."""
        networks = [
            RemoteNetworkResponseFactory.build(),
            RemoteNetworkResponseFactory(protocol=None),
        ]
        filtered = self.client._apply_filters(networks, {"protocol": ["bgp"]})
        assert len(filtered) == 0

    def test_protocol_filtering_single_value(self):
        """Test protocol filtering with single value."""
        networks = [
            RemoteNetworkResponseFactory.with_protocol_bgp(),
            RemoteNetworkResponseFactory(protocol=None),
        ]
        filtered = self.client._apply_filters(networks, {"protocol": "bgp"})
        assert len(filtered) == 1
        assert filtered[0].protocol.bgp is not None
        assert filtered[0].protocol.bgp.enable is True

    def test_protocol_filtering_none(self):
        """Test protocol filtering for None values."""
        networks = [
            RemoteNetworkResponseFactory.with_protocol_bgp(),
            RemoteNetworkResponseFactory(protocol=None),
        ]
        filtered = self.client._apply_filters(networks, {"protocol": "None"})
        assert len(filtered) == 1
        assert filtered[0].protocol is None

    def test_multiple_filters(self):
        """Test applying multiple filters simultaneously."""
        networks = [
            RemoteNetworkResponseFactory(
                region="us-east-1", spn_name="spn1", subnets=["10.0.0.0/24"]
            ),
            RemoteNetworkResponseFactory(
                region="us-west-2", spn_name="spn2", subnets=["192.168.1.0/24"]
            ),
        ]
        filtered = self.client._apply_filters(
            networks,
            {"regions": "us-east-1", "spn_names": "spn1", "subnets": ["10.0.0.0/24"]},
        )
        assert len(filtered) == 1
        assert filtered[0].region == "us-east-1"
        assert filtered[0].spn_name == "spn1"
        assert "10.0.0.0/24" in filtered[0].subnets

    def test_empty_list_filters(self):
        """Test that empty list filters return empty results."""
        networks = [RemoteNetworkResponseFactory() for _ in range(3)]

        empty_filters = [
            {"regions": []},
            {"license_types": []},
            {"subnets": []},
            {"spn_names": []},
            {"ipsec_tunnels": []},
            {"protocol": []},
        ]

        for filter_dict in empty_filters:
            filtered = self.client._apply_filters(networks, filter_dict)
            assert len(filtered) == 0, f"Filter {filter_dict} should return empty list"


# -------------------- End of Test Classes --------------------
