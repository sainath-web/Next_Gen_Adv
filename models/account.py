from sqlalchemy import Column, String
from config.models_base import Base

class Account(Base):
    __tablename__ = 'accounts'

    account_id = Column(String, primary_key=True)
    account_name = Column(String, unique=True)
