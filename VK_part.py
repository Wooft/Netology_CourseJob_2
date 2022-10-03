import requests
import re
import time
import random
from main import gettoken


vk_token, my_token  = gettoken()
print(vk_token)
print(my_token)

class VK:
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    def get_user_info(self, user_id):
        # метод можно вызвать с ключом доступа пользователя
        # получаем инфо о пользователе, который общается с ботом
        # на вход подаем id пользователя
        # на выходе получаем список, содержащий по порядку год рождения, город, пол пользователя
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': self.token, 'v': '5.131', 'user_ids': user_id, 'fields': 'sex, city, bdate'}
        response = requests.get(url=url, params=params).json()['response'][0]
        year_of_birth = int(re.findall(string=response['bdate'], pattern='\d{4}')[0])
        city_id = response['city']['id']
        sex_id = response['sex']
        return year_of_birth, city_id, sex_id

    def get_persons_that_fit_our_user(self, user_id):
        # метод можно вызвать с ключом доступа пользователя
        # получаем людей с открытыми аккаунтами, подходящих по критериями (год рождения, город, противоположный пол)
        # на вход подаем результат метода get_user_info
        # на выходе получаем список списков (вложенные списки содержат id пользователя, имя, фамилию)
        url = 'https://api.vk.com/method/users.search'
        city = self.get_user_info(user_id)[1]
        year_of_birth = self.get_user_info(user_id)[0]
        sex = 1 if self.get_user_info(user_id)[2] == 2 else 2
        params = {'sex': sex, 'birth_year': year_of_birth, 'city': city, 'access_token': self.token, 'has_photo': '1', 'v': '5.131', 'count': '20', 'offset': '20', 'fields': 'sex, city, bdate'}
        fitted_person = requests.get(url=url, params=params).json()['response']['items']
        fitted_person_not_closed = list()
        for person in fitted_person:
            if not person['is_closed']:
                fitted_person_not_closed.append([person['id'], person['first_name'], person['last_name']])
        return fitted_person_not_closed

    def get_photo_id_list(self, user_id):
        # метод можно вызвать с ключом доступа пользователя
        # получаем список списков (каждый список для отдельного человека, вложенные списки содержат id трех
        # самых залайканных фотографий человека, подходящего по критериями
        # на вход подаем результат метода get_persons_that_fit_our_user
        # на выходе получаем список списков самых залайканных фотографий
        person_id_list = [a[0] for a in self.get_persons_that_fit_our_user(user_id)]
        photo_id_list_top_3_of_all_persons = list()
        for person_id in person_id_list:
            time.sleep(1)
            url = 'https://api.vk.com/method/photos.get'
            params = {'owner_id': person_id, 'album_id': 'profile', 'photo_sizes': '1', 'extended': '1',
                  'access_token': self.token, 'v': '5.131'}
            try:
                profile_photos = requests.get(url=url, params=params).json()['response']['items']
                likes_list = list()
                likes_list_top_3 = list()
                photo_id_list_top_3 = list()
                for photo in profile_photos:
                    likes_list.append(photo['likes']['count'])
                likes_list.sort(reverse=True)
                likes_list_top_3.append(likes_list[0])
                likes_list_top_3.append(likes_list[1])
                likes_list_top_3.append(likes_list[2])
                for photo in profile_photos:
                    if photo['likes']['count'] in likes_list_top_3:
                        if len(photo_id_list_top_3) < 3:
                            photo_id_list_top_3.append(photo['id'])
                photo_id_list_top_3_of_all_persons.append(photo_id_list_top_3)
            except: Exception
        return photo_id_list_top_3_of_all_persons

    def send_msg_account_link(self, user_id):
        # метод можно вызвать с ключом доступа сообщества
        # отправляем сообщение пользователю, который общается с ботом
        # на вход подаем результат методов get_persons_that_fit_our_user, get_photo_id_list
        # на выходе получаем отправленное сообщение, содержащее: имя и фамилию подходящего человека,
        # ссылку на его аккаунт, вложенные 3 самые залайканные фотографии из профиля
        url = 'https://api.vk.com/method/messages.send'
        for i in range(len(me.get_photo_id_list(user_id))):
            person_id = me.get_persons_that_fit_our_user(user_id)[i][0]
            time.sleep(1) #добавил задержку, чтобы обойти ограничение ВК на количество запросов в секунду
            person_first_name = me.get_persons_that_fit_our_user(user_id)[i][1]
            time.sleep(1) #добавил задержку, чтобы обойти ограничение ВК на количество запросов в секунду
            person_last_name = me.get_persons_that_fit_our_user(user_id)[i][2]
            time.sleep(1) #добавил задержку, чтобы обойти ограничение ВК на количество запросов в секунду
            photo_list = me.get_photo_id_list(user_id)[i]
            params = {'user_id': user_id, 'message': f'https://vk.com/id{person_id} \n {person_first_name} {person_last_name}', 'random_id': random.randint(0, 999999), 'attachment': f'photo{person_id}_{photo_list[0]},photo{person_id}_{photo_list[1]},photo{person_id}_{photo_list[2]}', 'access_token': self.token, 'v': '5.131'}
            response = requests.post(url=url, params=params).json()
            time.sleep(1) #добавил задержку, чтобы обойти ограничение ВК на количество запросов в секунду
        return response

me = VK('15565301', my_token)
my_group = VK('216216029', vk_token)
print(my_group.send_msg_account_link('15565301'))
