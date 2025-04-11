# tests/scm/models/objects/test_regions_models.py

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects import (GeoLocation, RegionCreateModel,
                                RegionResponseModel, RegionUpdateModel)
from tests.factories import RegionCreateModelFactory, RegionUpdateModelFactory

# -------------------- Test Classes for GeoLocation Model --------------------


class TestGeoLocationModel:
    """Tests for GeoLocation model validation."""

    def test_geo_location_with_valid_data(self):
        """Test GeoLocation with valid data."""
        geo = GeoLocation(latitude=37.7749, longitude=-122.4194)
        assert geo.latitude == 37.7749
        assert geo.longitude == -122.4194

    def test_geo_location_with_invalid_latitude(self):
        """Test validation when latitude is outside valid range."""
        with pytest.raises(ValidationError) as exc_info:
            GeoLocation(latitude=100, longitude=-122.4194)
        assert "Input should be less than or equal to 90" in str(exc_info.value)

    def test_geo_location_with_invalid_longitude(self):
        """Test validation when longitude is outside valid range."""
        with pytest.raises(ValidationError) as exc_info:
            GeoLocation(latitude=37.7749, longitude=200)
        assert "Input should be less than or equal to 180" in str(exc_info.value)

    def test_geo_location_with_extreme_valid_values(self):
        """Test GeoLocation with extreme but valid values."""
        geo = GeoLocation(latitude=-90, longitude=180)
        assert geo.latitude == -90
        assert geo.longitude == 180


# -------------------- Test Classes for Region Create Model --------------------


class TestRegionCreateModel:
    """Tests for RegionCreateModel validation."""

    def test_region_create_model_valid(self):
        """Test validation with valid data."""
        data = RegionCreateModelFactory.build_valid()
        model = RegionCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.geo_location.latitude == data["geo_location"]["latitude"]
        assert model.geo_location.longitude == data["geo_location"]["longitude"]
        assert model.address == data["address"]

    def test_region_create_model_with_invalid_name(self):
        """Test validation when name pattern is invalid."""
        data = RegionCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            RegionCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)

    def test_region_create_model_with_invalid_geo_location(self):
        """Test validation when geo_location is invalid."""
        data = RegionCreateModelFactory.build_with_invalid_latitude()
        with pytest.raises(ValidationError) as exc_info:
            RegionCreateModel(**data)
        assert "Input should be less than or equal to 90" in str(exc_info.value)

    def test_region_create_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = RegionCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            RegionCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_region_create_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = RegionCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            RegionCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_address_field_accepts_string(self):
        """Test that the 'address' field accepts a single string and converts it to a list."""
        data = RegionCreateModelFactory.build_valid()
        data["address"] = "192.168.1.0/24"
        model = RegionCreateModel(**data)
        assert model.address == ["192.168.1.0/24"]

    def test_address_field_accepts_list(self):
        """Test that the 'address' field accepts a list of strings."""
        data = RegionCreateModelFactory.build_valid()
        data["address"] = ["192.168.1.0/24", "10.0.0.0/8"]
        model = RegionCreateModel(**data)
        assert model.address == ["192.168.1.0/24", "10.0.0.0/8"]

    def test_address_field_rejects_invalid_type(self):
        """Test that the 'address' field rejects invalid types."""
        data = RegionCreateModelFactory.build_valid()
        data["address"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            RegionCreateModel(**data)
        assert "1 validation error for RegionCreateModel" in str(exc_info.value)

    def test_address_field_rejects_integer(self):
        """Test that the 'address' field rejects integer values."""
        data = RegionCreateModelFactory.build_valid()
        data["address"] = 123
        with pytest.raises(ValidationError) as exc_info:
            RegionCreateModel(**data)
        assert "1 validation error for RegionCreateModel" in str(exc_info.value)

    def test_ensure_list_of_strings_function(self):
        """Test that the ensure_list_of_strings validator function works directly."""
        from scm.models.objects.regions import RegionBaseModel

        # Test with None value
        assert RegionBaseModel.ensure_list_of_strings(None) is None

        # Test with string value
        assert RegionBaseModel.ensure_list_of_strings("192.168.1.1") == ["192.168.1.1"]

        # Test with list value
        test_list = ["192.168.1.1", "10.0.0.1"]
        assert RegionBaseModel.ensure_list_of_strings(test_list) == test_list

        # Test with invalid type
        with pytest.raises(ValueError) as exc_info:
            RegionBaseModel.ensure_list_of_strings({"invalid": "type"})
        assert "Value must be a string or a list of strings" in str(exc_info.value)

    def test_address_field_rejects_duplicate_items(self):
        """Test that the 'address' field rejects duplicate items."""
        data = RegionCreateModelFactory.build_valid()
        data["address"] = ["192.168.1.0/24", "192.168.1.0/24"]
        with pytest.raises(ValidationError) as exc_info:
            RegionCreateModel(**data)
        assert "List of addresses must contain unique values" in str(exc_info.value)


# -------------------- Test Classes for Region Update Model --------------------


class TestRegionUpdateModel:
    """Tests for RegionUpdateModel validation."""

    def test_region_update_model_valid(self):
        """Test validation with valid data."""
        data = RegionUpdateModelFactory.build_valid()
        model = RegionUpdateModel(**data)
        assert model.id.hex
        assert model.name == data["name"]
        assert model.geo_location.latitude == data["geo_location"]["latitude"]
        assert model.geo_location.longitude == data["geo_location"]["longitude"]

    def test_region_update_model_with_invalid_fields(self):
        """Test validation with invalid fields."""
        data = RegionUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            RegionUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "String should match pattern" in error_msg  # Invalid name
        assert "uuid" in error_msg.lower()  # Invalid UUID

    def test_region_update_model_minimal(self):
        """Test validation with minimal fields."""
        data = RegionUpdateModelFactory.build_minimal_update()
        model = RegionUpdateModel(**data)
        assert model.id.hex
        assert model.name == data["name"]
        assert model.geo_location is None  # Optional field not provided

    def test_address_field_accepts_string(self):
        """Test that the 'address' field accepts a single string and converts it to a list."""
        data = RegionUpdateModelFactory.build_valid()
        data["address"] = "192.168.1.0/24"
        model = RegionUpdateModel(**data)
        assert model.address == ["192.168.1.0/24"]

    def test_address_field_accepts_list(self):
        """Test that the 'address' field accepts a list of strings."""
        data = RegionUpdateModelFactory.build_valid()
        data["address"] = ["192.168.1.0/24", "10.0.0.0/8"]
        model = RegionUpdateModel(**data)
        assert model.address == ["192.168.1.0/24", "10.0.0.0/8"]

    def test_address_field_rejects_invalid_type(self):
        """Test that the 'address' field rejects invalid types."""
        data = RegionUpdateModelFactory.build_valid()
        data["address"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            RegionUpdateModel(**data)
        assert "1 validation error for RegionUpdateModel" in str(exc_info.value)

    def test_address_field_rejects_duplicate_items(self):
        """Test that the 'address' field rejects duplicate items."""
        data = RegionUpdateModelFactory.build_valid()
        data["address"] = ["192.168.1.0/24", "192.168.1.0/24"]
        with pytest.raises(ValidationError) as exc_info:
            RegionUpdateModel(**data)
        assert "List of addresses must contain unique values" in str(exc_info.value)


# -------------------- Test Classes for Region Response Model --------------------


class TestRegionResponseModel:
    """Tests for RegionResponseModel validation."""

    def test_region_response_model_valid(self):
        """Test validation with valid data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "geo_location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
            },
            "address": ["192.168.1.0/24", "10.0.0.0/8"],
        }
        model = RegionResponseModel(**data)
        assert str(model.id) == "123e4567-e89b-12d3-a456-426655440000"
        assert model.name == "TestRegion"
        assert model.folder == "Global"
        assert model.geo_location.latitude == 37.7749
        assert model.geo_location.longitude == -122.4194
        assert model.address == ["192.168.1.0/24", "10.0.0.0/8"]

    def test_region_response_model_with_snippet(self):
        """Test validation with snippet container."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "snippet": "TestSnippet",
        }
        model = RegionResponseModel(**data)
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_region_response_model_with_device(self):
        """Test validation with device container."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "device": "TestDevice",
        }
        model = RegionResponseModel(**data)
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_region_response_model_without_id(self):
        """Test validation when 'id' field is missing."""
        data = {
            "name": "TestRegion",
            "folder": "Global",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegionResponseModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_address_field_accepts_string(self):
        """Test that the 'address' field accepts a single string and converts it to a list."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "address": "192.168.1.0/24",
        }
        model = RegionResponseModel(**data)
        assert model.address == ["192.168.1.0/24"]

    def test_address_field_accepts_list(self):
        """Test that the 'address' field accepts a list of strings."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "address": ["192.168.1.0/24", "10.0.0.0/8"],
        }
        model = RegionResponseModel(**data)
        assert model.address == ["192.168.1.0/24", "10.0.0.0/8"]

    def test_address_field_rejects_invalid_type(self):
        """Test that the 'address' field rejects invalid types."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "address": {"invalid": "type"},
        }
        with pytest.raises(ValidationError) as exc_info:
            RegionResponseModel(**data)
        assert "1 validation error for RegionResponseModel" in str(exc_info.value)

    def test_address_field_rejects_duplicate_items(self):
        """Test that the 'address' field rejects duplicate items."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "address": ["192.168.1.0/24", "192.168.1.0/24"],
        }
        with pytest.raises(ValidationError) as exc_info:
            RegionResponseModel(**data)
        assert "List of addresses must contain unique values" in str(exc_info.value)

    def test_tag_field_accepts_string(self):
        """Test that the 'tag' field accepts a single string and converts it to a list."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "tag": "prod",
        }
        model = RegionResponseModel(**data)
        assert model.tag == ["prod"]

    def test_tag_field_accepts_list(self):
        """Test that the 'tag' field accepts a list of strings."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "tag": ["prod", "web"],
        }
        model = RegionResponseModel(**data)
        assert model.tag == ["prod", "web"]

    def test_tag_field_rejects_invalid_type(self):
        """Test that the 'tag' field rejects invalid types."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "tag": {"invalid": "type"},
        }
        with pytest.raises(ValidationError) as exc_info:
            RegionResponseModel(**data)
        assert "1 validation error for RegionResponseModel" in str(exc_info.value)

    def test_tag_field_rejects_duplicate_items(self):
        """Test that the 'tag' field rejects duplicate items."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRegion",
            "folder": "Global",
            "tag": ["prod", "prod"],
        }
        with pytest.raises(ValidationError) as exc_info:
            RegionResponseModel(**data)
        assert "List of tags must contain unique values" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
