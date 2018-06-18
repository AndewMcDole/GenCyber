#!/usr/local/bin/python3

# Python program to implement server side of chat room.
import socket
import random
import select
import sys
import datetime
import time
from _thread import *

import ClientDirectory

"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
if len(sys.argv) != 4:
    print ("Correct usage: script, ip address, port number, number of clients")
    exit()

IP_address = sys.argv[1]

# takes first argument from command prompt as port number
Port = int(sys.argv[2])

# tales second argument from command prompt as number of clients
Number_Of_Clients = int(sys.argv[3])
"""
binds the server to an entered IP address and at the
specified port number.
The client must be aware of these parameters
"""
server.bind((IP_address, Port))
server.listen(Number_Of_Clients)

client_directory = ClientDirectory.ClientDirectory(Number_Of_Clients)
# list_of_clients = []

def generateSecretKey(key_length):
    # list of possible key characters
    list_of_characters = ["9","8","7","6","5","4","3","2","1","0"]

    key = ""
    for x in range(key_length):
        key = key + random.choice(list_of_characters)

    return str(key)

# generate secret key of length 12
SECRET_KEY = generateSecretKey(12)

def clientthread(conn, addr):

    # sends a message to the client whose user object is conn
    conn.send("Welcome to the Avenger's Stone Hunt Game!".encode())
    name = conn.recv(2048).decode()

    """Maintains a list of clients for ease of broadcasting
    a message to all available people in the chatroom"""
    if (name != "server_master"):
        stones, location = client_directory.addClient(name, conn)
        conn.send("You have {}\nLocation: {}".format(stones, location).encode())

        # Wait before sending again or the client will receive the data incorrectly
        time.sleep(.2)
        # Send secret key
        conn.send(SECRET_KEY.encode())

        # prints the name and address of the user that just connected
        print (name + " connected on " + addr[0])


    while True:
            try:
                message = conn.recv(2048)
                if message:

                    date_time = datetime.datetime.now()
                    sys.stdout.write("{} ".format(date_time))
                    sys.stdout.flush()

                    if message.decode().split()[0] == "clients_list":
                        sendClientList(name, conn)
                    """prints the message and address of the
                    user who just sent the message on the server
                    terminal"""
                    # print ("<" + name + "> " + message.decode())
                    if (name != "server_master"):
                        sendMessage(message.decode(), name)
                    else:
                        serverMessage(message.decode(), conn)
                    # Calls broadcast function to send message to all
                    # message_to_send = "<" + name + "> " + message.decode()
                    # broadcast(message_to_send, conn)

                else:
                    """message may have no content if the connection
                    is broken, in this case we remove the connection"""
                    remove(conn)

            except:
                continue

def serverMessage(message, conn):
    message_part = message.split(";")[0]
    if (message_part == "game_state"):
        messsage_to_send = client_directory.getGameState()
        conn.send(str(messsage_to_send).encode())
        print ("Server requested GameState")

    elif (message_part == "delete"):
        name_to_delete = message_part.split(";")[1]
        if client_directory.deleteClient(name_to_delete) == 1:
            conn.send("Deleted {}".format(name_to_delete))
        else:
            conn.send("Failed to delete {}".format(name_to_delete))

def sendMessage(message, sender):
    message_parts = message.split(";")
    del message_parts[-1] # remove the last element
    # Locates connection associated with name of client
    destination_client = message_parts[0]
    destination_client_conn = client_directory.findClient(destination_client)

    # The following line displays the destination and the full list in case a client isnt found
    # print ("destination_client: {} {}".format(destination_client, client_directory.getAllClients()))

    # findClient() returns -1 if the client isn't found
    if destination_client_conn != -1:
        print ("<{} to {}>".format(sender, destination_client))

        for i in range(len(message_parts))[1:]:
            if i % 2 == 1:
                sys.stdout.write("{} ".format(message_parts[i]))
                sys.stdout.flush()
            else:
                sys.stdout.write("{}\n".format(message_parts[i]))
                sys.stdout.flush()

        # Remove the receiver name from the beginning and prepend on the sender name
        message_to_send = sender + ";"
        # print (message_parts)
        for message_part in message_parts[1:]:
            message_to_send = message_to_send + message_part + ";"

        list_of_conns = client_directory.getAllConn()
        for conn in list_of_conns:
            if conn == destination_client_conn:
                try:
                    conn.send(message_to_send.encode())
                except:
                    conn.close()

                    # if the link is broken, we remove the client
                    client_directory.deleteConn(conn)
                    print ("Lost connection with {}".format(conn))

def sendClientList(name, conn):
    if name != "server_master":
        print ("Client list requested by {}".format(name))
    else:
        print ("Client list requested by Server")
    message = str(client_directory.getAllClients())
    conn.send(message.encode())

"""Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """
def broadcast(message, connection):
    list_of_conns = client_directory.getAllConn()
    for conn in list_of_conns:
        if conn != connection:
            try:
                conn.send(message.encode())
            except:
                conn.close()

                # if the link is broken, we remove the client
                client_directory.deleteConn(conn)
                print ("Lost connection with {}".format(conn))

while True:

    """Accepts a connection request and stores two parameters,
    conn which is a socket object for that user, and addr
    which contains the IP address of the client that just
    connected"""
    conn, addr = server.accept()

    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread,(conn,addr))

conn.close()
server.close()
