from app.database.engine import Base
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, Float, Date, func
from sqlalchemy.orm import relationship


class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    is_rub = Column(Boolean)
    is_euro = Column(Boolean)
    is_rsd = Column(Boolean)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, server_default=func.current_date())

    category = relationship('Category', back_populates='purchases')
    user = relationship('User', back_populates='purchases')
