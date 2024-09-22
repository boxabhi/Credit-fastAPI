
from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..utility.utils import hash_password, create_access_token, verify_password
from fastapi import FastAPI, Depends, HTTPException, status
from ..utility.auth import get_current_user
from fastapi.responses import JSONResponse
from typing import List
from fastapi.encoders import jsonable_encoder


app = FastAPI()
router = APIRouter()


@router.post("/companies/", response_model=schemas.CompanyBase)
def create_company(company: schemas.CompanyCreate, current_user: 
                   str = Depends(get_current_user), db: Session = Depends(get_db)):

    company = db.query(models.Company).filter(models.Company.company_id 
                                              == company.company_id).first()
    if company:
        return JSONResponse(content=jsonable_encoder({
        "status":False,
        "data" : {},
        "message" : "company with this is already exits"
    }))

       
    db_company = models.Company(
        company_name=company.company_name,
        company_id=company.company_id,
        address=company.address,
        registration_date=company.registration_date,
        number_of_employees=company.number_of_employees,
        contact_number=company.contact_number,
        contact_email=company.contact_email,
        company_website=company.company_website,
    )

    for annual in company.annual_info:
        db_annual_info = models.AnnualInformation(
            annual_turnover=annual.annual_turnover,
            profit=annual.profit,
            fiscal_year=annual.fiscal_year,
            reported_date=annual.reported_date,
        )
        db_company.annual_info.append(db_annual_info)

    for loan in company.loans:
        db_loan_info = models.LoanInformation(
            loan_amount=loan.loan_amount,
            taken_on=loan.taken_on,
            loan_bank_provider=loan.loan_bank_provider,
            loan_status=loan.loan_status,
        )
        db_company.loans.append(db_loan_info)

    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : db_company,
        "message" : "company fetched"
    }))



@router.get("/credits/", response_model=List[schemas.GetCreditResponse])
def get_all_credits( current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    companies = db.query(models.Company).all()
    credits = []
    
    for company in companies:
        # Fetch loans for the company
        loans = db.query(models.LoanInformation).filter(models.LoanInformation.company_id == company.id).all()
        print(f"Loans for company {company.company_name}: {loans}")
        loan_data = [schemas.LoanResponse(
            loan_amount=loan.loan_amount,
            taken_on=loan.taken_on,
            loan_bank_provider=loan.loan_bank_provider,
            loan_status=loan.loan_status.value  # Enum to string
        ) for loan in loans]
        
        # Fetch turnover information for the company
        turnovers = db.query(models.AnnualInformation).filter(models.AnnualInformation.company_id == company.id).all()
        turnover_data = [schemas.TurnoverResponse(
            annual_turnover=turnover.annual_turnover,
            profit=turnover.profit,
            fiscal_year=turnover.fiscal_year,
            reported_date=turnover.reported_date
        ) for turnover in turnovers]

        # Calculate the credit value (this logic is simplified, adjust it as per your needs)
        credit_value = compute_credit_for_company(company, db)
        
        # Append company details along with loans and turnovers
        credits.append(schemas.GetCreditResponse(
            company_id=company.company_id,
            company_name=company.company_name,
            credit_value=credit_value,
            loans=loan_data,
            turnovers=turnover_data
        ))
        print(credits)

    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : credits,
        "message" : "credits fetched"
    }))

    return credits

@router.get("/credits/{company_id}/", response_model=schemas.CreditResponse)
def get_credit_by_company_id(company_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    credit_value = compute_credit_for_company(company, db)
    

    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : schemas.CreditResponse(
        company_id=company.company_id,
        company_name=company.company_name,
        credit_value=credit_value
    ),
        "message" : "credits fetched"
    }))

@router.post("/credits/", response_model=schemas.CreditCreate)
def add_credit_for_company(credit_data: schemas.CreditCreate,current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):

    company = db.query(models.Company).filter(models.Company.company_id == 
                                              credit_data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if credit_data.loan_data:
        new_loan = models.LoanInformation(
            company_id=company.id,
            loan_amount=credit_data.loan_data.loan_amount,
            taken_on=credit_data.loan_data.taken_on,
            loan_bank_provider=credit_data.loan_data.loan_bank_provider,
            loan_status=credit_data.loan_data.loan_status
        )
        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)
        credit_value = None 

        return {
            "message": "Loan information saved successfully",
            "company_id": company.company_id,
            "company_name": company.company_name,
            "credit_value": credit_value,
            "loan_data": {
                "loan_amount": new_loan.loan_amount,
                "taken_on": new_loan.taken_on,
                "loan_bank_provider": new_loan.loan_bank_provider,
                "loan_status": new_loan.loan_status.value,  
                "company_id": company.company_id
            }
        }


    if credit_data.turnover_data:
        new_annual = models.AnnualInformation(
            company_id=company.id,
            annual_turnover=credit_data.turnover_data.annual_turnover,
            profit=credit_data.turnover_data.profit,
            fiscal_year=credit_data.turnover_data.fiscal_year,
            reported_date=credit_data.turnover_data.reported_date
        )
        db.add(new_annual)
        db.commit()
        db.refresh(new_annual)
        return {
            "message": "Annual turnover information saved successfully",
            "company_id": company.company_id,
            "company_name": company.company_name,
            "credit_value": None,  # Or implement logic for credit calculation
            "turnover_data": {
                "annual_turnover": new_annual.annual_turnover,
                "profit": new_annual.profit,
                "fiscal_year": new_annual.fiscal_year,
                "reported_date": new_annual.reported_date
            }
        }

    raise HTTPException(status_code=400, detail="Either loan_data or turnover_data must be provided")



@router.patch("/company/{company_id}")
def update_company(company_id: str, company_data: schemas.UpdateCompanyBase,
                current_user: str = Depends(get_current_user),     db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.company_id
                                               == company_id).first()

    if company is None:
        return {"message" :"company not found"}


    if company_data.company_name is not None:
        company.company_name = company_data.company_name
    if company_data.address is not None:
        company.address = company_data.address
    if company_data.registration_date is not None:
        company.registration_date = company_data.registration_date
    if company_data.number_of_employees is not None:
        company.number_of_employees = company_data.number_of_employees
    if company_data.contact_number is not None:
        company.contact_number = company_data.contact_number
    if company_data.contact_email is not None:
        company.contact_email = company_data.contact_email
    if company_data.company_website is not None:
        company.company_website = company_data.company_website
    

    db.commit()

    db.refresh(company)
       
    
    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : schemas.CompanyBase(
        company_name = company.company_name,
        company_id = company.company_id,
        address = company.address,
        registration_date = company.registration_date,
        number_of_employees = company.number_of_employees,
        contact_number = company.contact_number,
        contact_email = company.contact_email,
        company_website = company.company_website,
    ),
        "message" : "company updated"
    }))
    
    return 



@router.post("/company", response_model=schemas.CompanyCreate)
def create_company(company: schemas.CompanyCreate,current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    db_company = models.Company(
        company_name=company.company_name,
        company_id=company.company_id,
        address=company.address,
        registration_date=company.registration_date,
        number_of_employees=company.number_of_employees,
        contact_number=company.contact_number,
        contact_email=company.contact_email,
        company_website=company.company_website,
    )

    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : db_company,
        "message" : "company created"
    }))






# Utility function to compute credit for a company
def compute_credit_for_company(company: models.Company, db: Session):
    # Get the last two years of annual turnover
    annuals = db.query(models.AnnualInformation).filter(
        models.AnnualInformation.company_id == company.id
    ).order_by(models.AnnualInformation.fiscal_year.desc()).limit(2).all()

    if len(annuals) == 0:
        return 0.0 


    annual_turnover_sum = sum(annual.annual_turnover for annual in annuals)


    loans_due = db.query(models.LoanInformation).filter(
        models.LoanInformation.company_id == company.id,
        models.LoanInformation.loan_status == models.LoanStatus.DUE
    ).all()
    total_due_loans = sum(loan.loan_amount for loan in loans_due)


    credit_value = annual_turnover_sum - total_due_loans
    return credit_value