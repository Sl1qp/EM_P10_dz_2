from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

Base = declarative_base()


class genre(Base):
    __tablename__ = "genre"

    genre_id = Column(Integer, primary_key=True)
    name_genre = Column(String)


class author(Base):
    __tablename__ = "author"

    author_id = Column(Integer, primary_key=True)
    name_author = Column(String)


class city(Base):
    __tablename__ = "city"

    city_id = Column(Integer, primary_key=True)
    name_city = Column(String)
    days_delivery = Column(DateTime)


class step(Base):
    __tablename__ = "step"
    step_id = Column(Integer, primary_key=True)
    name_step = Column(String)


class Book(Base):
    __tablename__ = "book"

    book_id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey("author.author_id"))
    genre_id = Column(Integer, ForeignKey("genre.genre_id"))
    price = Column(Integer)
    amount = Column(Integer)


class client(Base):
    __tablename__ = "client"
    client_id = Column(Integer, primary_key=True)
    client_name = Column(String)
    city_id = Column(Integer, ForeignKey("city.city_id"))
    email = Column(String)


class buy(Base):
    __tablename__ = "buy"
    buy_id = Column(Integer, primary_key=True)
    buy_description = Column(String)
    client_id = Column(Integer, ForeignKey("client.client_id"))

class buy_book(Base):
    __tablename__ = "buy_book"
    buy_book_id = Column(Integer, primary_key=True)
    buy_id = Column(Integer, ForeignKey("buy.buy_id"))
    book_id = Column(Integer, ForeignKey("book.book_id"))
    amount = Column(Integer)

class buy_step(Base):
    __tablename__ = "buy_step"
    buy_step_id = Column(Integer, primary_key=True)
    buy_id = Column(Integer, ForeignKey("buy.buy_id"))
    step_id = Column(Integer, ForeignKey("step.step_id"))
    date_step_begin = Column(DateTime)
    date_step_end = Column(DateTime)