from pydantic import BaseModel, Field

class AuthRequest(BaseModel):
    client_id: str
    client_secret: str
    tsg_id: str
    token_url: str = Field(
        default="https://auth.apps.paloaltonetworks.com/am/oauth2/access_token"
    )
