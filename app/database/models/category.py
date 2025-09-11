from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True} #если таблица уже объявленна в метаданных, мы используем ее

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    category_name = Column(String)
    is_root = Column(Boolean, default=False)

    purchases = relationship("Purchase", back_populates='category')
    user = relationship("User", back_populates='categories')