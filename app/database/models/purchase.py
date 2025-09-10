from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, func
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
    created_at = Column(DateTime, server_default=func.now())

    category = relationship("Category", back_populates='purchases')
    # Указываем foreign_keys, так как поле называется owner_id
    user = relationship("User", back_populates='purchases', foreign_keys=[owner_id])
