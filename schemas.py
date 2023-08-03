from pydantic import BaseModel

class ZomatoBase(BaseModel):
    rest_id: int

class ZomatoCreate(ZomatoBase):
    rest_name: str
    onl_ord: int
    tbl_bk: int
    rating: float
    votes: int
    phno: str
    location: str
    rest_type: str
    cuisines: str
    cost: int
    listed_in: str

class Zomato(ZomatoBase):
    rest_name: str
    phno: str 
    rating: float
    listed_in: str 

    class Config:
        orm_mode=True


class ReviewsBase(BaseModel):
    rev_id: int

class Reviews(ReviewsBase):
    rest_name: str
    rating: float 
    review: str 
    tag: str
    
    class Config:
        orm_mode = True 
