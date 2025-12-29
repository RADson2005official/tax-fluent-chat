"""Re-export all schemas from the schemas package for backward compatibility."""
from app.schemas import *
from app.schemas import (
    UserBase, UserCreate, UserUpdate, User,
    Token, TokenData,
    UserProfileBase, UserProfileUpdate, UserProfile,
    TaxFormBase, TaxFormCreate, TaxFormUpdate, TaxForm,
    DependentBase, DependentCreate, DependentUpdate, Dependent,
    W2FormBase, W2FormCreate, W2FormUpdate, W2Form,
    Form1099Base, Form1099Create, Form1099Update, Form1099,
    UserInputDataCreate, UserInputData,
    ComplianceCheckCreate, ComplianceCheck,
    ChatMessage, ChatResponse,
    HealthCheck
)
