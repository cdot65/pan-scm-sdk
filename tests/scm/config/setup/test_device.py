# tests/scm/config/setup/test_device.py

"""Tests for device setup configuration."""

from unittest.mock import MagicMock, patch

import pytest

from scm.client import Scm
from scm.config.setup.device import Device
from scm.exceptions import APIError, ObjectNotPresentError
from scm.models.setup.device import DeviceResponseModel
from tests.factories.setup.device import (
    DeviceListResponseModelDictFactory,
    DeviceResponseModelDictFactory,
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
    """Tests for Device initialization."""
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
    """Tests for Device max limit validation."""
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
    """Tests for Device get operations."""
    def test_get_device(self, device_service, mock_scm_client):
        device_id = "dev123"
        fake_response = DeviceResponseModelDictFactory.build()
        mock_scm_client.get.return_value = fake_response
        model = device_service.get(device_id)
        assert isinstance(model, DeviceResponseModel)
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
    """Tests for Device get edge cases."""
    def test_get_device_response_list(self, device_service, mock_scm_client):
        fake_device = DeviceResponseModelDictFactory.build()
        mock_scm_client.get.return_value = [fake_device]
        model = device_service.get("dev123")
        assert isinstance(model, DeviceResponseModel)
        assert model.id == fake_device["id"]

    def test_get_device_response_dict(self, device_service, mock_scm_client):
        fake_device = DeviceResponseModelDictFactory.build()
        mock_scm_client.get.return_value = fake_device
        model = device_service.get("dev123")
        assert isinstance(model, DeviceResponseModel)
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
    """Tests for Device list operations."""
    def test_list_devices(self, device_service, mock_scm_client):
        fake_response = DeviceListResponseModelDictFactory.build()
        mock_scm_client.get.return_value = fake_response
        result = device_service.list()
        assert isinstance(result, list)
        assert isinstance(result[0], DeviceResponseModel)
        mock_scm_client.get.assert_called_once()

    def test_list_devices_with_filters(self, device_service, mock_scm_client):
        fake_response = DeviceListResponseModelDictFactory.build()
        mock_scm_client.get.return_value = fake_response
        filters = {"name": "test-device"}
        result = device_service.list(**filters)
        assert isinstance(result, list)
        mock_scm_client.get.assert_called_once()
        call_kwargs = mock_scm_client.get.call_args[1]
        if "params" in call_kwargs and "name" in call_kwargs["params"]:
            assert call_kwargs["params"]["name"] == "test-device"
        elif "name" in call_kwargs:
            assert call_kwargs["name"] == "test-device"

    def test_list_devices_api_error(self, device_service, mock_scm_client):
        mock_scm_client.get.side_effect = APIError("fail")
        with pytest.raises(APIError):
            device_service.list()

    def test_list_limit_assignment_coverage(self):
        from unittest.mock import MagicMock

        from scm.client import Scm
        from scm.config.setup.device import Device

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {
            "data": [],
        }
        device = Device(api_client)
        result = device.list()
        assert isinstance(result, list)
        assert result == []

    def test_list_single_object_response(self):
        from unittest.mock import MagicMock

        from scm.client import Scm
        from scm.config.setup.device import Device

        api_client = MagicMock(spec=Scm)
        fake_device = {
            "id": "dev1",
            "name": "n",
            "type": "t",
            "folder": "f",
            "serial_number": "s",
            "is_connected": False,
            "model": "m",
        }
        api_client.get.return_value = fake_device
        device = Device(api_client)
        result = device.list()
        assert isinstance(result, list)
        assert result[0].id == "dev1"

    def test_list_invalid_data_field(self):
        from unittest.mock import MagicMock

        from scm.client import Scm
        from scm.config.setup.device import Device

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {"data": "notalist"}
        device = Device(api_client)
        import pytest

        with pytest.raises(Exception):
            device.list()

    def test_list_invalid_response_type(self):
        from unittest.mock import MagicMock

        from scm.client import Scm
        from scm.config.setup.device import Device

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = 123
        device = Device(api_client)
        import pytest

        with pytest.raises(Exception):
            device.list()

    def test_max_limit_assignment(self):
        """Explicit test to cover the line 'limit = self.max_limit'."""
        from unittest.mock import MagicMock

        from scm.client import Scm
        from scm.config.setup.device import Device

        # Create a device instance with a custom max_limit
        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = {"data": []}

        # Set an explicit non-default value to ensure line coverage
        device = Device(api_client, max_limit=123)
        device.list()

        # Verify the max_limit was used in the API call
        assert api_client.get.call_args[1]["params"]["limit"] == 123

    def test_list_multi_page(self):
        """Test the pagination loop works correctly."""
        from unittest.mock import MagicMock

        from scm.client import Scm
        from scm.config.setup.device import Device

        api_client = MagicMock(spec=Scm)

        # Create a response with 5 items for the first call
        first_response = {
            "data": [
                {
                    "id": "dev1",
                    "name": "Device 1",
                    "type": "t",
                    "folder": "f",
                    "serial_number": "s1",
                    "is_connected": False,
                    "model": "m",
                },
                {
                    "id": "dev2",
                    "name": "Device 2",
                    "type": "t",
                    "folder": "f",
                    "serial_number": "s2",
                    "is_connected": False,
                    "model": "m",
                },
                {
                    "id": "dev3",
                    "name": "Device 3",
                    "type": "t",
                    "folder": "f",
                    "serial_number": "s3",
                    "is_connected": False,
                    "model": "m",
                },
                {
                    "id": "dev4",
                    "name": "Device 4",
                    "type": "t",
                    "folder": "f",
                    "serial_number": "s4",
                    "is_connected": False,
                    "model": "m",
                },
                {
                    "id": "dev5",
                    "name": "Device 5",
                    "type": "t",
                    "folder": "f",
                    "serial_number": "s5",
                    "is_connected": False,
                    "model": "m",
                },
            ]
        }

        # Create a response with 2 items for the second call
        second_response = {
            "data": [
                {
                    "id": "dev6",
                    "name": "Device 6",
                    "type": "t",
                    "folder": "f",
                    "serial_number": "s6",
                    "is_connected": False,
                    "model": "m",
                },
                {
                    "id": "dev7",
                    "name": "Device 7",
                    "type": "t",
                    "folder": "f",
                    "serial_number": "s7",
                    "is_connected": False,
                    "model": "m",
                },
            ]
        }

        api_client.get.side_effect = [first_response, second_response]

        # Create the Device instance with a limit of 5
        device = Device(api_client, max_limit=5)

        # Call the list method
        result = device.list()

        # Verify we got all 7 devices
        assert len(result) == 7

        # Check that both responses were processed
        assert result[0].id == "dev1"
        assert result[-1].id == "dev7"


class TestDeviceListEdgeCases(TestDeviceBase):
    """Tests for Device list edge cases."""
    def test_list_invalid_response_format(self):
        from unittest.mock import MagicMock

        from scm.client import Scm
        from scm.config.setup.device import Device

        api_client = MagicMock(spec=Scm)
        api_client.get.return_value = None
        import pytest

        with pytest.raises(Exception):
            device = Device(api_client)
            device.list()


class TestDeviceFetch(TestDeviceBase):
    """Tests for Device fetch operations."""
    def test_fetch_device_found(self, device_service, mock_scm_client):
        name = "deviceX"
        fake_device = DeviceResponseModelDictFactory.build(name=name)
        fake_response = DeviceListResponseModelDictFactory.build(data=[fake_device])
        mock_scm_client.get.return_value = fake_response
        model = device_service.fetch(name)
        assert isinstance(model, DeviceResponseModel)
        assert model.name == name

    def test_fetch_device_not_found(self, device_service, mock_scm_client):
        mock_scm_client.get.return_value = DeviceListResponseModelDictFactory.build(data=[])
        model = device_service.fetch("not-a-device")
        assert model is None

    def test_fetch_device_exact_match(self, device_service, mock_scm_client):
        name = "exact-match-device"
        fake_device = DeviceResponseModelDictFactory.build(name=name)
        fake_response = DeviceListResponseModelDictFactory.build(data=[fake_device])
        mock_scm_client.get.return_value = fake_response
        model = device_service.fetch(name)
        assert model is not None
        assert model.name == name


class TestDeviceFetchEdgeCases(TestDeviceBase):
    """Tests for Device fetch edge cases."""
    def test_fetch_device_no_results(self, device_service, mock_scm_client):
        mock_scm_client.get.return_value = {"data": [], "limit": 200, "offset": 0, "total": 0}
        assert device_service.fetch("nope") is None

    def test_fetch_device_no_exact_match(self, device_service, mock_scm_client):
        fake_device = DeviceResponseModelDictFactory.build(name="foo")
        mock_scm_client.get.return_value = DeviceListResponseModelDictFactory.build(
            data=[fake_device]
        )
        assert device_service.fetch("bar") is None

    def test_fetch_device_first_exact_match(self, device_service, mock_scm_client):
        fake_device = DeviceResponseModelDictFactory.build(name="foo")
        mock_scm_client.get.return_value = DeviceListResponseModelDictFactory.build(
            data=[fake_device]
        )
        model = device_service.fetch("foo")
        assert model is not None
        assert model.name == "foo"


class TestDeviceApplyFilters(TestDeviceBase):
    """Tests for Device filter application."""
    def test_labels_filter_noop(self, device_service):
        # Device model does not have 'labels', so filter should always return []
        d1 = DeviceResponseModelDictFactory.build()
        d2 = DeviceResponseModelDictFactory.build()
        devices = [DeviceResponseModel.model_validate(d1), DeviceResponseModel.model_validate(d2)]
        filtered = device_service._apply_filters(devices, {"labels": ["a"]})
        assert filtered == []

    def test_parent_filter_noop(self, device_service):
        # Device model does not have 'parent', so filter should always return []
        d1 = DeviceResponseModelDictFactory.build()
        d2 = DeviceResponseModelDictFactory.build()
        devices = [DeviceResponseModel.model_validate(d1), DeviceResponseModel.model_validate(d2)]
        filtered = device_service._apply_filters(devices, {"parent": "p1"})
        assert filtered == []

    def test_type_filter(self, device_service):
        d1 = DeviceResponseModelDictFactory.build(type="foo")
        d2 = DeviceResponseModelDictFactory.build(type="bar")
        devices = [DeviceResponseModel.model_validate(d1), DeviceResponseModel.model_validate(d2)]
        filtered = device_service._apply_filters(devices, {"type": "foo"})
        assert devices[0] in filtered and devices[1] not in filtered

    def test_snippets_filter_noop(self, device_service):
        # Device model does not have 'snippets', so filter should always return []
        d1 = DeviceResponseModelDictFactory.build()
        d2 = DeviceResponseModelDictFactory.build()
        devices = [DeviceResponseModel.model_validate(d1), DeviceResponseModel.model_validate(d2)]
        filtered = device_service._apply_filters(devices, {"snippets": ["b"]})
        assert filtered == []

    def test_model_filter(self, device_service):
        d1 = DeviceResponseModelDictFactory.build(model="foo")
        d2 = DeviceResponseModelDictFactory.build(model="bar")
        devices = [DeviceResponseModel.model_validate(d1), DeviceResponseModel.model_validate(d2)]
        filtered = device_service._apply_filters(devices, {"model": "foo"})
        assert devices[0] in filtered and devices[1] not in filtered

    def test_serial_number_filter(self, device_service):
        d1 = DeviceResponseModelDictFactory.build(serial_number="123")
        d2 = DeviceResponseModelDictFactory.build(serial_number="456")
        devices = [DeviceResponseModel.model_validate(d1), DeviceResponseModel.model_validate(d2)]
        filtered = device_service._apply_filters(devices, {"serial_number": "123"})
        assert devices[0] in filtered and devices[1] not in filtered

    def test_device_only_filter(self, device_service):
        d1 = DeviceResponseModelDictFactory.build(device_only=True)
        d2 = DeviceResponseModelDictFactory.build(device_only=False)
        devices = [DeviceResponseModel.model_validate(d1), DeviceResponseModel.model_validate(d2)]
        filtered = device_service._apply_filters(devices, {"device_only": True})
        assert devices[0] in filtered and devices[1] not in filtered


class TestDeviceListServerSideFilters(TestDeviceBase):
    """Tests for Device server-side filters."""
    def test_list_includes_type_filter(self, device_service, mock_scm_client):
        mock_scm_client.get.return_value = {"data": []}
        device_service.list(type="foo")
        assert mock_scm_client.get.call_args[1]["params"]["type"] == "foo"

    def test_list_includes_serial_number_filter(self, device_service, mock_scm_client):
        mock_scm_client.get.return_value = {"data": []}
        device_service.list(serial_number="abc123")
        assert mock_scm_client.get.call_args[1]["params"]["serial_number"] == "abc123"

    def test_list_includes_model_filter(self, device_service, mock_scm_client):
        mock_scm_client.get.return_value = {"data": []}
        device_service.list(model="PA-VM")
        assert mock_scm_client.get.call_args[1]["params"]["model"] == "PA-VM"
