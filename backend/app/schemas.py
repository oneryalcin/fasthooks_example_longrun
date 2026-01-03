from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Category Schema
class CategoryEnum(str, Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    HEALTH = "Health"
    SHOPPING = "Shopping"
    OTHER = "Other"

# Authentication Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UpdateProfile(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

# Expense Schemas
class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    category: CategoryEnum
    description: Optional[str] = Field(None, max_length=500)
    date: datetime

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v > 1_000_000:
            raise ValueError("Amount cannot exceed 1,000,000")
        return v

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[CategoryEnum] = None
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None

class ExpenseResponse(ExpenseBase):
    id: int
    owner_id: int
    receipt_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExpenseListResponse(BaseModel):
    items: List[ExpenseResponse]
    total: int
    total_amount: float

# Budget Schemas
class BudgetBase(BaseModel):
    category: CategoryEnum
    monthly_limit: float = Field(..., gt=0)

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    monthly_limit: float = Field(..., gt=0)

class BudgetResponse(BudgetBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Recurring Expense Schemas
class FrequencyEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class RecurringExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    category: CategoryEnum
    description: Optional[str] = Field(None, max_length=500)
    frequency: FrequencyEnum

class RecurringExpenseCreate(RecurringExpenseBase):
    pass

class RecurringExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[CategoryEnum] = None
    description: Optional[str] = Field(None, max_length=500)
    frequency: Optional[FrequencyEnum] = None
    is_active: Optional[bool] = None

class RecurringExpenseResponse(RecurringExpenseBase):
    id: int
    owner_id: int
    is_active: bool
    last_generated: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analytics Schemas
class CategorySummary(BaseModel):
    category: CategoryEnum
    total: float
    percentage: float
    count: int

class MonthlySummary(BaseModel):
    month: str
    total: float
    by_category: List[CategorySummary]

class AnalyticsSummary(BaseModel):
    total_spending: float
    current_month_spending: float
    by_category: List[CategorySummary]
    monthly_trends: List[MonthlySummary]

# Error Response
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
