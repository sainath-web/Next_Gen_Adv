from sqlalchemy import Column, String, Float, Integer, DateTime
from config.models_base import Base

class Opportunity(Base):
    __tablename__ = 'opportunities'

    opportunity_id = Column(String, primary_key=True)
    opportunity_name = Column(String)
    account_name = Column(String)
    close_date = Column(DateTime)
    amount = Column(Float)
    description = Column(String)
    dealer_id = Column(String)
    dealer_code = Column(String)
    dealer_name_or_opportunity_owner = Column(String)
    stage = Column(String)
    probability = Column(Integer)
    next_step = Column(String)
    amount_usd = Column(Float) 
    amount_aud = Column(Float)  
    amount_cad = Column(Float)

    def to_dict(self):
        return {
            "opportunity_id": self.opportunity_id,
            "opportunity_name": self.opportunity_name,
            "account_name": self.account_name,
            "close_date": str(self.close_date),
            "amount": self.amount,
            "description": self.description,
            "dealer_id": self.dealer_id,
            "dealer_code": self.dealer_code,
            "dealer_name_or_opportunity_owner": self.dealer_name_or_opportunity_owner,
            "stage": self.stage,
            "probability": self.probability,
            "next_step": self.next_step
        }
