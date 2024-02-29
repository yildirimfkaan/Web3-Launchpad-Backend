from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
import sys
import os
Base = declarative_base()
db_path = os.getenv("postgre_connection_string")
def change_status(id: int, status: str = "completed"):
    engine = create_engine(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    project = Table('project', Base.metadata, autoload=True, autoload_with=engine)
    session.query(project).filter(project.c.id == id).update({"is_active":status})
    session.commit()

if __name__ == "__main__":
    id = sys.argv[1]
    status = sys.argv[2]
    change_status(int(id), status)