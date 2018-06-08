#!/usr/local/bin/python3

import socket
import select
import sys

import ChaffFactory


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print ("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))

#User setup
name = input("Who are you? ")
server.send(name.encode())

# Receive the opening message
message = server.recv(2048)
print (message.decode())

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    # used for chaffing/winnowing
    CF = ChaffFactory.ChaffFactory()

    """ There are two possible input situations. Either the
    user wants to give  manual input to send to other people,
    or the server is sending a message  to be printed on the
    screen. Select returns from sockets_list, the stream that
    is reader for input. So for example, if the server wants
    to send a message, then the if condition will hold true
    below.If the user wants to send a message, the else
    condition will evaluate as true"""
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)

            # Once we receive a message, we need to strip off the name and winnow the message
            message_parts = message.decode().split(";")
        
            print ("< {} >".format(message_parts[0]))
            message_to_winnow = ""
            for message_part in message_parts[1:-2]:
                message_to_winnow = message_to_winnow + message_part + ";"

            CF.winnow(message_to_winnow)
        else:
            message = sys.stdin.readline()
            # Remove the \n created by readline()
            message = message.split("\n")[0]

            # Once the user types a name to send, ask for a message to write
            message = message + ";" + CF.constructMessage()

            server.send(message.encode())
            sys.stdout.write("<You>")
            sys.stdout.write(message)
            sys.stdout.flush()
server.close()
