# tests/scm/models/mobile_agent/test_auth_settings_models.py

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.mobile_agent.auth_settings import (
    AuthSettingsBaseModel,
    AuthSettingsCreateModel,
    AuthSettingsMoveModel,
    AuthSettingsUpdateModel,
    MovePosition,
    OperatingSystem,
)
from tests.scm.models.mobile_agent.factories import (
    AuthSettingsBaseModelFactory,
    AuthSettingsCreateModelFactory,
    AuthSettingsMoveModelFactory,
    AuthSettingsResponseModelFactory,
    AuthSettingsUpdateModelFactory,
)


class TestOperatingSystem:
    """Tests for the OperatingSystem enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert OperatingSystem.ANY == "Any"
        assert OperatingSystem.ANDROID == "Android"
        assert OperatingSystem.BROWSER == "Browser"
        assert OperatingSystem.CHROME == "Chrome"
        assert OperatingSystem.IOT == "IoT"
        assert OperatingSystem.LINUX == "Linux"
        assert OperatingSystem.MAC == "Mac"
        assert OperatingSystem.SATELLITE == "Satellite"
        assert OperatingSystem.WINDOWS == "Windows"
        assert OperatingSystem.WINDOWS_UWP == "WindowsUWP"
        assert OperatingSystem.IOS == "iOS"


class TestMovePosition:
    """Tests for the MovePosition enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert MovePosition.BEFORE == "before"
        assert MovePosition.AFTER == "after"
        assert MovePosition.TOP == "top"
        assert MovePosition.BOTTOM == "bottom"


class TestAuthSettingsBaseModel:
    """Tests for AuthSettingsBaseModel validation."""

    def test_base_model_minimal(self):
        """Test that a minimal base model can be created."""
        model = AuthSettingsBaseModelFactory(
            folder=None, user_credential_or_client_cert_required=None
        )
        assert model.name is not None
        assert model.authentication_profile is not None
        assert model.os is not None
        assert model.user_credential_or_client_cert_required is None
        assert model.folder is None

    def test_base_model_complete(self):
        """Test that a complete base model can be created."""
        model = AuthSettingsBaseModelFactory(os=OperatingSystem.WINDOWS)
        assert model.name is not None
        assert model.authentication_profile is not None
        assert model.os == OperatingSystem.WINDOWS
        # This field can be either boolean or None
        assert model.user_credential_or_client_cert_required is not None
        assert model.folder == "Mobile Users"

    def test_base_model_invalid_name(self):
        """Test validation when name has invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsBaseModel(
                name="invalid@name",
                authentication_profile="test-profile",
            )
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_base_model_missing_required_fields(self):
        """Test validation when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsBaseModel(name="test-settings")
        assert "authentication_profile\n  Field required" in str(exc_info.value)
        # user_credential_or_client_cert_required is now optional, so we shouldn't check for it

    def test_base_model_invalid_folder(self):
        """Test validation when folder value is invalid."""
        with pytest.raises(ValueError) as exc_info:
            AuthSettingsBaseModel(
                name="test-settings", authentication_profile="test-profile", folder="Invalid Folder"
            )
        assert "Folder must be 'Mobile Users'" in str(exc_info.value)

    def test_base_model_folder_pattern_validation(self):
        """Test folder pattern validation."""
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsBaseModel(
                name="test-settings",
                authentication_profile="test-profile",
                folder="Invalid@Folder",  # contains invalid character
            )
        assert "folder\n  String should match pattern" in str(exc_info.value)

    def test_model_dump(self):
        """Test model dumping to dictionary."""
        model = AuthSettingsBaseModelFactory(os=OperatingSystem.WINDOWS)
        model_dict = model.model_dump()
        assert model_dict["name"] == model.name
        assert model_dict["authentication_profile"] == model.authentication_profile
        assert model_dict["os"] == OperatingSystem.WINDOWS
        assert (
            model_dict["user_credential_or_client_cert_required"]
            == model.user_credential_or_client_cert_required
        )
        assert model_dict["folder"] == "Mobile Users"

    def test_name_validation_length(self):
        """Test name length validation."""
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsBaseModel(
                name="a" * 64,  # Max length is 63
                authentication_profile="test-profile",
            )
        assert "name\n  String should have at most 63 characters" in str(exc_info.value)


class TestAuthSettingsCreateModel:
    """Tests for AuthSettingsCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = AuthSettingsCreateModelFactory.build_valid()
        model = AuthSettingsCreateModel(**data)
        assert model.name == data["name"]
        assert model.authentication_profile == data["authentication_profile"]
        assert model.os == data["os"]
        # This might be None in the model if the field is optional
        if "user_credential_or_client_cert_required" in data:
            assert (
                model.user_credential_or_client_cert_required
                == data["user_credential_or_client_cert_required"]
            )
        assert model.folder == data["folder"]

    def test_create_model_invalid_name(self):
        """Test validation when name has invalid format."""
        data = AuthSettingsCreateModelFactory.build_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsCreateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_create_model_invalid_folder(self):
        """Test validation when folder value is invalid."""
        data = AuthSettingsCreateModelFactory.build_invalid_folder()
        with pytest.raises(ValueError) as exc_info:
            AuthSettingsCreateModel(**data)
        assert "Folder must be 'Mobile Users'" in str(exc_info.value)

    def test_create_model_missing_folder(self):
        """Test validation when folder is not provided."""
        data = AuthSettingsCreateModelFactory.build_missing_folder()
        with pytest.raises(ValueError) as exc_info:
            AuthSettingsCreateModel(**data)
        assert "Folder is required for GlobalProtect Authentication Settings" in str(exc_info.value)

    def test_create_model_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  Field required" in error_msg
        assert "authentication_profile\n  Field required" in error_msg
        # user_credential_or_client_cert_required is now optional, should not be in error message

    def test_create_model_with_all_operating_systems(self):
        """Test creating models with all possible operating system values."""
        for os_value in OperatingSystem:
            model = AuthSettingsCreateModelFactory(os=os_value)
            assert model.os == os_value


class TestAuthSettingsUpdateModel:
    """Tests for AuthSettingsUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = AuthSettingsUpdateModelFactory.build_valid()
        model = AuthSettingsUpdateModel(**data)
        assert model.name == data["name"]
        assert model.authentication_profile == data["authentication_profile"]
        assert model.os == data["os"]
        # This might be None in the model if the field is optional
        if "user_credential_or_client_cert_required" in data:
            assert (
                model.user_credential_or_client_cert_required
                == data["user_credential_or_client_cert_required"]
            )
        assert model.folder == data["folder"]

    def test_update_model_minimal(self):
        """Test validation with minimal update data."""
        data = AuthSettingsUpdateModelFactory.build_minimal_update()
        model = AuthSettingsUpdateModel(**data)
        assert model.authentication_profile == data["authentication_profile"]
        assert model.name is None
        assert model.os is None
        assert model.user_credential_or_client_cert_required is None
        assert model.folder is None

    def test_update_model_invalid_name(self):
        """Test validation when name has invalid format."""
        data = AuthSettingsUpdateModelFactory.build_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsUpdateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_update_model_invalid_folder(self):
        """Test validation when folder value is invalid."""
        data = AuthSettingsUpdateModelFactory.build_invalid_folder()
        with pytest.raises(ValueError) as exc_info:
            AuthSettingsUpdateModel(**data)
        assert "Folder must be 'Mobile Users'" in str(exc_info.value)

    def test_update_model_partial_updates(self):
        """Test that partial updates work correctly."""
        # Test each field individually
        fields_to_test = [
            {"name": "new-name"},
            {"authentication_profile": "new-profile"},
            {"os": OperatingSystem.IOS},
            {"user_credential_or_client_cert_required": False},
            {"folder": "Mobile Users"},
        ]

        for field_data in fields_to_test:
            data = {}
            data.update(field_data)

            model = AuthSettingsUpdateModel(**data)

            for key, value in field_data.items():
                assert getattr(model, key) == value


class TestAuthSettingsResponseModel:
    """Tests for AuthSettingsResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        model = AuthSettingsResponseModelFactory()
        assert model.name is not None
        assert model.authentication_profile is not None
        assert model.os is not None
        assert (
            model.user_credential_or_client_cert_required is not None
            or model.user_credential_or_client_cert_required is None
        )
        assert model.folder == "Mobile Users"

    def test_response_model_minimal(self):
        """Test validation with minimal response data."""
        model = AuthSettingsResponseModelFactory(
            folder=None, user_credential_or_client_cert_required=None
        )
        assert model.name is not None
        assert model.authentication_profile is not None
        assert model.folder is None
        assert model.user_credential_or_client_cert_required is None

    def test_response_model_inheritance(self):
        """Test that ResponseModel inherits properly from BaseModel."""
        model = AuthSettingsResponseModelFactory(os=OperatingSystem.WINDOWS)

        # Test that validators from base class are inherited
        assert model.folder == "Mobile Users"

        # Test model configuration inheritance
        assert model.model_config["arbitrary_types_allowed"] is True

        # Convert to dict and verify
        model_dict = model.model_dump()
        assert model_dict["os"] == OperatingSystem.WINDOWS


class TestAuthSettingsMoveModel:
    """Tests for AuthSettingsMoveModel validation."""

    def test_move_model_valid_before(self):
        """Test validation with valid before move configuration."""
        data = AuthSettingsMoveModelFactory.build_valid_before()
        model = AuthSettingsMoveModel(**data)
        assert model.name == data["name"]
        assert model.where == MovePosition.BEFORE
        assert model.destination == data["destination"]

    def test_move_model_valid_after(self):
        """Test validation with valid after move configuration."""
        data = AuthSettingsMoveModelFactory.build_valid_after()
        model = AuthSettingsMoveModel(**data)
        assert model.name == data["name"]
        assert model.where == MovePosition.AFTER
        assert model.destination == data["destination"]

    def test_move_model_valid_top(self):
        """Test validation with valid top move configuration."""
        data = AuthSettingsMoveModelFactory.build_valid_top()
        model = AuthSettingsMoveModel(**data)
        assert model.name == data["name"]
        assert model.where == MovePosition.TOP
        assert model.destination is None

    def test_move_model_valid_bottom(self):
        """Test validation with valid bottom move configuration."""
        data = AuthSettingsMoveModelFactory.build_valid_bottom()
        model = AuthSettingsMoveModel(**data)
        assert model.name == data["name"]
        assert model.where == MovePosition.BOTTOM
        assert model.destination is None

    def test_move_model_missing_name(self):
        """Test validation when name is missing."""
        data = {
            "where": MovePosition.TOP,
        }
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsMoveModel(**data)
        assert "name\n  Field required" in str(exc_info.value)

    def test_move_model_missing_where(self):
        """Test validation when where is missing."""
        data = {
            "name": "test-settings",
        }
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsMoveModel(**data)
        assert "where\n  Field required" in str(exc_info.value)

    def test_move_model_before_missing_destination(self):
        """Test validation when destination is missing for before move."""
        data = AuthSettingsMoveModelFactory.build_invalid_before_missing_destination()
        with pytest.raises(ValueError) as exc_info:
            AuthSettingsMoveModel(**data)
        # The error message in the model may contain both 'before' and 'after'
        assert "Destination is required when where is" in str(exc_info.value)
        assert "before" in str(exc_info.value)

    def test_move_model_after_missing_destination(self):
        """Test validation when destination is missing for after move."""
        data = {
            "name": "test-auth-settings",
            "where": MovePosition.AFTER,
        }
        with pytest.raises(ValueError) as exc_info:
            AuthSettingsMoveModel(**data)
        # The error message in the model may contain both 'before' and 'after'
        assert "Destination is required when where is" in str(exc_info.value)
        assert "after" in str(exc_info.value)

    def test_move_model_top_with_destination(self):
        """Test validation when destination is provided for top move."""
        data = AuthSettingsMoveModelFactory.build_invalid_top_with_destination()
        with pytest.raises(ValueError) as exc_info:
            AuthSettingsMoveModel(**data)
        assert "Destination should not be provided" in str(exc_info.value)

    def test_move_model_bottom_with_destination(self):
        """Test validation when destination is provided for bottom move."""
        data = {
            "name": "test-auth-settings",
            "where": MovePosition.BOTTOM,
            "destination": "target-auth-settings",
        }
        with pytest.raises(ValueError) as exc_info:
            AuthSettingsMoveModel(**data)
        assert "Destination should not be provided" in str(exc_info.value)

    def test_move_model_invalid_where(self):
        """Test validation when where has invalid value."""
        data = {
            "name": "test-settings",
            "where": "invalid",
        }
        with pytest.raises(ValidationError) as exc_info:
            AuthSettingsMoveModel(**data)
        assert "where\n  Input should be" in str(exc_info.value)
