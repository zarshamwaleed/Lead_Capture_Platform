from pydantic import BaseModel, Field, validator, EmailStr, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class SubmissionStatus(str, Enum):
    NEW = "new"
    READ = "read"
    CONTACTED = "contacted"
    CONVERTED = "converted"
    SPAM = "spam"

class SubmissionCreate(BaseModel):
    widget_id: int = Field(..., description="ID of the widget")
    data: Dict[str, Any] = Field(..., description="Form data")
    honeypot: Optional[str] = Field(None, description="Honeypot field for spam detection")

    @validator('data')
    def validate_form_data(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Form data cannot be empty')
        
        # Check for common spam patterns
        spam_indicators = ['http://', 'https://', 'www.', '.com', '.net', '.org']
        for key, value in v.items():
            if isinstance(value, str):
                value_lower = value.lower()
                # Check for URLs in text fields (spam indicator)
                if len(value) > 100 and any(indicator in value_lower for indicator in spam_indicators):
                    raise ValueError('Spam detected: URLs in form data')
        return v

    @validator('honeypot')
    def validate_honeypot(cls, v):
        # If honeypot field is filled, it's spam
        if v and v.strip():
            raise ValueError('Spam detected: honeypot field filled')
        return v

class SubmissionResponse(BaseModel):
    id: int
    widget_id: int
    owner_id: int
    form_data: Dict[str, Any]
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class SubmissionUpdate(BaseModel):
    status: SubmissionStatus

class SubmissionStats(BaseModel):
    total: int
    new: int
    read: int
    contacted: int
    converted: int
    spam: int
    by_country: Dict[str, int]
    by_widget: Dict[str, int]
    last_7_days: List[Dict[str, Any]]
