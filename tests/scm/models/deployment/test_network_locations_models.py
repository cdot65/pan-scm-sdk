# tests/scm/models/deployment/test_network_locations_models.py

from pydantic import ValidationError
import pytest

from scm.models.deployment.network_locations import NetworkLocationModel
from tests.factories.deployment.network_locations import (
    NetworkLocationModelFactory,
)


class TestNetworkLocationModel:
    """Tests for NetworkLocationModel validation."""

    def test_valid_model_creation(self):
        """Test creating a valid model with all required fields."""
        data = NetworkLocationModelFactory.build_valid()
        model = NetworkLocationModel(**data)
        assert model.value == "us-west-1"
        assert model.display == "US West"
        assert model.continent == "North America"
        assert model.latitude == 37.38314
        assert model.longitude == -121.98306
        assert model.region == "us-west-1"
        assert model.aggregate_region == "us-southwest"

    def test_minimal_model_creation(self):
        """Test creating a model with only required fields."""
        data = NetworkLocationModelFactory.build_minimal()
        model = NetworkLocationModel(**data)
        assert model.value == "us-west-1"
        assert model.display == "US West"
        assert model.continent is None
        assert model.latitude is None
        assert model.longitude is None
        assert model.region is None
        assert model.aggregate_region is None

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        # Missing 'value'
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_missing_required("value")
            NetworkLocationModel(**data)
        assert "value\n  Field required" in str(exc_info.value)

        # Missing 'display'
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_missing_required("display")
            NetworkLocationModel(**data)
        assert "display\n  Field required" in str(exc_info.value)

        # Missing both required fields
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel()
        assert "value\n  Field required" in str(exc_info.value)
        assert "display\n  Field required" in str(exc_info.value)

    def test_latitude_validation(self):
        """Test latitude field validation."""
        # Valid minimum value
        data = NetworkLocationModelFactory.build_minimal(latitude=-90)
        model = NetworkLocationModel(**data)
        assert model.latitude == -90

        # Valid maximum value
        data = NetworkLocationModelFactory.build_minimal(latitude=90)
        model = NetworkLocationModel(**data)
        assert model.latitude == 90

        # Valid value within range
        data = NetworkLocationModelFactory.build_minimal(latitude=45.123)
        model = NetworkLocationModel(**data)
        assert model.latitude == 45.123

        # Invalid: exceeds maximum
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_with_invalid_latitude(latitude=90.1)
            NetworkLocationModel(**data)
        assert "latitude\n  Input should be less than or equal to 90" in str(exc_info.value)

        # Invalid: below minimum
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_with_invalid_latitude(latitude=-90.1)
            NetworkLocationModel(**data)
        assert "latitude\n  Input should be greater than or equal to -90" in str(exc_info.value)

    def test_longitude_validation(self):
        """Test longitude field validation."""
        # Valid minimum value
        data = NetworkLocationModelFactory.build_minimal(longitude=-180)
        model = NetworkLocationModel(**data)
        assert model.longitude == -180

        # Valid maximum value
        data = NetworkLocationModelFactory.build_minimal(longitude=180)
        model = NetworkLocationModel(**data)
        assert model.longitude == 180

        # Valid value within range
        data = NetworkLocationModelFactory.build_minimal(longitude=45.123)
        model = NetworkLocationModel(**data)
        assert model.longitude == 45.123

        # Invalid: exceeds maximum
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_with_invalid_longitude(longitude=180.1)
            NetworkLocationModel(**data)
        assert "longitude\n  Input should be less than or equal to 180" in str(exc_info.value)

        # Invalid: below minimum
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_with_invalid_longitude(longitude=-180.1)
            NetworkLocationModel(**data)
        assert "longitude\n  Input should be greater than or equal to -180" in str(exc_info.value)

    def test_serialization(self):
        """Test model serialization to dict."""
        data = NetworkLocationModelFactory.build_valid()
        model = NetworkLocationModel(**data)
        serialized = model.model_dump()
        assert serialized["value"] == "us-west-1"
        assert serialized["display"] == "US West"
        assert serialized["continent"] == "North America"
        assert serialized["latitude"] == 37.38314
        assert serialized["longitude"] == -121.98306
        assert serialized["region"] == "us-west-1"
        assert serialized["aggregate_region"] == "us-southwest"

    def test_serialization_with_none_values(self):
        """Test model serialization with None values."""
        data = NetworkLocationModelFactory.build_minimal()
        model = NetworkLocationModel(**data)
        serialized = model.model_dump()
        assert serialized["continent"] is None
        assert serialized["latitude"] is None
        assert serialized["longitude"] is None
        assert serialized["region"] is None
        assert serialized["aggregate_region"] is None

    def test_serialization_exclude_none(self):
        """Test model serialization with exclude_none=True."""
        data = NetworkLocationModelFactory.build_minimal()
        model = NetworkLocationModel(**data)
        serialized = model.model_dump(exclude_none=True)
        assert "continent" not in serialized
        assert "latitude" not in serialized
        assert "longitude" not in serialized
        assert "region" not in serialized
        assert "aggregate_region" not in serialized
        assert "value" in serialized
        assert "display" in serialized

    def test_model_with_none_values(self):
        """Test model with explicit None values for optional fields."""
        data = NetworkLocationModelFactory.build_with_none_values()
        model = NetworkLocationModel(**data)
        assert model.value == "us-west-1"
        assert model.display == "US West"
        assert model.continent is None
        assert model.latitude is None
        assert model.longitude is None
        assert model.region is None
        assert model.aggregate_region is None

    def test_empty_string_values(self):
        """Test model with empty string values."""
        data = NetworkLocationModelFactory.build_with_empty_strings()
        model = NetworkLocationModel(**data)
        assert model.value == "us-west-1"
        assert model.display == "US West"
        assert model.continent == ""
        assert model.region == ""
        assert model.aggregate_region == ""

    def test_model_invalid_types(self):
        """Test validation fails with invalid types."""
        # Invalid latitude type
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_with_invalid_latitude_type()
            NetworkLocationModel(**data)
        assert "latitude\n  Input should be a valid number" in str(exc_info.value)

        # Invalid longitude type
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_with_invalid_longitude_type()
            NetworkLocationModel(**data)
        assert "longitude\n  Input should be a valid number" in str(exc_info.value)

        # Invalid value type
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_with_invalid_value_type()
            NetworkLocationModel(**data)
        assert "value\n  Input should be a valid string" in str(exc_info.value)

        # Invalid display type
        with pytest.raises(ValidationError) as exc_info:
            data = NetworkLocationModelFactory.build_with_invalid_display_type()
            NetworkLocationModel(**data)
        assert "display\n  Input should be a valid string" in str(exc_info.value)

    def test_model_config_options(self):
        """Test that model config options are set correctly."""
        assert NetworkLocationModel.model_config["populate_by_name"] is True
        assert NetworkLocationModel.model_config["validate_assignment"] is True
