import os
import pathlib
import pprint
from bot_vk import Vk_bot
import telebot
from telebot import types
from VK_part import get_photos_byid, check_id, get_user_and_persons_info_from_vk, get_user_photo
from database.vkinder_db import VKinderDB
from VK_part import check_id, get_user_and_persons_info_from_vk, get_self_info

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
newbot = Vk_bot(group_token) #запускаем нового VK бота
bot = telebot.TeleBot(tg_token) #Создание нового бота Telegram

def botkeyboard(): #Создание клавиатуры Telegram бота
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_search = types.KeyboardButton("Начать поиск")
    next = types.KeyboardButton("Следующий")
    keyboard.row(start_search, next)
    return keyboard

@bot.message_handler(content_types=['text', 'photo']) #Бот обрабатывает событие,когда ему отпраляют текст
def get_text_messages(message):
    msg = message.text
    #Полученное сообщение сохраняется в переменную
    #Если сообщение содержит стартовую команду, то:
    if msg == '/start':
        #Возвращаем боту клавиатуру
        keyword = botkeyboard()
        #Отправляется приветсвенный текст и указание на то, что все взаимодействие с ботом осуществляется через клавиатуру
        hitext = 'Привет! \n' \
                 'Это бот для знакомств. Для начала работы с ботом - пришли свой id ответным сообщением\n' \
                 'Для работы бота профиль страницы должен быть открыт, а в основном альбоме доллжно быть не менее трёх фотографий.\n' \
                 'Для взаимодействия с ботом используйте меню или клавиатуру'
        bot.send_message(message.chat.id, text = hitext, reply_markup=keyword)

    #В целом, бесполезный код, отвечает на "привет" от пользователя
    if msg.lower() == "привет":
        keyboard = botkeyboard()
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}!".format(
                             message.from_user), reply_markup=keyboard)
        bot.send_message(message.chat.id,
                         text=f'{message.chat.id}', reply_markup=keyboard)

    #Если сообщение представялет собой набор чисел, то оно распознается как ID пользователя Вконтакте
    if msg.isdigit() == True:
        keyboard = botkeyboard()
        vk_id = msg
        """ Запускается проверка на то, что введенный ID действителен
         Если это так, то возвращается информация о пользователе, ID которого введен
         Если нет, то повтоярется запрос ID """
        if check_id(vk_id, group_token):
            # Вызов функции, которая внесет id телеграма и VK ID в таблицу
            bot.send_message(message.chat.id, text="id принят", reply_markup=keyboard)
            self_person = get_self_info(some_id=vk_id, token=vk_user_token)
            # vkinder.insert_new_data_from_vk(user_id=msg, token=vk_user_token)
            vkinder.add_telegram(table='telegram', vk_id=msg, telegram_id=message.chat.id)
            bot.send_message(message.chat.id, text=f"Имя: {self_person['name']}, Фамилия: {self_person['last_name']}",
                             reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, text="Введенный ID недействителен, повторите ввод ID", reply_markup=keyboard)

    if msg == "/start_search" or msg == "Начать поиск":
        #Функция, которая проверяет, привязан ли к Telegram_id какой то VK_id
        if vkinder.get_vkid_by_telegram(message.chat.id) == None:
            bot.send_message(message.chat.id, text="Введите ID пользователя для работы с ботом")
        else:
            vk_id = vkinder.get_vkid_by_telegram(message.chat.id)
            #Счетчик порядкового номера записи в выдаче, глобальный
            #Присваивается первоначальное значение
            petson_to_send(message, vk_id, vk_user_token)



    # if msg == "/next_person" or msg == "Следующий":
    #     if vkinder.get_vkid_by_telegram(message.chat.id) == None:
    #         bot.send_message(message.chat.id, text="Введите ID пользователя для работы с ботом")
    #     else:
    #         person, photos, offset = get_user_and_persons_info_from_vk(vkinder.get_vkid_by_telegram(message.chat.id), vk_user_token, offset)
    #         # Отправка информации о пользователе
    #         bot.send_message(message.chat.id, text=f"Имя: {person['person_first_name']}\n"
    #                                                f"Фамилия: {person['person_last_name']}\n"
    #                                                f"Ссылка на профиль: {person['person_url']}")
    #         # 3 лучших фото из профиля пользователя отправляются
    #         send_photos(message=message, person=person, token=vk_user_token, path=getpath(), offset=offset)
    #
    # else:
    #     keyboard = botkeyboard()
    #     bot.send_message(message.chat.id, text='Для взаимоделйствия с ботом необходимо использовать только клавиатуру / команды\n'
    #                                            'ID пользователя вводится только в цифровом формате', reply_markup=keyboard)

#Функция, высылающая фото пользователя по ID
@bot.message_handler(content_types=['photo']) #Бот обрабатывает событие,когда ему отпраляют текст
def send_photos(message, person, token, offset, path):
    photoid = get_user_photo(person['person_id'], token, offset)
    send_photos = get_photos_byid(person['person_id'], photoid, token, path)
    #Если у пользователя есть три фото, отправляются три фото
    if len(send_photos) == 3:
        bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(open(send_photos[0], 'rb')),
                                               telebot.types.InputMediaPhoto(open(send_photos[1], 'rb')),
                                               telebot.types.InputMediaPhoto(open(send_photos[2], 'rb'))])
    #Если фото в провиле 2 или 1, то отправялется только одно фото
    elif len(send_photos) >= 1:
        bot.send_photo(message.chat.id, open(send_photos[0], 'rb'))
    #Если в профиле нет фото, пользователь получает соответсвующее уведомление
    elif len(send_photos) == 0:
        bot.send_message(message.chat.id, text='У пользователя нет фото в профиле')
    #Удаляются временные файлы
    for elements in send_photos:
        os.remove(elements)

def send_info(message, person_to_send):
    bot.send_message(message.chat.id, text=f"Имя: {person_to_send[1]}\n"
                                           f"Фамилия: {person_to_send[2]}\n"
                                           f"Ссылка на профиль: {person_to_send[3]}")

def petson_to_send(message, vk_id, vk_user_token):
    pprint.pprint(locals())
    if 'offset' not in globals():
        global offset
    offset = +1
    print(offset)
    person, photos, offset = get_user_and_persons_info_from_vk(vk_id, vk_user_token, offset)
    bot.send_message(message.chat.id, text=f"Имя: {person['person_first_name']}\n"
                                           f"Фамилия: {person['person_last_name']}\n"
                                           f"Ссылка на профиль: {person['person_url']}")
    send_photos(message=message, person=person, token=vk_user_token, offset=offset, path=getpath())


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