# tests/scm/models/deployment/test_network_locations_models.py

import pytest
from pydantic import ValidationError

from scm.models.deployment.network_locations import NetworkLocationModel


class TestNetworkLocationModel:
    """Tests for NetworkLocationModel validation."""

    def test_valid_model_creation(self):
        """Test creating a valid model with all required fields."""
        data = {
            "value": "us-west-1",
            "display": "US West",
            "continent": "North America",
            "latitude": 37.38314,
            "longitude": -121.98306,
            "region": "us-west-1",
            "aggregate_region": "us-southwest"
        }
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
        model = NetworkLocationModel(value="us-west-1", display="US West")
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
            NetworkLocationModel(display="US West")
        assert "value\n  Field required" in str(exc_info.value)

        # Missing 'display'
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel(value="us-west-1")
        assert "display\n  Field required" in str(exc_info.value)

        # Missing both required fields
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel()
        assert "value\n  Field required" in str(exc_info.value)
        assert "display\n  Field required" in str(exc_info.value)

    def test_latitude_validation(self):
        """Test latitude field validation."""
        # Valid minimum value
        model = NetworkLocationModel(value="test", display="Test", latitude=-90)
        assert model.latitude == -90
        
        # Valid maximum value
        model = NetworkLocationModel(value="test", display="Test", latitude=90)
        assert model.latitude == 90
        
        # Valid value within range
        model = NetworkLocationModel(value="test", display="Test", latitude=45.123)
        assert model.latitude == 45.123
        
        # Invalid: exceeds maximum
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel(value="test", display="Test", latitude=90.1)
        assert "latitude\n  Input should be less than or equal to 90" in str(exc_info.value)
        
        # Invalid: below minimum
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel(value="test", display="Test", latitude=-90.1)
        assert "latitude\n  Input should be greater than or equal to -90" in str(exc_info.value)

    def test_longitude_validation(self):
        """Test longitude field validation."""
        # Valid minimum value
        model = NetworkLocationModel(value="test", display="Test", longitude=-180)
        assert model.longitude == -180
        
        # Valid maximum value
        model = NetworkLocationModel(value="test", display="Test", longitude=180)
        assert model.longitude == 180
        
        # Valid value within range
        model = NetworkLocationModel(value="test", display="Test", longitude=45.123)
        assert model.longitude == 45.123
        
        # Invalid: exceeds maximum
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel(value="test", display="Test", longitude=180.1)
        assert "longitude\n  Input should be less than or equal to 180" in str(exc_info.value)
        
        # Invalid: below minimum
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel(value="test", display="Test", longitude=-180.1)
        assert "longitude\n  Input should be greater than or equal to -180" in str(exc_info.value)

    def test_model_serialization(self):
        """Test model serialization to dictionary."""
        data = {
            "value": "us-west-1",
            "display": "US West",
            "continent": "North America",
            "latitude": 37.38314,
            "longitude": -121.98306,
            "region": "us-west-1",
            "aggregate_region": "us-southwest"
        }
        model = NetworkLocationModel(**data)
        model_dict = model.model_dump()
        
        assert model_dict["value"] == "us-west-1"
        assert model_dict["display"] == "US West"
        assert model_dict["continent"] == "North America"
        assert model_dict["latitude"] == 37.38314
        assert model_dict["longitude"] == -121.98306
        assert model_dict["region"] == "us-west-1"
        assert model_dict["aggregate_region"] == "us-southwest"
        
        # Test with exclude_none option
        minimal_model = NetworkLocationModel(value="us-west-1", display="US West")
        minimal_dict = minimal_model.model_dump(exclude_none=True)
        assert "value" in minimal_dict
        assert "display" in minimal_dict
        assert "continent" not in minimal_dict
        assert "latitude" not in minimal_dict
        assert "longitude" not in minimal_dict
        assert "region" not in minimal_dict
        assert "aggregate_region" not in minimal_dict

    def test_model_with_none_values(self):
        """Test model with explicit None values for optional fields."""
        data = {
            "value": "us-west-1",
            "display": "US West",
            "continent": None,
            "latitude": None,
            "longitude": None,
            "region": None,
            "aggregate_region": None
        }
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
        data = {
            "value": "us-west-1",
            "display": "US West",
            "continent": "",
            "region": "",
            "aggregate_region": ""
        }
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
            NetworkLocationModel(
                value="test", 
                display="Test", 
                latitude="invalid"
            )
        assert "latitude\n  Input should be a valid number" in str(exc_info.value)
        
        # Invalid longitude type
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel(
                value="test", 
                display="Test", 
                longitude="invalid"
            )
        assert "longitude\n  Input should be a valid number" in str(exc_info.value)
        
        # Invalid value type
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel(
                value=123, 
                display="Test"
            )
        assert "value\n  Input should be a valid string" in str(exc_info.value)
        
        # Invalid display type
        with pytest.raises(ValidationError) as exc_info:
            NetworkLocationModel(
                value="test", 
                display=123
            )
        assert "display\n  Input should be a valid string" in str(exc_info.value)

    def test_model_config_options(self):
        """Test that model config options are set correctly."""
        assert NetworkLocationModel.model_config["populate_by_name"] is True
        assert NetworkLocationModel.model_config["validate_assignment"] is True
