from sqlalchemy import Boolean, Column, Integer, String, BigInteger, Float
from database import Base

class ZomatoData(Base):
    __tablename__ = "zom_data"
    rest_id = Column(Integer, primary_key=True, autoincrement=True)
    rest_name = Column(String(100))
    onl_ord = Column(Integer)
    tbl_bk = Column(Integer)
    rating = Column(Float())
    votes = Column(Integer)
    phno = Column(String(50))
    location = Column(String(50))
    rest_type = Column(String(50))
    cuisines = Column(String(200))
    cost = Column(Integer)
    listed_in = Column(String(50))

class Reviews(Base):
    __tablename__ = "reviews"
    rev_id = Column(Integer, primary_key=True, autoincrement=True)
    rest_name = Column(String(512))
    rating = Column(Float())
    review = Column(String(200))
    tag = Column(String(10))