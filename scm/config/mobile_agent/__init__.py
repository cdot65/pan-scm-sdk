"""scm.config.mobile_agent: Mobile Agent service classes."""
# scm/config/mobile_agent/__init__.py

from scm.config.mobile_agent.agent_versions import AgentVersions
from scm.config.mobile_agent.auth_settings import AuthSettings

__all__ = [
    "AgentVersions",
    "AuthSettings",
]
