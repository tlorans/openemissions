# main.py

from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.v1.endpoints import carbon_emissions

# Create the database and table if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the router for the carbon emissions endpoints
app.include_router(carbon_emissions.router, prefix="/api/v1/carbon-emissions", tags=["carbon-emissions"])

@app.on_event("startup")
def on_startup():
    from app.crud.carbon_emissions import CarbonEmissionsCRUD
    from app.db.session import SessionLocal
    db = SessionLocal()
    data = CarbonEmissionsCRUD.load_json_files(json_folder_path="json_reports")
    CarbonEmissionsCRUD.save_to_db(db, data)

@app.get("/")
def read_root():
    return {"Hello": "World"}
