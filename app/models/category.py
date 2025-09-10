from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = 'categories'
    __table_name__ = {'extend_existing': True} #если таблица уже объявленна в метаданных, мы используем ее

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String)
    parent_id_category = Column(Integer, ForeignKey('categories.id'), nullable=True)

    purchases = relationship("Purchase", back_populates='category')