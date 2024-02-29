from fastapi import FastAPI
import models
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)
s = Session(engine)
# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:8008",
#     "http://192.168.1.27:8008",
#     "http://192.168.1.27:8000",
# ]

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(middleware=middleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from logger import *
from auth import *
from project import *
