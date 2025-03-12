import pytest
from pydantic import ValidationError

from scm.models.operations import CandidatePushRequestModel


class TestCandidatePushRequestModel:
    """Tests for CandidatePushRequestModel validators."""

    def test_valid_model(self):
        """Test model with valid data."""
        valid_data = {
            "folders": ["folder1", "folder2"],
            "admin": ["admin@example.com", "other@example.com"],
            "description": "Test commit",
        }
        model = CandidatePushRequestModel(**valid_data)
        assert model.folders == valid_data["folders"]
        assert model.admin == valid_data["admin"]
        assert model.description == valid_data["description"]

    def test_folders_empty_list(self):
        """Test validation with empty folders list."""
        invalid_data = {
            "folders": [],
            "admin": ["admin@example.com"],
            "description": "Test commit",
        }
        with pytest.raises(ValidationError) as exc_info:
            CandidatePushRequestModel(**invalid_data)

        error = exc_info.value
        assert (
            "1 validation error for CandidatePushRequestModel\nfolders\n  List should have at least 1 item after validation, not 0"
            in str(error)
        )

    def test_validate_folders_empty_value(self):
        """Test validate_folders method with empty value."""
        with pytest.raises(ValueError) as exc_info:
            CandidatePushRequestModel.validate_folders(None)
        assert str(exc_info.value) == "At least one folder must be specified"

        with pytest.raises(ValueError) as exc_info:
            CandidatePushRequestModel.validate_folders([])
        assert str(exc_info.value) == "At least one folder must be specified"

    def test_validate_admin_empty_value(self):
        """Test validate_admin method with empty value."""
        with pytest.raises(ValueError) as exc_info:
            CandidatePushRequestModel.validate_admin(None)
        assert str(exc_info.value) == "At least one admin must be specified"

        with pytest.raises(ValueError) as exc_info:
            CandidatePushRequestModel.validate_admin([])
        assert str(exc_info.value) == "At least one admin must be specified"

    def test_folders_invalid_strings(self):
        """Test validation with invalid folder strings."""
        test_cases = [
            {"folders": ["", "folder2"], "desc": "empty string"},
            {"folders": ["folder1", "   "], "desc": "whitespace string"},
            {"folders": [123, "folder2"], "desc": "non-string value"},
        ]

        for case in test_cases:
            invalid_data = {
                "folders": case["folders"],
                "admin": ["admin@example.com"],
                "description": "Test commit",
            }
            with pytest.raises(ValidationError) as exc_info:
                CandidatePushRequestModel(**invalid_data)

            error = exc_info.value
            assert "1 validation error for CandidatePushRequestModel" in str(error), (
                f"Failed for {case['desc']}"
            )

    def test_admin_empty_list(self):
        """Test validation with empty admin list."""
        invalid_data = {
            "folders": ["folder1"],
            "admin": [],
            "description": "Test commit",
        }
        with pytest.raises(ValidationError) as exc_info:
            CandidatePushRequestModel(**invalid_data)

        error = exc_info.value
        assert "1 validation error for CandidatePushRequestModel" in str(error)

    def test_admin_invalid_emails(self):
        """Test validation with invalid email addresses."""
        test_cases = [
            {"admin": ["invalid-email", "admin@example.com"], "desc": "no @ symbol"},
            {"admin": ["admin@example.com", ""], "desc": "empty string"},
            {"admin": [123, "admin@example.com"], "desc": "non-string value"},
            {"admin": ["admin@example.com", "   "], "desc": "whitespace string"},
        ]

        for case in test_cases:
            invalid_data = {
                "folders": ["folder1"],
                "admin": case["admin"],
                "description": "Test commit",
            }
            with pytest.raises(ValidationError) as exc_info:
                CandidatePushRequestModel(**invalid_data)

            error = exc_info.value
            assert "1 validation error for CandidatePushRequestModel" in str(error), (
                f"Failed for {case['desc']}"
            )

    def test_multiple_validation_errors(self):
        """Test handling of multiple validation errors."""
        invalid_data = {
            "folders": [],  # Empty folders list
            "admin": ["invalid-email"],  # Invalid email
            "description": "Test commit",
        }
        with pytest.raises(ValidationError) as exc_info:
            CandidatePushRequestModel(**invalid_data)

        error = exc_info.value
        error_str = str(error)
        assert "2 validation errors for CandidatePushRequestModel" in error_str

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        test_cases = [
            # Minimum valid case
            {
                "data": {
                    "folders": ["folder1"],
                    "admin": ["admin@example.com"],
                    "description": "x",
                },
                "should_pass": True,
                "desc": "minimum valid case",
            },
            # Unicode characters in folders
            {
                "data": {
                    "folders": ["文件夹1", "फ़ोल्डर2"],
                    "admin": ["admin@example.com"],
                    "description": "Test unicode folders",
                },
                "should_pass": True,
                "desc": "unicode folder names",
            },
            # Special characters in email
            {
                "data": {
                    "folders": ["folder1"],
                    "admin": ["user+test@example.com"],
                    "description": "Test special email",
                },
                "should_pass": True,
                "desc": "special characters in email",
            },
        ]

        for case in test_cases:
            if case["should_pass"]:
                try:
                    model = CandidatePushRequestModel(**case["data"])
                    assert model is not None, f"Failed to create model for {case['desc']}"
                except ValidationError as e:
                    pytest.fail(f"Should have passed for {case['desc']}: {str(e)}")
            else:
                with pytest.raises(ValidationError):
                    CandidatePushRequestModel(**case["data"])

    def test_admin_string_all(self):
        """Test validation when 'all' is passed as a string directly."""
        invalid_data = {
            "folders": ["folder1"],
            "admin": "all",  # Invalid string value
            "description": "Test invalid admin string",
        }
        with pytest.raises(ValidationError) as exc_info:
            CandidatePushRequestModel(**invalid_data)

        error = exc_info.value
        assert "Input should be a valid list" in str(error)

    def test_admin_normalized_values(self):
        """Test that 'all' values are properly normalized in mixed lists."""
        # Test mixed case normalization
        valid_data = {
            "folders": ["folder1"],
            "admin": ["ALL", "aLl", "all", "admin@example.com"],
            "description": "Test case normalization",
        }
        model = CandidatePushRequestModel(**valid_data)

        # All 'all' variants should be lowercase, email should remain unchanged
        assert model.admin == ["all", "all", "all", "admin@example.com"]
