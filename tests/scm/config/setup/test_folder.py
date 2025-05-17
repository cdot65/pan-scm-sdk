# tests/scm/config/setup/test_folder.py

"""Tests for folder setup configuration."""

# Standard library imports
from unittest.mock import MagicMock, patch

# External libraries
import pytest

# Local SDK imports
from scm.client import Scm
from scm.config.setup.folder import Folder
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.folder import (
    FolderResponseModel,
    FolderUpdateModel,
)
from tests.factories.setup.folder import (
    FolderCreateApiFactory,
    FolderResponseFactory,
    FolderUpdateApiFactory,
)


class TestFolderBase:
    """Base class for folder tests with common fixtures."""

    @pytest.fixture
    def mock_scm_client(self):
        """Create a properly mocked SCM client that passes type checks."""
        client = MagicMock(spec=Scm)
        return client

    @pytest.fixture
    def folder_service(self, mock_scm_client):
        """Create a Folder service with a mocked client for testing."""
        with patch("scm.config.isinstance", return_value=True):
            service = Folder(mock_scm_client)
            return service


class TestFolderInitialization(TestFolderBase):
    """Tests for Folder service initialization."""

    def test_init_with_default_max_limit(self, mock_scm_client):
        """Test initialization with default max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            folder = Folder(mock_scm_client)
            assert folder.api_client == mock_scm_client
            assert folder.ENDPOINT == "/config/setup/v1/folders"
            assert folder.max_limit == Folder.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_scm_client):
        """Test initialization with custom max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 100
            folder = Folder(mock_scm_client, max_limit=custom_limit)
            assert folder.max_limit == custom_limit

    def test_init_with_exceeding_max_limit(self, mock_scm_client):
        """Test initialization with max_limit exceeding the absolute maximum."""
        with patch("scm.config.isinstance", return_value=True):
            exceeding_limit = 10000
            folder = Folder(mock_scm_client, max_limit=exceeding_limit)
            assert folder.max_limit == Folder.ABSOLUTE_MAX_LIMIT


class TestFolderCreate(TestFolderBase):
    """Tests for Folder.create method."""

    def test_create_folder(self, folder_service, mock_scm_client):
        """Test creating a folder with minimum required fields."""
        # Setup test data
        folder_data = FolderCreateApiFactory()
        response_data = FolderResponseFactory.from_request(folder_data)

        # Mock API response
        mock_scm_client.post.return_value = response_data.model_dump()

        # Call create method (now expects a data dict)
        result = folder_service.create(folder_data.model_dump(exclude_unset=True))

        # Assert result is as expected
        assert isinstance(result, FolderResponseModel)
        assert result.name == folder_data.name
        assert result.parent == folder_data.parent

    def test_create_folder_with_labels(self, folder_service, mock_scm_client):
        """Test creating a folder with labels."""
        folder_data = FolderCreateApiFactory(labels=["red", "blue"])
        response_data = FolderResponseFactory.from_request(folder_data)
        mock_scm_client.post.return_value = response_data.model_dump()
        result = folder_service.create(folder_data.model_dump(exclude_unset=True))
        assert isinstance(result, FolderResponseModel)
        assert set(result.labels) == set(["red", "blue"])


class TestFolderGet(TestFolderBase):
    """Tests for Folder.get method."""

    def test_get_folder(self, folder_service, mock_scm_client):
        """Test retrieving a folder by ID."""
        # Setup test data
        folder_id = "12345678-1234-1234-1234-123456789012"
        mock_response = FolderResponseFactory(id=folder_id)

        # Mock API response
        mock_scm_client.get.return_value = mock_response.model_dump()

        # Call get method
        result = folder_service.get(folder_id)

        # Verify API call
        mock_scm_client.get.assert_called_once_with(f"{folder_service.ENDPOINT}/{folder_id}")

        # Verify response
        assert isinstance(result, FolderResponseModel)
        assert str(result.id) == folder_id
        assert result.name == mock_response.name
        assert result.parent == mock_response.parent

    def test_get_folder_404_and_other_error(self, folder_service, mock_scm_client):
        # 404 error -> ObjectNotPresentError
        mock_scm_client.get.side_effect = APIError("not found", http_status_code=404)
        with pytest.raises(ObjectNotPresentError):
            folder_service.get("doesnotexist")
        # 500 error -> APIError
        mock_scm_client.get.side_effect = APIError("fail", http_status_code=500)
        with pytest.raises(APIError):
            folder_service.get("fail")


class TestFolderFetch(TestFolderBase):
    """Tests for Folder.fetch method."""

    def test_fetch_folder_found(self, folder_service, mock_scm_client):
        """Test fetching a folder by name when it's found."""
        folder = FolderResponseFactory(name="target")
        api_response = {"data": [folder.model_dump()]}
        mock_scm_client.get.return_value = api_response
        result = folder_service.fetch(name="target")
        assert result is not None
        assert result.name == "target"

    def test_fetch_folder_empty_results(self, folder_service, mock_scm_client):
        """Test that fetch returns None when list returns empty results."""
        mock_scm_client.get.return_value = {"data": []}
        result = folder_service.fetch(name="any")
        assert result is None

    def test_fetch_folder_with_mocked_list(self, folder_service):
        """Comprehensive test covering different behaviors using mocked list method."""
        # Test case 1: Empty results
        with patch.object(folder_service, "list", return_value=[]):
            result = folder_service.fetch("test_name")
            assert result is None

        # Test case 2: One result matching the name
        test_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012", name="TestFolder", parent="parent-id"
        )
        with patch.object(folder_service, "list", return_value=[test_folder]):
            result = folder_service.fetch("TestFolder")
            assert result == test_folder

        # Test case 3: Multiple results including one exact match
        target_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012", name="TargetFolder", parent="parent-id"
        )
        child_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789013", name="ChildFolder", parent="TargetFolder"
        )
        other_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789014", name="OtherFolder", parent="parent-id"
        )
        with patch.object(
            folder_service, "list", return_value=[child_folder, target_folder, other_folder]
        ):
            result = folder_service.fetch("TargetFolder")
            assert result == target_folder

        # Test case 4: Multiple results but no exact match
        folder1 = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012", name="Folder1", parent="parent-id"
        )
        folder2 = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789013", name="Folder2", parent="parent-id"
        )
        with patch.object(folder_service, "list", return_value=[folder1, folder2]):
            result = folder_service.fetch("MissingFolder")
            assert result is None


class TestFolderList(TestFolderBase):
    """Tests for Folder.list method."""

    def test_list_folders(self, folder_service, mock_scm_client):
        """Test listing folders with default parameters."""
        # Setup test data
        mock_folders = [
            FolderResponseFactory().model_dump(),
            FolderResponseFactory().model_dump(),
            FolderResponseFactory().model_dump(),
        ]

        # Mock API response
        mock_scm_client.get.return_value = {"data": mock_folders}

        # Call list method
        results = folder_service.list()

        # Verify API call
        mock_scm_client.get.assert_called_once()
        args, kwargs = mock_scm_client.get.call_args
        assert args[0] == folder_service.ENDPOINT
        assert "limit" in kwargs["params"]
        assert kwargs["params"]["limit"] == folder_service.max_limit

        # Verify results
        assert len(results) == len(mock_folders)
        assert all(isinstance(folder, FolderResponseModel) for folder in results)

    def test_list_folders_name_filter(self, folder_service, mock_scm_client):
        """Test listing folders with a name filter (client-side)."""
        # Setup test data: two folders, only one matches the name exactly
        folder1 = FolderResponseFactory(name="foo")
        folder2 = FolderResponseFactory(name="bar")
        api_response = {"data": [folder1.model_dump(), folder2.model_dump()]}
        mock_scm_client.get.return_value = api_response
        # Call list with name filter (client-side filtering)
        results = folder_service.list()
        filtered = [f for f in results if f.name == "foo"]
        assert len(filtered) == 1
        assert filtered[0].name == "foo"

    def test_list_folders_exact_match_filter(self, folder_service, mock_scm_client):
        """Test listing folders with an exact match filter (client-side)."""
        folder1 = FolderResponseFactory(name="foo")
        folder2 = FolderResponseFactory(name="foo")
        folder3 = FolderResponseFactory(name="bar")
        api_response = {"data": [folder1.model_dump(), folder2.model_dump(), folder3.model_dump()]}
        mock_scm_client.get.return_value = api_response
        results = folder_service.list()
        filtered = [f for f in results if f.name == "foo"]
        assert len(filtered) == 2
        for f in filtered:
            assert f.name == "foo"

    def test_list_server_side_param_building(self, folder_service, mock_scm_client):
        # labels param
        mock_scm_client.get.return_value = {"data": []}
        folder_service.list(labels=["a", "b"])
        args, kwargs = mock_scm_client.get.call_args
        assert kwargs["params"]["labels"] == "a,b"
        # type param
        folder_service.list(type="foo")
        args, kwargs = mock_scm_client.get.call_args
        assert kwargs["params"]["type"] == "foo"
        # parent param
        folder_service.list(parent="pid")
        args, kwargs = mock_scm_client.get.call_args
        assert kwargs["params"]["parent"] == "pid"


class TestFolderUpdate(TestFolderBase):
    """Tests for Folder.update method."""

    def test_update_folder(self, folder_service, mock_scm_client):
        """Test updating a folder by direct mocking of BaseObject methods."""
        update_model = FolderUpdateApiFactory()
        response_data = FolderResponseFactory.from_request(update_model)
        mock_scm_client.put.return_value = response_data.model_dump()
        # Call update method (now expects a FolderUpdateModel)
        result = folder_service.update(update_model)
        assert isinstance(result, FolderResponseModel)
        assert result.id == update_model.id
        assert result.name == update_model.name


class TestFolderDelete(TestFolderBase):
    """Tests for Folder.delete method."""

    def test_delete_folder(self, folder_service, mock_scm_client):
        """Test deleting a folder."""
        # Setup test data
        folder_id = "12345678-1234-1234-1234-123456789012"

        # Call delete method
        folder_service.delete(folder_id)

        # Verify API call
        mock_scm_client.delete.assert_called_once_with(f"{folder_service.ENDPOINT}/{folder_id}")


class TestFolderMisc(TestFolderBase):
    """Tests for Folder service miscellaneous methods."""

    def test_validate_max_limit_none(self, folder_service):
        assert folder_service._validate_max_limit(None) == folder_service.DEFAULT_MAX_LIMIT

    def test_validate_max_limit_invalid_type(self, folder_service):
        with pytest.raises(InvalidObjectError) as exc:
            folder_service._validate_max_limit("not-an-int")
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc.value
        )

    def test_validate_max_limit_invalid_value(self, folder_service):
        with pytest.raises(InvalidObjectError) as exc:
            folder_service._validate_max_limit(0)
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc.value
        )

    def test_validate_max_limit_exceeds_absolute(self, folder_service):
        over = folder_service.ABSOLUTE_MAX_LIMIT + 100
        assert folder_service._validate_max_limit(over) == folder_service.ABSOLUTE_MAX_LIMIT

    def test_validate_max_limit_valid(self, folder_service):
        assert folder_service._validate_max_limit(123) == 123

    def test_apply_filters_all_branches(self):
        from scm.models.setup.folder import FolderResponseModel

        base = dict(
            name="foo",
            parent="p",
            labels=["a", "b"],
            type="t",
            snippets=["s1"],
            model="m",
            serial_number="sn",
            device_only=True,
        )
        folder = FolderResponseModel(id="baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e", **base)
        # labels
        out = Folder._apply_filters([folder], {"labels": ["a"]})
        assert out
        # parent
        out = Folder._apply_filters([folder], {"parent": "p"})
        assert out
        # type
        out = Folder._apply_filters([folder], {"type": "t"})
        assert out
        # snippets
        out = Folder._apply_filters([folder], {"snippets": ["s1"]})
        assert out
        # model
        out = Folder._apply_filters([folder], {"model": "m"})
        assert out
        # serial_number
        out = Folder._apply_filters([folder], {"serial_number": "sn"})
        assert out
        # device_only
        out = Folder._apply_filters([folder], {"device_only": True})
        assert out
        # no filters
        out = Folder._apply_filters([folder], {})
        assert out

    def test_list_invalid_response_format(self, folder_service, mock_scm_client):
        mock_scm_client.get.return_value = "not-a-dict"
        with pytest.raises(InvalidObjectError):
            folder_service.list()

    def test_list_data_not_list(self, folder_service, mock_scm_client):
        mock_scm_client.get.return_value = {"data": "notalist"}
        with pytest.raises(InvalidObjectError):
            folder_service.list()

    def test_list_single_object_response(self, folder_service, mock_scm_client):
        from scm.models.setup.folder import FolderResponseModel

        folder = FolderResponseFactory()
        mock_scm_client.get.return_value = folder.model_dump()
        results = folder_service.list()
        assert isinstance(results[0], FolderResponseModel)

    def test_list_pagination(self, folder_service, mock_scm_client):
        # Simulate two pages
        page1 = [FolderResponseFactory().model_dump() for _ in range(2)]
        page2 = [FolderResponseFactory().model_dump() for _ in range(1)]

        def side_effect(*args, **kwargs):
            offset = kwargs["params"]["offset"]
            if offset == 0:
                return {"data": page1}
            else:
                return {"data": page2}

        mock_scm_client.get.side_effect = side_effect
        folder_service.max_limit = 2
        results = folder_service.list()
        assert len(results) == 3

    def test_update_folder_api_error(self, folder_service, mock_scm_client):
        update_model = FolderUpdateModel(
            id="baf4dc4c-9ea2-4a3d-92bb-6f8a9e60822e", name="n", parent="p"
        )
        mock_scm_client.put.side_effect = APIError("fail", http_status_code=500)
        with pytest.raises(APIError):
            folder_service.update(update_model)

    def test_delete_folder_not_found(self, folder_service, mock_scm_client):
        mock_scm_client.delete.side_effect = APIError("fail", http_status_code=404)
        with pytest.raises(ObjectNotPresentError):
            folder_service.delete("notfound")

    def test_delete_folder_other_api_error(self, folder_service, mock_scm_client):
        mock_scm_client.delete.side_effect = APIError("fail", http_status_code=500)
        with pytest.raises(APIError):
            folder_service.delete("notfound")

    def test__get_paginated_results_data(self, folder_service, mock_scm_client):
        # Patch api_client.get to return dict with 'data'
        endpoint = "endpoint"
        params = {"a": 1}
        mock_scm_client.get.return_value = {"data": [1, 2, 3]}
        out = folder_service._get_paginated_results(endpoint, params, 10, 0)
        assert out == [1, 2, 3]

    def test__get_paginated_results_list(self, folder_service, mock_scm_client):
        endpoint = "endpoint"
        params = {"a": 1}
        mock_scm_client.get.return_value = [4, 5]
        out = folder_service._get_paginated_results(endpoint, params, 10, 0)
        assert out == [4, 5]

    def test__get_paginated_results_unexpected(self, folder_service, mock_scm_client):
        endpoint = "endpoint"
        params = {"a": 1}
        mock_scm_client.get.return_value = "weird"
        out = folder_service._get_paginated_results(endpoint, params, 10, 0)
        assert out == []
