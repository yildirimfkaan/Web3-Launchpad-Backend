from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy_utils import database_exists, create_database
# from dotenv import load_dotenv

# load_dotenv()

from hubspot import HubSpot
API_CLIENT = HubSpot(access_token=os.getenv("hubspot_access_token"))
postgreConnString = os.getenv("postgre_connection_string")
SQLALCHEMY_DATABASE_URL = postgreConnString

engine = create_engine(SQLALCHEMY_DATABASE_URL)

if not database_exists(engine.url):
    create_database(engine.url)
else:
    engine.connect()
DB_NAME = engine.url.database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
