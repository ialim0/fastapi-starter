from pydantic import BaseModel

class OAuthURLResponse(BaseModel):
    url: str
