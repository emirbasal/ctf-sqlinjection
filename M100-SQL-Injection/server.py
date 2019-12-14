#!/usr/bin/env python


import SocketServer
import time
import threading
import sqlite3
import traceback
import errno
import logging


def main():
    logging.basicConfig(format='%(asctime)s - %(message)s', filename='sql_injection.log', filemode='w',
                        level=logging.INFO)

    port = 6667
    host = '0.0.0.0'

    service = Service
    server = ThreadedService((host, port), service)

    server.allow_reuse_address = True

    server_thread = threading.Thread(target=server.serve_forever)

    server_thread.daemon = True
    server_thread.start()
    print 'Server loop running in thread:', server_thread.name

    print 'Server started on port', port
    logging.info('Server started on port %s' % port)
    print 'Type "exit" to shutdown server'

    if raw_input() == 'exit':
        server.shutdown()
        server.server_close()

    server.shutdown()
    server.server_close()
    logging.info('Server is shutting down')


class Service(SocketServer.BaseRequestHandler):

    def handle(self):

        try:
            print 'Client with IP %s connected ' % self.client_address[0]
            logging.info('Client with IP %s connected ' % self.client_address[0])
            try:
                self.run_challenge()
            except Exception:
                self.send(traceback.format_exc())
                print 'Client with IP %s disconnected' % self.client_address[0]
                logging.info('Client with IP %s disconnected' % self.client_address[0])
                self.finish()

        except IOError as e:
            if e.errno == errno.EPIPE:
                print 'Client with IP %s disconnected unexpectedly' % self.client_address[0]
                logging.info('Client with IP %s connected ' % self.client_address[0])
                self.finish()

    def receive(self):
        return self.request.recv(4096).strip()

    def send(self, string):
        self.request.sendall(string + '\n')

    def finish(self):
        return SocketServer.BaseRequestHandler.finish(self)

    def run_challenge(self):
        with open('admin_password.txt') as pwd:
            flag = pwd.read()

        connection = sqlite3.connect(':memory:')
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE admin (password text)")
        cursor.execute("CREATE TABLE games (publisher text, game text)")
        cursor.execute("INSERT INTO admin VALUES ('%s')" % flag)

        def send_games(query):
            for res in cursor.execute(query).fetchall():
                self.send('"%s": "%s"' % (res[0], res[1]))

        title = "<<< Gamelib >>>"
        menu = """\
        --MENU--
        1) buy game
        2) play game
        3) show game library 
        4) exit"""

        self.send(title)

        while True:
            self.send(menu)
            self.send("-----------")
            choice = self.receive()
            if choice not in ['1', '2', '3', '4']:
                self.send('invalid input')
                continue
            if choice == '1':
                self.send("Publisher of game?")
                publisher = self.receive().replace('"', "")
                self.send("Game title?")
                game = self.receive().replace('"', "")
                cursor.execute("""INSERT INTO games VALUES ("%s", "%s")""" % (publisher, game))
            elif choice == '2':
                self.send("Which game?")
                game = self.receive()
                logging.info('Client %s wants to play: %s' % (self.client_address[0], game))
                result = cursor.execute(("SELECT publisher, game FROM games WHERE game = '%s'" % game)).fetchall()
                if len(result) != 0:
                    self.send('Playing now %s developed by %s' % (result[0][1], result[0][0]))
                    time.sleep(1)
                    self.send('playing....')
                    time.sleep(1)
                    self.send('playing....')
                    time.sleep(1)
                    self.send('You played enough. Back to work!')
                else:
                    self.send('This game is not in your library. You have to buy it first.')
            elif choice == '3':
                publisher_list = list(cursor.execute("SELECT DISTINCT publisher FROM games"))
                for publisher in publisher_list:
                    send_games("""SELECT publisher, game FROM games WHERE publisher = "%s" """ % publisher[0])

            else:
                self.send("Program is now terminated.")
                print 'Client with IP %s disconnected' % self.client_address[0]
                logging.info('Client with IP %s disconnected' % self.client_address[0])
                self.finish()
                break


class ThreadedService(SocketServer.ThreadingMixIn, SocketServer.TCPServer, SocketServer.DatagramRequestHandler):
    pass


if __name__ == "__main__":
    main()

