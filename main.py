import os
import pathlib


def getpath():
    path = pathlib.Path.cwd()
    return path

def gettoken():
    os.chdir(getpath())
    with open('token', 'r') as file:
        token = file.readline().strip()
        user_token = file.readline().strip()
    return token, user_token