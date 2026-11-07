from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Validate data submitted when registering a user."""

    name:str = Field(min_length=1, max_length=100)
    email: EmailStr 
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Define the user information returned by the API."""

    id:int
    name:str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

model_config = ConfigDict(from_attributes=True)


