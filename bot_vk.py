import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from main import gettoken

token, my_token = gettoken()
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpool = VkLongPoll(vk_session)

class Vk_bot():
    def __int__(self):
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
                        keyboard = self.firts_keyboard()
                        self.sent_some_msg(id, some_text, keyboard)
                    if msg == "начать поиск": #Начинаем поиск, тут должен быть вызов функции заполнения БД, а также выдача первого результата
                        keyboard = self.two_keyboard()
                        self.sent_some_msg(id, "first_keyboard", keyboard)

                    if msg == "Предыдущий": #Возвращаемся к предыдущему результату выдач
                        pass

                    if msg == "Следующий": #Переходи к седующему результату выдачи
                        pass

                    if msg == "В черный список": #Добавляем пользователя в черный список и исключаем его из списка выдачи юзеру
                        pass

                    if msg == "В избранное": #Добавяление в избранное пользователя (опционально - отправляем уведмоление о лайке тому кого лайкнули)
                        pass


                    if event.type == VkEventType.USER_OFFLINE or msg == "остановить поиск":
                        some_text = 'Поиск остановлен. \n Чтобы начать поиск заново, нажми на кнопку снизу'
                        keyboard = self.firts_keyboard()
                        self.sent_some_msg(id, some_text, keyboard)



    def sent_some_msg(self, id, some_text, keyboard):
        vk_session.method("messages.send",
                          {"user_id": id, "message": some_text, "random_id": 0, "keyboard": keyboard.get_keyboard()})

VKBot = Vk_bot()

if __name__ == "__main__":
    VKBot.some_bot()
