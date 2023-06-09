from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base
import jwt
import time
def generate_token():
    signing_key = "your_signing_key"  # Replace with your actual signing key

    headers = {
        'alg': "HS256",  
    }
    token_dict = {
        'iat': time.time(),  
        'name': 'Alexandre', 
        'email': 'alexandre.verriere@cgrcinemas.fr'
    } 

    jwt_token = jwt.encode(token_dict, 
                           signing_key, 
                           algorithm="HS256", 
                           headers=headers
                           )
    return jwt_token

engine = create_engine('your_database_connection_string')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

token = generate_token()
print(token)