#!/usr/local/bin/python3

import socket
import sys

# s = socket.socket()
# host = "127.0.0.1"
# port = 6789
#
# s.connect((host, port))
# print ("Successfully Connected to Server")
# # print (s.recv(1024).decode())
# s.close()

HOST, PORT = "localhost", 6789
data = " ".join(sys.argv[1:])

# Create a socket to server and send data
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server and send data
    sock.connect((HOST, PORT))
    sock.send((data + "\n").encode())

    # Receive data form the server and shut down
    received = sock.recv(1024)
finally:
    sock.close()

print ("Sent:    {}".format(data))
print ("Received:    {}".format(received))
