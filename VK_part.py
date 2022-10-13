import os
import time
import requests
import re
import datetime
import wget
from main import getpath
import pprint

with open('token') as file:
    group_token = file.readline().strip()
    vk_user_token = file.readline().strip()


class VK:
    def __init__(self, token):
        self.token = token

    def get_user_id(self, url):
        pass

    def get_user_and_persons_info_from_vk(self, user_id):
        # На вход подается ID пользователя, который общается с ботом
        # На выходе получаем список со списками. Вложенные списки имеют 6 элементов и содержат информацию о
        # подходящих под критерии поиска людях (кандидатах):
        # [ID кандидата, Имя кандидата, Фамилия кандидата, ID фото №1, ID фото №2, ID фото №3].
        # Кандидаты с закрытыми профилями и имеющие меньше 3 фотографий профиля отсеиваются
        url_users_get = 'https://api.vk.com/method/users.get'
        params_users_get = {'access_token': self.token,
                            'v': '5.131',
                            'user_ids': user_id,
                            'fields': 'sex, city, bdate'}
        user_info = requests.get(url=url_users_get, params=params_users_get).json()['response'][0]
        user_year_of_birth = int(re.findall(string=user_info['bdate'], pattern='\d{4}')[0])
        user_city_id = user_info['city']['id']
        user_sex_id = user_info['sex']
        user_first_name = user_info['first_name']
        user_last_name = user_info['last_name']
        url_users_search = 'https://api.vk.com/method/users.search'
        sex_users_search = 1 if user_sex_id == 2 else 2
        params_users_search = {'sex': sex_users_search, 'birth_year': user_year_of_birth, 'city': user_city_id,
                               'access_token': self.token, 'has_photo': '1', 'v': '5.131',
                               'count': '50', 'offset': '50', 'fields': 'sex, city, bdate'}
        fitted_person = requests.get(url=url_users_search, params=params_users_search).json()['response']['items']
        fitted_person_not_closed = list()
        fitted_person_not_closed.append([user_id, user_first_name, user_last_name, datetime.datetime.now().year - user_year_of_birth, user_sex_id, user_city_id, f'https://vk.com/id{user_id}'])
        person_list = list()
        person_info_result_list = list()
        person_photo_result_list = list()
        for person in fitted_person:
            if not person['is_closed']:
                fitted_person_not_closed.append([person['id'], person['first_name'], person['last_name'], datetime.datetime.now().year - user_year_of_birth, sex_users_search, user_city_id, f"https://vk.com/id{person['id']}"])
        for person in fitted_person_not_closed:
            url_person_photos_get = 'https://api.vk.com/method/photos.get'
            params_person_photos_get = {'owner_id': person[0], 'album_id': 'profile', 'photo_sizes': '1',
                                        'extended': '1', 'access_token': self.token, 'v': '5.131'}
            try:
                profile_photos = requests.get(url=url_person_photos_get,
                                              params=params_person_photos_get).json()['response']['items']
                likes_list = list()
                for photo in profile_photos:
                    likes_list.append(photo['likes']['count'])
                likes_list.sort(reverse=True)
                likes_list_top_3 = likes_list[:3]
                for photo in profile_photos:
                    if photo['likes']['count'] in likes_list_top_3:
                        if len(person) < 10:
                            person.append(photo['id'])
                if len(person) > 9:
                    person_list.append(person)
            except KeyError:
                pass
        for person in person_list:
            dict_person_info = dict()
            dict_person_info['person_id'] = person[0]
            dict_person_info['person_first_name'] = person[1]
            dict_person_info['person_last_name'] = person[2]
            dict_person_info['person_age'] = person[3]
            dict_person_info['person_sex'] = 'Male' if person[4] == 2 else 'Female'
            dict_person_info['person_city_id'] = person[5]
            dict_person_info['person_url'] = person[6]
            person_info_result_list.append(dict_person_info)
            dict_person_photo = dict()
            dict_person_photo['photo_url'] = f'photo{person[0]}_{person[7]}'
            dict_person_photo['person_id'] = person[0]
            person_photo_result_list.append(dict_person_photo)
            dict_person_photo = dict()
            dict_person_photo['photo_url'] = f'photo{person[0]}_{person[8]}'
            dict_person_photo['person_id'] = person[0]
            person_photo_result_list.append(dict_person_photo)
            dict_person_photo = dict()
            dict_person_photo['photo_url'] = f'photo{person[0]}_{person[9]}'
            dict_person_photo['person_id'] = person[0]
            person_photo_result_list.append(dict_person_photo)
        return person_info_result_list, person_photo_result_list

    def get_photos_yid(self, some_id: int, list_photos: list):
        path = getpath()
        if 'temp' not in os.listdir(path):
            os.mkdir('temp')
        os.chdir(os.path.join(path, 'temp')) #переходим во временную папку
        time.sleep(1)
        urls = {}
        url_person_photos_get = 'https://api.vk.com/method/photos.get'
        params_person_photos_get = {'owner_id': some_id, 'album_id': 'profile', 'photo_sizes': '1',
                                    'extended': '1', 'access_token': self.token, 'v': '5.131'}
        profile_photos = requests.get(url=url_person_photos_get,
                                      params=params_person_photos_get).json()['response']['items']

        for elements in list_photos:
            for photo in profile_photos:
                if photo['id'] == elements:
                    for size in photo['sizes']:
                        if size['type'] == 'y' or size['type'] == 'x':
                            urls[f'{elements}.jpg'] = size['url']
        photo_upload = []

        for keys, items in urls.items(): #Скачиваем все фото
            photo_upload.append(keys)
            wget.download(items, keys)
        return photo_upload

me = VK(vk_user_token)
