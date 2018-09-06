import datetime
from termcolor import colored
import time
import os
import pickle # used for serializing lists allowing them to be sent over sockets
import random

"""
Client Object
"""

class Client():

    def __init__(self, connection, sessionKey, name):
        self.connection = connection
        self.sessionKey = sessionKey
        self.name = name
        self.stones = []
        self.location = None
        self.isGatherer = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def getSetup(self):
        return self.name, self.stones, self.location, self.sessionKey, self.isGatherer

    def getConn(self):
        return self.connection

    def getName(self):
        return self.name

    def getStones(self):
        return self.stones

    def addStone(self, stone):
        self.stones.append(stone)

    def getLocation(self):
        return self.location

    def setLocation(self, location):
        self.location = location

    def checkGatherer(self):
        return self.isGatherer

    def setGatherer(self):
        self.isGatherer = True

    def getSessionKey(self):
        return self.sessionKey

    def reconnectClient(self, conn):
        self.connection = conn
        return self.name


class Admin():

    def __init__(self, connection):
        self.connection = connection

    def __str__(self):
        return "admin"

"""
Stone Hunt Game
"""

class StoneHuntGame:

    def __init__(self, NumPlayers):
        self.listOfClients = []
        self.listOfAdmins = []
        self.maxNumClients = NumPlayers
        self.numClientsReady = 0

        # store list of possible character names from text file
        currDir = os.getcwd()
        characterFilepath = os.path.join(currDir, "CharacterList.txt")
        self.characterList = []
        characterFile = open(characterFilepath, "r")
        for line in characterFile:
            self.characterList.append(line.strip("\n"))

        # Names are moved from valid to used so clients cant choose the same name
        self.valid_hero_names = self.characterList.copy()
        self.used_hero_names = []

        # store list of possible locations from text file
        locationsFilepath = os.path.join(currDir, "Locations.txt")
        self.locationsList = []
        locationFile = open(locationsFilepath, "r")
        for line in locationFile:
            self.locationsList.append(line.strip("\n"))

        self.valid_locations = self.locationsList.copy()
        self.used_locations = []

        # 1 session key per hero connected
        self.used_session_keys = []

        # switches to True when the gmae has started
        self.gameHasStarted = False

        self.SECRET_KEY = str(123)# self.generateSecretKey(10)

    def process(self, conn, message):
        command = message.split(";")[0]
        if command == "client_list":
            self.clientList(conn)
        elif command == "help":
            self.commandList(conn)
        elif command == "location_list":
            self.locationList(conn)
        elif command == "client_setup":
            self.sendClientSetup(conn)
        elif command == "send":
            self.transmitMessage(conn)

    """
    Commands
    """

    def transmitMessage(self, conn):
        # transmit client list
        listOfClients = []
        for client in self.listOfClients:
            listOfClients.append(str(client))
        conn.send(pickle.dumps(listOfClients))

        # receive the destination client and the message
        message = conn.recv(2048).decode()
        if message == "cancel":
            return

        sender = self.findClient(conn)
        receiver = message.split(";")[1]
        receiver = self.findClient(None,receiver)
        print("{} {} to {}".format(colored(datetime.datetime.now(), "green"), colored(sender,"cyan"), colored(receiver, "cyan")))

        # print out the message starting after the LOW;RECEIVER until the second to last
        messageParts = message.split(";")
        for i in range(len(messageParts))[2:-1]:
            if i % 2 == 0:
                print(colored(messageParts[i], "white"), end='')
            else:
                print(" " + colored(messageParts[i], "red"))
        print()

        # replace the name of the sender with the name of the receiver
        messageParts[1] = str(sender)
        message = ";".join(messageParts)

        # send the message to the proper client
        receiverConn = receiver.getConn()
        receiverConn.send(message.encode())


    def locationList(self, conn):
        conn.send(pickle.dumps(self.locationsList))

    def commandList(self, conn):
        listOfCommands = ["help","who","setup","locations","clear","send","winnow","exit"]
        conn.send(pickle.dumps(listOfCommands))

    def clientList(self, conn):
        request_client = self.findClient(conn)
        listOfClients = []
        for client in self.listOfClients:
            listOfClients.append(str(client))
        conn.send(pickle.dumps(listOfClients))
        print("{} Client list requested by {}".format(colored(datetime.datetime.now(), "green"), colored(str(request_client), "cyan")))

    # Should only be given to the admin
    def sendGameState(self, conn):
        listOfClients = []
        for client in self.listOfClients:
            name, stones, location, key, isGatherer = client.getSetup()
            setup = str(name + " " + str(stones) + " " + location + " " + str(isGatherer) + " " + key)
            listOfClients.append(setup)
        conn.send(pickle.dumps(listOfClients))
        return False

    """
    Connections and game setup
    """

    def clientReady(self, conn, sessionKey, name):
        # create a new client object with this information
        client = Client(conn, sessionKey, name)
        self.listOfClients.append(client)

        # check to see if enough clients have connected to start the game
        if len(self.listOfClients) >= int(self.maxNumClients):
            self.initializeGame()

        self.numClientsReady += 1
        print(str(self.numClientsReady) + " " + str(self.maxNumClients)
        if int(self.numClientsReady) == int(self.maxNumClients)):
            print("All players ready, begin!")
            self.gameHasStarted = True
        else:
            print("jksdgvckhwdjgvckjweghv")

    def addClient(self, conn, sessionID):
        validName = False
        while not validName:
            conn.send(pickle.dumps(self.valid_hero_names))
            name = conn.recv(1024).decode()

            # if the client sends an empty message, it is likely they disconnected
            if not name:
                return False

            if name in self.valid_hero_names:
                self.valid_hero_names.remove(name)
                self.used_hero_names.append(name)
                validName = True
                conn.send("True".encode())
            else:
                conn.send("False".encode())

        sessionKey = self.generateSessionKey(4)
        message = str(sessionID) + ";" + str(sessionKey) + ";" + str(self.SECRET_KEY)
        conn.send(message.encode())
        conn.recv(1024).decode()
        time.sleep(0.01)

        # wait for the client to indicate they are ready to start
        readyMessage = conn.recv(1024).decode()
        if readyMessage == "ready":
            self.clientReady(conn, sessionKey, name)
            return True
        return False

    def reconnect(self, conn):
        # The message does no matter, we are telling the client the server is ready to receive
        conn.send("Ready to receive".encode())
        # receive the session key
        sk = conn.recv(1024).decode()
        # print("Received session key: " + sk)

        # check all of the clients to see if they have a matching key
        for client in self.listOfClients:
            if client.getSessionKey() == sk:
                conn.send("valid".encode())
                # overwrite connection and return name to client
                name = client.reconnectClient(conn)
                conn.send(name.encode())
                time.sleep(0.1)
                conn.send(self.SECRET_KEY.encode())
                return True

        conn.send("invalid".encode())
        return False

    def generateSessionKey(self, keyLength):
        # list of possible key characters
        list_of_characters = ["9","8","7","6","5","4","3","2","1","0"]
        validKey = False
        while not validKey:
            key = ""
            for x in range(keyLength):
                key = key + random.choice(list_of_characters)
            if key not in self.used_session_keys:
                validKey = True
                self.used_session_keys.append(key)

        return str(key)

    def generateSecretKey(self, keyLength):
        # list of possible key characters
        list_of_characters = ["9","8","7","6","5","4","3","2","1","0"]
        validKey = False
        while not validKey:
            key = ""
            for x in range(keyLength):
                key = key + random.choice(list_of_characters)

        return str(key)

    def hasGameStarted(self):
        return self.gameHasStarted

    def findClient(self, conn=None, name=None):
        if conn != None:
            for client in self.listOfClients:
                if client.getConn() == conn:
                    return client
        if name != None:
            for client in self.listOfClients:
                if client.getName() == name:
                    return client
        return -1

    def sendClientSetup(self, conn):
        client = self.findClient(conn)
        if client != -1:
            stones = client.getStones()
            location = client.getLocation()
            isGatherer = client.checkGatherer()
            setup = str(str(stones)+";"+location)
            if isGatherer:
                setup = setup + ";"
            conn.send(setup.encode())

    def initializeGame(self):
        print("All players connected, initializing game state...")
        listOfStones = ["Space Stone", "Reality Stone", "Power Stone", "Mind Stone", "Time Stone", "Soul Stone"]

        # everyone will get a location
        for client in self.listOfClients:
            location = random.choice(self.valid_locations)
            client.setLocation(location)
            self.valid_locations.remove(location)
            self.used_locations.append(location)

        # 1,2,3, and 6 players are special where the stones can be distributed evenely
        if len(self.listOfClients) <= 3 or len(self.listOfClients) == 6:
            while len(listOfStones) > 0:
                for client in self.listOfClients:
                    stone = random.choice(listOfStones)
                    listOfStones.remove(stone)
                    client.addStone(stone)
        # 4 or 5 clients, everyone will get at least 1
        elif len(self.listOfClients) == 4 or len(self.listOfClients) == 5:
            for client in self.listOfClients:
                stone = random.choice(listOfStones)
                listOfStones.remove(stone)
                client.addStone(stone)
            while len(listOfStones) > 0:
                client = random.choice(self.listOfClients)
                stone = random.choice(listOfStones)
                listOfStones.remove(stone)
                client.addStone(stone)
        # 7 or more players, just random distribution
        else:
            while len(listOfStones) > 0:
                client = random.choice(self.listOfClients)
                stone = random.choice(listOfStones)
                listOfStones.remove(stone)
                client.addStone(stone)

        # choose the gatherer
        client = random.choice(self.listOfClients)
        client.setGatherer()
