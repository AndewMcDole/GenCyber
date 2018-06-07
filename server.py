#!/usr/local/bin/python3

# Python program to implement server side of chat room.
import socket
import select
import sys
from _thread import *
import netifaces as ni
ni.ifaddresses('en0')

import ClientDirectory

"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
    print ("Correct usage: script, port number, number of clients")
    exit()

# ip address is found using netifaces and is the machine this script is called from
IP_address = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

# takes first argument from command prompt as port number
Port = int(sys.argv[1])

# tales second argument from command prompt as number of clients
Number_Of_Clients = int(sys.argv[2])
"""
binds the server to an entered IP address and at the
specified port number.
The client must be aware of these parameters
"""
server.bind((IP_address, Port))
server.listen(Number_Of_Clients)

client_directory = ClientDirectory.ClientDirectory(Number_Of_Clients)
# list_of_clients = []

def clientthread(conn, addr):

    # sends a message to the client whose user object is conn
    conn.send("Welcome to the Avenger's Stone Hunt Game!".encode())
    name = conn.recv(2048).decode()

    while True:
            try:
                message = conn.recv(2048)
                if message:

                    """prints the message and address of the
                    user who just sent the message on the server
                    terminal"""
                    print ("<" + addr[0] + "> " + message.decode())

                    # Calls broadcast function to send message to all
                    message_to_send = "<" + addr[0] + "> " + message.decode()
                    broadcast(message_to_send, conn)

                else:
                    """message may have no content if the connection
                    is broken, in this case we remove the connection"""
                    remove(conn)

            except:
                continue

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

    """Maintains a list of clients for ease of broadcasting
    a message to all available people in the chatroom"""
    client_directory.addClient("name", conn)

    # prints the address of the user that just connected
    print (addr[0] + " connected")

    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread,(conn,addr))

conn.close()
server.close()


# import socketserver
# import ClientDirectory
#
# CD = ClientDirectory.ClientDirectory(2)
#
# class AvengerHandler(socketserver.BaseRequestHandler):
#     """
#     The RequestHandler is instantiated once per connection
#     to the server, and must override the handle() method
#     to implement communication to the client
#     """
#
#     def handle(self):
#         # print("Request Received")
#         self.data = self.request.recv(1024).strip()
#         message = self.data.decode()
#         print ("{} wrote: {}".format(self.client_address[0], message))
#         #Check the first character
#         if message[0] == "0":
#             name = message[2:]
#             print ("Adding new client {} to client directory".format(name))
#             CD.addClient(name, self.client_address[0])
#             self.request.send("Thank you for connecting to the Avenger's Stone Hunt".encode())
#         else:
#             print ("Transmitting message")
#
#
# HOST, PORT = "", 6789
#
# #create a server, binding it to localhost on port 6789
# server = socketserver.TCPServer((HOST, PORT), AvengerHandler)
#
# #Activate the server; this will keep running until you interrupt
# server.serve_forever()
