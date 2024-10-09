from pydantic import BaseModel

class ExampleRequest(BaseModel):
    param1: str
    param2: int

class ExampleResponse(BaseModel):
    data: dict
    status: str
