from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from VK_part import get_user_and_persons_info_from_vk
from database.config_db import DSN, DB_NAME, DSN_ERROR
from database.models import create_table
from database.models import (
    User,
    Photo,
    Favorite,
    BlackList,
    Checked
)
import time

def connect_db():
    engine = create_engine(DSN, echo=True) #Создание временного движка
    if not database_exists(engine.url):
        create_database(engine.url)
    else:
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
    def insert_data(self, table: str, data) -> None:
        for item in data:
            is_data = self.get_data(table, item)
            if not is_data:
                self.session.add(self.models[table](**item))
                self.session.commit()
    def get_data(self, table: str, data: dict) -> object:
        record = self.session.query(self.models[table]).filter_by(**data).first()
        return record
    def get_user_photos(self, user_id: int) -> list:
        # получаем list из photo_url конкретного пользователя
        # на входе int (id пользователя ВК), на выходе list
        photos = self.session.query(Photo).join(User).filter(
            User.person_id == user_id
        ).all()
        return [photo.photo_url for photo in photos]

    def get_user_info_to_search(self, user_id: int) -> list:
        # получаем list критериев (возраст, пол, город)
        # для поиска подходящих конкретному пользователю людей по БД
        # на входе int (id пользователя, общающегося с ботом), на выходе list
        user_info_to_search = self.session.query(User).filter(
            User.person_id == user_id
        ).all()
        return [
            [
                info.person_age,
                'Female' if info.person_sex == 'Male' else 'Male',
                info.person_city_id
            ]
            for info in user_info_to_search
        ][0]

    def get_user_info_to_send(self, some_list):
        # получаем nested list подходящих под критерии людей
        # (в каждом вложенном list id, имя, фамилия, url подходящего человека)
        # на входе list, на выходе nested list
        infos = self.session.query(User).filter(
            User.person_age == some_list[0],
            User.person_sex == some_list[1],
            User.person_city_id == some_list[2]
        ).offset(0).all()
        return [
            [
                info.person_id,
                info.person_first_name,
                info.person_last_name,
                info.person_url
            ]
            for info in infos
        ]

    def get_info_and_photo_to_send(self, user_id: int) -> list:
        # получаем nested list с полной информацией
        # о подходящих под критерии поиска людях из БД
        # в каждом вложенном list:
        #   id,
        #   имя,
        #   фамилия,
        #   url,
        #   photo_url №1,
        #   photo_url №2,
        #   photo_url №3 подходящего человека
        # на входе int (id пользователя, общающегося с ботом),
        # на выходе nested list
        persons_info = self.get_user_info_to_send(
            self.get_user_info_to_search(user_id)
        )
        persons_photo = [
            self.get_user_photos(photo[0]) for photo in persons_info
        ]
        persons_info_and_photo = list()
        persons_info_and_photo.append([
            persons_info[person] + persons_photo[person]
            for person in range(len(persons_info))
        ])
        return persons_info_and_photo

    def insert_new_data_from_vk(self, user_id: int, token: str, offset) -> None:
        # добавляем в БД информацию о пользователе
        # и подходящих под его критерии поиска людях в БД
        # информация о самом пользователе будет добавлена в БД
        # независимо от количества фото в профиле
        # на входе int (id пользователя, общающегося с ботом)
        data = get_user_and_persons_info_from_vk(user_id=user_id, token=token, offset=offset)
        self.insert_data(table='user', data=data[0])
        self.insert_data(table='photo', data=data[1])

    def check_seen_persons(self, user_id, person_id):
        # проверка человека на наличие в черном списке/избранном/просмотренном
        in_black_list = self.session.query(BlackList).filter(
            BlackList.person_send_dislike_id == user_id,
            BlackList.person_get_dislike_id == person_id
        ).all()
        in_favorite = self.session.query(Favorite).filter(
            Favorite.person_send_like_id == user_id,
            Favorite.person_get_like_id == person_id
        ).all()
        in_checked = self.session.query(Checked).filter(
            Checked.person_checked_id == user_id,
            Checked.person_get_checked_id == person_id
        ).all()
        if in_black_list or in_favorite or in_checked:
            return True
        else:
            return False

    def get_person_to_send(self, user_id: int) -> list:
        # поиск в БД одного подходящего человека,
        # который не в черном списке/избранном/просмотренном
        data = self.get_info_and_photo_to_send(user_id=user_id)[0]
        result = list()
        for person in data:
            if not self.check_seen_persons(user_id=user_id, person_id=person[0]):
                result = person
                break
        return result

    def add_seen_person_to_database(
            self, table: str, user_id: int, person_id: int) -> None:
        # добавляем в черный список/избранное/просмотренное
        if table == 'checked':
            checked = Checked(
                person_checked_id=user_id,
                person_get_checked_id=person_id
            )
            self.session.add(checked)
            self.session.commit()
        if table == 'black_list':
            black_list = BlackList(
                person_send_dislike_id=user_id,
                person_get_dislike_id=person_id
            )
            self.session.add(black_list)
            self.session.commit()
        if table == 'favorite':
            favorite = Favorite(
                person_send_like_id=user_id,
                person_get_like_id=person_id
            )
            self.session.add(favorite)
            self.session.commit()
        return

    def get_favorite_list(self, user_id):
    	# На входе id пользователя. На выходе получаем ссылки на профили избранных людей в виде строки(str)
        persons = str()
        favorites = self.session.query(Favorite).filter(
            Favorite.person_send_like_id == user_id
        ).all()
        for person in favorites:
            persons += 'https://vk.com/id' + str(person.person_get_like_id) + ', '
        result = persons.rstrip(", ")
        return result

    #Возвращает сколько пользователей осталось непросмотренных
    def get_count_not_checked(self):
        count = len(self.session.query(User).all()) - \
                (len(self.session.query(Checked).all()) + len(self.session.query(Favorite).all()) +
                 len(self.session.query(BlackList).all()))
        return count

    def clear_seen_list(self, id):
        for c in self.session.query(Checked).filter(Checked.person_checked_id == id).all():
            self.session.delete(c)
        self.session.commit()