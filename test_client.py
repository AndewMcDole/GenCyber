import os
import pickle # used for serializing lists allowing them to be sent over sockets
import socket
import sys
from termcolor import colored

def main(argv):
    if len(sys.argv) != 3:
        print("Correct usage: script, IP Address, port number")
        exit()
    displayMainMenu(sys.argv)

def setupNetwork(ip_addr, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        print("Connecting to server...")
        server = setupNetwork(argv[1], int(argv[2]))
        print("Setting up client...")
        name = setupClient(server)
        mainGameLoop(server, name)

    elif userChoice == "2":
        print("Reconnecting to server...")
        server = setupNetwork(argv[1], int(argv[2]))
        print("Sending session key...")
        name = reconnect(server)
        mainGameLoop(server, name)

    else:
        print("Exiting...")

def mainGameLoop(server, name):
    nameColor, locationColor = customizePrompt()

    print("Waiting for game to start...")
    setup = server.recv(2048).decode().split(";")
    stones = setup[0]
    print("Stone(s): " + stones)
    location = setup[1]
    print("Location: " + location)
    if len(setup) > 3:
        print("You are the Gatherer! You must locate the 6 Infinity Stones before Thanos can find them!")

    while True:

        sys.stdout.write("{}@{}$ ".format(colored(name, nameColor), colored("location", locationColor)))
        sys.stdout.flush()

        server.recv(1024).decode()

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
            sessionKey = server.recv(1024).decode()

    # write the session key to a file
    file = open("SessionKey.txt", "w+")
    file.write(str(sessionKey))
    file.close()

    return name

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
    return name

def customizePrompt():
    print("\nname@location $   <---- Default Prompt")

    valid_choice = False
    list_of_colors = ["none", "red", "green", "yellow", "blue", "magenta","cyan","white"]
    color_choice = ""
    print (list_of_colors)
    while not valid_choice:
        color_choice = input ("\nPlease select a color for your name: ").lower()
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
