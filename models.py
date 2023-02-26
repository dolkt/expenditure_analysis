from sqlalchemy import Column, String, Integer, Float, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import relationship
from database import Base

#Setting up tables in the database
class Users(Base):
    #Table name
    __tablename__ = "users"

    #Table columns
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)

    expenditure = relationship("Expenditures", back_populates="user_expenditure")
    category = relationship("Categories", back_populates="user_category")


class Expenditures(Base):
    
    __tablename__ = "expenditures"

    expenditure_id = Column(Integer, primary_key=True, index=True)
    Transaktionsdatum = Column(DateTime, index=True)
    Text = Column(String)
    Belopp = Column(Float)
    Saldo = Column(Float)
    Typ = Column(String)
    Kategori = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    user_expenditure = relationship("Users", back_populates="expenditure")


class Categories(Base):

    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    text = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    user_category = relationship("Users", back_populates="category")
