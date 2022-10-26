import os
import pathlib
from bot_vk import Vk_bot
from multiprocessing import Pool
def getpath(): #Получаем текущий путь каталога с программой
    path = pathlib.Path.cwd()
    return path

def gettoken(): #Функция для получения токенов
    os.chdir(getpath())
    with open('token', 'r') as file:
        group_token = file.readline().strip()
        vk_user_token = file.readline().strip()
    return group_token, vk_user_token

group_token, vk_user_token = gettoken()
newbot = Vk_bot(group_token) #запускаем нового бота

if __name__ == '__main__':
    newbot.some_bot(vk_user_token)