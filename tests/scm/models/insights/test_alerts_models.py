"""Test suite for Alert model validators and parsing."""

from scm.models.insights.alerts import Alert


class TestAlertModels:
    """Tests for Alert model validators and parsing."""

    def test_alert_with_json_string_metadata(self):
        """Test Alert model with JSON string in resource_context field."""
        # Create alert with JSON string metadata (using alias)
        alert_data = {
            "alert_id": "test-123",
            "severity": "high",
            "message": "Test alert",
            "state": "Raised",
            "resource_context": '{"key": "value", "number": 123}',
        }

        alert = Alert(**alert_data)

        # Should parse JSON string to dict
        assert isinstance(alert.metadata, dict)
        assert alert.metadata["key"] == "value"
        assert alert.metadata["number"] == 123

    def test_alert_with_invalid_json_metadata_field(self):
        """Test that the validator's JSONDecodeError path is covered."""
        # The test_alert_json_validator_parses_before_type_check test
        # already covers the JSONDecodeError case directly
        # This test documents that invalid JSON strings cannot be used
        # for dict fields even with the validator
        pass

    def test_alert_with_dict_metadata(self):
        """Test Alert model with dict metadata (already parsed)."""
        # Create alert with dict metadata
        alert_data = {
            "alert_id": "test-789",
            "severity": "low",
            "message": "Test alert",
            "state": "Raised",
            "resource_context": {"already": "parsed", "as": "dict"},
        }

        alert = Alert(**alert_data)

        # Should keep dict as-is
        assert isinstance(alert.metadata, dict)
        assert alert.metadata["already"] == "parsed"
        assert alert.metadata["as"] == "dict"

    def test_alert_with_json_string_impacted_resources(self):
        """Test Alert model with JSON string in primary_impacted_objects field."""
        # Create alert with JSON string impacted_resources (using alias)
        alert_data = {
            "alert_id": "test-resource-1",
            "severity": "critical",
            "message": "Test alert",
            "state": "Raised",
            "primary_impacted_objects": '["user1", "device1"]',
        }

        alert = Alert(**alert_data)

        # Should parse JSON string to list
        assert isinstance(alert.impacted_resources, list)
        assert len(alert.impacted_resources) == 2
        assert alert.impacted_resources[0] == "user1"
        assert alert.impacted_resources[1] == "device1"

    def test_alert_with_nested_json_strings(self):
        """Test Alert model with nested JSON strings in metadata."""
        # Create alert with nested JSON
        alert_data = {
            "alert_id": "test-nested",
            "severity": "informational",
            "message": "Test alert",
            "state": "Raised",
            "resource_context": '{"outer": "value", "nested": "{\\"inner\\": \\"value\\"}"}',
        }

        alert = Alert(**alert_data)

        # Should parse outer JSON but keep inner as string
        assert isinstance(alert.metadata, dict)
        assert alert.metadata["outer"] == "value"
        assert alert.metadata["nested"] == '{"inner": "value"}'

    def test_alert_with_none_values(self):
        """Test Alert model with None values for optional fields."""
        # Create minimal alert
        alert_data = {
            "alert_id": "test-minimal",
            "severity": "high",
            "message": "Minimal alert",
            "state": "Raised",
            "resource_context": None,
            "primary_impacted_objects": None,
        }

        alert = Alert(**alert_data)

        # None values should remain None
        assert alert.metadata is None
        assert alert.impacted_resources is None

    def test_alert_field_aliases(self):
        """Test Alert model field aliases work correctly."""
        # Test with field names
        alert1 = Alert(alert_id="test-1", message="Test message", state="Raised")

        assert alert1.id == "test-1"
        assert alert1.name == "Test message"
        assert alert1.status == "Raised"

        # Test with model attribute names
        alert2 = Alert(id="test-2", name="Another message", status="Cleared")

        assert alert2.id == "test-2"
        assert alert2.name == "Another message"
        assert alert2.status == "Cleared"

    def test_alert_json_validator_parses_before_type_check(self):
        """Test the parse_json_string validator directly."""
        # Test the validator method directly to ensure coverage of lines 52-53

        # Test with valid JSON string
        result1 = Alert.parse_json_string('{"key": "value"}')
        assert isinstance(result1, dict)
        assert result1["key"] == "value"

        # Test with invalid JSON string - this covers lines 52-53
        result2 = Alert.parse_json_string("invalid {json}")
        assert result2 == "invalid {json}"

        # Test with non-string input
        input_dict = {"already": "dict"}
        result3 = Alert.parse_json_string(input_dict)
        assert result3 is input_dict

        # Test with None
        result4 = Alert.parse_json_string(None)
        assert result4 is None
