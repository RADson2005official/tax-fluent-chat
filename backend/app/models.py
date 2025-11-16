"""SQLAlchemy database models for the Tax Filing System."""
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tax_forms = relationship("TaxForm", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class UserProfile(Base):
    """User profile with adaptive UI preferences."""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Adaptive UI Settings
    preferred_mode = Column(String, default="novice")  # novice, intermediate, expert
    interaction_count = Column(Integer, default=0)
    help_requests = Column(Integer, default=0)
    interaction_speed_avg_ms = Column(Integer, default=0)
    error_rate_percent = Column(Float, default=0.0)
    cognitive_load_score = Column(Float, default=0.0)
    
    # User Preferences
    theme = Column(String, default="light")  # light, dark, auto
    language = Column(String, default="en")
    notifications_enabled = Column(Boolean, default=True)
    
    # Tax-specific preferences
    filing_status_history = Column(JSON, default=list)  # List of past filing statuses
    preferred_tax_year = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, mode={self.preferred_mode})>"


class TaxForm(Base):
    """Main tax form/return model."""
    __tablename__ = "tax_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year = Column(Integer, index=True, nullable=False)
    filing_status = Column(String)  # single, married_filing_jointly, married_filing_separately, head_of_household
    status = Column(String, default="in_progress")  # in_progress, completed, filed, accepted, rejected
    
    # Form data stored as JSON for flexibility
    form_data = Column(JSON, default=dict)
    
    # Calculated fields
    total_income = Column(Float, default=0.0)
    adjusted_gross_income = Column(Float, default=0.0)
    taxable_income = Column(Float, default=0.0)
    total_tax = Column(Float, default=0.0)
    total_payments = Column(Float, default=0.0)
    refund_or_amount_owed = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    filed_at = Column(DateTime(timezone=True))
    
    # Relationships
    owner = relationship("User", back_populates="tax_forms")
    dependents = relationship("Dependent", back_populates="tax_form", cascade="all, delete-orphan")
    w2_forms = relationship("W2Form", back_populates="tax_form", cascade="all, delete-orphan")
    form_1099s = relationship("Form1099", back_populates="tax_form", cascade="all, delete-orphan")
    user_inputs = relationship("UserInputData", back_populates="tax_form", cascade="all, delete-orphan")
    compliance_checks = relationship("ComplianceCheck", back_populates="tax_form", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TaxForm(id={self.id}, year={self.year}, status={self.status})>"


class Dependent(Base):
    """Dependent information model."""
    __tablename__ = "dependents"
    
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("tax_forms.id"), nullable=False)
    
    full_name = Column(String, nullable=False)
    ssn_encrypted = Column(String, nullable=False)  # Encrypted SSN
    date_of_birth = Column(DateTime)
    relationship_type = Column(String)  # child, parent, other - renamed to avoid conflict with SQLAlchemy relationship
    months_lived_with_taxpayer = Column(Integer)
    
    # Qualifying criteria
    is_qualifying_child = Column(Boolean, default=False)
    is_qualifying_relative = Column(Boolean, default=False)
    claimed_by_another = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tax_form = relationship("TaxForm", back_populates="dependents")
    
    def __repr__(self):
        return f"<Dependent(id={self.id}, name={self.full_name})>"


class W2Form(Base):
    """W-2 form data model."""
    __tablename__ = "w2_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("tax_forms.id"), nullable=False)
    
    employer_name = Column(String, nullable=False)
    employer_ein = Column(String)
    
    # W-2 boxes
    box_1_wages = Column(Float, default=0.0)
    box_2_federal_tax_withheld = Column(Float, default=0.0)
    box_3_social_security_wages = Column(Float, default=0.0)
    box_4_social_security_tax_withheld = Column(Float, default=0.0)
    box_5_medicare_wages = Column(Float, default=0.0)
    box_6_medicare_tax_withheld = Column(Float, default=0.0)
    box_12_codes = Column(JSON, default=list)  # List of code-amount pairs
    box_13_checkboxes = Column(JSON, default=dict)  # Retirement plan, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tax_form = relationship("TaxForm", back_populates="w2_forms")
    
    def __repr__(self):
        return f"<W2Form(id={self.id}, employer={self.employer_name})>"


class Form1099(Base):
    """1099 form data model (various types)."""
    __tablename__ = "form_1099s"
    
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("tax_forms.id"), nullable=False)
    
    form_type = Column(String, nullable=False)  # 1099-INT, 1099-DIV, 1099-MISC, etc.
    payer_name = Column(String, nullable=False)
    payer_ein = Column(String)
    
    # Common fields (stored as JSON for flexibility across different 1099 types)
    form_data = Column(JSON, default=dict)
    total_amount = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tax_form = relationship("TaxForm", back_populates="form_1099s")
    
    def __repr__(self):
        return f"<Form1099(id={self.id}, type={self.form_type}, payer={self.payer_name})>"


class UserInputData(Base):
    """Track all user input for audit and analysis."""
    __tablename__ = "user_input_data"
    
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("tax_forms.id"), nullable=False)
    
    field_key = Column(String, nullable=False)  # e.g., "charitable_donations", "mortgage_interest"
    field_value = Column(Text)  # Store as text, convert as needed
    field_type = Column(String)  # string, number, date, boolean, etc.
    
    # Metadata
    source = Column(String, default="manual")  # manual, ocr, ai_extracted, imported
    confidence_score = Column(Float)  # For AI-extracted data
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tax_form = relationship("TaxForm", back_populates="user_inputs")
    
    def __repr__(self):
        return f"<UserInputData(id={self.id}, field={self.field_key})>"


class ComplianceCheck(Base):
    """Store compliance check results."""
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("tax_forms.id"), nullable=False)
    
    check_type = Column(String, nullable=False)  # irs_validation, cross_reference, math_check
    check_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # passed, failed, warning
    
    message = Column(Text)
    details = Column(JSON, default=dict)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tax_form = relationship("TaxForm", back_populates="compliance_checks")
    
    def __repr__(self):
        return f"<ComplianceCheck(id={self.id}, type={self.check_type}, status={self.status})>"


class AuditLog(Base):
    """Comprehensive audit trail for compliance and security."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    action = Column(String, nullable=False)  # login, logout, form_created, form_updated, etc.
    resource_type = Column(String)  # user, tax_form, w2, etc.
    resource_id = Column(Integer)
    
    details = Column(JSON, default=dict)
    ip_address = Column(String)
    user_agent = Column(String)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, timestamp={self.timestamp})>"
