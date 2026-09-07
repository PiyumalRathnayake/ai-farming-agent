from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class ProtectedResponse(BaseModel):
    message: str
    user_id: int
    email: str