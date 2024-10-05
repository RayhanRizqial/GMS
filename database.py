from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define the Base
Base = declarative_base()

# Configure the MySQL database connection (using PyMySQL as driver)
DATABASE_URL = "mysql+pymysql://root:@localhost:3307/bigproject"

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for SQL logging

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tambahkan fungsi create_tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Create a new session instance
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()