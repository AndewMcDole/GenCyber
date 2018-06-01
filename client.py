#!/usr/local/bin/python3

import socket

s = socket.socket()
host = "10.122.130.230"
port = 6789

s.connect((host, port))
print (s.recv(1024).decode())
s.close()
