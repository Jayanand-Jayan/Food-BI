from sqlalchemy.orm import Session 
import crud, models, schemas
from database import SessionLocal, engine
import pandas as pd
import nltk
# nltk.download('vader_lexicon')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi import Depends

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
    
#     finally:
#         db.close()

db = SessionLocal()

# df = pd.read_csv('Ratings.csv', encoding='latin-1')   

sia = SentimentIntensityAnalyzer()

try:
    all_data = db.query(models.Reviews)
    for row in all_data:
        rev = row.review 
        pol_sc = sia.polarity_scores(rev)
        if (pol_sc['pos'] >= pol_sc['neg']):
            row.tag = 'pos'
        else:
            row.tag = 'neg'
        
        db.commit()
    
finally: 
    db.close()
