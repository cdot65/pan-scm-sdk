# pan_scm_sdk/models/auth.py

from pydantic import BaseModel, Field, model_validator

class AuthRequest(BaseModel):
    client_id: str
    client_secret: str
    tsg_id: str
    scope: str = Field(default=None)
    token_url: str = Field(
        default="https://auth.apps.paloaltonetworks.com/am/oauth2/access_token"
    )

    @model_validator(mode='before')
    @classmethod
    def construct_scope(cls, values):
        if values.get('scope') is None:
            tsg_id = values.get('tsg_id')
            if tsg_id is None:
                raise ValueError('tsg_id is required to construct scope')
            values['scope'] = f"tsg_id:{tsg_id}"
        return values
