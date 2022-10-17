import os
import pathlib
from VK_part import check_id
from bot_vk import Vk_bot

def getpath(): #Получаем текущий путь каталога с программой
    path = pathlib.Path.cwd()
    return path

def gettoken(): #Функция для получения токенов
    os.chdir(getpath())
    with open('token', 'r') as file:
        group_token = file.readline().strip()
        vk_user_token = file.readline().strip()
        sometoken = file.readline().strip()
        token = file.readline().strip()
    return group_token, vk_user_token, sometoken, token

group_token, vk_user_token, token_2, token_3 = gettoken()
# newbot = Vk_bot(group_token) #запускаем нового бота
#
if __name__ == '__main__':
    list_1 = check_id(12, vk_user_token)
    list_2 = check_id(12, vk_user_token)
    print(list_1)
    print(list_2)
#     newbot.some_bot(vk_user_token)

