# db.py
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Double, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "postgresql://vincent:vincent@localhost/projet-certification"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Data_Csv(Base):
    __tablename__ = "data_csv"
    index = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    YEAR = Column(Integer)
    MONTH = Column(Integer)
    DAY_OF_MONTH = Column(Integer)
    DAY_OF_WEEK = Column(Integer)
    AIRLINE_ID = Column(Integer)
    ORIGIN_AIRPORT_ID = Column(Integer)
    DEST_AIRPORT_ID = Column(Integer)
    CRS_DEP_TIME = Column(Integer)
    DEP_DELAY = Column(Integer)
    DEP_TIME_BLK = Column(String)
    CRS_ARR_TIME = Column(Integer)
    ARR_DEL15 = Column(Boolean)  # This is the target variable
    ARR_TIME_BLK = Column(String)
    CRS_ELAPSED_TIME = Column(Integer)


    # Add other fields as necessary


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def engine_connect():
    return engine.connect()