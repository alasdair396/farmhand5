from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker
import sqlalchemy as _sql

# #Set up sqlite connection
# SQLALCHEMY_DATABASE_URI = "sqlite:///./droid.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URI,
#     connect_args={"check_same_thread": False}
# )

DATABASE_URL = "postgresql://droid:r2d2droid@localhost/droid"

engine = _sql.create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()

# sets up so can work with database with dependancies
class DBContext:
    def __init__(self):
        self.db = SessionLocal()
    def __enter__(self):
        return self.db
    def __exit__(self,et,ev, traceback):
        self.db.close()


    
