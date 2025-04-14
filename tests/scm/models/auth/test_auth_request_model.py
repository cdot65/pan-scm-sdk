# tests/scm/models/auth/test_auth_request_model.py

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.auth import AuthRequestModel

# -------------------- Test Classes for Pydantic Models --------------------


class TestAuthRequestModel:
    """Tests for AuthRequestModel validation."""

    def test_auth_request_model_valid(self):
        """Test validation with valid data."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
        }
        model = AuthRequestModel(**data)
        assert model.client_id == data["client_id"]
        assert model.client_secret == data["client_secret"]
        assert model.tsg_id == data["tsg_id"]
        assert model.scope == "tsg_id:test_tsg_id"
        assert model.token_url == "https://auth.apps.paloaltonetworks.com/am/oauth2/access_token"

    def test_auth_request_model_with_custom_scope(self):
        """Test validation when custom scope is provided."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": "custom_scope",
        }
        model = AuthRequestModel(**data)
        assert model.scope == "custom_scope"

    def test_auth_request_model_with_custom_token_url(self):
        """Test validation when custom token URL is provided."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "token_url": "https://custom.auth.url/token",
        }
        model = AuthRequestModel(**data)
        assert model.token_url == "https://custom.auth.url/token"

    def test_auth_request_model_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {"client_id": "test_client_id"}
        with pytest.raises(ValidationError) as exc_info:
            AuthRequestModel(**data)
        error_msg = str(exc_info.value)
        assert (
            "1 validation error for AuthRequestModel\n  Value error, tsg_id is required to construct scope"
            in error_msg
        )

    # def test_auth_request_model_empty_fields(self):
    #     """Test validation when fields are empty strings."""
    #     data = {
    #         "client_id": "",
    #         "client_secret": "",
    #         "tsg_id": "",
    #     }
    #     with pytest.raises(ValidationError) as exc_info:
    #         AuthRequestModel(**data)
    #     error_msg = str(exc_info.value)
    #     assert "validation error" in error_msg

    def test_auth_request_model_missing_tsg_id_with_no_scope(self):
        """Test validation when tsg_id is missing and no scope is provided."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": None,
        }
        with pytest.raises(ValueError) as exc_info:
            AuthRequestModel(**data)
        assert "tsg_id is required to construct scope" in str(exc_info.value)

    def test_auth_request_model_empty_scope(self):
        """Test validation when scope is an empty string."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": "",
        }
        with pytest.raises(ValueError) as exc_info:
            AuthRequestModel(**data)
        assert "Scope cannot be empty string" in str(exc_info.value)

    def test_auth_request_model_whitespace_scope(self):
        """Test validation when scope contains only whitespace."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": "   ",
        }
        with pytest.raises(ValueError) as exc_info:
            AuthRequestModel(**data)
        assert "Scope cannot be empty string" in str(exc_info.value)

    def test_auth_request_model_none_scope(self):
        """Test validation when scope is explicitly set to None."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": None,
        }
        model = AuthRequestModel(**data)
        assert model.scope == "tsg_id:test_tsg_id"

    def test_auth_request_model_invalid_type(self):
        """Test validation when fields have invalid types."""
        data = {
            "client_id": 123,  # Should be string
            "client_secret": ["secret"],  # Should be string
            "tsg_id": {"id": "test"},  # Should be string
        }
        with pytest.raises(ValidationError) as exc_info:
            AuthRequestModel(**data)
        error_msg = str(exc_info.value)
        assert "3 validation errors for AuthRequestModel" in error_msg
        assert "client_id\n  Input should be a valid string" in error_msg
        assert "client_secret\n  Input should be a valid string" in error_msg
        assert "tsg_id\n  Input should be a valid string" in error_msg

    def test_construct_scope_validator_with_missing_tsg_id(self):
        """Test scope construction validator when tsg_id is missing."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": None,
            "scope": None,
        }
        with pytest.raises(ValueError) as exc_info:
            AuthRequestModel(**data)
        assert "tsg_id is required to construct scope" in str(exc_info.value)

    def test_construct_scope_validator_with_none_scope(self):
        """Test scope construction validator when scope is None."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": None,
        }
        model = AuthRequestModel(**data)
        assert model.scope == "tsg_id:test_tsg_id"

    def test_construct_scope_validator_with_existing_scope(self):
        """Test scope construction validator when scope is provided."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": "custom:scope",
        }
        model = AuthRequestModel(**data)
        assert model.scope == "custom:scope"

    def test_validate_scope_with_empty_string(self):
        """Test scope validator with empty string."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": "",
        }
        with pytest.raises(ValueError) as exc_info:
            AuthRequestModel(**data)
        assert "Scope cannot be empty string" in str(exc_info.value)

    def test_validate_scope_with_whitespace(self):
        """Test scope validator with whitespace string."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": "   ",
        }
        with pytest.raises(ValueError) as exc_info:
            AuthRequestModel(**data)
        assert "Scope cannot be empty string" in str(exc_info.value)

    def test_validate_scope_with_valid_string(self):
        """Test scope validator with valid string."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": "valid:scope",
        }
        model = AuthRequestModel(**data)
        assert model.scope == "valid:scope"

    def test_validate_scope_with_none_value(self):
        """Test scope validator with None value."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": None,
        }
        model = AuthRequestModel(**data)
        assert model.scope == "tsg_id:test_tsg_id"

    def test_construct_scope_validator_order(self):
        """Test that construct_scope validator runs before validate_scope."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "test_tsg_id",
            "scope": None,
        }
        model = AuthRequestModel(**data)
        # If construct_scope runs first, we should get a valid constructed scope
        # If validate_scope ran first, it might incorrectly validate None
        assert model.scope == "tsg_id:test_tsg_id"

    def test_scope_validators_with_empty_tsg_id(self):
        """Test both validators with empty tsg_id string."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "",
            "scope": None,
        }
        model = AuthRequestModel(**data)
        assert model.scope == "tsg_id:"

    def test_scope_construction_with_special_characters(self):
        """Test scope construction with special characters in tsg_id."""
        data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tsg_id": "special@#$%^&*",
            "scope": None,
        }
        model = AuthRequestModel(**data)
        assert model.scope == "tsg_id:special@#$%^&*"


# -------------------- End of Test Classes --------------------
