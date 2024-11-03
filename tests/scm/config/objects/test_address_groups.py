# tests/scm/config/objects/test_address_groups.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import AddressGroup
from scm.exceptions import ValidationError, NotFoundError, APIError
from scm.models.objects import AddressGroupResponseModel, AddressGroupCreateModel
from scm.models.objects.address_group import DynamicFilter

from tests.factories import (
    AddressGroupStaticFactory,
    AddressGroupDynamicFactory,
)

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestAddressGroupBase:
    """Base class for Address Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AddressGroup(self.mock_scm)  # noqa


class TestAddressGroupAPI(TestAddressGroupBase):
    """Tests for Address Group API operations."""

    def test_list_address_groups(self):
        """
        Test listing address groups.

        **Objective:** Test listing all address groups.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing address groups.
            2. Calls the `list` method of `self.client` with a filter parameter (`folder="All"`).
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of address groups, checking their types and attributes.
        """
        mock_response = {
            "data": [
                {
                    "id": "a952ca48-9127-4012-be3b-71741ddd5767",
                    "name": "DAG_test",
                    "folder": "All",
                    "dynamic": {
                        "filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
                    },
                },
                {
                    "id": "54b2087b-b733-46d9-a0ff-fe9ee4bdcbac",
                    "name": "Moishy_Test",
                    "folder": "Shared",
                    "description": "test",
                    "dynamic": {
                        "filter": "'Api test' or 'Hamuzim' and 'best-practice'"
                    },
                },
                {
                    "id": "b2a7a7a1-cb15-463d-88be-80729bb1be37",
                    "name": "Moishy Api",
                    "folder": "Shared",
                    "description": "test",
                    "static": ["shachar_test2"],
                },
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        address_groups = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={"folder": "All"},
        )
        assert isinstance(address_groups, list)
        assert isinstance(address_groups[0], AddressGroupResponseModel)
        assert len(address_groups) == 3
        assert address_groups[0].name == "DAG_test"
        assert (
            address_groups[0].dynamic.filter
            == "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
        )

    def test_create_address_group_with_dynamic_filter(self):
        """
        Test creating an address group with a dynamic filter.

        **Objective:** Test creating an address group with a dynamic filter.
        **Workflow:**
            1. Uses `AddressGroupDynamicFactory` to create a test address group with dynamic filters.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the address group data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created address group's attributes.
        """
        test_address_group = AddressGroupDynamicFactory()
        mock_response = test_address_group.model_dump()
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_address_group.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            json=test_address_group.model_dump(exclude_unset=True),
        )
        assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
        assert created_group.name == test_address_group.name
        assert created_group.dynamic.filter == test_address_group.dynamic.filter
        assert created_group.folder == test_address_group.folder

    def test_create_address_group_with_static_entries(self):
        """
        Test creating an address group with static entries.

        **Objective:** Test creating an address group with static entries.
        **Workflow:**
            1. Uses `AddressGroupStaticFactory` to create a test address group with dynamic filters.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the address group data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created address group's attributes.
        """
        test_address_group = AddressGroupStaticFactory()
        mock_response = test_address_group.model_dump()
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_address_group.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            json=test_address_group.model_dump(exclude_unset=True),
        )
        assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
        assert created_group.name == test_address_group.name
        assert created_group.folder == test_address_group.folder

    def test_get_address_group(self):
        """
        Test retrieving an address group by ID.

        **Objective:** Test retrieving an address group by its ID.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an address group by ID.
            2. Calls the `get` method of `self.client` with a specific group ID.
            3. Asserts that the mocked service was called with the correct URL.
            4. Validates the returned address group's attributes.
        """
        group_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": group_id,
            "name": "TestGroup",
            "folder": "Shared",
            "description": "A test address group",
            "static": ["Address1", "Address2"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        address_group = self.client.get(group_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{group_id}"
        )
        assert isinstance(address_group, AddressGroupResponseModel)
        assert address_group.id == group_id
        assert address_group.name == "TestGroup"
        assert address_group.description == "A test address group"
        assert address_group.static == ["Address1", "Address2"]

    def test_update_address_group(self):
        """
        Test updating an address group.

        **Objective:** Test updating an existing address group.
        **Workflow:**
            1. Sets up the update data for the address group.
            2. Sets up a mock response that includes the updated data.
            3. Calls the `update` method of `self.client` with the update data.
            4. Asserts that the mocked service was called with the correct URL and data.
            5. Validates the updated address group's attributes.
        """
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedGroup",
            "folder": "Shared",
            "description": "An updated address group",
            "static": ["Address3", "Address4"],
        }

        mock_response = update_data.copy()

        self.mock_scm.put.return_value = mock_response  # noqa
        updated_group = self.client.update(update_data)

        # Prepare the expected payload by excluding 'id'
        expected_payload = update_data.copy()
        expected_payload.pop("id")

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{update_data['id']}",
            json=expected_payload,
        )
        assert isinstance(updated_group, AddressGroupResponseModel)
        assert updated_group.id == update_data["id"]
        assert updated_group.name == "UpdatedGroup"
        assert updated_group.description == "An updated address group"
        assert updated_group.static == ["Address3", "Address4"]

    def test_fetch_address_group(self):
        """
        Test fetching an address group by name.

        **Objective:** Test retrieving an address group by its name using the `fetch` method.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an address group by name.
            2. Calls the `fetch` method of `self.client` with a specific name and container.
            3. Asserts that the mocked service was called with the correct URL and parameters.
            4. Validates the returned address group's attributes.
        """
        group_name = "TestGroup"
        folder_name = "Shared"
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": group_name,
            "folder": folder_name,
            "description": "A test address group",
            "static": ["Address1", "Address2"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        address_group = self.client.fetch(
            name=group_name,
            folder=folder_name,
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "folder": folder_name,
                "name": group_name,
            },
        )

        # Validate the returned address group
        assert isinstance(address_group, dict)
        assert address_group["id"] == mock_response["id"]
        assert address_group["name"] == group_name
        assert address_group["description"] == "A test address group"
        assert address_group["static"] == ["Address1", "Address2"]

    def test_fetch_address_group_not_found(self):
        """
        Test fetching an address group by name that does not exist.

        **Objective:** Test that fetching a non-existent address group raises NotFoundError.
        **Workflow:**
            1. Mocks the API response to return an empty 'data' list.
            2. Calls the `fetch` method with a name that does not exist.
            3. Asserts that NotFoundError is raised.
        """
        group_name = "NonExistentGroup"
        folder_name = "Shared"
        mock_response = {"data": []}

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method and expect a NotFoundError
        with pytest.raises(NotFoundError) as exc_info:
            self.client.fetch(
                name=group_name,
                folder=folder_name,
            )

        # Optionally, assert the exception message
        assert str(exc_info.value) == f"Address group '{group_name}' not found."

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "folder": folder_name,
                "name": group_name,
            },
        )

    def test_fetch_address_group_multiple_found(self):
        """
        Test fetching an address group by name when multiple are found.

        **Objective:** Test that fetching an address group by name raises APIError when multiple groups are found.
        **Workflow:**
            1. Mocks the API response to return multiple address groups.
            2. Calls the `fetch` method with a name that matches multiple groups.
            3. Asserts that APIError is raised.
        """
        group_name = "DuplicateGroup"
        folder_name = "Shared"
        mock_response = {
            "data": [
                {
                    "id": "id1",
                    "name": group_name,
                    "folder": folder_name,
                    "static": ["Address1"],
                },
                {
                    "id": "id2",
                    "name": group_name,
                    "folder": folder_name,
                    "static": ["Address2"],
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method and expect an APIError
        with pytest.raises(APIError):
            self.client.fetch(name=group_name, folder=folder_name)

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={"folder": folder_name, "name": group_name},
        )

    def test_fetch_address_group_no_name(self):
        """
        Test fetching an address group without providing the 'name' parameter.

        **Objective:** Ensure that the fetch method raises ValidationError when 'name' is not provided.
        **Workflow:**
            1. Calls the `fetch` method without the 'name' parameter.
            2. Asserts that ValidationError is raised.
        """
        folder_name = "Shared"
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(folder=folder_name, name="")
        assert (
            str(exc_info.value) == "Parameter 'name' must be provided for fetch method."
        )

    def test_fetch_address_group_multiple_containers(self):
        """
        Test fetching an address group with multiple containers provided.

        **Objective:** Ensure that the fetch method raises ValidationError when more than one of 'folder', 'snippet', or 'device' is provided.
        **Workflow:**
            1. Calls the `fetch` method with multiple container parameters.
            2. Asserts that ValidationError is raised.
        """
        group_name = "TestGroup"
        folder_name = "Shared"
        snippet_name = "TestSnippet"
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name=group_name, folder=folder_name, snippet=snippet_name)
        assert (
            str(exc_info.value)
            == "Exactly one of 'folder', 'snippet', or 'device' must be provided."
        )

    def test_fetch_address_group_unexpected_response_format(self):
        """
        Test fetching an address group when the API returns an unexpected response format.

        **Objective:** Ensure that the fetch method raises APIError when the response format is not as expected.
        **Workflow:**
            1. Mocks the API response to return an unexpected format.
            2. Calls the `fetch` method.
            3. Asserts that APIError is raised.
        """
        group_name = "TestGroup"
        folder_name = "Shared"
        # Mocking an unexpected response format
        mock_response = {"unexpected_key": "unexpected_value"}
        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name=group_name, folder=folder_name)
        assert str(exc_info.value) == "Unexpected response format."

    def test_fetch_address_group_single_in_data(self):
        """
        Test fetching an address group when the API returns a 'data' key with exactly one item.

        **Objective:** Ensure that the fetch method correctly returns the single item when 'data' contains exactly one address group.
        **Workflow:**
            1. Mocks the API response to return 'data' with one address group.
            2. Calls the `fetch` method.
            3. Asserts that the returned address group matches the expected data.
        """
        group_name = "TestGroup"
        folder_name = "Shared"
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": group_name,
                    "folder": folder_name,
                    "description": "A test address group",
                    "static": ["Address1", "Address2"],
                }
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        address_group = self.client.fetch(
            name=group_name,
            folder=folder_name,
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "folder": folder_name,
                "name": group_name,
            },
        )

        # Validate the returned address group
        assert isinstance(address_group, dict)
        expected_group = mock_response["data"][0]
        assert address_group == expected_group


class TestAddressGroupValidation(TestAddressGroupBase):
    """Tests for Address Group validation."""

    def test_address_group_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_address_group_request_model_no_type_provided(self):
        """Test validation when no type is provided."""
        data = {
            "name": "TestGroup",
            "folder": "Shared",
            # Neither 'static' nor 'dynamic' provided
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "Exactly one of 'static' or 'dynamic' must be provided." in str(
            exc_info.value
        )

    def test_address_group_request_model_both_types_provided(self):
        """Test validation when both types are provided."""
        data = {
            "name": "TestGroup",
            "folder": "Shared",
            "static": ["Address1"],
            "dynamic": DynamicFilter(
                filter="'Tag1'"
            ),  # Provide as an instance, not dict
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "Exactly one of 'static' or 'dynamic' must be provided." in str(
            exc_info.value
        )

    def test_address_group_request_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "TestGroup",
            "static": ["Address1"],
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_address_group_request_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "TestGroup",
            "static": ["Address1"],
            "folder": "Shared",
            "snippet": "TestSnippet",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_address_group_type_validation(self):
        """Test validation of address group type (static/dynamic)."""
        test_cases = [
            # Case 1: Neither static nor dynamic provided
            {
                "data": {
                    "name": "TestGroup",
                    "folder": "Shared",
                },
                "expected_error": "Exactly one of 'static' or 'dynamic' must be provided",
            },
            # Case 2: Both static and dynamic provided
            {
                "data": {
                    "name": "TestGroup",
                    "folder": "Shared",
                    "static": ["Address1"],
                    "dynamic": {"filter": "test-filter"},
                },
                "expected_error": "Exactly one of 'static' or 'dynamic' must be provided",
            },
        ]

        for test_case in test_cases:
            with pytest.raises(ValueError) as exc_info:
                AddressGroupCreateModel(**test_case["data"])
            assert test_case["expected_error"] in str(exc_info.value)

        # Positive test cases - should not raise errors
        valid_cases = [
            # Valid static group
            {
                "name": "StaticGroup",
                "folder": "Shared",
                "static": ["Address1"],
            },
            # Valid dynamic group
            {
                "name": "DynamicGroup",
                "folder": "Shared",
                "dynamic": {"filter": "test-filter"},
            },
        ]

        for valid_case in valid_cases:
            model = AddressGroupCreateModel(**valid_case)
            assert model is not None

    def test_address_group_container_validation_comprehensive(self):
        """Comprehensive test for container validation."""
        test_cases = [
            # No container
            {
                "data": {
                    "name": "TestGroup",
                    "static": ["Address1"],
                },
                "expected_errors": [
                    "Exactly one of 'folder', 'snippet', or 'device' must be provided",
                    "Value error",
                ],
            },
            # Multiple containers
            {
                "data": {
                    "name": "TestGroup",
                    "static": ["Address1"],
                    "folder": "Shared",
                    "snippet": "TestSnippet",
                },
                "expected_errors": [
                    "Exactly one of 'folder', 'snippet', or 'device' must be provided",
                    "Value error",
                ],
            },
        ]

        for test_case in test_cases:
            try:
                AddressGroupCreateModel(**test_case["data"])
                pytest.fail("Should have raised a validation error")
            except (PydanticValidationError, ValueError) as exc:
                assert any(error in str(exc) for error in test_case["expected_errors"])

    def test_address_group_response_model_invalid_uuid(self):
        """Test UUID validation in AddressGroupResponseModel."""
        invalid_data = {
            "id": "invalid-uuid",
            "name": "TestGroup",
            "static": ["Address1"],
            "folder": "Shared",
        }
        try:
            AddressGroupResponseModel(**invalid_data)
            pytest.fail("Should have raised a validation error")
        except (PydanticValidationError, ValueError) as exc:
            assert any(
                "Invalid UUID" in str(err) or "valid UUID" in str(err) for err in [exc]
            )

    def test_address_group_request_model_with_device_container(self):
        """Test address group creation with device container."""
        data = {
            "name": "TestGroup",
            "static": ["Address1"],
            "device": "Device1",
        }
        model = AddressGroupCreateModel(**data)
        assert model.device == "Device1"
        assert model.folder is None
        assert model.snippet is None

    def test_address_group_request_model_with_snippet_container(self):
        """Test address group creation with snippet container."""
        data = {
            "name": "TestGroup",
            "static": ["Address1"],
            "snippet": "Snippet1",
        }
        model = AddressGroupCreateModel(**data)
        assert model.snippet == "Snippet1"
        assert model.folder is None
        assert model.device is None

    def test_address_group_type_validation_all_cases(self):
        """Test all cases for address group type validation."""
        test_cases = [
            # Case 1: Neither static nor dynamic provided
            {
                "data": {
                    "name": "TestGroup",
                    "folder": "Shared",
                },
                "expected_error": "Exactly one of 'static' or 'dynamic' must be provided",
            },
            # Case 2: Both static and dynamic provided
            {
                "data": {
                    "name": "TestGroup",
                    "folder": "Shared",
                    "static": ["Address1"],
                    "dynamic": {"filter": "'Tag1'"},
                },
                "expected_error": "Exactly one of 'static' or 'dynamic' must be provided",
            },
        ]

        for test_case in test_cases:
            with pytest.raises(ValueError) as exc_info:
                AddressGroupCreateModel(**test_case["data"])
            assert test_case["expected_error"] in str(exc_info.value)

        # Test valid cases
        valid_static = {
            "name": "StaticGroup",
            "folder": "Shared",
            "static": ["Address1"],
        }
        static_model = AddressGroupCreateModel(**valid_static)
        assert static_model.static == ["Address1"]
        assert static_model.dynamic is None

        valid_dynamic = {
            "name": "DynamicGroup",
            "folder": "Shared",
            "dynamic": {"filter": "'Tag1'"},
        }
        dynamic_model = AddressGroupCreateModel(**valid_dynamic)
        assert dynamic_model.dynamic.filter == "'Tag1'"
        assert dynamic_model.static is None

    def test_address_group_response_model_validation(self):
        """Test validation in AddressGroupResponseModel for address group type."""
        test_cases = [
            # Case 1: Neither static nor dynamic provided
            {
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "TestGroup",
                    "folder": "Shared",
                },
                "expected_error": "Exactly one of 'static' or 'dynamic' must be provided",
            },
            # Case 2: Both static and dynamic provided
            {
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "TestGroup",
                    "folder": "Shared",
                    "static": ["Address1"],
                    "dynamic": {"filter": "test-filter"},
                },
                "expected_error": "Exactly one of 'static' or 'dynamic' must be provided",
            },
        ]

        for test_case in test_cases:
            with pytest.raises(ValueError) as exc_info:
                AddressGroupResponseModel(**test_case["data"])
            assert test_case["expected_error"] in str(exc_info.value)

        # Positive test cases to ensure valid data still works
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestGroup",
            "folder": "Shared",
            "static": ["Address1"],  # Only static provided
        }
        model = AddressGroupResponseModel(**valid_data)
        assert model.static == ["Address1"]
        assert model.dynamic is None

        valid_dynamic_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestGroup",
            "folder": "Shared",
            "dynamic": {"filter": "test-filter"},  # Only dynamic provided
        }
        model = AddressGroupResponseModel(**valid_dynamic_data)
        assert model.dynamic.filter == "test-filter"  # noqa
        assert model.static is None


class TestAddressGroupFilters(TestAddressGroupBase):
    """Tests for Address Group filtering functionality."""

    def test_address_group_list_with_filters(self):
        """Test listing address groups with filters."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "Group1",
                    "folder": "Shared",
                    "static": ["Address1"],
                },
                {
                    "id": "12345678-1234-5678-1234-567812345679",
                    "name": "Group2",
                    "folder": "Shared",
                    "static": ["Address2"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {
            "folder": "Shared",
            "names": ["Group1", "Group2"],
            "tags": ["Tag1", "Tag2"],
        }
        address_groups = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "name": "Group1,Group2",
            "tag": "Tag1,Tag2",
        }
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params=expected_params,
        )
        assert len(address_groups) == 2

    def test_address_group_list_with_types_filter(self):
        """Test listing address groups with types filter."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "DynamicGroup",
                    "folder": "Shared",
                    "type": "dynamic",
                    "dynamic": {"filter": "'Tag1'"},
                },
                {
                    "id": "12345678-1234-5678-1234-567812345679",
                    "name": "StaticGroup",
                    "folder": "Shared",
                    "type": "static",
                    "static": ["Address1"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {
            "folder": "Shared",
            "types": ["dynamic", "static"],
        }
        address_groups = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "type": "dynamic,static",
        }
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params=expected_params,
        )
        assert len(address_groups) == 2

    def test_address_group_list_with_values_filter(self):
        """Test listing address groups with values filter."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "Group1",
                    "folder": "Shared",
                    "static": ["Address1", "Address2"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {
            "folder": "Shared",
            "values": ["Address1", "Address2"],
        }
        address_groups = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "value": "Address1,Address2",
        }
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params=expected_params,
        )
        assert len(address_groups) == 1


class TestSuite(
    TestAddressGroupAPI,
    TestAddressGroupValidation,
    TestAddressGroupFilters,
):
    """Main test suite that combines all test classes."""

    pass
