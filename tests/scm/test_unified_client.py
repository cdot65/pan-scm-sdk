# tests/scm/test_unified_client.py

from unittest.mock import MagicMock, patch

import pytest

from scm.client import Scm


@pytest.fixture
def api_client():
    """Fixture to create a test Scm client instance with mocked auth."""
    with patch("scm.client.OAuth2Client") as mock_oauth:
        # Configure the mock OAuth2Client
        mock_oauth_instance = MagicMock()
        mock_oauth_instance.is_expired = False
        mock_oauth_instance.auth_request.client_id = "test_id"
        mock_oauth.return_value = mock_oauth_instance

        # Create the client with the mocked OAuth2Client
        client = Scm(
            client_id="test_id",
            client_secret="test_secret",
            tsg_id="test_tsg",
        )

        # Mock the request method to avoid real API calls
        client.request = MagicMock()

        yield client


class TestUnifiedClient:
    """Test suite for the unified client attribute access pattern."""

    def test_service_attribute_access(self, api_client):
        """Test dynamic service access via attributes."""
        # Mock the importlib.import_module function
        with patch("importlib.import_module") as mock_import:
            # Create mock service classes
            mock_address = MagicMock()
            mock_tag = MagicMock()
            mock_syslog = MagicMock()
            mock_region = MagicMock()
            mock_schedule = MagicMock()

            # Configure the mock modules to return mock service classes
            mock_module1 = MagicMock()
            mock_module1.Address = mock_address

            mock_module2 = MagicMock()
            mock_module2.Tag = mock_tag

            mock_module3 = MagicMock()
            mock_module3.SyslogServerProfile = mock_syslog

            mock_module4 = MagicMock()
            mock_module4.Region = mock_region

            mock_module5 = MagicMock()
            mock_module5.Schedule = mock_schedule

            # Set side_effect to return different modules based on import path
            def side_effect(module_name):
                if module_name == "scm.config.objects.address":
                    return mock_module1
                elif module_name == "scm.config.objects.tag":
                    return mock_module2
                elif module_name == "scm.config.objects.syslog_server_profiles":
                    return mock_module3
                elif module_name == "scm.config.objects.region":
                    return mock_module4
                elif module_name == "scm.config.objects.schedules":
                    return mock_module5
                raise ImportError(f"No module named '{module_name}'")

            mock_import.side_effect = side_effect

            # Access services via attributes
            api_client.address
            api_client.tag
            api_client.syslog_server_profile
            api_client.region
            api_client.schedule

            # Verify correct modules were imported
            mock_import.assert_any_call("scm.config.objects.address")
            mock_import.assert_any_call("scm.config.objects.tag")
            mock_import.assert_any_call("scm.config.objects.syslog_server_profiles")
            mock_import.assert_any_call("scm.config.objects.region")
            mock_import.assert_any_call("scm.config.objects.schedules")

            # Verify service classes were instantiated with api_client
            mock_address.assert_called_once_with(api_client)
            mock_tag.assert_called_once_with(api_client)
            mock_syslog.assert_called_once_with(api_client)
            mock_region.assert_called_once_with(api_client)
            mock_schedule.assert_called_once_with(api_client)

    def test_nonexistent_service(self, api_client):
        """Test accessing a non-existent service."""
        with pytest.raises(AttributeError) as exc_info:
            # Attempt to access a service that doesn't exist
            api_client.nonexistent_service

        # Verify error message
        assert "'Scm' object has no attribute 'nonexistent_service'" in str(exc_info.value)

    def test_service_caching(self, api_client):
        """Test that services are cached after first access."""
        with patch("importlib.import_module") as mock_import:
            # Create mock service class
            mock_module = MagicMock()
            mock_address_class = MagicMock()
            mock_module.Address = mock_address_class
            mock_import.return_value = mock_module

            # Access the service multiple times
            service1 = api_client.address
            service2 = api_client.address

            # Verify the module was imported only once
            mock_import.assert_called_once_with("scm.config.objects.address")

            # Verify the service class was instantiated only once
            mock_address_class.assert_called_once_with(api_client)

            # Verify we got the same service instance both times
            assert service1 is service2

    def test_import_error_handling(self, api_client):
        """Test proper error handling when import fails."""
        with patch("importlib.import_module") as mock_import:
            # Simulate import error
            mock_import.side_effect = ImportError(
                "No module named 'scm.config.objects.nonexistent'"
            )

            # Attempt to access a valid service name but with import error
            with pytest.raises(AttributeError) as exc_info:
                api_client.address

            # Verify error message contains the import error
            assert "Failed to load service 'address'" in str(exc_info.value)

    def test_integration_with_regular_methods(self, api_client):
        """Test that regular methods still work with the dynamic attribute access."""
        # Mock the get method with a valid response format for JobStatusResponse
        # Use proper types based on the validation errors
        mock_response = {
            "data": [
                {
                    "id": "job-123",
                    "job_type": "commit",
                    "job_status": "3",  # String not int
                    "status_i": "3",  # String not int
                    "status_str": "FIN",
                    "result_i": "0",  # String not int
                    "result_str": "OK",
                    "insert_ts": "1625097600",  # Could be string or int depending on model
                    "start_ts": "1625097601",
                    "last_update": "1625097610",
                    "owner": "test_user",
                    "percent": "100",  # String not int
                    "details": "{}",  # String not dict
                    "job_result": "{}",  # String not dict
                    "type_i": "1",  # String not int
                    "type_str": "commit",
                    "uname": "test_user@example.com",
                }
            ],
            "count": 1,
            "total": 1,
        }

        # Mock the get method directly to avoid having to import the real model
        api_client.get = MagicMock(return_value=mock_response)

        # Also mock the JobStatusResponse to avoid model validation issues
        with patch("scm.client.JobStatusResponse") as mock_job_status:
            # Configure the mock to return a simple object with the data we need
            mock_instance = MagicMock()
            mock_instance.data = [MagicMock(status_str="FIN", result_str="OK")]
            mock_job_status.return_value = mock_instance

            # Call a regular method
            result = api_client.get_job_status("test_job_id")

            # Verify the method was called
            api_client.get.assert_called_once_with("/config/operations/v1/jobs/test_job_id")

            # Verify the mock was called with our response
            mock_job_status.assert_called_once_with(**mock_response)

            # Verify the result was properly processed
            assert result.data[0].status_str == "FIN"
            assert result.data[0].result_str == "OK"


class TestScmClientAlias:
    """Test suite for the ScmClient alias class."""

    def test_scm_client_alias(self):
        """Test that ScmClient is an alias for Scm with the same functionality."""
        from scm.client import ScmClient

        # Verify ScmClient is a subclass of Scm
        assert issubclass(ScmClient, Scm)

        # Patch OAuth2Client for both class instantiations
        with patch("scm.client.OAuth2Client") as mock_oauth:
            # Configure the mock OAuth2Client
            mock_oauth_instance = MagicMock()
            mock_oauth_instance.is_expired = False
            mock_oauth_instance.auth_request.client_id = "test_id"
            mock_oauth.return_value = mock_oauth_instance

            # Create instances of both classes
            scm = Scm(
                client_id="test_id",
                client_secret="test_secret",
                tsg_id="test_tsg",
            )

            scm_client = ScmClient(
                client_id="test_id",
                client_secret="test_secret",
                tsg_id="test_tsg",
            )

            # Verify both instances have the same methods
            scm_methods = set(dir(scm))
            scm_client_methods = set(dir(scm_client))
            assert scm_methods.issubset(scm_client_methods)

            # Verify both can access service attributes
            with patch("importlib.import_module") as mock_import:
                # Create mock service class
                mock_module = MagicMock()
                mock_address_class = MagicMock()
                mock_module.Address = mock_address_class
                mock_import.return_value = mock_module

                # Access the service from both instances
                scm.address
                scm_client.address

                # Verify the service class was instantiated for both
                assert mock_address_class.call_count == 2
