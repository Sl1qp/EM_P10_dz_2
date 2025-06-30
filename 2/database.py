from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, Date, Float

Base = declarative_base()
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class spimex_trading_results(Base):
    __tablename__ = "spimex_trading_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_product_id = Column(Text)
    exchange_product_name = Column(Text)
    oil_id = Column(Text)
    delivery_basis_id = Column(Text)
    delivery_basis_name = Column(Text)
    delivery_type_id = Column(Text)
    volume = Column(Float)
    total = Column(Integer)
    count = Column(Integer)
    date = Column(Date)
    created_on = Column(Date)
    updated_on = Column(Date)


def get_engine_and_session():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return engine, Session


def create_table(engine) -> bool:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        print("БД уже существует")
        return False
    print("БД успешно создана")
    return True


def insert_to_db(obj: spimex_trading_results, session):
    session.add(obj)
    session.commit()
