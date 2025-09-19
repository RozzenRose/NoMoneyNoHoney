from app.database.engine import Base
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, Float, DateTime, func
from sqlalchemy.orm import relationship

class Income(Base):
    __tablename__ = 'incomes'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    description = Column(String)
    quantity = Column(Float)
    is_rub = Column(Boolean)
    is_euro = Column(Boolean)
    is_rsd = Column(Boolean)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship('User', back_populates='incomes')

    def to_dict(self):
        return {'id': self.id,
                'owner_id': self.owner_id,
                'description': self.description,
                'quantity': self.quantity,
                'is_rub': self.is_rub,
                'is_euro': self.is_euro,
                'is_rsd': self.is_rsd,
                'created_at': self.created_at.isoformat()}
