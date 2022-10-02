import os
import pathlib


def getpath():
    path = pathlib.Path.cwd()
    return path

def gettoken():
    os.chdir(getpath())
    with open('token', 'r') as file:
        token_1 = file.readline().strip()
        token_2 = file.readline().strip()
        token = file.readline().strip()
    return token