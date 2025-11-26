from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Report Schemas (Basic for now)
class ReportBase(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    lat: float
    lon: float

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    report_id: int
    user_id: int
    images: list[str] = []
    upvote_count: int
    status: str
    is_upvoted: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class AssignmentCreate(BaseModel):
    staff_name: str
    staff_phone: str
    note: Optional[str] = None
    expected_resolution_date: Optional[datetime] = None

class ReportStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None
