from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Date, func
from sqlalchemy.orm import relationship
from datetime import date


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

    category = relationship("Category", back_populates='purchases')
    # Указываем foreign_keys, так как поле называется owner_id
    user = relationship("User", back_populates='purchases', foreign_keys=[owner_id])


    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                'price': self.price,
                'is_rub': self.is_rub,
                'is_euro': self.is_euro,
                'is_rsd': self.is_rsd,
                'owner_id': self.owner_id,
                'category_id': self.category_id,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat()}
