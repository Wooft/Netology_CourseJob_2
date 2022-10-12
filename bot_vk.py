import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from main import gettoken
from database.vkinder_db import vkinder
import random

token, my_token = gettoken()
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpool = VkLongPoll(vk_session)

class Vk_bot():
    def __init__(self):
        pass

    def firts_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
        return keyboard

    def two_keyboard(self):
        keyboard = VkKeyboard(one_time=False, inline=False)
        keyboard.add_button('Предыдущий', VkKeyboardColor.SECONDARY)
        keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('В черный список', VkKeyboardColor.NEGATIVE)
        keyboard.add_button('В избранное', VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Остановить поиск', VkKeyboardColor.NEGATIVE)
        return keyboard

    def some_bot(self):
        for event in longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    if msg == "начать":  #Первое обращение к боту, указываем на то как начать с ним работу правильно
                        some_text = 'Чтобы начать поиск, нажми на кнопку снизу'
                        vkinder.insert_new_data_from_vk(user_id=id)
                        # в БД добавляются пользователи (до 50), подходящие под критерии поиска, чтобы БД не опустела
                        keyboard = self.firts_keyboard()
                        self.sent_some_msg(id, some_text, keyboard)
                    elif msg == "начать поиск":
                        #Начинаем поиск, тут должен быть вызов функции заполнения БД, а также выдача первого результата
                        vkinder.insert_new_data_from_vk(user_id=id)
                        # в БД добавляются пользователи (до 50), подходящие под критерии поиска, чтобы БД не опустела
                        person_to_send = vkinder.get_person_to_send(user_id=id)
                        # поиск в БД подходящего человека
                        current_person = person_to_send
                        keyboard = self.two_keyboard()
                        self.sent_some_msg(id, f'{person_to_send[1]} {person_to_send[2]} \n {person_to_send[3]}',
                                           f'{person_to_send[4]},{person_to_send[5]},{person_to_send[6]}', keyboard)
                    elif msg == "предыдущий": #Возвращаемся к предыдущему результату выдач
                        pass
                    elif msg == "следующий": #Переходи к седующему результату выдачи
                        vkinder.add_seen_person_to_database(table='checked', user_id=id, person_id=current_person[0])
                        # просмотренный человек добавляется в таблицу 'checked'
                        vkinder.insert_new_data_from_vk(user_id=id)
                        # в БД добавляются пользователи (до 50), подходящие под критерии поиска, чтобы БД не опустела
                        person_to_send = vkinder.get_person_to_send(user_id=id)
                        # поиск в БД подходящего человека
                        current_person = person_to_send
                        keyboard = self.two_keyboard()
                        self.sent_some_msg(id, f'{person_to_send[1]} {person_to_send[2]} \n {person_to_send[3]}',
                                           f'{person_to_send[4]},{person_to_send[5]},{person_to_send[6]}', keyboard)
                    elif msg == "в черный список": #Добавляем пользователя в черный список и исключаем его из списка выдачи юзеру
                        vkinder.add_seen_person_to_database(table='black_list', user_id=id, person_id=current_person[0])
                        # просмотренный человек добавляется в таблицу 'black_list'
                        vkinder.insert_new_data_from_vk(user_id=id)
                        # в БД добавляются пользователи (до 50), подходящие под критерии поиска, чтобы БД не опустела
                        person_to_send = vkinder.get_person_to_send(user_id=id)
                        # поиск в БД подходящего человека
                        current_person = person_to_send
                        keyboard = self.two_keyboard()
                        self.sent_some_msg(id, f'{person_to_send[1]} {person_to_send[2]} \n {person_to_send[3]}',
                                           f'{person_to_send[4]},{person_to_send[5]},{person_to_send[6]}', keyboard)
                    elif msg == "в избранное": #Добавление в избранное пользователя (опционально - отправляем уведмоление о лайке тому кого лайкнули)
                        vkinder.add_seen_person_to_database(table='favorite', user_id=id, person_id=current_person[0])
                        # просмотренный человек добавляется в таблицу 'favorite'
                        vkinder.insert_new_data_from_vk(user_id=id)
                        # в БД добавляются пользователи (до 50), подходящие под критерии поиска, чтобы БД не опустела
                        person_to_send = vkinder.get_person_to_send(user_id=id)
                        # поиск в БД подходящего человека
                        current_person = person_to_send
                        keyboard = self.two_keyboard()
                        self.sent_some_msg(id, f'{person_to_send[1]} {person_to_send[2]} \n {person_to_send[3]}',
                                           f'{person_to_send[4]},{person_to_send[5]},{person_to_send[6]}', keyboard)
                    elif event.type == VkEventType.USER_OFFLINE or msg == "остановить поиск":
                        some_text = 'Поиск остановлен. \n Чтобы начать поиск заново, нажми на кнопку снизу'
                        keyboard = self.firts_keyboard()
                        self.sent_some_msg(id, some_text, '', keyboard)

    def sent_some_msg(self, id, some_text, attachment, keyboard):
        vk_session.method(method="messages.send", values={"user_id": id, "message": some_text,
                                                          "attachment": attachment, "random_id": random.randint(0, 999999), "keyboard": keyboard.get_keyboard()})

VKBot = Vk_bot()

if __name__ == "__main__":
    VKBot.some_bot()
