# tests/scm/models/insights/test_common_models.py

"""Tests for Insights common models."""

import pytest
from pydantic import ValidationError

from scm.models.insights.common import InsightsResponse, InsightsResponseHeader


class TestInsightsResponseHeader:
    """Tests for InsightsResponseHeader model."""

    def test_valid_header(self):
        """Verify InsightsResponseHeader accepts all required fields."""
        header = InsightsResponseHeader(
            createdAt="2026-03-12T00:00:00Z",
            dataCount=10,
            requestId="req-123",
            queryInput={"filter": "test"},
            isResourceDataOverridden=False,
            fieldList=[{"name": "field1", "type": "string"}],
            status={"code": 200, "message": "OK"},
            name="test-query",
        )
        assert header.createdAt == "2026-03-12T00:00:00Z"
        assert header.dataCount == 10
        assert header.requestId == "req-123"
        assert header.cache_operation is None

    def test_with_cache_operation(self):
        """Verify optional cache_operation field is accepted."""
        header = InsightsResponseHeader(
            createdAt="2026-03-12T00:00:00Z",
            dataCount=0,
            requestId="req-456",
            queryInput={},
            isResourceDataOverridden=True,
            fieldList=[],
            status={"code": 200},
            name="cached-query",
            cache_operation="HIT",
        )
        assert header.cache_operation == "HIT"

    def test_missing_required_field(self):
        """Verify validation error when required fields are missing."""
        with pytest.raises(ValidationError):
            InsightsResponseHeader(
                createdAt="2026-03-12T00:00:00Z",
                dataCount=10,
            )


class TestInsightsResponse:
    """Tests for InsightsResponse model."""

    def test_valid_response(self):
        """Verify InsightsResponse with valid header and data."""
        response = InsightsResponse(
            header=InsightsResponseHeader(
                createdAt="2026-03-12T00:00:00Z",
                dataCount=1,
                requestId="req-789",
                queryInput={},
                isResourceDataOverridden=False,
                fieldList=[],
                status={"code": 200},
                name="test",
            ),
            data=[{"id": "1", "value": "test"}],
        )
        assert len(response.data) == 1
        assert response.header.dataCount == 1

    def test_empty_data(self):
        """Verify InsightsResponse accepts empty data list."""
        response = InsightsResponse(
            header=InsightsResponseHeader(
                createdAt="2026-03-12T00:00:00Z",
                dataCount=0,
                requestId="req-000",
                queryInput={},
                isResourceDataOverridden=False,
                fieldList=[],
                status={"code": 200},
                name="empty",
            ),
            data=[],
        )
        assert len(response.data) == 0

    def test_missing_header(self):
        """Verify validation error when header is missing."""
        with pytest.raises(ValidationError):
            InsightsResponse(data=[])

    def test_missing_data(self):
        """Verify validation error when data is missing."""
        with pytest.raises(ValidationError):
            InsightsResponse(
                header=InsightsResponseHeader(
                    createdAt="2026-03-12T00:00:00Z",
                    dataCount=0,
                    requestId="req-111",
                    queryInput={},
                    isResourceDataOverridden=False,
                    fieldList=[],
                    status={"code": 200},
                    name="no-data",
                ),
            )
