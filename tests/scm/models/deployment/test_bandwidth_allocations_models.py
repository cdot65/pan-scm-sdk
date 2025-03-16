# tests/scm/models/deployment/test_bandwidth_allocations_models.py

import pytest
from pydantic import ValidationError
from scm.models.deployment.bandwidth_allocations import (
    BandwidthAllocationBaseModel,
    BandwidthAllocationCreateModel,
    BandwidthAllocationUpdateModel,
    BandwidthAllocationResponseModel,
    BandwidthAllocationListResponseModel,
    QosModel
)


class TestQosModel:
    """Tests for the QosModel pydantic validation."""

    def test_valid_model_creation(self):
        """Test creating model with valid data."""
        data = {
            "enabled": True,
            "customized": True,
            "profile": "test-profile",
            "guaranteed_ratio": 0.5
        }
        model = QosModel(**data)
        assert model.enabled == data["enabled"]
        assert model.customized == data["customized"]
        assert model.profile == data["profile"]
        assert model.guaranteed_ratio == data["guaranteed_ratio"]

    def test_optional_fields(self):
        """Test creating model with minimal data."""
        model = QosModel()
        assert model.enabled is None
        assert model.customized is None
        assert model.profile is None
        assert model.guaranteed_ratio is None

    def test_guaranteed_ratio_validation(self):
        """Test that guaranteed_ratio accepts valid float values."""
        data = {
            "guaranteed_ratio": 0.75
        }
        model = QosModel(**data)
        assert model.guaranteed_ratio == 0.75

        data = {
            "guaranteed_ratio": 1.0
        }
        model = QosModel(**data)
        assert model.guaranteed_ratio == 1.0


class TestBandwidthAllocationBaseModel:
    """Tests for the BandwidthAllocationBaseModel pydantic validation."""

    def test_valid_model_creation(self):
        """Test creating model with valid data."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100,
            "spn_name_list": ["spn1", "spn2"],
            "qos": {
                "enabled": True,
                "customized": True,
                "profile": "test-profile",
                "guaranteed_ratio": 0.5
            }
        }
        model = BandwidthAllocationBaseModel(**data)
        assert model.name == data["name"]
        assert model.allocated_bandwidth == data["allocated_bandwidth"]
        assert model.spn_name_list == data["spn_name_list"]
        assert model.qos.enabled == data["qos"]["enabled"]
        assert model.qos.customized == data["qos"]["customized"]
        assert model.qos.profile == data["qos"]["profile"]
        assert model.qos.guaranteed_ratio == data["qos"]["guaranteed_ratio"]

    def test_minimal_model_creation(self):
        """Test creating model with only required fields."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100
        }
        model = BandwidthAllocationBaseModel(**data)
        assert model.name == data["name"]
        assert model.allocated_bandwidth == data["allocated_bandwidth"]
        assert model.spn_name_list is None
        assert model.qos is None

    def test_invalid_name_pattern(self):
        """Test validation fails with invalid name pattern."""
        data = {
            "name": "invalid@name#",
            "allocated_bandwidth": 100
        }
        with pytest.raises(ValidationError) as exc_info:
            BandwidthAllocationBaseModel(**data)
        
        # Check that the error is related to the name pattern
        error_details = str(exc_info.value)
        assert "name" in error_details
        assert "pattern" in error_details

    def test_negative_bandwidth(self):
        """Test validation fails with negative bandwidth."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": -100
        }
        with pytest.raises(ValidationError) as exc_info:
            BandwidthAllocationBaseModel(**data)
        
        # Check that the error is related to the allocated_bandwidth
        error_details = str(exc_info.value)
        assert "allocated_bandwidth" in error_details
        assert "greater than" in error_details

    def test_zero_bandwidth(self):
        """Test validation fails with zero bandwidth."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 0
        }
        with pytest.raises(ValidationError) as exc_info:
            BandwidthAllocationBaseModel(**data)
        
        # Check that the error is related to the allocated_bandwidth
        error_details = str(exc_info.value)
        assert "allocated_bandwidth" in error_details
        assert "greater than" in error_details


class TestBandwidthAllocationCreateModel:
    """Tests for the BandwidthAllocationCreateModel pydantic validation."""

    def test_valid_model_creation(self):
        """Test creating model with valid data."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100,
            "spn_name_list": ["spn1", "spn2"]
        }
        model = BandwidthAllocationCreateModel(**data)
        assert model.name == data["name"]
        assert model.allocated_bandwidth == data["allocated_bandwidth"]
        assert model.spn_name_list == data["spn_name_list"]
        
    def test_with_qos(self):
        """Test creating model with QoS data."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100,
            "qos": {
                "enabled": True,
                "profile": "test-profile"
            }
        }
        model = BandwidthAllocationCreateModel(**data)
        assert model.name == data["name"]
        assert model.allocated_bandwidth == data["allocated_bandwidth"]
        assert model.qos.enabled is True
        assert model.qos.profile == "test-profile"


class TestBandwidthAllocationUpdateModel:
    """Tests for the BandwidthAllocationUpdateModel pydantic validation."""

    def test_valid_model_update(self):
        """Test updating model with valid data."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 200,
            "spn_name_list": ["spn3", "spn4"]
        }
        model = BandwidthAllocationUpdateModel(**data)
        assert model.name == data["name"]
        assert model.allocated_bandwidth == data["allocated_bandwidth"]
        assert model.spn_name_list == data["spn_name_list"]
        
    def test_partial_update(self):
        """Test updating just some fields."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 300
        }
        model = BandwidthAllocationUpdateModel(**data)
        assert model.name == data["name"]
        assert model.allocated_bandwidth == data["allocated_bandwidth"]
        assert model.spn_name_list is None


class TestBandwidthAllocationResponseModel:
    """Tests for the BandwidthAllocationResponseModel pydantic validation."""

    def test_valid_response_model(self):
        """Test creating response model with valid data."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100,
            "spn_name_list": ["spn1", "spn2"],
            "qos": {
                "enabled": True,
                "customized": False,
                "profile": "default-profile",
                "guaranteed_ratio": 0.8
            }
        }
        model = BandwidthAllocationResponseModel(**data)
        assert model.name == data["name"]
        assert model.allocated_bandwidth == data["allocated_bandwidth"]
        assert model.spn_name_list == data["spn_name_list"]
        assert model.qos.enabled == data["qos"]["enabled"]
        assert model.qos.customized == data["qos"]["customized"]
        assert model.qos.profile == data["qos"]["profile"]
        assert model.qos.guaranteed_ratio == data["qos"]["guaranteed_ratio"]
        
    def test_minimal_response(self):
        """Test response with minimal fields."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100
        }
        model = BandwidthAllocationResponseModel(**data)
        assert model.name == data["name"]
        assert model.allocated_bandwidth == data["allocated_bandwidth"]
        assert model.spn_name_list is None
        assert model.qos is None


class TestBandwidthAllocationListResponseModel:
    """Tests for the BandwidthAllocationListResponseModel pydantic validation."""

    def test_valid_list_response_model(self):
        """Test creating list response model with valid data."""
        data = {
            "data": [
                {
                    "name": "region1",
                    "allocated_bandwidth": 100,
                    "spn_name_list": ["spn1", "spn2"]
                },
                {
                    "name": "region2",
                    "allocated_bandwidth": 200,
                    "spn_name_list": ["spn3", "spn4"],
                    "qos": {
                        "enabled": True,
                        "profile": "custom-profile"
                    }
                }
            ],
            "limit": 100,
            "offset": 0,
            "total": 2
        }
        model = BandwidthAllocationListResponseModel(**data)
        assert len(model.data) == 2
        assert model.data[0].name == "region1"
        assert model.data[1].name == "region2"
        assert model.limit == 100
        assert model.offset == 0
        assert model.total == 2

    def test_default_limit_and_offset(self):
        """Test list response model with default limit and offset."""
        data = {
            "data": [],
            "total": 0
        }
        model = BandwidthAllocationListResponseModel(**data)
        assert model.limit == 200  # Default value
        assert model.offset == 0   # Default value
        assert model.total == 0
        
    def test_empty_data_list(self):
        """Test list response with empty data list."""
        data = {
            "data": [],
            "limit": 200,
            "offset": 0,
            "total": 0
        }
        model = BandwidthAllocationListResponseModel(**data)
        assert len(model.data) == 0
        assert model.total == 0
