
# User Registration Schema
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegistrationSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = Field(..., description="Role of the user: farmer, supplier, expert")
    national_id: Optional[str] = Field(None, description="Tanzania National ID")
    driving_license: Optional[str] = Field(None, description="Tanzania Driving License")
    location: Optional[str] = None  # Optional field
    contact_number: Optional[str] = None  # Optional field



class LoginSchema(BaseModel):
    username: str
    password: str


# Update User Profile Schema
class UserProfileUpdateSchema(BaseModel):
    location: Optional[str] = None
    contact_number: Optional[str] = None


# Define a schema for the frontend app registration
class FrontendAppSchema(BaseModel):
    name: str



