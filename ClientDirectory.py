#!/usr/local/bin/python3

class ClientDirectory:

    def __init__(self, numClients):
        self.numberOfClients = 0
        self.maxNumberOfClients = numClients
        self.matrix = [[0 for x in range(2)] for y in range(self.maxNumberOfClients)]

    def allClientsConnected(self):
        if (self.numberOfClients == self.maxNumberOfClients):
            return True
        else:
            return False

    def addClient(self, name, socket):
        self.matrix[self.numberOfClients][0] = name
        self.matrix[self.numberOfClients][1] = socket
        print ("Added " + name + " on socket: " + str(socket))
        self.numberOfClients += 1

    def findSocket(self, name):
        for x in range(self.numberOfClients):
            if (name == self.matrix[x][0]):
                return self.matrix[x][1]
        return -1


if __name__ == "__main__":
    cd = ClientDirectory(2)
    cd.addClient("Andrew", 0)
    if (cd.allClientsConnected()):
        print ("All clients connected")
    cd.addClient("Josh", 1)
    if (cd.allClientsConnected()):
        print ("All clients connected")
    print ("Socket for Andrew: {}".format(cd.findSocket("Andrew")))
    print ("Socket for Josh: {}".format(cd.findSocket("Josh")))
    print ("Socket for James: {}".format(cd.findSocket("James")))
