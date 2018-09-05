import os
import pickle # used for serializing lists allowing them to be sent over sockets
import select
import socket
import sys
import time
from _thread import *

from Session import Session

"""""""""""""""""""""""""""""""""""""""""""""
                Session Server
"""""""""""""""""""""""""""""""""""""""""""""

class SessionServer():

    def __init__(self):
        self.list_of_clients = []
        self.list_of_commands = []
        self.list_of_sessions = []

        self.lifetime_num_sessions = 0
        self.lifetime_num_clients = 0

    def createNewSession(self, num_players):
        if num_players == None or num_players == "" or int(num_players) < 1:
            print("Failed to create session...")
            return

        self.lifetime_num_sessions += 1
        ID = self.lifetime_num_sessions

        new_session = Session(ID, num_players)
        self.list_of_sessions.append(new_session)
        print("Created new session for {} players".format(num_players))
        start_new_thread(new_session.start, ())


    def findSession(self, ID):
        for sess in self.list_of_sessions:
            if int(sess.ID) == int(ID):
                return sess
        return None

    def closeSession(self, ID):
        session = self.findSession(ID)

        if session == None:
            print("Session does not exist")
            return

        # grab all of those client connections first
        for client in session.list_of_clients:
            self.list_of_clients.append(client)

        # tell the session to close itself
        session.close()
        self.list_of_sessions.remove(session)

    def refreshSessions(self):
        


    def addNewClient(self, conn, ip):
        # Send initial session list
        self.sendSessionList(conn)

        self.list_of_clients.append(conn)
        self.lifetime_num_clients += 1

    def proccessCommands(self):
        for command in self.list_of_commands:
            num_args = len(command.split(" "))

            if num_args == 1:
                if command == "help" or command == "?":
                    list_of_commands = ["help", "clients", "sessions", "refresh", "create [num_players]"]
                    print(list_of_commands)
                    print()
                elif command == "clients":
                    print("Total number of clients: {}".format(len(self.list_of_clients)))
                    print()
                elif command == "sessions":
                    if len(self.list_of_sessions) == 0:
                        print("No sessions active...")
                    for s in self.list_of_sessions:
                        print(s)
                    print()
                elif command == "clear":
                    os.system("clear")
                elif command == "refresh":
                    self.refreshSessions()

            elif num_args == 2:
                first = command.split(" ")[0]
                second = command.split(" ")[1]
                if first == "create":
                    self.createNewSession(second)
                    print()
                elif first == "close":
                    self.closeSession(second)
                    print()

            self.list_of_commands.remove(command)

    def listenForCommands(self):
        while True:
            command = sys.stdin.readline()
            command = command.split("\n")[0]
            if command != "":
                self.list_of_commands.append(command.lower())

    def sendSessionList(self, conn):
        sessions = []
        for sess in self.list_of_sessions:
            sessions.append(str(sess))
        conn.send(pickle.dumps(sessions))

    def processClients(self):
        while True:
            # Check each client to see if they want to join a session
            read_socks, write_socks, error_socks = select.select(self.list_of_clients, [], [], 2)

            # Proccess each request
            for client in read_socks:
                try:
                    msg = client.recv(2048).decode()
                except ConnectionResetError:
                    print("Client disconnected")
                    self.list_of_clients.remove(client)

                if msg:
                    print("Processing Client Request")
                    if msg == "refresh":
                        self.sendSessionList(client)
                    elif msg.split(" ")[0] == "join":
                        session = self.findSession(msg.split(" ")[1])
                        if session == None or session.state == "Closed":
                            client.send("reject".encode())
                        elif session.state == "Running":
                            client.send("running".encode())
                        else:
                            session.list_of_clients.append(client)
                            client.send("success".encode())

                else:
                    print("Client disconnected")
                    self.list_of_clients.remove(client)


            # Proccess any server commands
            self.proccessCommands()

"""""""""""""""""""""""""""""""""""""""""""""
                    Main
"""""""""""""""""""""""""""""""""""""""""""""

def main(argv):
     server = setupNetwork(argv[1], int(argv[2]))

     SS = SessionServer()
     start_new_thread(SS.listenForCommands, ())
     start_new_thread(SS.processClients, ())

     while True:
         conn, addr = server.accept()
         SS.addNewClient(conn, addr)

def setupNetwork(ip_addr, port):
    """The first argument AF_INET is the address domain of the
    socket. This is used when we have an Internet Domain with
    any two hosts The second argument is the type of socket.
    SOCK_STREAM means that data or characters are read in
    a continuous flow."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip_addr, port))
    server.listen(100)
    return server

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Proper Usage: python3 server.py ip_addr port NumPlayers")
        exit()
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("\r[CRITICAL] Server stopped by keyboard!!!\n")
