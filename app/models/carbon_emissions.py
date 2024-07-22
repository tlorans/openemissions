from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from app.db.base import Base

class CarbonEmissionsModel(Base):
    __tablename__ = "carbon_emissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    year_published = Column(Integer)
    scope_1 = Column(Float)
    scope_2 = Column(Float)
    scope_3 = Column(Float)

