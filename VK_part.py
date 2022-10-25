import os
import pathlib
import pprint
import time
import requests
import re
import datetime
import wget


def get_user_and_persons_info_from_vk(user_id, token, offset):
    # На вход подается ID пользователя, который общается с ботом
    # На выходе получаем список со списками. Вложенные списки имеют 6 элементов и содержат информацию о
    # подходящих под критерии поиска людях (кандидатах):
    # [ID кандидата, Имя кандидата, Фамилия кандидата, ID фото №1, ID фото №2, ID фото №3].
    # Кандидаты с закрытыми профилями и имеющие меньше 3 фотографий профиля отсеиваются
    fitted_person, offset = search_user(user_id, token, offset)
    photos = list()
    #Проверка на то, что профиль пользователя открыт
    time.sleep(0.33)
    photos = get_user_photo(fitted_person['id'], token)
    if len(photos) < 3:
        offset += 1
        time.sleep(0.33)
        get_user_and_persons_info_from_vk(user_id, token, offset)

    person_info = {
        'id': fitted_person['id'],
        'name': fitted_person['first_name'],
        'last_name': fitted_person['last_name']
    }
    return person_info, photos, offset

def search_user(user_id, token, offset):
    global person
    time.sleep(0.33)
    url_users_get = 'https://api.vk.com/method/users.get'
    params_users_get = {'access_token': token, 'v': '5.131', 'user_ids': user_id, 'fields': 'sex, city, bdate'}
    user_info = requests.get(url=url_users_get, params=params_users_get).json()['response'][0]
    url_users_search = 'https://api.vk.com/method/users.search'
    sex_users_search = 1 if user_info['sex'] == 2 else 2
    # в параметры поиска подставляется номер следующей записи
    params_users_search = {'sex': sex_users_search, 'birth_year': int(re.findall(string=user_info['bdate'], pattern='\d{4}')[0]), 'city': user_info['city']['id'],
                           'access_token': token, 'has_photo': '1', 'v': '5.131',
                           'count': '1', 'offset': offset, 'fields': 'sex, city, bdate'}
    if requests.get(url=url_users_search, params=params_users_search).json()['response']['items'][0]['is_closed'] == False:
        person = requests.get(url=url_users_search, params=params_users_search).json()['response']['items'][0]
    else:
        offset += 1
        search_user(user_id, token, offset)
    print(f'offset = {offset}')
    return person, offset



def get_user_photo(user_id, token):
    time.sleep(0.33)
    url_person_photos_get = 'https://api.vk.com/method/photos.get'
    params_person_photos_get = {'owner_id': user_id, 'album_id': 'profile', 'photo_sizes': '1',
                                'extended': '1', 'access_token': token, 'v': '5.131'}
    profile_photos = requests.get(url=url_person_photos_get,
                                  params=params_person_photos_get).json()['response']['items']
    print(profile_photos)
    likes_list = list()
    for photo in profile_photos:
        likes_list.append(photo['likes']['count'])
    likes_list.sort(reverse=True)
    likes_list_top_3 = likes_list[:3]
    photos = list()
    for photo in profile_photos:
        if photo['likes']['count'] in likes_list_top_3:
                            photos.append(photo['id'])
    return photos

def get_photos_byid(some_id: int, list_photos: list, token, path):
    if 'temp' not in os.listdir(path):
        os.mkdir('temp')
    os.chdir(os.path.join(path, 'temp')) #переходим во временную папку
    urls = {}
    profile_photos = get_urls(some_id, token)
    for elements in list_photos:
        for photo in profile_photos['response']['items']:
            if photo['id'] == elements:
                for size in photo['sizes']:
                    if size['type'] == 'y' or size['type'] == 'x':
                        urls[f'{elements}.jpg'] = size['url']
    photo_upload = []

    for keys, items in urls.items(): #Скачиваем все фото
        photo_upload.append(keys)
        wget.download(items, keys)
    return photo_upload

def get_urls(some_id, token):
    url_person_photos_get = 'https://api.vk.com/method/photos.get'
    params_person_photos_get = {'owner_id': some_id, 'album_id': 'profile', 'photo_sizes': '1',
                                'extended': '1', 'access_token': token, 'v': '5.131'}
    profile_photos = requests.get(url=url_person_photos_get,
                                    params=params_person_photos_get).json()
    if 'error' in profile_photos.keys():
        time.sleep(1)
        get_urls(some_id, token)
    else:
        return profile_photos

def check_id(some_id, token):
    url_users_get = 'https://api.vk.com/method/users.get'
    params_users_get = {'access_token': token, 'v': '5.131', 'user_ids': some_id, 'fields': 'sex, city, bdate'}
    response = requests.get(url=url_users_get, params=params_users_get).json()
    if len(response['response']) == 0 or 'deactivated' in response['response'][0].keys() or response['response'][0]['is_closed'] == True:
        return False
    else:
        return True


