#!/usr/bin/python

import socket

s = socket.socket()
host = "10.122.130.230"
port = 6789

s.connect((host, port))
print (s.recv(1024))
s.close()
