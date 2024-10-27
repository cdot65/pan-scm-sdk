# tests/test_address_groups.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import AddressGroup
from scm.exceptions import ValidationError
from scm.models.objects import AddressGroupResponseModel, AddressGroupRequestModel
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
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AddressGroup(self.mock_scm)


class TestAddressGroupAPI(TestAddressGroupBase):
    """Tests for Address Group API operations."""

    def test_list_address_groups(self):
        """Test listing address groups."""
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

        self.mock_scm.get.return_value = mock_response
        address_groups = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(
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
        """Test creating an address group with a dynamic filter."""
        test_address_group = AddressGroupDynamicFactory()
        mock_response = test_address_group.model_dump()
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.post.return_value = mock_response
        created_group = self.client.create(
            test_address_group.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/address-groups",
            json=test_address_group.model_dump(exclude_unset=True),
        )
        assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
        assert created_group.name == test_address_group.name
        assert created_group.dynamic.filter == test_address_group.dynamic.filter
        assert created_group.folder == test_address_group.folder

    def test_create_address_group_with_static_entries(self):
        """Test creating an address group with static entries."""
        test_address_group = AddressGroupStaticFactory()
        mock_response = test_address_group.model_dump()
        mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.post.return_value = mock_response
        created_group = self.client.create(
            test_address_group.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/address-groups",
            json=test_address_group.model_dump(exclude_unset=True),
        )
        assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
        assert created_group.name == test_address_group.name
        assert created_group.folder == test_address_group.folder

    def test_get_address_group(self):
        """Test retrieving an address group by ID."""
        group_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": group_id,
            "name": "TestGroup",
            "folder": "Shared",
            "description": "A test address group",
            "static": ["Address1", "Address2"],
        }

        self.mock_scm.get.return_value = mock_response
        address_group = self.client.get(group_id)

        self.mock_scm.get.assert_called_once_with(
            f"/config/objects/v1/address-groups/{group_id}"
        )
        assert isinstance(address_group, AddressGroupResponseModel)
        assert address_group.id == group_id
        assert address_group.name == "TestGroup"
        assert address_group.description == "A test address group"
        assert address_group.static == ["Address1", "Address2"]

    def test_update_address_group(self):
        """Test updating an address group."""
        group_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = {
            "name": "UpdatedGroup",
            "folder": "Shared",
            "description": "An updated address group",
            "static": ["Address3", "Address4"],
        }

        mock_response = update_data.copy()
        mock_response["id"] = group_id

        self.mock_scm.put.return_value = mock_response
        updated_group = self.client.update(group_id, update_data)

        self.mock_scm.put.assert_called_once_with(
            f"/config/objects/v1/address-groups/{group_id}",
            json=update_data,
        )
        assert isinstance(updated_group, AddressGroupResponseModel)
        assert updated_group.id == group_id
        assert updated_group.name == "UpdatedGroup"
        assert updated_group.description == "An updated address group"
        assert updated_group.static == ["Address3", "Address4"]


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
            AddressGroupRequestModel(**data)
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
            AddressGroupRequestModel(**data)
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
            AddressGroupRequestModel(**data)
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
            AddressGroupRequestModel(**data)
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
                AddressGroupRequestModel(**test_case["data"])
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
            model = AddressGroupRequestModel(**valid_case)
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
                AddressGroupRequestModel(**test_case["data"])
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
        model = AddressGroupRequestModel(**data)
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
        model = AddressGroupRequestModel(**data)
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
                AddressGroupRequestModel(**test_case["data"])
            assert test_case["expected_error"] in str(exc_info.value)

        # Test valid cases
        valid_static = {
            "name": "StaticGroup",
            "folder": "Shared",
            "static": ["Address1"],
        }
        static_model = AddressGroupRequestModel(**valid_static)
        assert static_model.static == ["Address1"]
        assert static_model.dynamic is None

        valid_dynamic = {
            "name": "DynamicGroup",
            "folder": "Shared",
            "dynamic": {"filter": "'Tag1'"},
        }
        dynamic_model = AddressGroupRequestModel(**valid_dynamic)
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
        assert model.dynamic.filter == "test-filter"
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
        self.mock_scm.get.return_value = mock_response

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
        self.mock_scm.get.assert_called_once_with(
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
        self.mock_scm.get.return_value = mock_response

        filters = {
            "folder": "Shared",
            "types": ["dynamic", "static"],
        }
        address_groups = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "type": "dynamic,static",
        }
        self.mock_scm.get.assert_called_once_with(
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
        self.mock_scm.get.return_value = mock_response

        filters = {
            "folder": "Shared",
            "values": ["Address1", "Address2"],
        }
        address_groups = self.client.list(**filters)

        expected_params = {
            "folder": "Shared",
            "value": "Address1,Address2",
        }
        self.mock_scm.get.assert_called_once_with(
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
