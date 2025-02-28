from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ConfirmUserRequest(BaseModel):
    email: EmailStr
    confirmation_code: str
