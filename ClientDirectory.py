#!/usr/local/bin/python3

import random
import os
filepath = os.getcwd()
filepath = os.path.join(filepath, "locations.txt")

# list of locations
list_of_locations = []
location_list_file = open(filepath, "r")
num_locations = 0
for line in location_list_file:
    list_of_locations.append(line.strip("\n"))
    num_locations = num_locations + 1

list_of_stones = ["No Stone", "Space Stone", "Reality Stone", "Power Stone", "Mind Stone", "Soul Stone", "Time Stone", "Gatherer"]
list_of_names = ["Iron Man", "Captain America", "Black Panther", "Thor", "Black Widow", "Hulk", "Vision", "Star Lord", "Groot", "Loki"]
names_chosen = []
garbage_list = []

class ClientDirectory:

    def __init__(self, numClients):
        self.numberOfClients = 0
        self.stonesLeft= 7 # include the gatherer role
        self.maxNumberOfClients = numClients
        # targetNumberOfClients will be used for the stone distribution so all of the stones will be distributed
        # targetNumberOfClients will not be changed
        self.targetNumberOfClients = numClients
        self.matrix = [[0 for x in range(4)] for y in range(self.maxNumberOfClients)]

    def getNumClients(self):
        return self.numberOfClients

    def allClientsConnected(self):
        if (self.numberOfClients == self.maxNumberOfClients):
            return True
        else:
            return False

    def addClient(self, name, conn):
        print ("CD: addClient")
        self.matrix[self.numberOfClients][0] = name
        self.matrix[self.numberOfClients][1] = conn
        # print ("Added " + name + " on ip_address: " + str(ip_address))

        # Get a stone and a location
        self.matrix[self.numberOfClients][2] = self.selectStone()
        self.matrix[self.numberOfClients][3] = self.selectLocation()

        self.numberOfClients += 1
        self.resize()
        # self.display()
        return str(self.matrix[self.numberOfClients - 1][2]), str(self.matrix[self.numberOfClients - 1][3])

    def resize(self):
        self.maxNumberOfClients = self.maxNumberOfClients * 2
        self.matrix2 = [[0 for x in range(4)] for y in range(self.maxNumberOfClients)]
        for i in range(self.numberOfClients):
            for j in range(4):
                self.matrix2[i][j] = self.matrix[i][j]
        self.matrix = self.matrix2

    def selectStone(self):
        client_stone = []

        valid_choice = False
        while not valid_choice:
            # print ("Choose 1")
            stone_choice = random.choice(list_of_stones)

            #check to see if the choice that was just picked already was chosen
            if stone_choice not in garbage_list or stone_choice == "No Stone":
                valid_choice = True
                client_stone.append(stone_choice)
                garbage_list.append(stone_choice)
                if stone_choice != "No Stone":
                    self.stonesLeft -= 1

        # print ("{} vs. {}".format(self.stonesLeft, (self.targetNumberOfClients - self.numberOfClients)))
        while self.stonesLeft >= (self.targetNumberOfClients - self.numberOfClients) and self.stonesLeft != 0:
            # print ("Choose 3")
            valid_choice = False
            while not valid_choice:
                stone_choice = random.choice(list_of_stones)

                #check to see if the choice that was just picked already was chosen
                if stone_choice not in garbage_list and stone_choice != "No Stone":
                    valid_choice = True
                    client_stone.append(stone_choice)
                    garbage_list.append(stone_choice)
                    self.stonesLeft -= 1

        # remove unnecessary "No Stone" form listen
        if len(client_stone) > 1 and client_stone[0] == "No Stone":
            client_stone.remove("No Stone")


        # print ("Dice_Roll: {}".format(dice_roll))
        # print ("Stone_Choice: {}".format(client_stone))
        # print ("Stones left: {}".format(self.stonesLeft))
        return client_stone

    def selectLocation(self):
        dice_roll = random.randint(0,10)
        location_choice = random.choice(list_of_locations)
        # print ("Dice_Roll: {}".format(dice_roll))
        # print ("location_Choice: {}".format(location_choice))
        return location_choice

    def findClient(self, name):
        print ("CD: findClient")
        for x in range(self.numberOfClients):
            #print ( self.matrix[x][0])
            if (self.compareStrings(name, self.matrix[x][0])):
                return self.matrix[x][1]
        return int(-1)

    def deleteClient(self, name):
        print ("CD: deleteClient")
        for x in range(self.numberOfClients):
            #if (name == self.matrix[x][0]):
            if (self.compareStrings(name, self.matrix[x][0])):
                for y in range(x, self.numberOfClients - 1):
                    self.matrix[y][0] = self.matrix[y + 1][0]
                    self.matrix[y][1] = self.matrix[y + 1][1]
                    self.matrix[y][2] = self.matrix[y + 1][2]
                    self.matrix[y][3] = self.matrix[y + 1][3]
                self.numberOfClients -= 1
                self.removeName(name)
                return 1
        return -1

    def deleteConn(self, conn):
        print ("CD: deleteConn")
        for x in range(self.numberOfClients):
            #if (name == self.matrix[x][0]):
            if conn == self.matrix[x][1]:
                for y in range(x, self.numberOfClients - 1):
                    self.matrix[y][0] = self.matrix[y + 1][0]
                    self.matrix[y][1] = self.matrix[y + 1][1]
                    self.matrix[y][2] = self.matrix[y + 1][2]
                    self.matrix[y][3] = self.matrix[y + 1][3]
                self.numberOfClients -= 1
                return 1
        return -1

    def display(self):
        for x in range(self.numberOfClients):
            print(self.matrix[x])

    def getGameState(self):
        message_to_send = " "
        for client in range(self.numberOfClients):
            message_to_send = message_to_send + str(self.matrix[client])
            # print (message_to_send)
        return message_to_send

    def compareStrings(self, str1, str2):
        str1 = str1.replace(" ", "")
        str2 = str2.replace(" ", "")
        if str1.lower() == str2.lower():
            # print ("Comparing {} and {}".format(str1.lower(), str2.lower()))
            return True
        return False

    def getAllClients(self):
        print ("CD: getAllClients")
        clientList = []
        for client in range(self.numberOfClients):
            print ( self.matrix[client][0] )
            clientList.append(self.matrix[client][0])
        return clientList

    def getAllConn(self):
        connList = []
        for client in range(self.numberOfClients):
            connList.append(self.matrix[client][1])
        return connList

    def getAllLocations(self):
        return list_of_locations

    def getRemainingNames(self):
        print ("CD: getRemainingNames")
        names = ""
        count = 1
        for name in list_of_names:
            names += ("\n" + str(count) + ". " + name)
            count += 1
        return str(names)

    def validNameByStr(self, name):
        print ("CD: validByStr")
        for name_ in list_of_names:
            if self.compareStrings(name_, name):
                return True
        return False

    def validNameByNum(self, name):
        print ("CD: validByNum")
        name = int(name)
        if name >= 1 and name <= len(list_of_names):
            return True
        return False

    def namePicked(self, name):
        print ("CD: namePicked")
        for name_ in list_of_names:
            if self.compareStrings(name_, name):
                list_of_names.remove(name_)
                names_chosen.append(name_)
                return True

        name = int(name)
        if name >= 1 and name <= len(list_of_names):
            index = int(name) - 1
            name_ = list_of_names[index]
            list_of_names.remove(name_)
            names_chosen.append(name_)
            return True
        return False

    def removeName(self, name):
        print ("CD: removeName")
        for name_ in names_chosen:
            if self.compareStrings(name_, name):
                list_of_names.append(name_)
                names_chosen.remove(name_)

    def getNameByIndex(self, index):
        print ("CD: getNameByIndex")
        return list_of_names[index - 1]

    def getNameByStr(self, name):
        print ("CD: getNameByStr")
        for name_ in list_of_names:
            if self.compareStrings(name_, name):
                return name_
        return "Name not found"

    def castInt(self, name):
        print ("CD: castInt")
        try:
            name = int(name)
            return True
        except ValueError:
            return False

"""
if __name__ == "__main__":
    cd = ClientDirectory(4)
    cd.addClient("Iron Man", 2)
    cd.addClient("Captain", 3)
    print (cd.getAllClients())

    cd.deleteClient("Iron Man")
    print (cd.getAllClients())

    message = "captain\n;Hello;123;Fake;123;Fake;123"
    destination_client = message.split(";")[0]

    print ("Find Client: {}".format(cd.findClient(destination_client)))
"""
