from pydantic import BaseModel, Field


class LoginPayload(BaseModel):
    username: str
    password: str


class PinLoginPayload(BaseModel):
    pin: str = Field(min_length=4, max_length=8, pattern=r"^\d+$")


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
