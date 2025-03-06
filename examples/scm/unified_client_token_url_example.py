"""
Example showing how to initialize the ScmClient with a custom token URL.
"""

from scm.client import ScmClient

# Create client with custom token URL
client = ScmClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tsg-id",
    token_url="https://custom.auth.server.example.com/oauth2/token",
    log_level="INFO"
)

# The client is now configured to use the custom token URL for authentication
# You can use all standard client methods