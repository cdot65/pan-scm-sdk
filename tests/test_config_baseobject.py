# tests/test_config_baseobject.py

import pytest
from unittest.mock import MagicMock
from scm.config import BaseObject
from scm.client import Scm


class SampleObject(BaseObject):
    ENDPOINT = "/test-endpoint"


@pytest.fixture
def mock_api_client():
    mock_client = MagicMock(spec=Scm)
    return mock_client


def test_baseobject_init(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    assert test_object.api_client == mock_api_client


def test_baseobject_create(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    mock_api_client.post.return_value = {"id": "123", "name": "test"}

    data = {"name": "test"}
    response = test_object.create(data)

    mock_api_client.post.assert_called_once_with("/test-endpoint", json=data)
    assert response == {"id": "123", "name": "test"}


def test_baseobject_get(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    object_id = "123"
    mock_api_client.get.return_value = {"id": "123", "name": "test"}

    response = test_object.get(object_id)

    mock_api_client.get.assert_called_once_with("/test-endpoint/123")
    assert response == {"id": "123", "name": "test"}


def test_baseobject_update(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    object_id = "123"
    data = {"name": "updated"}
    mock_api_client.put.return_value = {"id": "123", "name": "updated"}

    response = test_object.update(object_id, data)

    mock_api_client.put.assert_called_once_with("/test-endpoint/123", json=data)
    assert response == {"id": "123", "name": "updated"}


def test_baseobject_delete(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    object_id = "123"

    test_object.delete(object_id)

    mock_api_client.delete.assert_called_once_with("/test-endpoint/123")


def test_baseobject_list(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    mock_api_client.get.return_value = {
        "data": [{"id": "123", "name": "test"}],
        "total": 1,
    }

    filters = {"filter1": "value1", "filter2": None}
    response = test_object.list(**filters)

    expected_params = {"filter1": "value1"}  # filter2 is None, so it should be excluded
    mock_api_client.get.assert_called_once_with(
        "/test-endpoint", params=expected_params
    )
    assert response == [{"id": "123", "name": "test"}]


def test_baseobject_list_empty_response(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    mock_api_client.get.return_value = {}  # No 'data' key

    response = test_object.list()

    mock_api_client.get.assert_called_once_with("/test-endpoint", params={})
    assert response == []  # Should return an empty list


def test_baseobject_list_no_filters(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    mock_api_client.get.return_value = {
        "data": [{"id": "123", "name": "test"}],
        "total": 1,
    }

    response = test_object.list()

    mock_api_client.get.assert_called_once_with("/test-endpoint", params={})
    assert response == [{"id": "123", "name": "test"}]


from scm.exceptions import APIError


def test_baseobject_create_api_error(mock_api_client):
    test_object = SampleObject(api_client=mock_api_client)
    mock_api_client.post.side_effect = APIError("API Error")

    data = {"name": "test"}

    with pytest.raises(APIError) as exc_info:
        test_object.create(data)

    assert "API Error" in str(exc_info.value)
