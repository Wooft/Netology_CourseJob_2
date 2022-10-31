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

    person_id = Column(Integer, primary_key=True)
    person_first_name = Column(String(length=60), nullable=False)
    person_last_name = Column(String(length=60), nullable=False)
    person_age = Column(Integer)
    person_sex = Column(String(length=10))
    person_city_id = Column(Integer)
    person_url = Column(String(length=100), unique=True)
    # token = Column(String(length=100))


class Photo(Base):

    __tablename__ = 'photo'

    photo_url = Column(String(length=150), primary_key=True)
    person_id = Column(Integer, ForeignKey('user.person_id'))

    user = relationship(User, backref='photos')


class Favorite(Base):

    __tablename__ = 'favorite'

    like_id = Column(Integer, primary_key=True)
    person_send_like_id = Column(
        Integer, ForeignKey('user.person_id'),
        nullable=False
    )
    person_get_like_id = Column(
        Integer,
        ForeignKey('user.person_id'),
        nullable=False
    )


class BlackList(Base):

    __tablename__ = 'black_list'

    dislike_id = Column(Integer, primary_key=True)
    person_send_dislike_id = Column(
        Integer, ForeignKey('user.person_id'),
        nullable=False
    )
    person_get_dislike_id = Column(
        Integer, ForeignKey('user.person_id'),
        nullable=False
    )

    # user = relationship(User, backref='black_list')


class Checked(Base):

    __tablename__ = 'checked'
    checked_id = Column(Integer, primary_key=True)
    person_checked_id = Column(
        Integer, ForeignKey('user.person_id'),
        nullable=False
    )
    person_get_checked_id = Column(
        Integer, ForeignKey('user.person_id'),
        nullable=False
    )

def create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
