from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WidgetType(str, Enum):
    SIGNUP_FORM = "signup_form"
    CONTACT_FORM = "contact_form"
    CTA = "cta"
    POPOVER = "popover"

class WidgetBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Widget title")
    description: Optional[str] = Field(None, description="Widget description")
    widget_type: WidgetType = Field(default=WidgetType.SIGNUP_FORM, description="Type of widget")
    fields: List[str] = Field(default=["name", "email"], description="Form fields")
    button_text: str = Field(default="Submit", min_length=1, max_length=100, description="Button text")
    display_options: Optional[Dict[str, Any]] = Field(default=None, description="Display customization options")
    is_active: bool = Field(default=True, description="Whether widget is active")

    @validator('fields')
    def validate_fields(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Widget must have at least one field')
        return v

class WidgetCreate(WidgetBase):
    pass

class WidgetUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    widget_type: Optional[WidgetType] = None
    fields: Optional[List[str]] = None
    button_text: Optional[str] = Field(None, min_length=1, max_length=100)
    display_options: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class WidgetResponse(WidgetBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    embed_snippet: Optional[str] = None

    class Config:
        from_attributes = True

class WidgetPublicConfig(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    widget_type: str
    fields: List[str]
    button_text: str
    display_options: Optional[Dict[str, Any]] = None
    is_active: bool

    class Config:
        from_attributes = True
