"""Tests for job operation models."""

from datetime import datetime, timezone

from scm.models.operations.jobs import JobListItem, JobStatusData


class TestJobStatusData:
    """Tests for JobStatusData model."""

    def test_serialize_datetime_with_value(self):
        """Test datetime serialization with valid datetime."""
        # Create a datetime object
        test_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Create a JobStatusData instance with test datetime
        job_data = JobStatusData(
            details="test details",
            id="123",
            insert_ts=test_dt,
            job_result="2",
            job_status="2",
            job_type="53",
            last_update=test_dt,
            owner="test",
            percent="100",
            result_i="2",
            result_str="OK",
            start_ts=test_dt,
            status_i="2",
            status_str="FIN",
            type_i="53",
            type_str="CommitAndPush",
            uname="test@example.com",
            end_ts=test_dt,
        )

        # Convert to dict to trigger serialization
        serialized = job_data.model_dump()

        # Verify all datetime fields are serialized correctly
        expected_iso = "2024-01-01T12:00:00+00:00"
        assert serialized["end_ts"] == expected_iso
        assert serialized["insert_ts"] == expected_iso
        assert serialized["last_update"] == expected_iso
        assert serialized["start_ts"] == expected_iso

    def test_serialize_datetime_with_none(self):
        """Test datetime serialization with None value."""
        # Create a JobStatusData instance with None for optional datetime
        job_data = JobStatusData(
            details="test details",
            id="123",
            insert_ts=datetime.now(),
            job_result="2",
            job_status="2",
            job_type="53",
            last_update=datetime.now(),
            owner="test",
            percent="100",
            result_i="2",
            result_str="OK",
            start_ts=datetime.now(),
            status_i="2",
            status_str="FIN",
            type_i="53",
            type_str="CommitAndPush",
            uname="test@example.com",
            end_ts=None,  # Optional field set to None
        )

        # Convert to dict to trigger serialization
        serialized = job_data.model_dump()

        # Verify None is preserved
        assert serialized["end_ts"] is None


class TestJobListItem:
    """Tests for JobListItem model."""

    def test_validate_timestamp_with_empty_string(self):
        """Test timestamp validation with empty string."""
        # Create JobListItem with empty string timestamps
        job_item = JobListItem(
            id="123",
            job_result="2",
            job_status="2",
            job_type="53",
            parent_id="0",
            result_str="OK",
            start_ts="",  # Empty string
            status_str="FIN",
            type_str="CommitAndPush",
            uname="test@example.com",
            end_ts="",  # Empty string
        )

        # Verify empty strings are converted to None
        assert job_item.end_ts is None
        assert job_item.start_ts is None

    def test_validate_timestamp_with_value(self):
        """Test timestamp validation with valid timestamp string."""
        timestamp = "2024-01-01T12:00:00Z"
        job_item = JobListItem(
            id="123",
            job_result="2",
            job_status="2",
            job_type="53",
            parent_id="0",
            result_str="OK",
            start_ts=timestamp,
            status_str="FIN",
            type_str="CommitAndPush",
            uname="test@example.com",
            end_ts=timestamp,
        )

        # Verify valid timestamps are preserved
        assert job_item.end_ts == timestamp
        assert job_item.start_ts == timestamp

    def test_validate_timestamp_with_none(self):
        """Test timestamp validation with None value."""
        job_item = JobListItem(
            id="123",
            job_result="2",
            job_status="2",
            job_type="53",
            parent_id="0",
            result_str="OK",
            start_ts="2024-01-01T12:00:00Z",  # Required field
            status_str="FIN",
            type_str="CommitAndPush",
            uname="test@example.com",
            end_ts=None,  # Optional field
        )

        # Verify None is preserved for optional field
        assert job_item.end_ts is None

    def test_validate_timestamp_direct_validation(self):
        """Test timestamp validator method directly."""
        # Test with empty string
        assert JobListItem.validate_timestamp("") is None

        # Test with valid timestamp
        timestamp = "2024-01-01T12:00:00Z"
        assert JobListItem.validate_timestamp(timestamp) == timestamp

        # Test with None
        assert JobListItem.validate_timestamp(None) is None
