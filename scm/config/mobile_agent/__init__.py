"""scm.config.mobile_agent: Mobile Agent service classes."""
# scm/config/mobile_agent/__init__.py

from scm.config.mobile_agent.agent_profiles import AgentProfiles
from scm.config.mobile_agent.agent_versions import AgentVersions
from scm.config.mobile_agent.auth_settings import AuthSettings
from scm.config.mobile_agent.forwarding_profile_destinations import (
    ForwardingProfileDestinations,
)
from scm.config.mobile_agent.forwarding_profile_regional_and_custom_proxies import (
    ForwardingProfileRegionalAndCustomProxies,
)
from scm.config.mobile_agent.forwarding_profile_source_applications import (
    ForwardingProfileSourceApplications,
)
from scm.config.mobile_agent.forwarding_profile_user_locations import (
    ForwardingProfileUserLocations,
)
from scm.config.mobile_agent.forwarding_profiles import ForwardingProfiles
from scm.config.mobile_agent.global_settings import GlobalSettings
from scm.config.mobile_agent.infrastructure_settings import InfrastructureSettings
from scm.config.mobile_agent.tunnel_profiles import TunnelProfiles

__all__ = [
    "AgentProfiles",
    "AgentVersions",
    "AuthSettings",
    "ForwardingProfileDestinations",
    "ForwardingProfileRegionalAndCustomProxies",
    "ForwardingProfileSourceApplications",
    "ForwardingProfileUserLocations",
    "ForwardingProfiles",
    "GlobalSettings",
    "InfrastructureSettings",
    "TunnelProfiles",
]
