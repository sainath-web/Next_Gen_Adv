from sqlalchemy import Column, String
from config.models_base import Base

class Dealer(Base):
    __tablename__ = 'dealers'

    dealer_id = Column(String, primary_key=True)
    dealer_code = Column(String)
    opportunity_owner = Column(String)
