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

    def addClient(self, name, ip_address):
        self.matrix[self.numberOfClients][0] = name
        self.matrix[self.numberOfClients][1] = ip_address
        # print ("Added " + name + " on ip_address: " + str(ip_address))
        self.numberOfClients += 1

    def findClient(self, name):
        for x in range(self.numberOfClients):
            if (self.compareStrings(name, self.matrix[x][0])):
                return self.matrix[x][1]
        return -1

    def deleteClient(self, name):
        for x in range(self.numberOfClients):
            #if (name == self.matrix[x][0]):
            if (self.compareStrings(name, self.matrix[x][0])):
                for y in range(x, self.numberOfClients - 1):
                    self.matrix[y][0] = self.matrix[y + 1][0]
                    self.matrix[y][1] = self.matrix[y + 1][1]
                self.numberOfClients -= 1
                return 1
        return -1

    def display(self):
        for x in range(self.numberOfClients):
            print(self.matrix[x])

    def compareStrings(self, str1, str2):
        str1 = str1.replace(" ", "")
        str2 = str2.replace(" ", "")
        if str1.lower() == str2.lower():
            print ("Comparing {} and {}".format(str1.lower(), str2.lower()))
            return True
        return False

    def getAllClients(self):
        clientList = []
        for client in range(self.numberOfClients):
            clientList.append(self.matrix[client][0])
        return clientList

if __name__ == "__main__":
    cd = ClientDirectory(10)
    cd.addClient("Will", 2)
    cd.addClient("Nancy", 3)
    cd.addClient("Caesar", 4)
    cd.addClient("Andrew McDole", 0)
    if (cd.allClientsConnected()):
        print ("All clients connected")
    cd.addClient("Josh", 1)
    if (cd.allClientsConnected()):
        print ("All clients connected")
    print ("ip_address for Andrew: {}".format(cd.findClient("    Andr ew Mcdole")))
    print ("ip_address for Josh: {}".format(cd.findClient("Josh")))
    print ("ip_address for James: {}".format(cd.findClient("James")))
    print ("Removing Client Josh: {}".format(cd.deleteClient("  josh   ")))
    cd.display()
    print (cd.getAllClients())
