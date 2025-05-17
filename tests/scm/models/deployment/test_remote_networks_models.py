# tests/scm/models/deployment/test_remote_networks_models.py

"""Tests for remote network deployment models."""

from pydantic import ValidationError
import pytest

from scm.models.deployment.remote_networks import (
    RemoteNetworkCreateModel,
    RemoteNetworkUpdateModel,
)
from tests.factories.deployment.remote_networks import (
    RemoteNetworkCreateModelFactory,
    RemoteNetworkUpdateModelFactory,
)


class TestRemoteNetworkCreateModel:
    """Tests for the RemoteNetworkCreateModel pydantic validation."""

    def test_valid_model_creation(self):
        """Test creating model with valid data."""
        data = RemoteNetworkCreateModelFactory.build_valid()
        model = RemoteNetworkCreateModel(**data)
        assert model.name == data["name"]
        assert model.region == data["region"]
        assert model.folder == data["folder"]

    def test_ecmp_enabled_validation(self):
        """Test validation fails when ecmp_load_balancing=enable but no ecmp_tunnels provided."""
        data = RemoteNetworkCreateModelFactory.build_valid()
        data["ecmp_load_balancing"] = "enable"
        data["ecmp_tunnels"] = None
        with pytest.raises(ValueError) as exc_info:
            RemoteNetworkCreateModel(**data)
        assert "ecmp_tunnels is required when ecmp_load_balancing is enable" in str(exc_info.value)

    def test_disable_ecmp_missing_ipsec_tunnel(self):
        """Test validation fails when ecmp_load_balancing=disable (the default).

        But ipsec_tunnel is not provided.
        """
        data = RemoteNetworkCreateModelFactory.build_valid()
        # ecmp_load_balancing is disable by default, so just ensure ipsec_tunnel is None
        data["ipsec_tunnel"] = None

        with pytest.raises(ValueError) as exc_info:
            RemoteNetworkCreateModel(**data)

        # Verify the error message
        assert "ipsec_tunnel is required when ecmp_load_balancing is disable" in str(exc_info.value)

    def test_no_container(self):
        """Test validation fails when no container field is provided at all."""
        data = RemoteNetworkCreateModelFactory.build_no_container()
        with pytest.raises(ValueError) as exc_info:
            RemoteNetworkCreateModel(**data)
        assert "Exactly one of 'folder' must be provided" in str(exc_info.value)

    def test_missing_spn_name(self):
        """Test validation fails when license_type=FWAAS-AGGREGATE but spn_name is missing."""
        data = RemoteNetworkCreateModelFactory.without_spn_name()
        with pytest.raises(ValueError) as exc_info:
            RemoteNetworkCreateModel(**data)
        assert "spn_name is required when license_type is FWAAS-AGGREGATE" in str(exc_info.value)

    def test_ecmp_tunnels_limit(self):
        """Test validation of max_length=4 for ecmp_tunnels."""
        data = RemoteNetworkCreateModelFactory.build_ecmp_enabled(ecmp_count=5)
        with pytest.raises(ValidationError) as exc_info:
            RemoteNetworkCreateModel(**data)
        assert "List should have at most 4 items after validation, not 5" in str(exc_info.value)

    def test_valid_ecmp_config(self):
        """Test valid ECMP configuration passes validation."""
        data = RemoteNetworkCreateModelFactory.build_ecmp_enabled()
        model = RemoteNetworkCreateModel(**data)
        assert model.ecmp_load_balancing == "enable"
        assert len(model.ecmp_tunnels) > 0

    def test_invalid_peering_type(self):
        """Test validation with invalid peering type."""
        data = RemoteNetworkCreateModelFactory.build_valid()
        data["protocol"] = {"bgp": {"peering_type": "invalid"}}
        with pytest.raises(ValidationError):
            RemoteNetworkCreateModel(**data)

    def test_name_pattern_validation(self):
        """Test name field pattern validation."""
        data = RemoteNetworkCreateModelFactory.build_valid()
        data["name"] = "@invalid-name"
        with pytest.raises(ValidationError):
            RemoteNetworkCreateModel(**data)


class TestRemoteNetworkUpdateModel:
    """Tests for the RemoteNetworkUpdateModel pydantic validation."""

    def test_valid_model_update(self):
        """Test updating model with valid data."""
        data = RemoteNetworkUpdateModelFactory.build_valid()
        model = RemoteNetworkUpdateModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.region == data["region"]

    def test_ecmp_enabled_validation(self):
        """Test validation fails when ecmp_load_balancing=enable but no ecmp_tunnels are provided."""
        data = RemoteNetworkUpdateModelFactory.build_valid()
        data["ecmp_load_balancing"] = "enable"
        data["ecmp_tunnels"] = None
        with pytest.raises(ValueError) as exc_info:
            RemoteNetworkUpdateModel(**data)
        assert "ecmp_tunnels is required when ecmp_load_balancing is enable" in str(exc_info.value)

    def test_missing_spn_name(self):
        """Test validation fails when license_type=FWAAS-AGGREGATE but spn_name is missing."""
        data = RemoteNetworkUpdateModelFactory.without_spn_name()
        with pytest.raises(ValueError) as exc_info:
            RemoteNetworkUpdateModel(**data)
        assert "spn_name is required when license_type is FWAAS-AGGREGATE" in str(exc_info.value)

    def test_disable_ecmp_missing_ipsec_tunnel(self):
        """Test validation fails when ecmp_load_balancing=disable (the default).

        But ipsec_tunnel is not provided on update.
        """
        data = RemoteNetworkUpdateModelFactory.build_valid()
        data["ipsec_tunnel"] = None

        with pytest.raises(ValueError) as exc_info:
            RemoteNetworkUpdateModel(**data)

        assert "ipsec_tunnel is required when ecmp_load_balancing is disable" in str(exc_info.value)
