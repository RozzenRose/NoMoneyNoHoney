from app.database.engine import Base
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, Float, Date, func
from sqlalchemy.orm import relationship
from datetime import date


class Income(Base):
    __tablename__ = 'incomes'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    description = Column(String)
    quantity = Column(Float)
    is_rub = Column(Boolean)
    is_euro = Column(Boolean)
    is_rsd = Column(Boolean)
    created_at = Column(Date, server_default=func.current_date())

    user = relationship('User', back_populates='incomes')