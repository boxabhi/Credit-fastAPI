from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Interval
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from enum import Enum as PyEnum
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, Enum, Table, UniqueConstraint

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)




    

class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    

    

class LoanStatus(PyEnum):
    PAID = "PAID"
    DUE = "DUE"
    INITIATED = "INITIATED"

# Company Information Table
class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    company_id = Column(String, unique=True, nullable=False)  # CIN for Indian companies
    address = Column(String, nullable=False)
    registration_date = Column(String, nullable=False)
    number_of_employees = Column(Integer, nullable=False)
    contact_number = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    company_website = Column(String, nullable=True)
    
    # Relationship to annual information
    annual_info = relationship("AnnualInformation", back_populates="company", cascade="all, delete-orphan")
    # Relationship to loans
    loans = relationship("LoanInformation", back_populates="company", cascade="all, delete-orphan")

# Annual Information Table
class AnnualInformation(Base):
    __tablename__ = "annual_information"
    
    id = Column(Integer, primary_key=True, index=True)
    annual_turnover = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    fiscal_year = Column(String, nullable=False)
    reported_date = Column(Date, nullable=False)
    
    # Foreign Key for Company
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="annual_info")

# Loan Information Table
class LoanInformation(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_amount = Column(Float, nullable=False)
    taken_on = Column(Date, nullable=False)
    loan_bank_provider = Column(String, nullable=False)
    loan_status = Column(Enum(LoanStatus), nullable=False)
    
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="loans")

