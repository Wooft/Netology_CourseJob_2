from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError, PendingRollbackError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from config_db import DSN, DB_NAME, DSN_ERROR
from models import create_table
from models import (
    User,
    Photo,
    Favorite,
    BlackList
)


def connect_db():
    try:
        temp_engine = create_engine(DSN)
        temp_engine.connect()
    except OperationalError:
        temp_engine = create_engine(DSN_ERROR)
        with temp_engine.connect() as connection:
            connection.connection.set_isolation_level(
                ISOLATION_LEVEL_AUTOCOMMIT
            )
            connection.execute(f'CREATE DATABASE {DB_NAME}')
    finally:
        return create_engine(DSN)


class VKinderDB:

    def __init__(self):
        self.engine = connect_db()
        create_table(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.models = {
            'user': User,
            'photo': Photo,
            'favorite': Favorite,
            'black_list': BlackList
        }

    def insert_data(self, table: str, data: dict) -> bool:
        try:
            self.session.add(self.models[table](**data))
            self.session.commit()
            return True
        except (IntegrityError, PendingRollbackError):
            self.session.rollback()
            return False

    def find_matches(self, user: dict) -> list:
        matches = list()
        query = self.session.query(User).filter(
            User.id != user['id'],
            User.age == user['age'],
            User.city == user['city']
        ).all()
        for match in query:
            matches.append(self.user_info_to_list(match))
        return matches

    def get_favorites(self, user_id: int) -> list:
        favorites = list()
        query = self.session.query(User).join(
            Favorite, User.id == Favorite.person_id
        ).filter(Favorite.user_id == user_id).all()
        for favorite in query:
            favorites.append(self.user_info_to_list(favorite))
        return favorites

    def user_info_to_list(self, user_info: object()) -> list:
        return [
            user_info.id,
            user_info.first_name,
            user_info.last_name,
            user_info.url
        ] + self.get_user_photos(user_info.id)

    def get_user_photos(self, user_id: int) -> list:
        photos = self.session.query(Photo).join(User).filter(
            User.id == user_id
        ).all()
        return [photo.url for photo in photos]
