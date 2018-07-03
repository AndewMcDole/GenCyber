import enum
import math
import os
import pickle # used for serializing lists allowing them to be sent over sockets
import random
import select
import socket
import sys
from termcolor import colored
import time

import Hashing

class MessageCode(enum.Enum):
    HIGH_PRIORITY="HIGH"
    LOW_PRIORITY="LOW"
    FULL_STOP="FULL_STOP"

def main(argv):
    if len(sys.argv) != 3:
        print("Correct usage: script, IP Address, port number")
        exit()
    displayMainMenu(sys.argv)

def setupNetwork(ip_addr, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # animation
    sleepFactor = 0.01
    for i in range(100):
        print("\rConnecting to server...[{}%]".format(i), end="")
        time.sleep(sleepFactor)
    print("\rConnecting to server...[100%]")

    server.connect((ip_addr, port))
    return server

def displayMainMenu(argv):
    userOptions = ["Connect to a game", "Reconnect to a game", "Exit"]
    print()
    for i in range(len(userOptions)):
        print("{}. {}".format(i + 1, userOptions[i]))
    userChoice = input("\nWhat would you like to do? ")

    while not userChoice or int(userChoice) not in range(len(userOptions) + 1):
        userChoice = input("What would you like to do? ")

    if userChoice == "1":
        server = setupNetwork(argv[1], int(argv[2]))
        print("Setting up client...")
        name, nameColor, locationColor, location, SECRET_KEY = setupClient(server)
        mainGameLoop(server, name, nameColor, locationColor, location, SECRET_KEY)

    elif userChoice == "2":
        server = setupNetwork(argv[1], int(argv[2]))
        print("Sending session key...")
        name, nameColor, locationColor, location, SECRET_KEY = reconnect(server)
        mainGameLoop(server, name, nameColor, locationColor, location, SECRET_KEY)

    else:
        print("Exiting...")

def mainGameLoop(server, name, nameColor, locationColor, location, SECRET_KEY):
    """
    This list will hold messsages until the
    user is ready
    """
    lowPriorityMessageQueue = []

    while True:

        # maintains a list of possible input streams
        sockets_list = [sys.stdin, server]

        sys.stdout.write("{}@{}$ ".format(colored(name, nameColor), colored(location, locationColor)))
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
            sys.stdout.flush()
            if socks == server:
                message = receiveMessage(server, lowPriorityMessageQueue, MessageCode.LOW_PRIORITY)
                lowPriorityMessageQueue.append(message)
                print("Message Received...")
                # check for notifications
                displayNotifications(lowPriorityMessageQueue)
            else:
                message = sys.stdin.readline()
                if message == "\n":
                    break

                command = message.split()[0]

                if (command.lower() == "help" or command == "?"):
                    getListOfCommands(server)
                elif (command.lower() == "who"):
                    getClientList(server)
                elif (command.lower() == "locations"):
                    getLocationList(server)
                elif (command.lower() == "setup"):
                    getClientSetup(server)
                elif (command.lower() == "send"):
                    sendMessage(server, SECRET_KEY)
                elif (command.lower() == "exit"):
                    exitSequence(server)
                elif (command.lower() == "clear"):
                    os.system("clear")
                elif (command.lower() == "winnow"):
                    winnowAllMessages(lowPriorityMessageQueue, SECRET_KEY)
                else:
                    print("Unknown command")

def winnowAllMessages(LPQ, SECRET_KEY):
    numMessages = len(LPQ)
    if numMessages == 0:
        print("No messages to winnow yet\n")
        return

    # animation
    sleepFactor = math.log10(numMessages) + numMessages * 2
    sleepFactor = sleepFactor * 0.01
    # print("Sleep Factor: " + str(sleepFactor))
    for i in range(100):
        print("\rWinnowing messages...[{}%]".format(i), end="")
        time.sleep(sleepFactor)
    print("\rWinnowing messages...[100%]")

    for message in LPQ:
        winnow(message, SECRET_KEY)
    LPQ.clear()

def winnow(message, SECRET_KEY):
    # strip off the name and the message code
    messageParts = message.split(";")
    print("From: {}".format(messageParts[1]))

    line = ""
    for x in range(len(messageParts))[2:]:
        if x % 2 == 0:
            line += messageParts[x]
            line += " "
        else:
            line += messageParts[x]
            hash_result = Hashing.check_hash(messageParts[x - 1], messageParts[x], str(SECRET_KEY))
            if hash_result:
                line = line + " Hashes Match"
                print (colored(line, "green"))
            else:
                line = line + " Hashes Do Not Match"
                print (colored(line, "red"))
            line = ""
    print()

def receiveMessage(server, lowPriorityMessageQueue, targetMessageType):
    messageHasBeenReceived = False
    while not messageHasBeenReceived:
        # receive possibly multiple messages
        bulkMessage = server.recv(4096).decode()

        # split the messages up into individual messages
        messages = bulkMessage.split("FULL_STOP")

        for message in messages[:-1]:
            messagePieces = message.split(";")
            messageType = message.split(";")[0]
            messageType = MessageCode(messageType)

            # piece the message together without the message type in front
            message = ";".join(messagePieces)

            if messageType == targetMessageType:
                targetMessage = message
                messageHasBeenReceived = True
            else:
                lowPriorityMessageQueue.append(message)

    return targetMessage

def exitSequence(server):
    print("Exiting...")
    exit(0)

def sendMessage(server, SECRET_KEY):
    server.send("send".encode())

    # we need to get the most recent list of connections
    listOfClients = pickle.loads(server.recv(2048))
    print(listOfClients)
    # lowercase everything - Look up python list comprehension for syntax below
    # lowerlistOfClients = [i.lower() for i in listOfClients]

    # prompt the user for who to send a message to
    validName = False
    while not validName:
        userChoice = input("Who to send to? ").lower()
        if userChoice == 'cancel':
            server.send("cancel".encode())
            print()
            return
        for client in listOfClients:
            if client.lower() == userChoice:
                targetClient = client
                validName = True

    # create the message and the chaffs
    message = createMessage(targetClient, SECRET_KEY)

    # animation
    sleepFactor = 0.01
    for i in range(100):
        print("\rTransmitting message...[{}%]".format(i), end="")
        time.sleep(sleepFactor)
    print("\rTransmitting message...[100%]")

    server.send(message.encode())
    print()

def createMessage(targetClient, SECRET_KEY):
    numberOfChaffs = 3
    validMessage = False
    while not validMessage:
        phrases = []
        phrase = input ("Enter your correct message: ")
        if phrase.lower() == 'cancel':
            return "cancel"

        phrase = phrase + ";" + Hashing.get_hash_(phrase, str(SECRET_KEY)) + ";"
        phrases.append(phrase)
        for x in range (numberOfChaffs - 1):
            phrase = input ("Enter a fake message: ")
            if phrase.lower() == 'cancel' or phrase.lower() == 'redo':
                break
            phrase = phrase + ";" + Hashing.get_hash_(phrase, str(random.random() * int(SECRET_KEY))) + ";"
            phrases.append(phrase)

        if phrase.lower() == 'cancel':
            return "cancel"
        elif phrase.lower() == 'redo':
            continue

        random.shuffle(phrases)
        validMessage = True

    fullMessage = "LOW;" + targetClient + ";" + ''.join(phrases) + "FULL_STOP"
    return fullMessage

def getClientSetup(server):
    server.send("client_setup".encode())
    setup = server.recv(2048).decode().split(";")
    stones = setup[0]
    print("Stone(s): " + stones)
    location = setup[1]
    print("Location: " + location)
    if len(setup) > 3:
        print("You are the Gatherer!")
    print()


def getLocationList(server):
    server.send("location_list".encode())
    print(pickle.loads(server.recv(2048)))
    print()

def getListOfCommands(server):
    server.send("help".encode())
    print(pickle.loads(server.recv(2048)))
    print()

def getClientList(server):
    server.send("client_list".encode())
    print(pickle.loads(server.recv(2048)))
    print()

def displayNotifications(lowPriorityMessageQueue):
    numLowPriority = len(lowPriorityMessageQueue)
    if numLowPriority > 0:
        print("You have {} messages to winnow! Type 'winnow' to winnow remaining messages!".format(numLowPriority))
        print()

def setupClient(server):
    # send opening message
    server.send("connect".encode())

    # check if server is full
    if server.recv(1024).decode() == "full":
        print("Server is full")
        exit()

    # set up name
    name = ""
    validName = False
    while not validName:
        userChoice = -99
        listOfNames = pickle.loads(server.recv(1024))
        for i in range(len(listOfNames)):
            print("{}. {}".format(i + 1, listOfNames[i]))
        try:
            userChoice = int(input("\nChoose your character: "))
        except ValueError:
            print("Please use numbers for selections")

        while not userChoice or not 1 <= userChoice <= len(listOfNames):
            try:
                userChoice = int(input("Choose your character: "))
            except ValueError:
                print("Please use numbers for selections")

        # once we choose a name from the list, send it to the server for approval
        server.send(listOfNames[userChoice - 1].encode())
        serverResponse = server.recv(1024).decode()
        if serverResponse == "True":
            validName = True
            name = listOfNames[userChoice - 1]
            message = server.recv(1024).decode()

    # receive sessionKey and secret key
    SECRET_KEY = message.split(";")[1]
    sessionKey = message.split(";")[0]

    # write the session key to a file
    file = open("SessionKey.txt", "w+")
    file.write(str(sessionKey))
    file.close()

    nameColor, locationColor = customizePrompt()

    print("Waiting for game to start...")
    setup = server.recv(2048).decode().split(";")
    print()
    stones = setup[0]
    print("Stone(s): " + stones)
    location = setup[1]
    print("Location: " + location)
    if len(setup) > 3:
        print("You are the Gatherer! You must locate the 6 Infinity Stones before Thanos can find them!")

    return name, nameColor, locationColor, location, SECRET_KEY

def reconnect(server):
    server.send("reconnect".encode())
    sessionKey = 0
    if os.path.isfile("SessionKey.txt"):
        with open("sessionKey.txt", "r") as file:
            sessionKey = file.readline()
    else:
        sessionKey = input("SessionKey.txt not found, please enter a session key")
    # block until server is ready
    server.recv(1024)
    server.send(sessionKey.encode())

    # receive confirmation from server
    if server.recv(1024).decode() == "invalid":
        print("Invalid session key")
        exit()

    name = server.recv(1024).decode()
    # receive SECRET KEY
    SECRET_KEY = server.recv(1024).decode()
    nameColor, locationColor = customizePrompt()

    server.send("setup".encode())
    setup = server.recv(2048).decode().split(";")
    print()
    stones = setup[0]
    print("Stone(s): " + stones)
    location = setup[1]
    print("Location: " + location)
    if len(setup) > 3:
        print("You are the Gatherer! You must locate the 6 Infinity Stones before Thanos can find them!")

    return name, nameColor, locationColor, location, SECRET_KEY

def customizePrompt():
    print("\nname@location $   <---- Default Prompt")

    valid_choice = False
    list_of_colors = ["none", "red", "green", "yellow", "blue", "magenta","cyan","white"]
    color_choice = ""
    print(list_of_colors)
    print()
    while not valid_choice:
        color_choice = input ("Please select a color for your name: ").lower()
        if color_choice in list_of_colors:
            if color_choice == "none":
                color_choice = "white"
            valid_choice = True
    name_choice = color_choice
    valid_choice = False
    while not valid_choice:
        color_choice = input ("Please select a color for your Location: ").lower()
        if color_choice in list_of_colors:
            if color_choice == "none":
                color_choice = "white"
            valid_choice = True
    location_choice = color_choice

    return name_choice, location_choice

if __name__ == "__main__":
    main(sys.argv)
