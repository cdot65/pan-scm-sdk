# tests/scm/config/objects/test_external_dynamic_lists.py

import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from requests.exceptions import HTTPError

from scm.config.objects.external_dynamic_lists import ExternalDynamicLists
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.objects.external_dynamic_lists import (
    ExternalDynamicListsResponseModel,
    ExternalDynamicListsCreateModel,
    ExternalDynamicListsUpdateModel,
)
from tests.factories import (
    ExternalDynamicListsCreateApiFactory,
    ExternalDynamicListsUpdateApiFactory,
    ExternalDynamicListsResponseFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestExternalDynamicListsBase:
    """Base class for EDL tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = ExternalDynamicLists(self.mock_scm)


class TestExternalDynamicListsList(TestExternalDynamicListsBase):
    def test_list_valid(self):
        mock_response = {
            "data": [
                ExternalDynamicListsResponseFactory.valid().model_dump(),
                ExternalDynamicListsResponseFactory.valid().model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        edls = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/external-dynamic-lists",
            params={"limit": 10000, "folder": "All"},
        )

        assert len(edls) == 2
        assert isinstance(edls[0], ExternalDynamicListsResponseModel)

    def test_list_folder_empty_error(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert '"folder" is not allowed to be empty' in str(exc_info.value)

    def test_list_no_container(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_multiple_containers(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Multiple containers provided",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="FolderA", snippet="SnippetA")

    def test_list_response_not_dict(self):
        self.mock_scm.get.return_value = ["not", "a", "dict"]
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="All")
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_missing_data(self):
        self.mock_scm.get.return_value = {}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="All")
        assert '"data" field missing in the response' in str(exc_info.value)

    def test_list_response_data_not_list(self):
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="All")
        assert '"data" field must be a list' in str(exc_info.value)


class TestExternalDynamicListsCreate(TestExternalDynamicListsBase):
    def test_create_valid(self):
        test_object = ExternalDynamicListsCreateApiFactory.valid()
        model = ExternalDynamicListsCreateModel(**test_object)
        mock_response = ExternalDynamicListsResponseFactory.from_request(model)
        self.mock_scm.post.return_value = mock_response.model_dump()

        created = self.client.create(test_object)
        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/external-dynamic-lists",
            json=test_object,
        )
        assert isinstance(created, ExternalDynamicListsResponseModel)
        assert created.name == model.name

    def test_create_no_container(self):
        data = ExternalDynamicListsCreateApiFactory.without_container()
        # Now data is a dict without container keys
        with pytest.raises(ValidationError) as exc_info:
            ExternalDynamicListsCreateModel(**data)
        assert "1 validation error for ExternalDynamicListsCreateModel" in str(
            exc_info.value
        )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_create_multiple_containers(self):
        data = ExternalDynamicListsCreateApiFactory.multiple_containers()
        # Data with multiple containers (folder + snippet)
        with pytest.raises(ValidationError) as exc_info:
            ExternalDynamicListsCreateModel(**data)
        assert "1 validation error for ExternalDynamicListsCreateModel" in str(
            exc_info.value
        )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_create_http_error_no_response_content(self):
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.create({"name": "test-edl", "folder": "My Folder"})

    def test_create_generic_exception(self):
        self.mock_scm.post.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.create({"name": "test-edl", "folder": "My Folder"})
        assert "Generic error" in str(exc_info.value)


class TestExternalDynamicListsGet(TestExternalDynamicListsBase):
    def test_get_valid(self):
        mock_response = ExternalDynamicListsResponseFactory.valid()
        self.mock_scm.get.return_value = mock_response.model_dump()

        retrieved = self.client.get(str(mock_response.id))
        self.mock_scm.get.assert_called_once_with(
            f"/config/objects/v1/external-dynamic-lists/{mock_response.id}"
        )
        assert isinstance(retrieved, ExternalDynamicListsResponseModel)
        assert retrieved.id == mock_response.id

    def test_get_object_not_found(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.get("nonexistent")
        # Check the API error response JSON
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"

    def test_get_generic_exception(self):
        self.mock_scm.get.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.get("some-id")
        assert "Generic error" in str(exc_info.value)


class TestExternalDynamicListsUpdate(TestExternalDynamicListsBase):
    def test_update_valid(self):
        update_data = ExternalDynamicListsUpdateApiFactory.valid()  # returns a dict
        update_model = ExternalDynamicListsUpdateModel(
            **update_data
        )  # convert to model
        # Create a mock response from the update_model
        mock_response = ExternalDynamicListsResponseFactory(**update_model.model_dump())
        self.mock_scm.put.return_value = mock_response.model_dump()

        updated = self.client.update(update_model)
        self.mock_scm.put.assert_called_once()
        assert isinstance(updated, ExternalDynamicListsResponseModel)
        assert updated.name == update_model.name

    def test_update_object_not_present(self):
        update_data = ExternalDynamicListsUpdateApiFactory.valid()
        update_model = ExternalDynamicListsUpdateModel(**update_data)
        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_model)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"

    def test_update_http_error_no_response_content(self):
        update_data = ExternalDynamicListsUpdateApiFactory.valid()
        update_model = ExternalDynamicListsUpdateModel(**update_data)
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.put.side_effect = HTTPError(response=mock_response)

        with pytest.raises(HTTPError):
            self.client.update(update_model)

    def test_update_generic_exception(self):
        update_data = ExternalDynamicListsUpdateApiFactory.valid()
        update_model = ExternalDynamicListsUpdateModel(**update_data)
        self.mock_scm.put.side_effect = Exception("Generic error")

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_model)
        assert "Generic error" in str(exc_info.value)


class TestExternalDynamicListsDelete(TestExternalDynamicListsBase):
    def test_delete_success(self):
        edl_id = "123e4567-e89b-12d3-a456-426655440000"
        self.mock_scm.delete.return_value = None
        self.client.delete(edl_id)
        self.mock_scm.delete.assert_called_once_with(
            f"/config/objects/v1/external-dynamic-lists/{edl_id}"
        )

    def test_delete_object_not_present(self):
        edl_id = "nonexistent-id"
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(edl_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"

    def test_delete_http_error_no_response_content(self):
        edl_id = "some-id"
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.delete.side_effect = HTTPError(response=mock_response)

        with pytest.raises(HTTPError):
            self.client.delete(edl_id)

    def test_delete_generic_exception(self):
        self.mock_scm.delete.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.delete("some-id")
        assert "Generic error" in str(exc_info.value)


class TestExternalDynamicListsFetch(TestExternalDynamicListsBase):
    def test_fetch_valid_predefined(self):
        mock_response = ExternalDynamicListsResponseFactory.predefined()
        self.mock_scm.get.return_value = mock_response.model_dump()

        fetched = self.client.fetch(name="predefined-edl", snippet="predefined")
        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/external-dynamic-lists",
            params={"snippet": "predefined", "name": "predefined-edl"},
        )
        assert fetched.snippet == "predefined"
        assert fetched.id is None
        assert fetched.type is None

    def test_fetch_valid_non_predefined(self):
        mock_response = ExternalDynamicListsResponseFactory.valid()
        self.mock_scm.get.return_value = mock_response.model_dump()

        fetched = self.client.fetch(
            name=mock_response.name, folder=mock_response.folder
        )
        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/external-dynamic-lists",
            params={"folder": mock_response.folder, "name": mock_response.name},
        )
        assert fetched.id == mock_response.id
        assert fetched.name == mock_response.name

    def test_fetch_object_not_found(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="nonexistent-edl", folder="My Folder")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"

    def test_fetch_empty_name(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"name" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="", folder="My Folder")

    def test_fetch_empty_container(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="test-edl", folder="")

    def test_fetch_no_container(self):
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="test-edl")

    def test_fetch_multiple_containers(self):
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="test-edl", folder="My Folder", snippet="My Snippet")

    def test_fetch_missing_id_field_non_predefined(self):
        self.mock_scm.get.return_value = {
            "name": "test-edl",
            "folder": "My Folder",
            "type": {
                "ip": {
                    "url": "http://example.com/edl.txt",
                    "recurring": {"daily": {"at": "03"}},
                }
            },
        }

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-edl", folder="My Folder")
        assert "Response missing 'id' field" in str(exc_info.value)

    def test_fetch_invalid_response_type(self):
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-edl", folder="My Folder")
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_fetch_http_error_no_content(self):
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-edl", folder="My Folder")

    def test_fetch_generic_exception(self):
        self.mock_scm.get.side_effect = Exception("Generic error")
        with pytest.raises(Exception):
            self.client.fetch(name="test-edl", folder="My Folder")


class TestExternalDynamicListsApplyFilters(TestExternalDynamicListsBase):
    def test_apply_filters_non_list_types(self):
        edls = []
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(edls, {"types": "ip"})
        # Check the exception's message field
        assert "'types' filter must be a list" in exc_info.value.message

    def test_apply_filters_unknown_types(self):
        edls = []
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(edls, {"types": ["unknown_type"]})
        assert "Unknown type(s) in filter: unknown_type" in exc_info.value.message

    def test_apply_filters_valid_type(self):
        # Modify the factory to accept kwargs
        # In factories.py, ensure ExternalDynamicListsResponseFactory.valid() can take **kwargs:
        # class ExternalDynamicListsResponseFactory(factory.Factory):
        #     ...
        #     @classmethod
        #     def valid(cls, **kwargs):
        #         data = {}
        #         return cls(**{**data, **kwargs})

        mock_edl = ExternalDynamicListsResponseFactory.valid(
            type={"ip": {"url": "test", "recurring": {"daily": {"at": "03"}}}}
        )
        filtered = self.client._apply_filters([mock_edl], {"types": ["ip"]})
        assert len(filtered) == 1
        assert filtered[0].name == mock_edl.name

    def test_apply_filters_no_match(self):
        mock_edl = ExternalDynamicListsResponseFactory.valid(
            type={"url": {"url": "test", "recurring": {"daily": {"at": "03"}}}}
        )
        filtered = self.client._apply_filters([mock_edl], {"types": ["ip"]})
        assert len(filtered) == 0
