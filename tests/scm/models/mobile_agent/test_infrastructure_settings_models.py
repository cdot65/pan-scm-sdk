# tests/scm/models/mobile_agent/test_infrastructure_settings_models.py

"""Tests for mobile agent infrastructure settings models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.infrastructure_settings import (
    EnableWins,
    InfrastructureSettingsBaseModel,
    InfrastructureSettingsCreateModel,
    InfrastructureSettingsResponseModel,
    InfrastructureSettingsUpdateModel,
    StaticIpPool,
    UdpQueryRetries,
)
from tests.scm.models.mobile_agent.factories import (
    InfrastructureSettingsCreateModelFactory,
    InfrastructureSettingsResponseModelFactory,
    InfrastructureSettingsUpdateModelFactory,
)


class TestInfrastructureSettingsBaseModel:
    """Tests for InfrastructureSettingsBaseModel validation."""

    def test_base_model_valid(self):
        """Test that a valid base model can be created."""
        data = InfrastructureSettingsCreateModelFactory.build_valid()
        model = InfrastructureSettingsBaseModel(**data)
        assert model.name == data["name"]
        assert len(model.dns_servers) == 1
        assert len(model.ip_pools) == 1
        assert model.portal_hostname.default_domain.hostname is not None

    def test_base_model_missing_required_fields(self):
        """Test validation when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            InfrastructureSettingsBaseModel(name="test-settings")
        errors = str(exc_info.value)
        assert "dns_servers\n  Field required" in errors
        assert "ip_pools\n  Field required" in errors
        assert "portal_hostname\n  Field required" in errors

    def test_base_model_optional_fields(self):
        """Test that optional fields can be provided."""
        data = InfrastructureSettingsCreateModelFactory.build_valid()
        data["ipv6"] = True
        data["enable_wins"] = {"yes": {"wins_servers": [{"name": "w1", "primary": "1.1.1.1"}]}}
        data["udp_queries"] = {"retries": {"attempts": 5, "interval": 2}}
        data["static_ip_pools"] = [
            {
                "name": "pool-1",
                "pool_type": "Static-IP",
                "ip_pool": ["10.1.0.0/24"],
                "user_groups": [{"name": "cn=group,dc=example,dc=com", "directory": "ldap"}],
            }
        ]
        model = InfrastructureSettingsBaseModel(**data)
        assert model.ipv6 is True
        assert model.enable_wins.yes.wins_servers[0].primary == "1.1.1.1"
        assert model.udp_queries.retries.attempts == 5
        assert model.static_ip_pools[0].pool_type == "Static-IP"

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = InfrastructureSettingsCreateModelFactory.build_valid()
        data["unknown_field"] = "value"
        with pytest.raises(ValidationError) as exc_info:
            InfrastructureSettingsBaseModel(**data)
        assert "unknown_field" in str(exc_info.value)

    def test_base_model_no_folder_field(self):
        """Test that folder is not a body field (it's a query parameter)."""
        data = InfrastructureSettingsCreateModelFactory.build_valid()
        data["folder"] = "Mobile Users"
        with pytest.raises(ValidationError) as exc_info:
            InfrastructureSettingsBaseModel(**data)
        assert "folder" in str(exc_info.value)


class TestInfrastructureSettingsCreateModel:
    """Tests for InfrastructureSettingsCreateModel validation."""

    def test_create_model_valid(self):
        """Test that a valid create model can be built."""
        data = InfrastructureSettingsCreateModelFactory.build_valid()
        model = InfrastructureSettingsCreateModel(**data)
        assert model.name == data["name"]

    def test_create_model_from_factory(self):
        """Test that the factory builds a valid model instance."""
        model = InfrastructureSettingsCreateModelFactory()
        assert isinstance(model, InfrastructureSettingsCreateModel)
        assert model.name is not None

    def test_create_model_missing_required(self):
        """Test validation when a required field is missing."""
        data = InfrastructureSettingsCreateModelFactory.build_missing_required()
        with pytest.raises(ValidationError) as exc_info:
            InfrastructureSettingsCreateModel(**data)
        assert "dns_servers\n  Field required" in str(exc_info.value)

    def test_create_model_no_id_field(self):
        """Test that id is not accepted on create (it is read-only)."""
        data = InfrastructureSettingsCreateModelFactory.build_valid()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"
        with pytest.raises(ValidationError) as exc_info:
            InfrastructureSettingsCreateModel(**data)
        assert "id" in str(exc_info.value)


class TestInfrastructureSettingsUpdateModel:
    """Tests for InfrastructureSettingsUpdateModel validation."""

    def test_update_model_valid(self):
        """Test that a valid update model can be built."""
        data = InfrastructureSettingsUpdateModelFactory.build_valid()
        model = InfrastructureSettingsUpdateModel(**data)
        assert model.name == data["name"]

    def test_update_model_requires_name(self):
        """Test that the update model requires name (addressed by name, not ID)."""
        data = InfrastructureSettingsUpdateModelFactory.build_valid()
        del data["name"]
        with pytest.raises(ValidationError) as exc_info:
            InfrastructureSettingsUpdateModel(**data)
        assert "name\n  Field required" in str(exc_info.value)


class TestInfrastructureSettingsResponseModel:
    """Tests for InfrastructureSettingsResponseModel validation."""

    def test_response_model_valid(self):
        """Test that a valid response model can be built."""
        data = InfrastructureSettingsResponseModelFactory.build_valid()
        model = InfrastructureSettingsResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]

    def test_response_model_requires_id(self):
        """Test that the response model requires the id field."""
        data = InfrastructureSettingsCreateModelFactory.build_valid()
        with pytest.raises(ValidationError) as exc_info:
            InfrastructureSettingsResponseModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that the response model ignores unknown fields from the API."""
        data = InfrastructureSettingsResponseModelFactory.build_valid()
        data["future_api_field"] = "value"
        model = InfrastructureSettingsResponseModel(**data)
        assert not hasattr(model, "future_api_field")


class TestInfrastructureSettingsNestedModels:
    """Tests for the nested supporting models."""

    def test_udp_query_retries_constraints(self):
        """Test that attempts and interval enforce the 1-30 range."""
        assert UdpQueryRetries(attempts=1, interval=30).attempts == 1

        with pytest.raises(ValidationError):
            UdpQueryRetries(attempts=0)

        with pytest.raises(ValidationError):
            UdpQueryRetries(attempts=31)

        with pytest.raises(ValidationError):
            UdpQueryRetries(interval=31)

    def test_static_ip_pool_pool_type_enum(self):
        """Test that pool_type only accepts 'Static-IP'."""
        assert StaticIpPool(pool_type="Static-IP").pool_type == "Static-IP"

        with pytest.raises(ValidationError):
            StaticIpPool(pool_type="Dynamic-IP")

    def test_static_ip_pool_name_max_length(self):
        """Test that the static IP pool name enforces its maximum length."""
        with pytest.raises(ValidationError):
            StaticIpPool(name="a" * 129)

    def test_static_ip_pool_user_group_name_max_length(self):
        """Test that the user group name enforces its maximum length."""
        with pytest.raises(ValidationError):
            StaticIpPool(user_groups=[{"name": "a" * 321}])

    def test_enable_wins_choice(self):
        """Test the yes/no WINS configuration shapes."""
        disabled = EnableWins(no={})
        assert disabled.no == {}
        assert disabled.yes is None

        enabled = EnableWins(yes={"wins_servers": [{"name": "w1", "primary": "1.1.1.1"}]})
        assert enabled.yes.wins_servers[0].name == "w1"
        assert enabled.no is None
