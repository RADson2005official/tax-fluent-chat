"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


# ============================================================================
# Authentication Schemas
# ============================================================================

class Token(BaseModel):
    """OAuth2 token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[str] = None
    user_id: Optional[int] = None


# ============================================================================
# User Profile Schemas
# ============================================================================

class UserProfileBase(BaseModel):
    """Base user profile schema."""
    preferred_mode: str = "novice"
    theme: str = "light"
    language: str = "en"
    notifications_enabled: bool = True


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    preferred_mode: Optional[str] = None
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None


class UserProfile(UserProfileBase):
    """Schema for user profile response."""
    id: int
    user_id: int
    interaction_count: int
    help_requests: int
    interaction_speed_avg_ms: int
    error_rate_percent: float
    cognitive_load_score: float
    
    class Config:
        from_attributes = True


# ============================================================================
# Tax Form Schemas
# ============================================================================

class TaxFormBase(BaseModel):
    """Base tax form schema."""
    year: int = Field(..., ge=2000, le=2030)
    filing_status: Optional[str] = None


class TaxFormCreate(TaxFormBase):
    """Schema for creating a new tax form."""
    pass


class TaxFormUpdate(BaseModel):
    """Schema for updating tax form."""
    filing_status: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class TaxForm(TaxFormBase):
    """Schema for tax form response."""
    id: int
    owner_id: int
    status: str
    form_data: Dict[str, Any]
    total_income: float
    adjusted_gross_income: float
    taxable_income: float
    total_tax: float
    total_payments: float
    refund_or_amount_owed: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Dependent Schemas
# ============================================================================

class DependentBase(BaseModel):
    """Base dependent schema."""
    full_name: str
    date_of_birth: datetime
    relationship: str


class DependentCreate(DependentBase):
    """Schema for creating a dependent."""
    ssn: str  # Will be encrypted before storage
    months_lived_with_taxpayer: int = 12


class Dependent(DependentBase):
    """Schema for dependent response (SSN excluded for security)."""
    id: int
    form_id: int
    months_lived_with_taxpayer: int
    is_qualifying_child: bool
    is_qualifying_relative: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# W-2 Form Schemas
# ============================================================================

class W2FormBase(BaseModel):
    """Base W-2 schema."""
    employer_name: str
    employer_ein: Optional[str] = None


class W2FormCreate(W2FormBase):
    """Schema for creating a W-2."""
    box_1_wages: float = 0.0
    box_2_federal_tax_withheld: float = 0.0
    box_3_social_security_wages: float = 0.0
    box_4_social_security_tax_withheld: float = 0.0
    box_5_medicare_wages: float = 0.0
    box_6_medicare_tax_withheld: float = 0.0
    box_12_codes: Optional[List[Dict[str, Any]]] = []
    box_13_checkboxes: Optional[Dict[str, bool]] = {}


class W2Form(W2FormBase):
    """Schema for W-2 response."""
    id: int
    form_id: int
    box_1_wages: float
    box_2_federal_tax_withheld: float
    box_3_social_security_wages: float
    box_4_social_security_tax_withheld: float
    box_5_medicare_wages: float
    box_6_medicare_tax_withheld: float
    
    class Config:
        from_attributes = True


# ============================================================================
# 1099 Form Schemas
# ============================================================================

class Form1099Base(BaseModel):
    """Base 1099 schema."""
    form_type: str  # 1099-INT, 1099-DIV, 1099-MISC, etc.
    payer_name: str
    payer_ein: Optional[str] = None


class Form1099Create(Form1099Base):
    """Schema for creating a 1099."""
    form_data: Dict[str, Any] = {}
    total_amount: float = 0.0


class Form1099(Form1099Base):
    """Schema for 1099 response."""
    id: int
    form_id: int
    form_data: Dict[str, Any]
    total_amount: float
    
    class Config:
        from_attributes = True


# ============================================================================
# User Input Schemas
# ============================================================================

class UserInputDataCreate(BaseModel):
    """Schema for creating user input."""
    field_key: str
    field_value: str
    field_type: str = "string"
    source: str = "manual"
    confidence_score: Optional[float] = None


class UserInputData(UserInputDataCreate):
    """Schema for user input response."""
    id: int
    form_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Compliance Check Schemas
# ============================================================================

class ComplianceCheckCreate(BaseModel):
    """Schema for creating compliance check."""
    check_type: str
    check_name: str
    status: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = {}


class ComplianceCheck(ComplianceCheckCreate):
    """Schema for compliance check response."""
    id: int
    form_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Chat/Agent Schemas
# ============================================================================

class ChatMessage(BaseModel):
    """Schema for chat message."""
    message: str
    conversation_history: List[Dict[str, str]] = []
    context: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    """Schema for chat response."""
    response: str
    conversation_history: List[Dict[str, str]]
    metadata: Optional[Dict[str, Any]] = {}


# ============================================================================
# Health Check Schema
# ============================================================================

class HealthCheck(BaseModel):
    """Schema for health check response."""
    status: str
    database: bool
    timestamp: datetime
    version: str = "1.0.0"
