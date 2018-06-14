#!/usr/local/bin/python3


# The Students DO NOT GET A COPY of This
# This is to be used to issue commands to the server
# without the commands being displayed on the server itself


import socket
import select
import sys
import datetime

def displayHelpMenu():
    listOfCommands = ["Game_State", "Delete", "Who", "Help"]
    print ("List of commands: {}".format(listOfCommands))

def requestClients(socks):
    socks.send("clients_list".encode())
    message = socks.recv(2048)
    print (message.decode())

def compareStrings(str1, str2):
    str1 = str1.replace(" ", "")
    str2 = str2.replace(" ", "")
    if str1.lower() == str2.lower():
        # print ("Comparing {} and {}".format(str1.lower(), str2.lower()))
        return True
    return False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print ("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))

#User setup
name = "server_master"
server.send(name.encode())

# Receive the opening message
message = server.recv(2048)
print (message.decode())

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]


    sys.stdout.write("> ")
    sys.stdout.flush()

    """ There are two possible input situations. Either the
    user wants to give  manual input to send to other people,
    or the server is sending a message  to be printed on the
    screen. Select returns from sockets_list, the stream that
    is reader for input. So for example, if the server wants
    to send a message, then the if condition will hold true
    below.If the user wants to send a message, the else
    condition will evaluate as true"""
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)

            date_time = datetime.datetime.now()
            sys.stdout.write("{} {}".format(date_time, message.decode()))
            sys.stdout.flush()

        else:
            message = sys.stdin.readline()

            #Allow the user to begin sending a messge by typing in "send"
            command = message.split()[0]

            if (compareStrings(command, "game_state")):
                server.send("game_state;".encode())
                print(server.recv(4096).decode())

            elif (compareStrings(command, "delete")):
                name_to_delete = input ("Who to delete: ")
                message = "delete;" + name_to_delete
                server.send(message.encode())

            elif compareStrings(command, "help"):
                displayHelpMenu()

            elif compareStrings(command, "Who"):
                requestClients(server)

server.close()
