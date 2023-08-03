from sqlalchemy.orm import Session
import models, schemas

def get_rest(db: Session, rest_name: str):
    return db.query(models.ZomatoData).filter(models.ZomatoData.rest_name == rest_name).first()

def get_rest_by_name(db: Session, rest_name: str):
    return db.query(models.ZomatoData).filter(models.ZomatoData.rest_name == rest_name).first()

def create_rest(db: Session, restaurant: schemas.ZomatoCreate):
    db_user = models.ZomatoData(rest_name=restaurant.rest_name, 
                                onl_ord=restaurant.onl_ord, 
                                tbl_bk=restaurant.tbl_bk,
                                rating=restaurant.rating,
                                votes=restaurant.votes,
                                phno=restaurant.phno,
                                location=restaurant.location,
                                rest_type=restaurant.rest_type,
                                cuisines=restaurant.cuisines,
                                cost=restaurant.cost,
                                listed_in=restaurant.listed_in)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
