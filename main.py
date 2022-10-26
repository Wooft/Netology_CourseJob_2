import os
import pathlib
import pprint
import time

from bot_vk import Vk_bot
import telebot
from telebot import types
from VK_part import get_photos_byid, check_id, get_user_and_persons_info_from_vk, get_user_photo
from database.vkinder_db import VKinderDB
from VK_part import check_id, get_user_and_persons_info_from_vk

def getpath(): #Получаем текущий путь каталога с программой
    path = pathlib.Path.cwd()
    return path

def gettoken(): #Функция для получения токенов
    os.chdir(getpath())
    with open('token', 'r') as file:
        group_token = file.readline().strip()
        vk_user_token = file.readline().strip()
        tg_token = file.readline().strip()
    return group_token, vk_user_token, tg_token

group_token, vk_user_token, tg_token = gettoken()
newbot = Vk_bot(group_token) #запускаем нового бота

bot = telebot.TeleBot(tg_token) #Создание нового бота
def botkeyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_search = types.KeyboardButton("Начать поиск")
    next = types.KeyboardButton("Следующий")
    keyboard.row(start_search, next)
    return keyboard

@bot.message_handler(content_types=['text', 'photo']) #Бот обрабатывает событие,когда ему отпраляют текст
def get_text_messages(message):
    msg = message.text
    if msg == '/start':
        keyword = botkeyboard()
        hitext = 'Привет! \n' \
                 'Это бот для знакомств. Для начала работы с ботом - пришли свой id ответным сообщением\n' \
                 'Для работы бота профиль страницы должен быть открыт, а в основном альбоме доллжно быть не менее трёх фотографий.\n' \
                 'Для взаимодействия с ботом используйте меню или клавиатуру'
        bot.send_message(message.chat.id, text = hitext, reply_markup=keyword)

    if msg.lower() == "привет":
        keyboard = botkeyboard()
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}!".format(
                             message.from_user), reply_markup=keyboard)
        bot.send_message(message.chat.id,
                         text=f'{message.chat.id}', reply_markup=keyboard)

    if msg.isdigit() == True:
        keyboard = botkeyboard()
        vk_id = msg
        if check_id(vk_id, group_token):
            # Вызов функции, которая внесет id телеграма и VK ID в таблицу
            bot.send_message(message.chat.id, text="id принят", reply_markup=keyboard)
            vkinder.insert_new_data_from_vk(user_id=msg, token=vk_user_token)
            vkinder.add_telegram(table='telegram', vk_id=msg, telegram_id=message.chat.id)
            self_person = vkinder.get_user_info(vk_id)
            if self_person == None:
                bot.send_message(message.chat.id, text="Страница пользователя не удовлетворяет требованиям работы Бота", reply_markup=keyboard)
                vkinder.remove_telegram(message.chat.id)
            else:
                bot.send_message(message.chat.id, text=f"Имя: {self_person[0]}\n"
                                                       f"Фамилия: {self_person[1]}\n"
                                                       f"Возраст: {self_person[2]}\n"
                                                       f"Если данные верны, жми 'Начать поиск', если нет - введи свой ID заново",
                                 reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, text="Введенный ID недействителен, повторите ввод ID", reply_markup=keyboard)

    if msg == "/start_search" or msg == "Начать поиск":
        #Функция, которая проверяет, привязан ли к Telegram_id какой то VK_id
        vk_id = 15565301
        #Счетчик порядкового номера записи в выдаче
        global offset
        offset = 20
        person, photos, offset = get_user_and_persons_info_from_vk(vk_id, vk_user_token, offset)

        #Отправка информации о пользователе
        bot.send_message(message.chat.id, text=f"Имя: {person['person_first_name']}\n"
                                               f"Фамилия: {person['person_last_name']}\n"
                                               f"Ссылка на профиль: {person['person_url']}")
        #3 лучших фото из профиля пользователя отправляются
        send_photos(message=message, person=person, token=vk_user_token, path=getpath(), offset=offset)

    if msg == "/next_person" or msg == "Следующий":
        vk_id = 15565301
        offset +=1
        person, photos, offset = get_user_and_persons_info_from_vk(vk_id, vk_user_token, offset)
        # Отправка информации о пользователе
        bot.send_message(message.chat.id, text=f"Имя: {person['person_first_name']}\n"
                                               f"Фамилия: {person['person_last_name']}\n"
                                               f"Ссылка на профиль: {person['person_url']}")
        # 3 лучших фото из профиля пользователя отправляются
        send_photos(message=message, person=person, token=vk_user_token, path=getpath(), offset=offset)



    else:
        keyboard = botkeyboard()
        bot.send_message(message.chat.id, text='Для взаимоделйствия с ботом необходимо использовать только клавиатуру / команды\n'
                                               'ID пользователя вводится только в цифровом формате', reply_markup=keyboard)

@bot.message_handler(content_types=['photo']) #Бот обрабатывает событие,когда ему отпраляют текст
def send_photos(message, person, token, path, offset):
    photoid = get_user_photo(person['person_id'], token, offset)
    send_photos = get_photos_byid(person['person_id'], photoid, token, path)
    pprint.pprint(send_photos)
    if len(send_photos) == 3:
        bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(open(send_photos[0], 'rb')),
                                               telebot.types.InputMediaPhoto(open(send_photos[1], 'rb')),
                                               telebot.types.InputMediaPhoto(open(send_photos[2], 'rb'))])
    elif len(send_photos) >= 1:
        bot.send_photo(message.chat.id, open(send_photos[0], 'rb'))
    elif len(send_photos) == 0:
        bot.send_message(message.chat.id, text='У пользователя нет фото в профиле')
    for elements in send_photos:
        os.remove(elements)

def send_info(message, person_to_send):
    bot.send_message(message.chat.id, text=f"Имя: {person_to_send[1]}\n"
                                           f"Фамилия: {person_to_send[2]}\n"
                                           f"Ссылка на профиль: {person_to_send[3]}")
def get_person(message, vk_id, group_token, offset):
    person, photos, offset = get_user_and_persons_info_from_vk(vk_id, group_token, offset)

    # vkinder.insert_new_data_from_vk(user_id=vk_id, token=group_token)
    # person_to_send = vkinder.get_person_to_send(user_id=vk_id)
    # time.sleep(0.5)
    # if len(person_to_send) == 0:
    #     vkinder.insert_new_data_from_vk(user_id=vk_id, token=vk_user_token)
    #     person_to_send = vkinder.get_person_to_send(user_id=vk_id)
    # current_person = person_to_send
    # send_info(message, person_to_send)
    # send_photos(message, person_to_send, vk_user_token)
    # return current_person

vkinder = VKinderDB()

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
    # while True:
    #     try:
    #         answer = input('Если хотите запустить BK бота: введите "vk", если Telegram бота: введите "tg" ')
    #         if answer.lower() == 'vk':
    #             newbot.some_bot(vk_user_token)
    #             break
    #         if answer.lower() == 'tg':
    #             bot.polling(none_stop=True, interval=0)
    #             break
    #     except Exception as e:
    #         print('Данные введены неверно, попробуйте снова!')
    #         bot.polling(none_stop=True, interval=0)