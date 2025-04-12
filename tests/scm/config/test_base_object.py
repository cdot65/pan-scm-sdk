# tests/scm/config/test_base_object.py

from unittest.mock import MagicMock

import pytest

from scm.client import Scm
from scm.config import BaseObject
from scm.models.operations import (CandidatePushResponseModel, JobListResponse,
                                   JobStatusResponse)


@pytest.mark.usefixtures("load_env")
class TestBaseObject:
    """Tests for BaseObject class."""

    class MockConfigObject(BaseObject):
        """Mock implementation of BaseObject for testing."""

        ENDPOINT = "/api/v1/test-objects"

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        # Mock basic HTTP methods
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()

        # Mock API-specific methods
        self.mock_scm.list_jobs = MagicMock()
        self.mock_scm.get_job_status = MagicMock()
        self.mock_scm.commit = MagicMock()

        self.test_object = self.MockConfigObject(self.mock_scm)

    def test_initialization(self):
        """
        **Objective:** Test BaseObject initialization.
        **Workflow:**
            1. Verifies proper initialization with API client
            2. Checks endpoint setting
        """
        assert isinstance(self.test_object.api_client, Scm)
        assert self.test_object.ENDPOINT == "/api/v1/test-objects"

    def test_create_method(self):
        """
        **Objective:** Test create method of BaseObject.
        **Workflow:**
            1. Tests basic object creation
            2. Verifies proper API call
            3. Validates response handling
        """
        test_data = {"name": "test", "value": "data"}
        mock_response = {"id": "123", **test_data}
        self.mock_scm.post.return_value = mock_response  # noqa

        response = self.test_object.create(test_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/api/v1/test-objects", json=test_data
        )
        assert response == mock_response
        assert response["id"] == "123"
        assert response["name"] == "test"

    def test_get_method(self):
        """
        **Objective:** Test get method of BaseObject.
        **Workflow:**
            1. Tests object retrieval
            2. Verifies endpoint construction
            3. Validates response handling
        """
        object_id = "123"
        mock_response = {"id": object_id, "name": "test"}
        self.mock_scm.get.return_value = mock_response  # noqa

        response = self.test_object.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/api/v1/test-objects/{object_id}"
        )
        assert response == mock_response
        assert response["id"] == object_id

    def test_update_method(self):
        """
        **Objective:** Test update method of BaseObject.
        **Workflow:**
            1. Tests object update
            2. Verifies proper endpoint construction
            3. Validates payload handling
        """
        update_data = {"id": "123", "name": "updated_test", "value": "new_data"}
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        response = self.test_object.update(update_data)

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/api/v1/test-objects/{update_data['id']}", json=update_data
        )
        assert response == mock_response

    def test_delete_method(self):
        """
        **Objective:** Test delete method of BaseObject.
        **Workflow:**
            1. Tests object deletion
            2. Verifies endpoint construction
            3. Validates proper API call
        """
        object_id = "123"
        self.mock_scm.delete.return_value = None  # noqa

        self.test_object.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/api/v1/test-objects/{object_id}"
        )

    def test_list_method(self):
        """
        **Objective:** Test list method of BaseObject.
        **Workflow:**
            1. Tests object listing with various filters
            2. Verifies parameter handling
            3. Validates response processing
        """
        mock_response = {
            "data": [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}],
            "total": 2,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with no filters
        response = self.test_object.list()
        self.mock_scm.get.assert_called_with("/api/v1/test-objects", params={})  # noqa
        assert response == mock_response["data"]

        # Test with filters
        filters = {
            "name": "test1",
            "type": "example",
            "null_filter": None,  # Should be excluded
        }
        response = self.test_object.list(**filters)
        self.mock_scm.get.assert_called_with(  # noqa
            "/api/v1/test-objects", params={"name": "test1", "type": "example"}
        )
        assert response == mock_response["data"]

    def test_list_method_empty_response(self):
        """
        **Objective:** Test list method with empty response.
        **Workflow:**
            1. Tests handling of empty response
            2. Verifies default return value
        """
        mock_response = {}
        self.mock_scm.get.return_value = mock_response  # noqa

        response = self.test_object.list()
        assert response == []

    def test_update_method_missing_id(self):
        """
        **Objective:** Test update method with missing ID.
        **Workflow:**
            1. Tests error handling when ID is missing
            2. Verifies proper error raising
        """
        update_data = {"name": "test", "value": "data"}

        with pytest.raises(KeyError) as exc_info:
            self.test_object.update(update_data)
        assert "'id'" in str(exc_info.value)

    def test_endpoint_inheritance(self):
        """
        **Objective:** Test endpoint inheritance behavior.
        **Workflow:**
            1. Tests endpoint definition requirement
            2. Verifies error when ENDPOINT is not defined
        """

        class InvalidObject(BaseObject):
            # Intentionally not defining ENDPOINT
            pass

        with pytest.raises(AttributeError) as exc_info:
            InvalidObject(self.mock_scm)  # noqa
        assert "ENDPOINT must be defined in the subclass" in str(exc_info.value)

    def test_api_client_type_check(self):
        """
        **Objective:** Test API client type validation.
        **Workflow:**
            1. Tests initialization with invalid client type
            2. Verifies type checking
        """
        invalid_client = {"not": "a client"}

        with pytest.raises(TypeError) as exc_info:
            self.MockConfigObject(invalid_client)  # noqa
        assert "api_client must be an instance of Scm" in str(exc_info.value)

    def test_create_method_payload_validation(self):
        """
        **Objective:** Test create method payload handling.
        **Workflow:**
            1. Tests various payload types
            2. Verifies proper handling of different data structures
        """
        # Test with empty data
        empty_data = {}
        self.test_object.create(empty_data)
        self.mock_scm.post.assert_called_with(  # noqa
            "/api/v1/test-objects", json=empty_data
        )

        # Test with nested data
        nested_data = {
            "name": "test",
            "config": {"setting1": "value1", "setting2": ["item1", "item2"]},
        }
        self.test_object.create(nested_data)
        self.mock_scm.post.assert_called_with(  # noqa
            "/api/v1/test-objects",
            json=nested_data,
        )

    def test_list_jobs(self):
        """
        **Objective:** Test list_jobs method return value.
        **Workflow:**
            1. Tests job listing with pagination and filtering
            2. Verifies return type and value
            3. Validates parameter passing
        """
        mock_response = {
            "data": [
                {
                    "id": "1",
                    "status_str": "FIN",
                    "job_result": "2",
                    "job_status": "2",
                    "job_type": "53",
                    "type_str": "CommitAndPush",
                    "result_str": "OK",
                    "start_ts": "2024-11-30T10:00:00",
                    "uname": "test@example.com",
                    "parent_id": "0",
                }
            ],
            "total": 1,
            "limit": 100,
            "offset": 0,
        }
        self.mock_scm.list_jobs.return_value = JobListResponse(**mock_response)

        # Test with default parameters
        response = self.test_object.list_jobs()
        assert isinstance(response, JobListResponse)
        self.mock_scm.list_jobs.assert_called_with(limit=100, offset=0, parent_id=None)

        # Test with custom parameters
        response = self.test_object.list_jobs(limit=50, offset=10, parent_id="parent123")
        assert isinstance(response, JobListResponse)
        self.mock_scm.list_jobs.assert_called_with(limit=50, offset=10, parent_id="parent123")

    def test_get_job_status(self):
        """
        **Objective:** Test get_job_status method return value.
        **Workflow:**
            1. Tests job status retrieval
            2. Verifies return type and value
            3. Validates parameter passing
        """
        mock_response = {
            "data": [
                {
                    "id": "1595",
                    "status_str": "FIN",
                    "status_i": "2",
                    "start_ts": "2024-11-30T10:00:00",
                    "insert_ts": "2024-11-30T10:00:00",
                    "last_update": "2024-11-30T10:02:00",
                    "job_status": "2",
                    "job_type": "53",
                    "job_result": "2",
                    "result_i": "2",
                    "result_str": "OK",
                    "details": "completed",
                    "owner": "test",
                    "percent": "100",
                    "type_i": "53",
                    "type_str": "CommitAndPush",
                    "uname": "test-user",
                }
            ]
        }
        self.mock_scm.get_job_status.return_value = JobStatusResponse(**mock_response)

        response = self.test_object.get_job_status("1595")
        assert isinstance(response, JobStatusResponse)
        assert response.data[0].id == "1595"
        assert response.data[0].status_str == "FIN"
        self.mock_scm.get_job_status.assert_called_with("1595")

    def test_commit(self):
        """
        **Objective:** Test commit method return value.
        **Workflow:**
            1. Tests configuration commit operation
            2. Verifies return type and value
            3. Validates parameter passing with different combinations
        """
        mock_response = {
            "success": True,
            "job_id": "1586",
            "message": "CommitAndPush job enqueued with jobid 1586",
        }
        self.mock_scm.commit.return_value = CandidatePushResponseModel(**mock_response)

        # Test with minimal required parameters
        response = self.test_object.commit(folders=["folder1"], description="Test commit")
        assert isinstance(response, CandidatePushResponseModel)
        assert response.success is True
        assert response.job_id == "1586"
        self.mock_scm.commit.assert_called_with(
            folders=["folder1"],
            description="Test commit",
            admin=None,
            sync=False,
            timeout=300,
        )

        # Test with all parameters
        response = self.test_object.commit(
            folders=["folder1", "folder2"],
            description="Test commit with all params",
            admin=["admin@example.com"],
            sync=True,
            timeout=600,
        )
        assert isinstance(response, CandidatePushResponseModel)
        self.mock_scm.commit.assert_called_with(
            folders=["folder1", "folder2"],
            description="Test commit with all params",
            admin=["admin@example.com"],
            sync=True,
            timeout=600,
        )

        # Test with username of "all" passed in admins
        response = self.test_object.commit(
            folders=["folder1", "folder2"],
            description="Test commit with all params",
            admin=["all"],
            sync=True,
            timeout=600,
        )
        assert isinstance(response, CandidatePushResponseModel)
        self.mock_scm.commit.assert_called_with(
            folders=["folder1", "folder2"],
            description="Test commit with all params",
            admin=["all"],
            sync=True,
            timeout=600,
        )
