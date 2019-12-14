#!/usr/bin/env python

import time
import sqlite3


with open('admin_password.txt') as pwd:
    flag = pwd.read()

connection = sqlite3.connect(':memory:')
cursor = connection.cursor()

cursor.execute("CREATE TABLE admin (password text)")
cursor.execute("CREATE TABLE games (publisher text, game text)")
cursor.execute("INSERT INTO admin VALUES ('%s')" % flag)


def send_games(query):
    for res in cursor.execute(query).fetchall():
        print('"%s": "%s"' % (res[0], res[1]))


title = "<<< Gamelib >>>"
menu = """\
--MENU--
1) buy game
2) play game
3) show game library 
4) exit"""

print(title)

while True:
    print(menu)
    print("-----------")
    choice = input()
    if choice not in ['1', '2', '3', '4']:
        print('invalid input')
        continue
    if choice == '1':
        print("Publisher of game?")
        publisher = input().replace('"', "")
        print("Game title?")
        game = input().replace('"', "")
        cursor.execute("""INSERT INTO games VALUES ("%s", "%s")""" % (publisher, game))
    elif choice == '2':
        print("Which game?")
        game = input()
        result = cursor.execute(("SELECT publisher, game FROM games WHERE game = '%s'" % game)).fetchall()
        if len(result) != 0:
            print('Playing now %s developed by %s' % (result[0][1], result[0][0]))
            time.sleep(1)
            print('playing....')
            time.sleep(1)
            print('playing....')
            time.sleep(1)
            print('You played enough. Back to work!')
        else:
            print('This game is not in your library. You have to buy it first.')
    elif choice == '3':
        publisher_list = list(cursor.execute("SELECT DISTINCT publisher FROM games"))
        for publisher in publisher_list:
            send_games("""SELECT publisher, game FROM games WHERE publisher = "%s" """ % publisher[0])

    else:
        print("Program is now terminated.")
        exit(0)
