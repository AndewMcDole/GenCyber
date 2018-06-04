#!/usr/local/bin/python3

import socket

name = input("Who are you? ")
HOST = input("What IP are you trying to connect to? ")
PORT = int(input("What port are you trying to connect to? "))


# Create a socket to server and send data
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server and send data
    sock.connect((HOST, PORT))
    data = name + " "
    sock.send((data).encode())

    # Receive data form the server and shut down
    received = sock.recv(1024)
finally:
    sock.close()

print ("Sent:        {}".format(data))
print ("Received:    {}".format(received.decode()))
