import requests
import re
with open('vk_user_token') as file:
    vk_user_token = file.readline().strip()


class VK:
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    def get_user_and_persons_info(self, user_id):
        # На вход подается ID пользователя, который общается с ботом
        # На выходе получаем список со списками. Вложенные списки имеют 6 элементов и содержат информацию о
        # подходящих под критерии поиска людях (кандидатах):
        # [ID кандидата, Имя кандидата, Фамилия кандидата, ID фото №1, ID фото №2, ID фото №3].
        # Кандидаты с закрытыми профилями и имеющие меньше 3 фотографий профиля отсеиваются
        url_users_get = 'https://api.vk.com/method/users.get'
        params_users_get = {'access_token': self.token, 'v': '5.131', 'user_ids': user_id, 'fields': 'sex, city, bdate'}
        user_info = requests.get(url=url_users_get, params=params_users_get).json()['response'][0]
        user_year_of_birth = int(re.findall(string=user_info['bdate'], pattern='\d{4}')[0])
        user_city_id = user_info['city']['id']
        user_sex_id = user_info['sex']
        url_users_search = 'https://api.vk.com/method/users.search'
        sex_users_search = 1 if user_sex_id == 2 else 2
        params_users_search = {'sex': sex_users_search, 'birth_year': user_year_of_birth, 'city': user_city_id,
                               'access_token': self.token, 'has_photo': '1', 'v': '5.131',
                               'count': '1000', 'offset': '1000', 'fields': 'sex, city, bdate'}
        fitted_person = requests.get(url=url_users_search, params=params_users_search).json()['response']['items']
        fitted_person_not_closed = list()
        result_list = list()
        for person in fitted_person:
            if not person['is_closed']:
                fitted_person_not_closed.append([person['id'], person['first_name'], person['last_name']])
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
                        if len(person) < 6:
                            person.append(photo['id'])
                if len(person) > 5:
                    result_list.append(person)
            except KeyError:
                pass
        return result_list
