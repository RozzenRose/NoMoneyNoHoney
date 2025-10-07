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
    currency = Column(String, default='EUR')
    created_at = Column(Date, server_default=func.current_date())

    user = relationship('User', back_populates='incomes')

    def to_dict(self):
        return {'id': self.id,
                'owner_id': self.owner_id,
                'description': self.description,
                'quantity': self.quantity,
                'currency': self.currency,
                'created_at': self.created_at.isoformat()}

    @classmethod
    def from_json(cls, data: dict):
        return cls(id=data["id"],
                owner_id=data["owner_id"],
                description=data["description"],
                quantity=data["quantity"],
                currency=data["currency"],
                created_at=date.fromisoformat(data["created_at"]))
