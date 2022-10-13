import os
from main import gettoken, getpath
from telebot import types
from VK_part import VK
from database.vkinder_db import vkinder
import telebot

token_1, token_2, token_3, tg_token = gettoken() #Получаем токен Телеграм бота
bot = telebot.TeleBot(tg_token) #Создание нового бота
newVK = VK(token_2)
def botkeyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_search = types.KeyboardButton("Начать поиск")
    stop_search = types.KeyboardButton("Остановить поиск")
    next = types.KeyboardButton("Следующий")
    keyboard.row(start_search, stop_search)
    keyboard.row(next)
    return keyboard

@bot.message_handler(content_types=['text', 'photo']) #Бот обрабатывает событие,когда ему отпраляют текст
def get_text_messages(message):
    msg = message.text
    if msg == '/start':
        keyword = botkeyboard()
        hitext = 'Привет! \n' \
                 'Это бот для знакомств. Для начала работы с ботом - пришли свой id ответным сообщением\n' \
                 'Для взаимодействия с ботом используйте меню или клавиатуру'
        bot.send_message(message.chat.id, text = hitext, reply_markup=keyword)

    if msg.lower() == "привет":
        keyboard = botkeyboard()
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}!".format(
                             message.from_user), reply_markup=keyboard)

    if msg.isdigit() == True:
        keyboard = botkeyboard()
        global vk_id
        vk_id = msg
        bot.send_message(message.chat.id, text="id принят", reply_markup=keyboard)
        vkinder.insert_new_data_from_vk(user_id=vk_id)

    if msg == "/start_search" or msg == "Начать поиск":
        vkinder.insert_new_data_from_vk(user_id=vk_id)
        person_to_send = vkinder.get_person_to_send(user_id=vk_id)
        global current_person
        current_person = person_to_send
        send_info(message, person_to_send)
        send_photos(message, person_to_send)

    if msg == "/next_person" or msg == "Следующий":
        vkinder.add_seen_person_to_database(table='checked', user_id=vk_id, person_id=current_person[0])
        vkinder.insert_new_data_from_vk(user_id=vk_id)
        person_to_send = vkinder.get_person_to_send(user_id=vk_id)
        current_person = person_to_send
        send_info(message, person_to_send)
        send_photos(message, person_to_send)

@bot.message_handler(content_types=['photo']) #Бот обрабатывает событие,когда ему отпраляют текст
def send_photos(message, person_to_send):
    photoid = []
    for elements in person_to_send[4:]:  # получаем список id фото для загрузки в кэш
        photoid.append(int(elements[elements.index('_') + 1:]))
    send_photos = newVK.get_photos_yid(person_to_send[0], photoid)
    bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(open(send_photos[0], 'rb')),
                                           telebot.types.InputMediaPhoto(open(send_photos[1], 'rb')),
                                           telebot.types.InputMediaPhoto(open(send_photos[2], 'rb'))])
    for elements in send_photos:
        os.remove(elements)

def send_info(message, person_to_send):
    bot.send_message(message.chat.id, text=f"Имя: {person_to_send[1]}\n"
                                           f"Фамилия: {person_to_send[2]}\n"
                                           f"Ссылка на профиль: {person_to_send[3]}")

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)