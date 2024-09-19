from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from config.models_base import Base

class CustomerReview(Base):
    __tablename__ = 'customer_reviews'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    review_date = Column(DateTime)
    rating = Column(Integer)
    review_text = Column(Text)
    