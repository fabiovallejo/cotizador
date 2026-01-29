from pydantic import BaseModel, EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    """Schema para la solicitud de login."""
    email: EmailStr
    password: str

