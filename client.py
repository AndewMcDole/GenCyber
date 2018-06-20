#!/usr/local/bin/python3

import socket
import select
import sys
import datetime
from termcolor import colored
import ChaffFactory

def checkForConnectionLoss(message):
    if compareStrings(message.decode(), "-99"):
        print ("Connection Closed")
        sys.exit()

def displayHelpMenu():
    listOfCommands = ["Send", "Who", "Help", "Locations"]
    print ("List of commands: {}\n".format(listOfCommands))

def requestClients(socks):
    socks.send("clients_list".encode())
    message = socks.recv(2048)
    checkForConnectionLoss(message)
    print (message.decode(), "\n")

def requestListOfLocations(socks):
    socks.send("location_list".encode())
    message = socks.recv(2048)
    checkForConnectionLoss(message)
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
server.send("client".encode())

"""
Here we receive the opening message from the Server and ask the User
to pick a name from the provided list. The Server will continue to
ask for a name until one has been entered correctly.
"""
print(server.recv(2048).decode())
name = input("\nSelect your character:  ")
server.send(name.encode())
valid_name = server.recv(1024).decode()

while valid_name == "false":
    print(server.recv(2048).decode())
    name = input("\nSelect your character:  ")
    server.send(name.encode())
    valid_name = server.recv(1024).decode()


"""
# Receive the opening message
message = server.recv(2048)
print (message.decode())
"""

# Receive stone setup and key
message = server.recv(2048)
message_parts = message.decode().split(";")
stone_list = message_parts[0]
print ("You have {}".format(stone_list))
location = message_parts[1]
print ("Location: {}".format(location))
SECRET_KEY = int(message_parts[2])
print ("Secret Key: {}".format(SECRET_KEY))

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    # used for chaffing/winnowing
    CF = ChaffFactory.ChaffFactory()

    # colored('hello', 'red')
    sys.stdout.write("{}@{}$ ".format(colored(name, "red"), colored(location, "green")))
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

            checkForConnectionLoss(message)

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
            if message == "\n":
                break;

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

            elif compareStrings(command, "locations"):
                requestListOfLocations(server)

server.close()
