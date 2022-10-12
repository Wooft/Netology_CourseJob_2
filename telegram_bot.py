from main import gettoken
from telebot import types
import telebot

token_1, token_2, token_3, tg_token = gettoken() #Получаем токен Телеграм бота

bot = telebot.TeleBot(tg_token) #Создание нового бота

@bot.message_handler(content_types=['text']) #Бот обрабатывает событие,м когда ему отпраляют текст
def get_text_messages(message, chat_id=None):
    if message.text == "Привет":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_1 = types.KeyboardButton("Следующий")
        button_2 = types.KeyboardButton("Предыдущий")
        markup.add(button_1, button_2)
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}! Я тестовый бот для твоей статьи для habr.com".format(
                             message.from_user), reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)