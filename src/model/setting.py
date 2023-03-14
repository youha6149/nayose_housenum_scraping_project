from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_NAYOSE_DATABASE_URL = "sqlite:///./src/db/nayose.db"
nayose_engine = create_engine(
    SQLALCHEMY_NAYOSE_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionNayose = sessionmaker(autocommit=False, autoflush=False, bind=nayose_engine)
Base = declarative_base()


def get_nayose_db():
    try:
        with SessionNayose() as session:
            yield session
    except Exception as e:
        print(e)
