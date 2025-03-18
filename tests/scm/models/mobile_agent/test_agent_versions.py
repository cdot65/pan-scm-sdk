# tests/scm/models/mobile_agent/test_agent_versions.py

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.mobile_agent.agent_versions import AgentVersionsModel, AgentVersionModel
from tests.scm.models.mobile_agent.factories import AgentVersionsModelFactory, AgentVersionModelFactory


class TestAgentVersionModel:
    """Tests for AgentVersionModel."""

    def test_model_valid(self):
        """Test creation with valid data."""
        model = AgentVersionModelFactory()
        assert model.version is not None
        assert isinstance(model.version, str)
        
        # Optional fields may be None
        if model.release_date is not None:
            assert isinstance(model.release_date, str)
        
        assert isinstance(model.is_recommended, bool) or model.is_recommended is None

    def test_model_minimal(self):
        """Test creation with only required fields."""
        model = AgentVersionModel(version="5.3.0")
        assert model.version == "5.3.0"
        assert model.release_date is None
        assert model.is_recommended is None

    def test_model_complete(self):
        """Test creation with all fields."""
        data = {
            "version": "5.3.0",
            "release_date": "2023-05-15",
            "is_recommended": True
        }
        model = AgentVersionModel(**data)
        assert model.version == data["version"]
        assert model.release_date == data["release_date"]
        assert model.is_recommended == data["is_recommended"]

    def test_model_missing_required_field(self):
        """Test validation when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            AgentVersionModel()
        assert "version\n  Field required" in str(exc_info.value)

    def test_model_assignment_validation(self):
        """Test that assignment validation works."""
        model = AgentVersionModel(version="5.3.0")
        
        # Valid assignment
        model.version = "5.2.8"
        assert model.version == "5.2.8"
        
        # Valid optional field assignment
        model.release_date = "2023-06-20"
        assert model.release_date == "2023-06-20"
        
        model.is_recommended = True
        assert model.is_recommended is True

    def test_model_dump(self):
        """Test serialization to dictionary."""
        data = {
            "version": "5.3.0",
            "release_date": "2023-05-15",
            "is_recommended": True
        }
        model = AgentVersionModel(**data)
        model_dict = model.model_dump()
        
        assert model_dict["version"] == data["version"]
        assert model_dict["release_date"] == data["release_date"]
        assert model_dict["is_recommended"] == data["is_recommended"]


class TestAgentVersionsModel:
    """Tests for AgentVersionsModel validation."""

    def test_model_valid(self):
        """Test model creation with valid data."""
        model = AgentVersionsModelFactory()
        assert isinstance(model.agent_versions, list)
        assert all(isinstance(version, str) for version in model.agent_versions)
        assert len(model.agent_versions) > 0

    def test_model_with_empty_versions_list(self):
        """Test model creation with empty agent_versions list."""
        model = AgentVersionsModelFactory(agent_versions=[])
        assert isinstance(model.agent_versions, list)
        assert len(model.agent_versions) == 0

    def test_model_with_custom_versions(self):
        """Test model creation with custom agent versions."""
        custom_versions = ["5.3.0", "5.2.8", "5.2.7", "5.1.5"]
        model = AgentVersionsModelFactory(agent_versions=custom_versions)
        assert model.agent_versions == custom_versions
        assert len(model.agent_versions) == 4

    def test_model_missing_required_field(self):
        """Test validation when agent_versions field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            AgentVersionsModel()
        assert "agent_versions\n  Field required" in str(exc_info.value)

    def test_model_invalid_type(self):
        """Test validation when agent_versions is not a list."""
        with pytest.raises(ValidationError) as exc_info:
            AgentVersionsModel(agent_versions="5.3.0")
        assert "agent_versions\n  Input should be a valid" in str(exc_info.value)

    def test_model_invalid_items_type(self):
        """Test validation when agent_versions contains non-string items."""
        with pytest.raises(ValidationError) as exc_info:
            AgentVersionsModel(agent_versions=["5.3.0", 5.2, True])
        error_msg = str(exc_info.value)
        assert "Input should be a valid string" in error_msg

    def test_model_dump(self):
        """Test model serialization to dictionary."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        model = AgentVersionsModelFactory(agent_versions=versions)
        model_dict = model.model_dump()
        assert "agent_versions" in model_dict
        assert model_dict["agent_versions"] == versions

    def test_model_from_dict(self):
        """Test model creation from dictionary."""
        data = {"agent_versions": ["5.3.0", "5.2.8", "5.2.7"]}
        model = AgentVersionsModel(**data)
        assert model.agent_versions == data["agent_versions"]

    def test_model_assignment_validation(self):
        """Test that assignment validation works."""
        model = AgentVersionsModelFactory(agent_versions=["5.3.0"])
        
        # Valid assignment
        model.agent_versions = ["5.2.8", "5.2.7"]
        assert model.agent_versions == ["5.2.8", "5.2.7"]
        
        # Invalid assignment should raise ValidationError
        with pytest.raises(ValidationError):
            model.agent_versions = "not-a-list"
