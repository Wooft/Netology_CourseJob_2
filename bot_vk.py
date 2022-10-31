import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from database.vkinder_db import VKinderDB
import random


class Vk_bot:
    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token)
        self.session_api = self.vk_session.get_api()
        self.longpool = VkLongPoll(self.vk_session)
        self.offset = 0

    def firts_keyboard(self): #Первая клавиатура для начала взаимодействия с ботом
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
        return keyboard

    def two_keyboard(self): #Вторая клавиатура для вывода результатов поиска
        keyboard = VkKeyboard(one_time=False, inline=False)
        keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('В черный список', VkKeyboardColor.NEGATIVE)
        keyboard.add_button('В избранное', VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Остановить поиск', VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Показать избранных', VkKeyboardColor.PRIMARY)
        return keyboard

    def get_person(self, id, token):
        #Если количество непросмотренных пользователей меньше трех - запускаем повторный процесс наполнения БД новыми пользователями
        if vkinder.get_count_not_checked() < 3 and self.offset != -1:
            self.sent_some_msg(id, 'Обновляем результаты поиска, придется подождать несколько секунд...', '', keyboard=self.two_keyboard())
            self.offset += 50
            vkinder.insert_new_data_from_vk(user_id=id, token=token, offset=self.offset)
        #Если счетчик наполнения достиг своего максимума - очищаем таблицу просмотренных людей, чтобы перезапустить процесс выдачи результатов из базы данных
        elif self.offset == 1000:
            vkinder.clear_seen_list(id)
            self.offset = -1
        elif self.offset == -1 and vkinder.get_count_not_checked() == 1:
            vkinder.clear_seen_list(id)

        # в БД добавляются пользователи (до 50), подходящие под критерии поиска, чтобы БД не опустела
        person_to_send = vkinder.get_person_to_send(user_id=id)
        # поиск в БД подходящего человек
        current_person = person_to_send
        keyboard = self.two_keyboard()
        self.sent_some_msg(id, f'{person_to_send[1]} {person_to_send[2]} \n {person_to_send[3]}',
                           f'{person_to_send[4]},{person_to_send[5]},{person_to_send[6]}', keyboard)
        return current_person

    def some_bot(self, token: str):
        for event in self.longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    if msg == "начать":
                        #Первое обращение к боту, указываем на то как начать с ним работу правильно
                        some_text = 'Чтобы начать поиск, нажми на кнопку снизу'
                        keyboard = self.firts_keyboard()
                        self.sent_some_msg(id, some_text, '', keyboard=self.firts_keyboard())
                    elif msg == "начать поиск":
                        global current_person
                        current_person = self.get_person(id, token)
                    elif msg == "следующий": #Переходи к седующему результату выдачи
                        if 'current_person' not in globals():
                            self.fix_restart(id)
                        else:
                            vkinder.add_seen_person_to_database(table='checked', user_id=id, person_id=current_person[0])
                            current_person = self.get_person(id, token)
                    elif msg == "в черный список": #Добавляем пользователя в черный список и исключаем его из списка выдачи юзеру
                        if 'current_person' not in globals():
                            self.fix_restart(id)
                        else:
                            self.sent_some_msg(id, 'Пользователь добавлен в черный список\n'
                                                   'Исключен из списка выдачи', '', keyboard=self.two_keyboard())
                            vkinder.add_seen_person_to_database(table='black_list', user_id=id, person_id=current_person[0])
                            current_person = self.get_person(id, token)
                    elif msg == "в избранное": #Добавление в избранное пользователя (опционально - отправляем уведмоление о лайке тому кого лайкнули)
                        if 'current_person' not in globals():
                            self.fix_restart(id)
                        else:
                            self.sent_some_msg(id, 'Пользователь добавлен в избранное', '', keyboard=self.two_keyboard())
                            vkinder.add_seen_person_to_database(table='favorite', user_id=id, person_id=current_person[0])
                            # просмотренный человек добавляется в таблицу 'favorite'
                            current_person = self.get_person(id, token)
                    elif msg == 'показать избранных': #Отправка сообщения с ссылками на аккаунты избранных пользователей
                        self.sent_some_msg(id=id, some_text=vkinder.get_favorite_list(user_id=id), attachment='', keyboard=self.two_keyboard())
                    elif event.type == VkEventType.USER_OFFLINE or msg == "остановить поиск":
                        self.stop_search(id)
                    else:
                        some_text = 'Для взаимодействия с ботом необходимо использовать клавиатуру'
                        keyboard = self.two_keyboard()
                        self.sent_some_msg(id, some_text, '',keyboard)
            if event.type == VkEventType.USER_OFFLINE:
                self.stop_search(id)

    def fix_restart(self, id):
        self.sent_some_msg(id, 'Ошибка, нажмите "Начать поиск"', '', keyboard=self.two_keyboard())
        self.stop_search(id)

    def sent_some_msg(self, id, some_text, attachment, keyboard):
        self.vk_session.method(method="messages.send", values={"user_id": id, "message": some_text,
                                                          "attachment": attachment, "random_id": random.randint(0, 999999), "keyboard": keyboard.get_keyboard()})
    def stop_search(self, id):
        some_text = 'Поиск остановлен. \n Чтобы начать поиск заново, нажми на кнопку снизу'
        keyboard = self.firts_keyboard()
        self.sent_some_msg(id, some_text, '', keyboard)

vkinder = VKinderDB()