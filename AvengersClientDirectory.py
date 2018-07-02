import os

import AvengersEnum

# Each person that connects will be an AvengersClient object
# Somone can be a hero, thanos (which includes anyone on Thano's team), or admins
class AvengersClient:

    def __init__(self, name, conn, sessionKey):
        self.name = name
        self.conn = conn
        self.sessionKey = sessionKey
        self.activeConnection = True
        self.stone = "Time Stone"
        self.location = "Earth"

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def getName(self):
        return self.name

    def getConn(self):
        return self.conn

    def setConn(self, conn):
        self.conn = conn

    def getSessionKey(self):
        return self.sessionKey

    def getConnectionStatus(self):
        return self.activeConnection

    def setConnectionStatus(self, status):
        self.activeConnection = status

    def getSetup(self):
        setup = self.name + ";" + self.stone + ";" + self.location
        return setup

"""
The directory should not print out things if possible, leave the print outs to the RequestHandler

characterList - stores character names
locationList - stores names of locations
"""

class AvengersClientDirectory:

    def __init__(self):
        # This is the number of heroes needed before game starts
        self.num_heroes_to_start = 2
        self.game_has_started = False

        # initialize lists of clients
        self.list_of_heroes = []
        self.list_of_thanos = []
        self.list_of_admins = []

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

    def getAllClients(self):
        return self.list_of_heroes, self.list_of_thanos, self.list_of_admins

    def getCharacterList(self):
        return self.characterList

    def getLocationsList(self):
        return self.locationsList

    def getClientGroup(self, name):
        for client in self.list_of_heroes:
            if client.getName() == name:
                return AvengersEnum.Client_Group.HEROES

        for client in self.list_of_thanos:
            if client.getName() == name:
                return AvengersEnum.Client_Group.THANOS

        for client in self.list_of_admins:
            if client.getName() == name:
                return AvengersEnum.Client_Group.ADMINS

    def getConnName(self, conn):
        for client in self.list_of_heroes:
            if client.getConn() == conn:
                return client.getName()

        for client in self.list_of_thanos:
            if client.getConn() == conn:
                return client.getName()

        for client in self.list_of_admins:
            if client.getConn() == conn:
                return client.getName()

    def getClientSetup(self, name):
        for client in self.list_of_heroes:
            if client.getName() == name:
                return str(client.getSetup())

    def hasGameStarted(self):
        return self.game_has_started

    def initializeGame(self):
        pass

    """
    Name Checking
    """
    def getValidNames(self):
        return self.valid_hero_names

    def isValidName(self, name):
        if name in self.used_hero_names:
            return false

        self.valid_hero_names.remove(name)
        self.used_hero_names.append(name)

        return True



    """
    ADD/REMOVE/PAUSE/RECONNECT Clients
    """
    def addClient(self, name, conn, sessionKey, clientGroup):
        # Add the user to the correct group based on the client group
        new_client = AvengersClient(name, conn, sessionKey)
        clientGroup = AvengersEnum.Client_Group(clientGroup)
        if clientGroup == AvengersEnum.Client_Group.HEROES:
            self.list_of_heroes.append(new_client)
        elif clientGroup == AvengersEnum.Client_Group.THANOS:
            self.list_of_thanos.append(new_client)
        elif clientGroup == AvengersEnum.Client_Group.ADMINS:
            self.list_of_admins.append(new_client)

        if len(self.list_of_heroes) == self.num_heroes_to_start:
            self.game_has_started = True

        return name

    # client entry is removed
    def dropClient(self, name):
        # remove removes the first instance of the object
        # but no clients should share a name
        self.list_of_heroes.remove(name)
        self.list_of_thanos.remove(name)
        self.list_of_admins.remove(name)

    # client entry remains but is set to inactive
    def pauseClient(self, name):
        # search for the client and change their connection status
        for client in self.list_of_heroes:
            if client.getName() == name:
                client.setConnectionStatus(False)

    def resumeClient(self, name):
        for client in self.list_of_heroes:
            if client.getName() == name:
                client.setConnectionStatus(True)

    def reconnect(self, conn, sessionKey):
        # check the session key
        for client in self.list_of_heroes:
            if client.getSessionKey() == sessionKey:
                # overwrite the existing connectiong with the new one
                client.setConn(conn)
                return True

        for client in self.list_of_thanos:
            if client.getSessionKey() == sessionKey:
                # overwrite the existing connectiong with the new one
                client.setConn(conn)
                return True

        for client in self.list_of_admins:
            if client.getSessionKey() == sessionKey:
                # overwrite the existing connectiong with the new one
                client.setConn(conn)
                return True
                
        return False


if __name__ == "__main__":
    directory = AvengersClientDirectory()
    directory.addClient("Groot", 1, 1, "HEROES")
    directory.addClient("Thanos", 2, 2, "THANOS")
    directory.addClient("Admins", 1, 1, "ADMINS")
    heroes, thanos, admins = directory.getAllClients()
    print ("Heroes: {}".format(heroes))
    print ("Thanos: {}".format(thanos))
    print ("Admins: {}".format(admins))
