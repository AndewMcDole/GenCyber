#!/usr/local/bin/python3

import socket
import select
import sys
import datetime
import os
from termcolor import colored, cprint
import ChaffFactory
import ClientDirectory

def printPrompt(color, effect):
    if color != "none" and effect != "none":
        # colored('hello', 'red')
        sys.stdout.write("{}@{}$ ".format(colored(name, color, attrs=effect), colored(location, "green")))
        sys.stdout.flush()
    elif color != "none":
        sys.stdout.write("{}@{}$ ".format(colored(name, color), colored(location, "green")))
        sys.stdout.flush()
    elif effect != "none":
        sys.stdout.write("{}@{}$ ".format(colored(name, "white", attrs=effect), colored(location, "green")))
        sys.stdout.flush()
    else:
        sys.stdout.write("{}@{}$ ".format(name, colored(location, "green")))
        sys.stdout.flush()

def checkForConnectionLoss(message):
    if compareStrings(message.decode(), "-99"):
        print ("Connection Closed")
        sys.exit()

def displayHelpMenu():
    listOfCommands = ["Send", "Who", "Help", "Locations", "Exit", "Clear", "Redo"]
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

def exitSequence(conn):
    conn.send("disconnecting".encode())
    print ("Disconnecting from server...")
    if conn.recv(1024).decode() == "disconnect success":
        print ("Disconnect successful!")
        sys.exit(0)
    else:
        print ("Disconnect unsuccessful")

def clearScreen():
    os.system('clear')

def send():
    valid_name = False
    while not valid_name:
        message = input("Who to write to: ")

        # Check if client name is mistyped
        server.send(str("check_name " + message).encode())
        if (server.recv(1048).decode() != "success"):
            print ("Failed to send message: {} does not exist".format(message))
        else:
            valid_name = True

    # Remove the \n created by readline()
    message = message.split("\n")[0]

    # Once the user types a name to send, ask for a message to write
    next_part = CF.constructMessage(SECRET_KEY, delimeter)
    while compareStrings(next_part, 'redo'):
        print ("\nRestarting the message construction...\n")
        next_part = CF.constructMessage(SECRET_KEY, delimeter)
    message = message + delimeter + next_part

    server.send(message.encode())

def receive(sock):
    message = socks.recv(2048)
    checkForConnectionLoss(message)

    list_of_messages = message.decode().split(fullMessageDelimeter)

    for message in list_of_messages[:-1]:
        # Once we receive a message, we need to strip off the name and winnow the message
        message_parts = message.split(delimeter)

        date_time = datetime.datetime.now()
        sys.stdout.write("{} ".format(date_time))
        sys.stdout.flush()

        print (" {} <".format(message_parts[0]))
        message_to_winnow = ""
        for message_part in message_parts[1:-1]:
            message_to_winnow = message_to_winnow + message_part + delimeter

        CF.winnow(message_to_winnow, SECRET_KEY, delimeter)
        print ()

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

name = server.recv(1024).decode()

"""
Allow the user to pick their color of choice for their character
"""
valid_choice = False
list_of_colors = ["none", "red", "green", "yellow", "blue", "magenta","cyan","white"]
color_choice = ""
print (list_of_colors)
while not valid_choice:
    color_choice = input ("Please select a color: ").lower()
    if color_choice in list_of_colors:
        valid_choice = True

# list_of_backgrounds = ["none","grey", "red", "green", "yellow", "blue", "magenta","cyan","white"]
# valid_choice = False
# print (list_of_backgrounds)
# while not valid_choice:
#     bg_choice = input ("Please select a background: ").lower()
#     if bg_choice in list_of_backgrounds:
#         valid_choice = True

list_of_effects = ["none","bold","dark","blink","reverse"]
valid_choice = False
print (list_of_effects)
effect_choice = []
while not valid_choice:
    user_input = input ("Please select an effect: ").lower()
    if user_input in list_of_effects:
        effect_choice.append(user_input)
        valid_choice = True

# Receive stone setup and key
message = server.recv(2048)
message_parts = message.decode().split(";;")
stone_list = message_parts[0]
print ("You have {}".format(stone_list))
location = message_parts[1]
print ("Location: {}".format(location))
SECRET_KEY = int(message_parts[2])
print ("Secret Key: {}".format(SECRET_KEY))
delimeter = str(message_parts[3])
fullMessageDelimeter = str(message_parts[4])

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    # used for chaffing/winnowing
    CF = ChaffFactory.ChaffFactory()

    printPrompt(color_choice, effect_choice)

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
            receive(socks)
        else:
            message = sys.stdin.readline()
            if message == "\n":
                break

            #Allow the user to begin sending a messge by typing in "send"
            command = message.split()[0]

            if (compareStrings(command, "send")):
                send()

            elif compareStrings(command, "help"):
                displayHelpMenu()

            elif compareStrings(command, "Who"):
                requestClients(server)

            elif compareStrings(command, "locations"):
                requestListOfLocations(server)

            elif compareStrings(command, "exit"):
                exitSequence(server)

            elif compareStrings(command, "clear"):
                clearScreen()

server.close()
