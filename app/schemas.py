# app/schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from .models import LoanStatus
from datetime import date


# For creating a new user (POST request)
class UserCreate(BaseModel):
    email : EmailStr
    name : str
    password : str


class LoginUserCreate(BaseModel):
    email : EmailStr
    password : str


class CustomerResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    limit : int
    window_seconds : int

    class Config:
        orm_mode = True
        from_attributes = True



class CompanyBase(BaseModel):
    company_name: str
    company_id: str
    address: str
    registration_date: date
    number_of_employees: int
    contact_number: str
    contact_email: str
    company_website: Optional[str]

class UpdateCompanyBase(BaseModel):
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    registration_date: Optional[date] = None
    number_of_employees: Optional[int] = None
    contact_number: Optional[str] = None
    contact_email: Optional[str] = None
    company_website: Optional[str] = None

class AnnualInformationBase(BaseModel):
    annual_turnover: float
    profit: float
    fiscal_year: str
    reported_date: date

class LoanInformationBase(BaseModel):
    loan_amount: float
    taken_on: str
    loan_bank_provider: str
    loan_status: LoanStatus

class CompanyCreate(CompanyBase):
    annual_info: List[AnnualInformationBase] = []
    loans: List[LoanInformationBase] = []

class CreditResponse(BaseModel):
    company_id: str
    company_name: str
    credit_value: float

class CompanyUpdate(CompanyCreate):
    pass


class LoanCreate(BaseModel):
    loan_amount: float
    taken_on: date
    loan_bank_provider: str
    loan_status: LoanStatus

class AnnualTurnoverCreate(BaseModel):
    annual_turnover: float
    profit: float
    fiscal_year: str
    reported_date: date  

class CreditCreate(BaseModel):
    company_id: str
    loan_data: Optional[LoanCreate] = None
    turnover_data: Optional[AnnualTurnoverCreate] = None


class LoanResponse(BaseModel):
    loan_amount: float
    taken_on: date
    loan_bank_provider: str
    loan_status: str

# Turnover schema
class TurnoverResponse(BaseModel):
    annual_turnover: float
    profit: float
    fiscal_year: str
    reported_date: date


class GetCreditResponse(BaseModel):
    company_id: str
    company_name: str
    credit_value: Optional[float] = None
    loans: List[LoanResponse] = []
    turnovers: List[TurnoverResponse] = []