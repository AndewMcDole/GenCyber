import os
import pickle
import socket
import sys
import time

session_list = []
num_sessions = 0

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

def mainGameLoop(server):
    while True:
        print("Playing Stonehunt...")
        time.sleep(10)

def joinSession(server):
    printSessions()
    session = int(input("\nWhich session would you like to connect to? "))
    valid_sessions = range(1, num_sessions + 1)
    if session in valid_sessions:
        server.send("join {}".format(session).encode())
        msg = server.recv(1024).decode()
        if msg == "reject":
            print("Failed to join session...\n")
        elif msg == "running":
            print("Session in progress, if you are reconnecting, please use the reconnect option at the main menu...\n")
        elif msg == "success":
            print("Joined session {} successfully!\n".format(session))
            # Waiting for game to start
            msg = server.recv(2048).decode()
            while msg != "start":
                print(msg, end="")

            # Game has started
            mainGameLoop(server)

    else:
        print("Invalid session")

def displayMainMenu(server):
    userOptions = ["Connect to a session", "Reconnect to a session", "Refresh Session List", "Exit"]
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
        print("Refreshing Session List...")
        # Send request
        server.send("refresh".encode())
        session_list = pickle.loads(server.recv(2048))
        num_sessions = len(session_list)
        printSessions()

    elif userChoice == "4":
        exit()

    else:
        print("Invalid Option")

def printSessions():
    global session_list
    print("\tSession List\n-------------------------")
    for sess in session_list:
        print(sess)


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

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Proper Usage: python3 client.py ip_addr port")
        exit()
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("Client stopped by keyboard...")
