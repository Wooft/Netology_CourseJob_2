import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from main import gettoken

vk_session = vk_api.VkApi(token=gettoken())
session_api = vk_session.get_api()
longpool = VkLongPoll(vk_session)
class Vk_bot():
    def __int__(self):
        pass

    def some_bot(self):
        for event in longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    if msg == "привет":
                        self.sent_some_msg(id, "Привет, друг!")
                    if msg == "начать поиск":
                        keyboard = VkKeyboard(one_time=False, inline=False)
                        keyboard.add_button('Предыдущий', VkKeyboardColor.SECONDARY)
                        keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
                        keyboard.add_line()
                        keyboard.add_button('В избранное', VkKeyboardColor.POSITIVE)
                        keyboard.add_button('В черный список', VkKeyboardColor.NEGATIVE)
                        Vk_bot.send_some_msg(id, "first_keyboard", keyboard)

    def sent_some_msg(self, id, some_text):
        vk_session.method("messages.send", {"user_id": id, "message": some_text, "random_id": 0})

VKBot = Vk_bot()

if __name__ == "__main__":
    VKBot.some_bot()


