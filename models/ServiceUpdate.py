from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from config.models_base import Base

class ServiceUpdate(Base):
    __tablename__ = 'service_updates'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    service_date = Column(DateTime)
    update_description = Column(Text)
    status = Column(String)
