from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    is_activate = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Используем строку, чтобы избежать проблем с импортом
    purchases = relationship("Purchase", back_populates='user')
    incomes = relationship("Income", back_populates='user')
    categories = relationship("Category", back_populates='user')


    def to_dict(self):
        return {'id': self.id,
                'firstname': self.firstname,
                'lastname': self.lastname,
                'username': self.username,
                'email': self.email,
                'hashed_password': self.hashed_password,
                'is_active': self.is_activate,
                'is_admin': self.is_admin}
