import pickle
import socket
import sys
import time

if len(sys.argv) != 3:
    print("Correct usage: script, IP Address, port number")
    exit()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((sys.argv[1], int(sys.argv[2])))

server.send("admin".encode())

listOfClients = pickle.loads(server.recv(2048))
for client in listOfClients:
    print(client)

server.close()
