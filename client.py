#!/usr/local/bin/python3

import socket
import select
import sys
import datetime

import ChaffFactory

def displayHelpMenu():
    listOfCommands = ["Send", "Who", "Help"]
    print ("List of commands: {}\n".format(listOfCommands))

def requestClients(socks):
    socks.send("clients_list".encode())
    message = socks.recv(2048)
    print (message.decode(), "\n")

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
name = input("Who are you? ")
server.send(name.encode())

# Receive the opening message
message = server.recv(2048)
print (message.decode())

# Receive stone setup
message = server.recv(2048)
print (message.decode())

# receive Secret Key as a base 32 number
SECRET_KEY = int(server.recv(2048).decode())
print ("Secret Key: {}".format(SECRET_KEY))

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    # used for chaffing/winnowing
    CF = ChaffFactory.ChaffFactory()

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
    read_sockets, write_socket, error_socket = select.select(sockets_list,[],[])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)

            # Once we receive a message, we need to strip off the name and winnow the message
            message_parts = message.decode().split(";")

            date_time = datetime.datetime.now()
            sys.stdout.write("{} ".format(date_time))
            sys.stdout.flush()

            print (" {} <".format(message_parts[0]))
            message_to_winnow = ""
            for message_part in message_parts[1:-2]:
                message_to_winnow = message_to_winnow + message_part + ";"

            CF.winnow(message_to_winnow, SECRET_KEY)
            print ()
        else:
            message = sys.stdin.readline()

            #Allow the user to begin sending a messge by typing in "send"
            command = message.split()[0]

            if (compareStrings(command, "send")):
                message = input("Who to write to: ")

                # Remove the \n created by readline()
                message = message.split("\n")[0]

                # Once the user types a name to send, ask for a message to write
                message = message + ";" + CF.constructMessage(SECRET_KEY)

                server.send(message.encode())
                print ("Message Sent Successfully\n")

            elif compareStrings(command, "help"):
                displayHelpMenu()

            elif compareStrings(command, "Who"):
                requestClients(server)

server.close()
