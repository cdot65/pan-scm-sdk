"""Live API tests for validating Pydantic models against real SCM responses.

These tests are excluded from CI (marked with @pytest.mark.api) and only run locally
when SCM credentials are configured in .env file.

Run with: pytest -m api
"""
