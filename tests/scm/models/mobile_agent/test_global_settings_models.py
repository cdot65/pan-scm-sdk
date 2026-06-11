# tests/scm/models/mobile_agent/test_global_settings_models.py

"""Tests for mobile agent global settings models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.global_settings import (
    GlobalSettingsBaseModel,
    GlobalSettingsResponseModel,
    GlobalSettingsUpdateModel,
    ManualGateway,
    ManualGatewayRegion,
)
from tests.scm.models.mobile_agent.factories import (
    GlobalSettingsResponseModelFactory,
    GlobalSettingsUpdateModelFactory,
)


class TestGlobalSettingsBaseModel:
    """Tests for GlobalSettingsBaseModel validation."""

    def test_base_model_empty(self):
        """Test that the base model can be created with no fields (all optional)."""
        model = GlobalSettingsBaseModel()
        assert model.agent_version is None
        assert model.manual_gateway is None

    def test_base_model_complete(self):
        """Test that a complete base model can be created."""
        data = GlobalSettingsUpdateModelFactory.build_valid()
        model = GlobalSettingsBaseModel(**data)
        assert model.agent_version == "6.2.1"
        assert model.manual_gateway.region[0].name == "americas"
        assert model.manual_gateway.region[0].locations == ["us-east-1"]

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GlobalSettingsBaseModel(unknown_field="value")
        assert "unknown_field" in str(exc_info.value)


class TestGlobalSettingsUpdateModel:
    """Tests for GlobalSettingsUpdateModel validation."""

    def test_update_model_valid(self):
        """Test that a valid update model can be built."""
        data = GlobalSettingsUpdateModelFactory.build_valid()
        model = GlobalSettingsUpdateModel(**data)
        assert model.agent_version == "6.2.1"

    def test_update_model_from_factory(self):
        """Test that the factory builds a valid model instance."""
        model = GlobalSettingsUpdateModelFactory()
        assert isinstance(model, GlobalSettingsUpdateModel)
        assert model.agent_version is not None
        assert model.manual_gateway is not None

    def test_update_model_partial(self):
        """Test that a partial update payload is valid (singleton PUT)."""
        model = GlobalSettingsUpdateModel(agent_version="6.3.0")
        payload = model.model_dump(exclude_unset=True)
        assert payload == {"agent_version": "6.3.0"}


class TestGlobalSettingsResponseModel:
    """Tests for GlobalSettingsResponseModel validation."""

    def test_response_model_valid(self):
        """Test that a valid response model can be built."""
        model = GlobalSettingsResponseModelFactory()
        assert isinstance(model, GlobalSettingsResponseModel)
        assert model.agent_version is not None

    def test_response_model_ignores_extra_fields(self):
        """Test that the response model ignores unknown fields from the API."""
        model = GlobalSettingsResponseModel(agent_version="6.2.1", future_api_field="value")
        assert model.agent_version == "6.2.1"
        assert not hasattr(model, "future_api_field")


class TestManualGatewayModels:
    """Tests for the nested manual gateway models."""

    def test_manual_gateway_region_valid(self):
        """Test that a region entry can be created."""
        region = ManualGatewayRegion(name="americas", locations=["us-east-1", "us-west-201"])
        assert region.name == "americas"
        assert len(region.locations) == 2

    def test_manual_gateway_empty_region(self):
        """Test that the manual gateway accepts an absent region list."""
        gateway = ManualGateway()
        assert gateway.region is None

    def test_manual_gateway_extra_fields_forbidden(self):
        """Test that extra fields are rejected on nested models."""
        with pytest.raises(ValidationError):
            ManualGateway(unknown_field="value")
