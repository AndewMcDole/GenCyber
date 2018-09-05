import enum
import math
import os
import pickle # used for serializing lists allowing them to be sent over sockets
import random
import select
import socket
import sys
from sys import platform
from termcolor import colored
import time
from threading import *
import threading
import colorama

import Hashing

class MessageCode(enum.Enum):
    HIGH_PRIORITY="HIGH"
    LOW_PRIORITY="LOW"
    FULL_STOP="FULL_STOP"

class stdinThread(threading.Thread):
    def run(self):
        global commandQueue
        while True:
            message = sys.stdin.readline()
            if message == "\n":
                commandQueue.append("newline")
            else:
                command = message.split()[0]
                if (command.lower() == "help" or command == "?"):
                    commandQueue.append("help")
                elif (command.lower() == "who"):
                    commandQueue.append("who")
                elif (command.lower() == "locations"):
                    commandQueue.append("locations")
                elif (command.lower() == "setup"):
                    commandQueue.append("setup")
                elif (command.lower() == "send"):
                    commandQueue.append("send")
                    return
                elif (command.lower() == "exit"):
                    commandQueue.append("exit")
                    return
                elif (command.lower() == "clear"):
                    commandQueue.append("clear")
                elif (command.lower() == "winnow"):
                    commandQueue.append("winnow")
                else:
                    commandQueue.append("unknown")

def main(argv):
    print("Connecting to server on {} on port {}".format(argv[1], argv[2]))
    server = setupNetwork(argv[1], argv[2])

    # receive initial session list
    global session_list
    global  num_sessions
    session_list = pickle.loads(server.recv(2048))
    num_sessions = len(session_list)

    while True:
        displayMainMenu(server)

def setupNetwork(ip_addr, port):
    port = int(port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # animation
    sleepFactor = 0.01
    for i in range(100):
        print("\rConnecting to server...[{}%]".format(i), end="")
        time.sleep(sleepFactor)
    print("\rConnecting to server...[100%]")

    server.connect((ip_addr, port))
    return server

def joinSession(server):
    printSessions()
    global sessionNum
    sessionNum = int(input("\nWhich session would you like to connect to? "))
    valid_sessions = []
    global list_of_sessions
    for sess in session_list:
        valid_sessions.append(int(sess.split(" ")[1]))

    if sessionNum in valid_sessions:
        server.send("join {}".format(sessionNum).encode())
        msg = server.recv(1024).decode()
        print (msg)
        if msg == "reject":
            print("Failed to join session...\n")
        elif msg == "running":
            print("Session in progress, if you are reconnecting, please use the reconnect option at the main menu...\n")
        elif msg == "success":
            print("Joined session {} successfully!\n".format(sessionNum))
            # Waiting for game to start
            msg = server.recv(512).decode()
            while msg != "start":
                if msg == "close":
                    print("\nSession closed by server...\n")
                    return

                print(msg, end="")
                msg = server.recv(512).decode()
            print()
            # Game has started
            name, nameColor, location, locationColor, key = setupClient(server)

            mainGameLoop(server, name, nameColor, locationColor, location, key)

    else:
        print("Invalid session")

def displayMainMenu(server):
    userOptions = ["Connect to a session", "Reconnect to a session", "Create a new session", "Refresh Session List", "Exit"]
    print()
    for i in range(len(userOptions)):
        print("{}. {}".format(i + 1, userOptions[i]))
    try:
        userChoice = input("\nWhat would you like to do? ")
    except ValueError:
        print("Please use numbers for selections")

    while not userChoice or int(userChoice) not in range(len(userOptions) + 1):
        try:
            userChoice = input("What would you like to do? ")
        except ValueError:
            print("Please use numbers for selections")

    global num_sessions
    global session_list

    if userChoice == "1":
        joinSession(server)

    elif userChoice == "2":
        print("Reconnecting to previous session")
        # can be closed or refused

    elif userChoice == "3":
        numPlayers = input("\nHow many players will be in this new session? ")
        server.send(("create " + str(numPlayers)).encode())

    elif userChoice == "4":
        print("Refreshing Session List...")
        # Send request
        server.send("refresh".encode())
        session_list = pickle.loads(server.recv(2048))
        num_sessions = len(session_list)
        printSessions()

    elif userChoice == "5":
        exit()

    else:
        print("Invalid Option")

def setupClient(server):
    # set up name
    name = ""
    validName = False
    while not validName:
        userChoice = -99
        listOfNames = pickle.loads(server.recv(1024))
        for i in range(len(listOfNames)):
            print("{}. {}".format(i + 1, listOfNames[i]))
        try:
            userChoice = int(keyboardInput("\nChoose your character: "))
        except ValueError:
            print("Please use numbers for selections")

        while not userChoice or not 1 <= userChoice <= len(listOfNames):
            try:
                userChoice = int(keyboardInput("Choose your character: "))
            except ValueError:
                print("Please use numbers for selections")

        # once we choose a name from the list, send it to the server for approval
        server.send(listOfNames[userChoice - 1].encode())
        print("Waiting for name approval...")
        serverResponse = server.recv(1024).decode()
        if serverResponse == "True":
            validName = True
            name = listOfNames[userChoice - 1]
            print("Waiting on session key...")
            message = server.recv(1024).decode()

    # receive sessionKey and secret key
    SECRET_KEY = message.split(";")[1]
    sessionKey = message.split(";")[0]

    server.send("ready".encode())

    # write the session key to a file
    global sessionNum
    file = open("SessionKey.txt", "w+")
    file.write(str(sessionNum) + ";" + str(sessionKey))
    file.close()

    nameColor, locationColor = customizePrompt()

    # Tell the server that we are ready and waiting for the game to start
    server.send("ready".encode())

    print("Waiting for game to start...")
    setup = server.recv(2048).decode().split(";")

    print()
    stones = setup[0]
    print("Stone(s): " + stones)
    location = setup[1]
    print("Location: " + location)
    if len(setup) >= 3:
        print("You are the Gatherer! You must locate the 6 Infinity Stones before Thanos can find them!")

    return name, nameColor, locationColor, location, SECRET_KEY

def reconnect(server):
    server.send("reconnect".encode())
    sessionKey = 0
    if os.path.isfile("SessionKey.txt"):
        with open("SessionKey.txt", "r") as file:
            sessionKey = file.readline()
    else:
        sessionKey = keyboardInput("SessionKey.txt not found, please enter a session key")
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

def mainGameLoop(server, name, nameColor, locationColor, location, SECRET_KEY):
    lowPriorityMessageQueue = []
    global commandQueue
    commandQueue = []

    if sys.platform == "win32":
        colorama.init()

    global stdin
    stdin = stdinThread()
    stdin.start()

    while True:
        sys.stdout.write("{}@{}$ ".format(colored(name, nameColor), colored(location, locationColor)))
        sys.stdout.flush()

        commandExecuted = False

        while not commandExecuted:
            if executeCommand(server, lowPriorityMessageQueue, SECRET_KEY):
                commandExecuted = True
            else:
                server.settimeout(0.01)
                message = ""
                try:
                    message = receiveMessage(server, lowPriorityMessageQueue, MessageCode.LOW_PRIORITY)
                    if message != "":
                        commandExecuted = True

                    print("Message Received...")
                    # check for notifications
                    displayNotifications(lowPriorityMessageQueue)
                except:
                    server.settimeout(None)

def executeCommand(server, lowPriorityMessageQueue, SECRET_KEY):
    global commandQueue
    if len(commandQueue) == 0:
        return False

    next_command = commandQueue[0]

    if next_command == "help":
        getListOfCommands(server)
    elif next_command == "who":
        getClientList(server)
    elif next_command == "locations":
        getLocationList(server)
    elif next_command == "setup":
        getClientSetup(server)
    elif next_command == "send":
        sendMessage(server, SECRET_KEY)
    elif next_command == "exit":
        exitSequence()
    elif next_command == "clear":
        clearSequence()
    elif next_command == "winnow":
        winnowAllMessages(lowPriorityMessageQueue, SECRET_KEY)
    elif next_command == "unknown":
        print ("Unknown message...")

    commandQueue.pop(0)
    return True

def sendMessage(server, SECRET_KEY):

    server.send("send".encode())

    # we need to get the most recent list of connections
    listOfClients = pickle.loads(server.recv(2048))
    print(listOfClients)

    # prompt the user for who to send a message to
    validName = False
    while not validName:
        userChoice = input("Who to send to? ").lower()
        if userChoice == 'cancel':
            server.send("cancel".encode())
            print()
            stdin = stdinThread()
            stdin.start()
            return
        for client in listOfClients:
            if client.lower() == userChoice:
                targetClient = client
                validName = True

    # create the message and the chaffs
    message = createMessage(targetClient, SECRET_KEY)

    if message != "cancel":
        # animation
        sleepFactor = 0.01
        for i in range(100):
            print("\rTransmitting message...[{}%]".format(i), end="")
            time.sleep(sleepFactor)
        print("\rTransmitting message...[100%]")

    server.send(message.encode())
    print()
    stdin = stdinThread()
    stdin.start()

def createMessage(targetClient, SECRET_KEY):
    numberOfChaffs = 3
    validMessage = False
    while not validMessage:
        phrases = []
        phrase = keyboardInput ("Enter your correct message: ")
        if phrase.lower() == 'cancel':
            return "cancel"

        phrase = phrase + ";" + Hashing.get_hash_(phrase, str(SECRET_KEY)) + ";"
        phrases.append(phrase)
        for x in range (numberOfChaffs - 1):
            phrase = keyboardInput ("Enter a fake message: ")
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
    print("\nFrom: {}".format(messageParts[1]))

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
    messages = [" "]
    while not messageHasBeenReceived and len(messages) > 0:
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

            if messageType == MessageCode.LOW_PRIORITY:
                lowPriorityMessageQueue.append(message)
            if messageType == targetMessageType:
                targetMessage = message
                messageHasBeenReceived = True

            messages.remove(message)

    return targetMessage

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

def displayNotifications(lowPriorityMessageQueue):
    numLowPriority = len(lowPriorityMessageQueue)
    if numLowPriority > 0:
        print("You have {} messages to winnow! Type 'winnow' to winnow remaining messages!".format(numLowPriority))
        print()

def printSessions():
    global session_list
    print("\n\tSession List\n-------------------------")
    for sess in session_list:
        print(sess)

def exitSequence():
    global stdin
    print("Exiting...")
    if sys.platform == "linux" or sys.platform == "linux2":
        exit(0)
    elif sys.platform == "win32":
        sys.exit()

def clearSequence():
    if sys.platform == "linux" or sys.platform == "linux2":
        os.system("clear")
    elif sys.platform == "win32":
        os.system("cls")

def getClientSetup(server):
    server.send("client_setup".encode())
    setup = server.recv(2048).decode().split(";")
    stones = setup[0]
    print("Stone(s): " + stones)
    location = setup[1]
    print("Location: " + location)
    if len(setup) >= 3:
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

def keyboardInput(prompt):
    _input = input(prompt)
    # using a list to make modifications instead of modifying the string
    editedList = list(_input)

    list_of_forbidden_chars = [";"]
    # Sanitize input for any characters that would cause issues
    for forb_char in list_of_forbidden_chars:
        editedList = [i for i in editedList if i != forb_char]


    # rejoin the input list back together to a string
    output = "".join(editedList)
    return output

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Proper Usage: python3 client.py ip_addr port")
        exit()
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("Client stopped by keyboard...")
