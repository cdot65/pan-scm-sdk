# TODO: Implement Devices SDK Endpoint

This checklist is derived from `project3.md` for tracking the implementation of the Devices SDK functionality.

## Models (`scm/models/config/setup/devices.py`)

- [ ] Define `InstalledLicenseModel`.
- [ ] Define `AvailableLicenseModel` (handle potential `available_licensess` typo via alias).
- [ ] Define `DeviceGetResponseModel` with all required and optional fields identified in API responses.
       - [ ] Include `id`, `name`, `display_name`, `hostname`, `description`, `serial_number`, `folder`, `type`, `family`, `model`, `is_connected`, `connected_since`, etc.
       - [ ] Include `installed_licenses: Optional[List[InstalledLicenseModel]]`.
       - [ ] Include `available_licenses: Optional[List[AvailableLicenseModel]] = Field(alias="available_licensess")` (or similar handling).
- [ ] Add docstrings to all models.
- [ ] Update `scm/models/config/setup/__init__.py`.

## Service Class (`scm/config/setup/devices.py`)

- [ ] Create `Devices` class inheriting from `BaseObject`.
- [ ] Set `ENDPOINT = "/devices"`.
- [ ] Implement `get(self, id: str) -> DeviceGetResponseModel` method.
       - [ ] Call `GET /devices/{id}` endpoint.
       - [ ] Handle API returning the result within a list `[{...}]`.
- [ ] Implement `list(self, **kwargs) -> List[DeviceGetResponseModel]` method.
       - [ ] Call `GET /devices` endpoint.
       - [ ] Implement pagination logic (using `limit`, `offset`).
       - [ ] Add support for potential filtering kwargs if discovered.
- [ ] Add docstrings to the class and methods.
- [ ] Update `scm/config/setup/__init__.py`.

## Integration

- [ ] Register `Devices` service with the main `ScmClient` (e.g., update `service_imports` in `scm/client.py` or similar).

## Testing

### Factories (`tests/factories/config/setup/devices_factory.py`)

- [ ] Create `DevicesFactory` class.
- [ ] Implement factory logic to generate test data for `DeviceGetResponseModel` (including nested models).
- [ ] Update `tests/factories/config/setup/__init__.py`.

### Model Tests (`tests/models/config/setup/test_devices.py`)

- [ ] Create test file.
- [ ] Write tests for `InstalledLicenseModel`.
- [ ] Write tests for `AvailableLicenseModel`.
- [ ] Write tests for `DeviceGetResponseModel` (valid data, optional fields, potential edge cases).
- [ ] Write tests for any model validation rules.

### Service Tests (`tests/config/setup/test_devices.py`)

- [ ] Create test file.
- [ ] Write tests for `Devices.get()` method:
       - [ ] Mock `ScmClient._get`.
       - [ ] Verify correct endpoint (`/devices/{id}`).
       - [ ] Verify handling of list response format.
       - [ ] Verify successful response parsing.
       - [ ] Test error handling (e.g., 404 -> `ObjectNotPresentError`).
- [ ] Write tests for `Devices.list()` method:
       - [ ] Mock `ScmClient._list`.
       - [ ] Verify correct endpoint (`/devices`).
       - [ ] Verify pagination parameter handling (`limit`, `offset`).
       - [ ] Verify successful response parsing.
       - [ ] Test error handling.

## Documentation

- [ ] Add/update Google-style docstrings for all new/modified models, classes, and methods.
- [ ] Create usage examples for `client.setup.devices.get(...)`.
- [ ] Create usage examples for `client.setup.devices.list(...)`.
- [ ] Review and update MkDocs configuration if necessary to include the new module.

## Code Quality & Final Checks

- [ ] Run `ruff check --fix .`.
- [ ] Run `ruff format .`.
- [ ] Run `pytest tests/config/setup/test_devices.py` and `pytest tests/models/config/setup/test_devices.py`.
- [ ] Verify test coverage meets project standards (>80% for new files).
