from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(length=60), nullable=False)
    last_name = Column(String(length=60), nullable=False)
    age = Column(Integer)
    gender = Column(String(length=10))
    city = Column(String(length=80))
    url = Column(String(length=100), unique=True)
    token = Column(String(length=100))


class Photo(Base):

    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    url = Column(String(length=150), unique=True)

    user = relationship(User, backref='photos')


class Favorite(Base):

    __tablename__ = 'favorite'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    person_id = Column(Integer, ForeignKey('user.id'), nullable=False)


class BlackList(Base):

    __tablename__ = 'black_list'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    person_id = Column(Integer, ForeignKey('user.id'), nullable=False)


def create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
