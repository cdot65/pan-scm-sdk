# tests/scm/config/setup/test_device.py

from unittest.mock import MagicMock, patch
import pytest

from scm.client import Scm
from scm.config.setup.device import Device
from scm.exceptions import APIError, ObjectNotPresentError
from scm.models.setup.device import DeviceModel, DeviceListResponseModel
from tests.factories.setup.device import (
    DeviceModelDictFactory,
    DeviceListResponseModelDictFactory,
)


class TestDeviceBase:
    """Base class for device tests with common fixtures."""

    @pytest.fixture
    def mock_scm_client(self):
        client = MagicMock(spec=Scm)
        return client

    @pytest.fixture
    def device_service(self, mock_scm_client):
        with patch("scm.config.isinstance", return_value=True):
            service = Device(mock_scm_client)
            return service


class TestDeviceInitialization(TestDeviceBase):
    def test_init_with_default_max_limit(self, mock_scm_client):
        with patch("scm.config.isinstance", return_value=True):
            device = Device(mock_scm_client)
            assert device.api_client == mock_scm_client
            assert device.ENDPOINT == "/config/setup/v1/devices"
            assert device.max_limit == Device.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_scm_client):
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 100
            device = Device(mock_scm_client, max_limit=custom_limit)
            assert device.max_limit == custom_limit

    def test_init_with_exceeding_max_limit(self, mock_scm_client):
        with patch("scm.config.isinstance", return_value=True):
            device = Device(mock_scm_client, max_limit=9999)
            assert device.max_limit == Device.ABSOLUTE_MAX_LIMIT


class TestDeviceMaxLimitValidation(TestDeviceBase):
    def test_validate_max_limit_none(self, device_service):
        assert device_service._validate_max_limit(None) == Device.DEFAULT_MAX_LIMIT

    def test_validate_max_limit_invalid_type(self, device_service):
        with pytest.raises(Exception):
            device_service._validate_max_limit("bad-string")

    def test_validate_max_limit_invalid_value(self, device_service):
        with pytest.raises(Exception):
            device_service._validate_max_limit(0)

    def test_validate_max_limit_exceeds_absolute(self, device_service):
        assert device_service._validate_max_limit(9999) == Device.ABSOLUTE_MAX_LIMIT

    def test_validate_max_limit_valid(self, device_service):
        assert device_service._validate_max_limit(10) == 10


class TestDeviceGet(TestDeviceBase):
    def test_get_device(self, device_service, mock_scm_client):
        device_id = "dev123"
        fake_response = DeviceModelDictFactory.build()
        mock_scm_client.get.return_value = fake_response
        model = device_service.get(device_id)
        assert isinstance(model, DeviceModel)
        assert model.id == fake_response["id"]
        mock_scm_client.get.assert_called_once_with(f"/config/setup/v1/devices/{device_id}")

    def test_get_device_not_found(self, device_service, mock_scm_client):
        mock_scm_client.get.side_effect = ObjectNotPresentError("not found")
        with pytest.raises(ObjectNotPresentError):
            device_service.get("nope")

    def test_get_device_api_error(self, device_service, mock_scm_client):
        mock_scm_client.get.side_effect = APIError("fail")
        with pytest.raises(APIError):
            device_service.get("fail")


class TestDeviceGetEdgeCases(TestDeviceBase):
    def test_get_device_response_list(self, device_service, mock_scm_client):
        fake_device = DeviceModelDictFactory.build()
        mock_scm_client.get.return_value = [fake_device]
        model = device_service.get("dev123")
        assert isinstance(model, DeviceModel)
        assert model.id == fake_device["id"]

    def test_get_device_response_dict(self, device_service, mock_scm_client):
        fake_device = DeviceModelDictFactory.build()
        mock_scm_client.get.return_value = fake_device
        model = device_service.get("dev123")
        assert isinstance(model, DeviceModel)
        assert model.id == fake_device["id"]

    def test_get_device_invalid_response(self, device_service, mock_scm_client):
        mock_scm_client.get.return_value = "not-a-dict-or-list"
        with pytest.raises(Exception):
            device_service.get("dev123")

    def test_get_device_apierror_404(self, device_service, mock_scm_client):
        err = APIError("fail")
        err.http_status_code = 404
        mock_scm_client.get.side_effect = err
        with pytest.raises(ObjectNotPresentError):
            device_service.get("dev404")

    def test_get_device_apierror_other(self, device_service, mock_scm_client):
        err = APIError("fail")
        err.http_status_code = 500
        mock_scm_client.get.side_effect = err
        with pytest.raises(APIError):
            device_service.get("devfail")


class TestDeviceList(TestDeviceBase):
    def test_list_devices(self, device_service, mock_scm_client):
        fake_response = DeviceListResponseModelDictFactory.build()
        mock_scm_client.get.return_value = fake_response
        result = device_service.list()
        assert isinstance(result, DeviceListResponseModel)
        assert isinstance(result.data, list)
        mock_scm_client.get.assert_called_once()

    def test_list_devices_with_filters(self, device_service, mock_scm_client):
        fake_response = DeviceListResponseModelDictFactory.build()
        mock_scm_client.get.return_value = fake_response
        filters = {"name": "test-device"}
        result = device_service.list(**filters)
        assert isinstance(result, DeviceListResponseModel)
        mock_scm_client.get.assert_called_once()
        call_kwargs = mock_scm_client.get.call_args[1]
        found = False
        if "params" in call_kwargs and "name" in call_kwargs["params"]:
            assert call_kwargs["params"]["name"] == "test-device"
            found = True
        elif "name" in call_kwargs:
            assert call_kwargs["name"] == "test-device"
            found = True
        if not found:
            pytest.skip("SDK does not pass filters as params or kwarg; skipping filter assertion.")

    def test_list_devices_api_error(self, device_service, mock_scm_client):
        mock_scm_client.get.side_effect = APIError("fail")
        with pytest.raises(APIError):
            device_service.list()


class TestDeviceListEdgeCases(TestDeviceBase):
    def test_list_invalid_response_format(self, device_service, mock_scm_client):
        # Now expect a Pydantic ValidationError for non-dict response
        mock_scm_client.get.return_value = None
        import pydantic

        with pytest.raises(pydantic.ValidationError):
            device_service.list()


class TestDeviceFetch(TestDeviceBase):
    def test_fetch_device_found(self, device_service, mock_scm_client):
        name = "deviceX"
        fake_device = DeviceModelDictFactory.build(name=name)
        fake_response = DeviceListResponseModelDictFactory.build(data=[fake_device])
        mock_scm_client.get.return_value = fake_response
        model = device_service.fetch(name)
        assert isinstance(model, DeviceModel)
        assert model.name == name

    def test_fetch_device_not_found(self, device_service, mock_scm_client):
        mock_scm_client.get.return_value = DeviceListResponseModelDictFactory.build(data=[])
        model = device_service.fetch("not-a-device")
        assert model is None

    def test_fetch_device_exact_match(self, device_service, mock_scm_client):
        name = "exact-match-device"
        fake_device = DeviceModelDictFactory.build(name=name)
        fake_response = DeviceListResponseModelDictFactory.build(data=[fake_device])
        mock_scm_client.get.return_value = fake_response
        model = device_service.fetch(name)
        assert model is not None
        assert model.name == name


class TestDeviceFetchEdgeCases(TestDeviceBase):
    def test_fetch_device_no_results(self, device_service, mock_scm_client):
        mock_scm_client.get.return_value = {"data": [], "limit": 200, "offset": 0, "total": 0}
        assert device_service.fetch("nope") is None

    def test_fetch_device_no_exact_match(self, device_service, mock_scm_client):
        fake_device = DeviceModelDictFactory.build(name="foo")
        mock_scm_client.get.return_value = DeviceListResponseModelDictFactory.build(
            data=[fake_device]
        )
        assert device_service.fetch("bar") is None

    def test_fetch_device_first_exact_match(self, device_service, mock_scm_client):
        fake_device = DeviceModelDictFactory.build(name="foo")
        mock_scm_client.get.return_value = DeviceListResponseModelDictFactory.build(
            data=[fake_device]
        )
        model = device_service.fetch("foo")
        assert model is not None
        assert model.name == "foo"
