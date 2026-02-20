"""Test models for QoS Rules."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    QosMoveDestination,
    QosRulebase,
    QosRuleBaseModel,
    QosRuleCreateModel,
    QosRuleMoveModel,
    QosRuleResponseModel,
    QosRuleUpdateModel,
)


class TestQosRuleBaseModel:
    """Test QoS Rule base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = QosRuleBaseModel(name="test-rule", folder="Test Folder")
        assert model.name == "test-rule"
        assert model.folder == "Test Folder"
        assert model.description is None
        assert model.action is None
        assert model.schedule is None
        assert model.dscp_tos is None
        assert model.snippet is None
        assert model.device is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = QosRuleBaseModel(
            name="test-rule",
            folder="Test Folder",
            description="A test QoS rule",
            action={"class": "class1"},
            schedule="business-hours",
            dscp_tos={"codepoints": {"af11": {"codepoint": "001010"}}},
        )
        assert model.name == "test-rule"
        assert model.folder == "Test Folder"
        assert model.description == "A test QoS rule"
        assert model.action == {"class": "class1"}
        assert model.schedule == "business-hours"
        assert model.dscp_tos is not None

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            QosRuleBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = QosRuleBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = QosRuleBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = QosRuleBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        # Valid at max length (64 chars)
        model = QosRuleBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        # Invalid over max length
        with pytest.raises(ValidationError):
            QosRuleBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        # Valid patterns
        model = QosRuleBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        # Invalid pattern (special chars)
        with pytest.raises(ValidationError):
            QosRuleBaseModel(name="test", folder="Folder@#$")


class TestQosRuleCreateModel:
    """Test QoS Rule create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = QosRuleCreateModel(
            name="test-rule",
            folder="Test Folder",
        )
        assert model.name == "test-rule"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = QosRuleCreateModel(
            name="test-rule",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = QosRuleCreateModel(
            name="test-rule",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QosRuleCreateModel(name="test-rule")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QosRuleCreateModel(
                name="test-rule",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on QosRuleCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            QosRuleCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_create_with_action(self):
        """Test create model with action field."""
        model = QosRuleCreateModel(
            name="test-rule",
            folder="Test Folder",
            action={"class": "class1"},
        )
        assert model.action == {"class": "class1"}


class TestQosRuleUpdateModel:
    """Test QoS Rule update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = QosRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rule",
            folder="Test Folder",
            description="Updated description",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-rule"
        assert model.description == "Updated description"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            QosRuleUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            QosRuleUpdateModel(
                name="test",
                folder="Test Folder",
            )


class TestQosRuleResponseModel:
    """Test QoS Rule response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = QosRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-rule",
            folder="Test Folder",
            description="A test rule",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-rule"
        assert model.description == "A test rule"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            QosRuleResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestQosRuleMoveModel:
    """Test QoS Rule move model validation."""

    def test_valid_move_top(self):
        """Test valid move to top."""
        model = QosRuleMoveModel(
            destination=QosMoveDestination.TOP,
            rulebase=QosRulebase.PRE,
        )
        assert model.destination == QosMoveDestination.TOP
        assert model.rulebase == QosRulebase.PRE
        assert model.destination_rule is None

    def test_valid_move_bottom(self):
        """Test valid move to bottom."""
        model = QosRuleMoveModel(
            destination=QosMoveDestination.BOTTOM,
            rulebase=QosRulebase.POST,
        )
        assert model.destination == QosMoveDestination.BOTTOM
        assert model.rulebase == QosRulebase.POST
        assert model.destination_rule is None

    def test_valid_move_before(self):
        """Test valid move before a rule."""
        model = QosRuleMoveModel(
            destination=QosMoveDestination.BEFORE,
            rulebase=QosRulebase.PRE,
            destination_rule="987fcdeb-54ba-3210-9876-fedcba098765",
        )
        assert model.destination == QosMoveDestination.BEFORE
        assert model.destination_rule == UUID("987fcdeb-54ba-3210-9876-fedcba098765")

    def test_valid_move_after(self):
        """Test valid move after a rule."""
        model = QosRuleMoveModel(
            destination=QosMoveDestination.AFTER,
            rulebase=QosRulebase.PRE,
            destination_rule="987fcdeb-54ba-3210-9876-fedcba098765",
        )
        assert model.destination == QosMoveDestination.AFTER
        assert model.destination_rule == UUID("987fcdeb-54ba-3210-9876-fedcba098765")

    def test_before_without_destination_rule_raises_error(self):
        """Test that 'before' without destination_rule raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QosRuleMoveModel(
                destination=QosMoveDestination.BEFORE,
                rulebase=QosRulebase.PRE,
            )
        assert "destination_rule is required when destination is 'before'" in str(exc_info.value)

    def test_after_without_destination_rule_raises_error(self):
        """Test that 'after' without destination_rule raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QosRuleMoveModel(
                destination=QosMoveDestination.AFTER,
                rulebase=QosRulebase.PRE,
            )
        assert "destination_rule is required when destination is 'after'" in str(exc_info.value)

    def test_top_with_destination_rule_raises_error(self):
        """Test that 'top' with destination_rule raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QosRuleMoveModel(
                destination=QosMoveDestination.TOP,
                rulebase=QosRulebase.PRE,
                destination_rule="987fcdeb-54ba-3210-9876-fedcba098765",
            )
        assert "destination_rule should not be provided when destination is 'top'" in str(
            exc_info.value
        )

    def test_bottom_with_destination_rule_raises_error(self):
        """Test that 'bottom' with destination_rule raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QosRuleMoveModel(
                destination=QosMoveDestination.BOTTOM,
                rulebase=QosRulebase.PRE,
                destination_rule="987fcdeb-54ba-3210-9876-fedcba098765",
            )
        assert "destination_rule should not be provided when destination is 'bottom'" in str(
            exc_info.value
        )

    def test_invalid_destination_raises_error(self):
        """Test that invalid destination value raises ValidationError."""
        with pytest.raises(ValidationError):
            QosRuleMoveModel(
                destination="invalid",
                rulebase=QosRulebase.PRE,
            )

    def test_invalid_rulebase_raises_error(self):
        """Test that invalid rulebase value raises ValidationError."""
        with pytest.raises(ValidationError):
            QosRuleMoveModel(
                destination=QosMoveDestination.TOP,
                rulebase="invalid",
            )

    def test_missing_destination_raises_error(self):
        """Test that missing destination raises ValidationError."""
        with pytest.raises(ValidationError):
            QosRuleMoveModel(
                rulebase=QosRulebase.PRE,
            )

    def test_missing_rulebase_raises_error(self):
        """Test that missing rulebase raises ValidationError."""
        with pytest.raises(ValidationError):
            QosRuleMoveModel(
                destination=QosMoveDestination.TOP,
            )

    def test_move_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on QosRuleMoveModel."""
        with pytest.raises(ValidationError) as exc_info:
            QosRuleMoveModel(
                destination=QosMoveDestination.TOP,
                rulebase=QosRulebase.PRE,
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestExtraFieldsQosRule:
    """Tests for extra field handling on QoS Rule models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on QosRuleBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            QosRuleBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on QosRuleUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            QosRuleUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on QosRuleResponseModel."""
        model = QosRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
