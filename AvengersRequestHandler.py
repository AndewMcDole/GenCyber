import AvengersClientDirectory
import AvengersEnum

class AvengersRequestHandler:
    """
    These are the list of member variables this class contains

    listOfCommands - stores possible commands for clients
    listOfAdminCommands - stores possible commands for admins
    directory - AvengerClientDirectory which holds the clients
    gameStart - True if the game has started or not

    To add new functionality, make sure to create a new function for it
    and to add the ability to call it in the --> process <-- function
    """

    def __init__(self):
        # stores possible commands for clients
        self.listOfCommands = ["help","?"]

        # stoes possible commands for thanos
        self.listOfThanosCommands = ["help","?"]

        # stores possible commands for admins
        self.listOfAdminCommands = ["help","?"]

        # create list of AvengerClientDirectory
        self.directory = AvengersClientDirectory.AvengersClientDirectory()

    def process(self, name, conn, message):
        if not self.directory.hasGameStarted():
            conn.send("Game has not started yet".encode())
            return

        # any new functionality should be added here
        print ("PROCESSING...")

    # this uses the AvengersEnum to give different clients different functionality
    def getListOfCommands(self, name):
        client_group = self.directory.getClientGroup(name)
        if client_group == AvengersEnum.Client_Group.HEROES:
            return self.listOfCommands
        if client_group == AvengersEnum.Client_Group.THANOS:
            return self.listOfThanosCommands
        return self.listOfAdminCommands

    def hasGameStarted(self):
        return self.directory.hasGameStarted()

    def getClientSetup(self, name):
        message = "RESP;" + str(self.directory.getClientSetup(name))
        return message

    """
    ADD/REMOVE/PAUSE Clients
    """
    def addClient(self, conn):
        # send the valid name list


        # The client name is returned with the name;sessionKey;Client_Group
        print ("Name: {}".format(name))
        name_parts = name.split(";")
        name = name_parts[0]
        sessionKey = name_parts[1]
        clientGroup = name_parts[2]

        # check to see if this is a reconnect
        if name == "reconnect":
            if self.directory.reconnect(conn, sessionKey):
                conn.send("Successful Reconnect!".encode())
                name = self.directory.getConnName(conn)
            else:
                conn.send("Unsuccessful Reconnect".encode())
                conn.send("RESP;failure".encode())
                return "Failed Reconnect"

        # Respond to the client with their name, in case it was changed by the directory
        name = self.directory.addClient(name, conn, sessionKey, clientGroup)
        conn.send(str("RESP;" + name).encode())

        return name

    def dropClient(self, name):
        self.directory.dropClient(name)

    def pauseClient(self, name):
        self.directory.pauseClient()
