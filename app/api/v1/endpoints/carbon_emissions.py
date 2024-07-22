# app/api/v1/endpoints/carbon_emissions.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import re

from app.db.session import get_db
from app.models.carbon_emissions import CarbonEmissionsModel
from app.schemas.carbon_emissions import CarbonEmissionsModelResponse
from app.crud.carbon_emissions import CarbonEmissionsCRUD

router = APIRouter()

@router.get("/", response_model=List[CarbonEmissionsModelResponse])
def get_all_data(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    emissions = db.query(CarbonEmissionsModel).offset(skip).limit(limit).all()
    return emissions

@router.get("/{company_name}", response_model=List[CarbonEmissionsModelResponse])
def get_data_by_company_name(company_name: str, db: Session = Depends(get_db)):
    pattern = re.compile(company_name, re.IGNORECASE)
    emissions = db.query(CarbonEmissionsModel).all()
    filtered_emissions = [emission for emission in emissions if pattern.search(emission.name)]
    if not filtered_emissions:
        raise HTTPException(status_code=404, detail="Company not found")
    return filtered_emissions
