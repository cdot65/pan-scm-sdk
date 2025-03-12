# tests/examples/updated_conftest.py

"""
Shared fixtures and configuration for tests.
This configuration supports the new test category structure.
"""

# Standard library imports
import os
from unittest.mock import MagicMock
import pytest

# Local SDK imports
from scm.models.auth import AuthRequestModel


# -------------------- Environment Setup --------------------

@pytest.fixture
def load_env():
    """
    Load testing environment variables.
    This is used by all test categories.
    """
    # Set environment variables for testing
    os.environ.setdefault("CLIENT_ID", "test_client_id")
    os.environ.setdefault("CLIENT_SECRET", "test_client_secret")
    os.environ.setdefault("TOKEN_URL", "https://api.test.com/oauth2/token")
    os.environ.setdefault("SCOPE", "test_scope")
    os.environ.setdefault("TSG_ID", "test_tsg_id")
    yield
    # Clean up is not needed as these are just testing values


@pytest.fixture
def mock_scm():
    """
    Create a mock SCM client.
    This is used by most test categories.
    """
    scm = MagicMock()
    # Default configuration
    scm.base_url = "https://api.test.com"
    return scm


# -------------------- Category-Specific Fixtures --------------------

# Unit Test Fixtures

@pytest.fixture
def unit_test_config():
    """Configuration for unit tests."""
    return {
        "mock_external_deps": True,
        "validate_only": True,
    }


# Integration Test Fixtures

@pytest.fixture
def integration_test_config():
    """Configuration for integration tests."""
    return {
        "mock_external_deps": False,
        "validate_responses": True,
    }


@pytest.fixture
def mock_api_responses():
    """Common API response mocks for integration tests."""
    return {
        "success": {"status": "success"},
        "error": {"status": "error", "message": "Test error message"},
        "not_found": {"status": "error", "message": "Resource not found"},
    }


# Functional Test Fixtures

@pytest.fixture
def functional_test_workflow():
    """
    Setup for functional tests.
    Provides a workflow context that can be shared across steps.
    """
    return {
        "created_objects": [],
        "test_data": {},
        "cleanup_required": True,
    }


# Mock Test Fixtures

@pytest.fixture
def mock_auth_request():
    """Create a mock auth request for mock tests."""
    return AuthRequestModel(
        client_id="mock_client_id",
        client_secret="mock_client_secret",
        token_url="https://mock.api.test.com/oauth2/token",
        scope="mock_scope",
        tsg_id="mock_tsg_id",
    )


@pytest.fixture
def mock_token_response():
    """Create a mock token response for mock tests."""
    return {
        "access_token": "mock_access_token",
        "token_type": "Bearer",
        "expires_in": 3600,
    }


# Parametrized Test Fixtures

@pytest.fixture(params=["ip_netmask", "ip_range", "ip_wildcard", "fqdn"])
def address_type(request):
    """Parametrized fixture for address types."""
    return request.param


@pytest.fixture
def address_value(address_type):
    """Generate test values based on address_type."""
    values = {
        "ip_netmask": "192.168.1.0/24",
        "ip_range": "192.168.1.1-192.168.1.10",
        "ip_wildcard": "192.168.1.0/0.0.0.255",
        "fqdn": "test.example.com",
    }
    return values[address_type]


# Configuration Test Fixtures

@pytest.fixture
def environment_config():
    """Setup environment configurations for testing."""
    original_env = os.environ.copy()
    
    # Set test configuration
    os.environ["SCM_MAX_LIMIT"] = "3000"
    os.environ["SCM_TIMEOUT"] = "60"
    
    yield
    
    # Restore original environment
    for key in ["SCM_MAX_LIMIT", "SCM_TIMEOUT"]:
        if key in original_env:
            os.environ[key] = original_env[key]
        else:
            os.environ.pop(key, None)


# Documentation Test Fixtures

@pytest.fixture
def doc_example_context():
    """
    Setup context for documentation examples.
    This provides a clean environment for testing documentation examples.
    """
    return {
        "folder": "Examples",
        "test_ip": "10.0.0.1/32",
        "test_name": "doc-example-object",
    }